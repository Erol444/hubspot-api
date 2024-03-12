from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from markdownify import markdownify as md
from hubspot_api.private_api.api_client import ApiClient
from .converter import parse_datetime
from .actors import Actor, Actors
from .converter import remove_unsubscribe

@dataclass
class Client:
    clientType: str
    integrationAppId: Optional[int] = None

@dataclass
class DeliveryIdentifier:
    type: str
    value: str

    def to_dict(self):
        return {'type': self.type, 'value': self.value}

@dataclass
class SenderRecipient:
    name: Optional[str] = field(default=None)
    actorId: Optional[str] = field(default=None)
    senderField: Optional[str] = None
    recipientField: Optional[str] = None
    deliveryIdentifier: Optional[DeliveryIdentifier] = field(default=None)

    def to_dict(self):
        result = asdict(self)  # Converts the dataclass to a dict, but we need to handle DeliveryIdentifier separately
        if self.deliveryIdentifier is not None and isinstance(self.deliveryIdentifier, DeliveryIdentifier):
            result['deliveryIdentifier'] = self.deliveryIdentifier.to_dict()
        return result


@dataclass
class Attachment:
    # Assuming minimal structure; adjust fields as needed
    type: str
    details: Dict = field(default_factory=dict)
    fileId: Optional[str] = None
    url: Optional[str] = None
    fileUsageType: Optional[str] = None


@dataclass
class MessageBase:
    id: str
    api: ApiClient
    type: str
    createdAt: datetime
    updatedAt: datetime
    createdBy: str
    client: Client
    """
    Can be multiple senders, if the message was forwarded
    [
        SenderRecipient(name=None, actorId='V-14511701', senderField='ORIGINAL_FROM', recipientField=None, deliveryIdentifier={'type': 'HS_EMAIL_ADDRESS', 'value': 'noreply@extendedforms.io'}),
        SenderRecipient(name='Pavel Svatoš', actorId=None, senderField='FROM', recipientField=None, deliveryIdentifier={'type': 'HS_EMAIL_ADDRESS', 'value': 'pavel.svatos@centrum.cz'})
    ]
    """
    senders: List[SenderRecipient]
    recipients: List[SenderRecipient]
    archived: bool
    conversationsThreadId: int
    channelId: int = None
    channelAccountId: int = None
    text: Optional[str] = None
    richText: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict, api: ApiClient):
        data["createdAt"] = parse_datetime(data.get("createdAt"))
        data["updatedAt"] = parse_datetime(data.get("updatedAt"))
        data["client"] = Client(**data.get("client", {}))
        data["senders"] = [
            SenderRecipient(**sender) for sender in data.get("senders", [])
        ]
        data["recipients"] = [
            SenderRecipient(**recipient) for recipient in data.get("recipients", [])
        ]
        data["attachments"] = [
            Attachment(**attachment) for attachment in data.get("attachments", [])
        ]
        return cls(**data, api=api)

    def get_creator_actor(self) -> Optional[Actor]:
        if self.createdBy is None:
            return None
        return self.get_actors([self.createdBy]).get(self.createdBy)

    def get_actors(self, actors: List[str]) -> Dict[str, Actor]:
        if self.api is None:
            return {}
        res = self.api.api_call(
            "POST",
            "/conversations/v3/conversations/actors/batch/read",
            data={"inputs": actors},
        )
        actors: Actors = Actors.from_dict(res.data)
        dic = dict()
        for actor in actors.results:
            dic[actor.id] = actor
        return dic

    def get_text(self) -> str:
        """
        Either markdown-ified richText (HTML) if available, or plain text
        """
        text = md(self.richText) if self.richText else self.text
        return remove_unsubscribe(text)

    def from_integration(self) -> bool:
        return self.createdBy.startswith('I-')

    def is_newer_than(self, timestamp: datetime) -> bool:
        """
        Returns True if the message is newer than provided timestamp (datetime). Make sure it's in UTC timezone!
        """
        # Ensure self.createdAt is offset-aware by setting its timezone to UTC
        created_at_aware = self.createdAt.replace(tzinfo=timezone.utc)
        return created_at_aware > timestamp

