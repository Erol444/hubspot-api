import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from hubspot_api.public_api.api_client import ApiClient
from .message_base import MessageBase, SenderRecipient
from .conversation import Message, Conversation
from .converter import parse_datetime, to_richtext
from .agents import Agent

@dataclass
class Thread:
    id: str
    api: ApiClient
    createdAt: datetime
    status: str
    latestMessageTimestamp: datetime
    spam: bool
    inboxId: str
    associatedContactId: str
    archived: bool
    originalChannelId: Optional[str] = field(default=None)
    originalChannelAccountId : Optional[str] = field(default=None)
    messages: List[MessageBase] = field(default_factory=list)
    latestMessageReceivedTimestamp: Optional[datetime] = field(default=None)
    closedAt: Optional[datetime] = field(default=None)
    updatedAt: Optional[datetime] = field(default=None)
    latestMessageSentTimestamp: Optional[datetime] = field(default=None)
    assignedTo: Optional[str] = field(default=None)

    @staticmethod
    def from_dict(data: dict, api: ApiClient):
        return Thread(
            api=api,
            id=data.get("id"),
            createdAt=parse_datetime(data.get("createdAt")),
            status=data.get("status"),
            latestMessageTimestamp=parse_datetime(data.get("latestMessageTimestamp")),
            spam=data.get("spam"),
            inboxId=data.get("inboxId"),
            associatedContactId=data.get("associatedContactId"),
            archived=data.get("archived"),
            latestMessageReceivedTimestamp=parse_datetime(data.get("latestMessageReceivedTimestamp")),
            closedAt=parse_datetime(data.get("closedAt")),
            updatedAt=parse_datetime(data.get("updatedAt")),
            latestMessageSentTimestamp=parse_datetime(data.get("latestMessageSentTimestamp")),
            assignedTo=data.get("assignedTo"),
            originalChannelId=data.get("originalChannelId"),
            originalChannelAccountId=data.get("originalChannelAccountId")
        )

    def get_contact(self) -> 'Contact':
        """
        Get contact associated with the thread
        """
        return self.api.get_contact(self.associatedContactId)

    def get_hs_link(self) -> str:
        """
        Gets url for HubSpot conversation thread
        """
        data = self.api.get_acc_info()
        return f"https://{data['uiDomain']}/live-messages/{data['portalId']}/inbox/{self.id}#email"

    def latest_message(self) -> Message:
        """
        Gets latest message
        """
        if len(self.messages) == 0:
            self.messages = self.read_all()
        messages = [x for x in self.messages if isinstance(x, Message)]
        return messages[0]

    def read_all(self) -> List[MessageBase]:
        """
        Read all types of messages in the thread. First message in the list is the newest one.
        """
        res = self.api.api_call("GET", f"/conversations/v3/conversations/threads/{self.id}/messages")
        convo = Conversation.from_dict(res.data, self.api)
        self.messages = convo.results
        return self.messages

    def read_messages(self, oldest_first=False) -> List[Message]:
        """
        Get only messages from the thread. By default, first message in the list is the newest one.
        Args:
            oldest_first (bool): If True, oldest message will be first in the list
        """
        msgs = [x for x in self.read_all() if isinstance(x, Message)]
        if oldest_first:
            msgs.reverse()
        return msgs

    def send_message(self, from_agent: Agent, text: str):
        """
        Reply to the thread. It will copy cc and to fields from the last message

        Returns:
            bool: True if successful
        """
        latest_msg = self.latest_message()

        recipients = [x for x in latest_msg.recipients if x.recipientField != 'BCC']

        sender = [x for x in latest_msg.senders if x.senderField != 'ORIGINAL_FROM'][0]
        if sender.senderField == 'FROM': # If via email
            sender.senderField = None
            sender.recipientField = 'TO'
        recipients.append(sender)

        if latest_msg.channelId == 1000: # If live chat
            sender_actor = latest_msg.get_creator_actor()
            if sender_actor.email: # If they provided their email, rather send them update via email
                # Add to recipients
                recipients.append(SenderRecipient(
                    recipientField='TO',
                    deliveryIdentifier={
                        "type": "HS_EMAIL_ADDRESS",
                        "value": sender_actor.email
                }))

        data = {
            "type": "MESSAGE",
            "text": text,
            "richText": to_richtext(text),
            # "attachments":[{"@type":"MENTIONS","userIds":[27398965]}]
            "recipients": [r.to_dict() for r in recipients],
            "senderActorId": f"A-{from_agent.userId}",
            "channelId": latest_msg.channelId, # Recommended
            "channelAccountId": latest_msg.channelAccountId, # Recommended
            "subject": latest_msg.subject,
        }
        res = self.api.api_call("POST",
                                f"/conversations/v3/conversations/threads/{self.id}/messages",
                                data=data)

        return res.status_code // 100 == 2

    def comment(self, text: str):
        """
        Write a comment to the thread

        Returns:
            bool: True if successful
        """
        data = {
            "type": "COMMENT",
            "text": text,
            "richText": to_richtext(text),
            # "attachments":[{"@type":"MENTIONS","userIds":[27398965]}]
        }
        res = self.api.api_call("POST",
                                f"/conversations/v3/conversations/threads/{self.id}/messages",
                                data=data)

        return res.status_code // 100 == 2

    def update(self, status:str=None, archived:bool=None):
        """
        Args:
            status (str): "CLOSED" or "OPEN"
            archived (bool): True or False
        Returns:
            bool: True if successful
        """
        if status is None and archived is None:
            raise ValueError("You must provide either status or archived")
        data = {}
        if status:
            data["status"] = status
        if archived:
            data["archived"] = archived
        res = self.api.api_call("PATCH", f"/conversations/v3/conversations/threads/{self.id}", data=data)
        return res.status_code // 100 == 2

    def close(self):
        """
        Close the thread (status)
        """
        return self.update(status="CLOSED")
    def open(self):
        """
        Open the thread (status)
        """
        return self.update(status="OPEN")