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

    @classmethod
    def from_dict(cls, data: dict):
        if 'deliveryIdentifier' in data:
            data['deliveryIdentifier'] = DeliveryIdentifier(**data['deliveryIdentifier'])
        return cls(**data)

@dataclass
class Attachment:
    # Assuming minimal structure; adjust fields as needed
    type: str
    details: Dict = field(default_factory=dict)
    fileId: Optional[str] = None
    url: Optional[str] = None
    fileUsageType: Optional[str] = None
    name: Optional[str] = None

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
            SenderRecipient.from_dict(sender) for sender in data.get("senders", [])
        ]
        data["recipients"] = [
            SenderRecipient.from_dict(recipient) for recipient in data.get("recipients", [])
        ]
        data["attachments"] = [
            Attachment(**attachment) for attachment in data.get("attachments", [])
        ]
        return cls(**data, api=api)

    def get_creator_actor(self) -> Optional[Actor]:
        if self.createdBy is None:
            return None
        return self.get_actors([self.createdBy]).get(self.createdBy)

    def get_sender_email(self) -> str:
        """
        Get email of the sender
        """
        try:
            return list(filter(lambda x: x.senderField == 'FROM', self.senders))[0].deliveryIdentifier.value
        except IndexError:
            return 'Unknown'

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
        """
        Checks if the message was created by an integration
        """
        return self.createdBy.startswith('I-')

    def has_attachments(self) -> bool:
        """
        Checks if the message has any attachments
        """
        return len(self.attachments) > 0

    def serialize_attachments(self) -> str:
        """
        Returns a comma-separated list of attachment names
        """
        def file_name(attachment: Attachment) -> str:
            if attachment.type == 'FILE':
                import urllib.parse as urlparse
                from urllib.parse import unquote
                path = urlparse.urlparse(attachment.url).path
                path = unquote(path)
                if '/' in path:
                    path = path.split('/')[-1]
                return path
            return "Unknown attachment type " + attachment.type
        return ", ".join([file_name(a) for a in self.attachments])

    def is_newer_than(self, timestamp: datetime) -> bool:
        """
        Returns True if the message is newer than provided timestamp (datetime). Make sure it's in UTC timezone!
        """
        # Ensure self.createdAt is offset-aware by setting its timezone to UTC
        created_at_aware = self.createdAt.replace(tzinfo=timezone.utc)
        return created_at_aware > timestamp

    def get_hs_link(self) -> str:
        """
        Gets url for HubSpot conversation thread
        """
        data = self.api.get_acc_info()
        return f"https://{data['uiDomain']}/live-messages/{data['portalId']}/inbox/{self.conversationsThreadId}#email"

