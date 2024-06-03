from dataclasses import dataclass, field
from typing import List, Dict, Optional

from markdownify import markdownify as md
from hubspot_api.private_api.api_client import ApiClient
from .paging import Paging
from .message_base import MessageBase
from .converter import remove_unsubscribe

def get_agent(actors, id: str) -> str:
    if id is None:
        return 'Unknown'
    if id == 'S-hubspot':
        return 'CRM'
    actor = actors.get(id)
    return actor.name if actor else id

@dataclass
class Comment(MessageBase):
    def __str__(self):
        actors = self.get_actors([self.createdBy])
        auditer = get_agent(actors, self.createdBy)
        return f"COMMENT FROM {auditer}:\n{self.get_text()}"


@dataclass
class WelcomeMessage(MessageBase):
    def __str__(self):
        return "Thread was created"

@dataclass
class Assignment(MessageBase):
    assignedTo: str = field(default=None)
    assignedFrom: str = field(default=None)

    def __str__(self):
        actors = self.get_actors([self.createdBy, self.assignedTo, self.assignedFrom])
        auditer = get_agent(actors, self.createdBy)
        assignedAgent = get_agent(actors, self.assignedTo)
        unassignedAgent = get_agent(actors, self.assignedFrom)

        if auditer == assignedAgent:
            assignedAgent = 'themself'
        if auditer == unassignedAgent:
            unassignedAgent = 'themself'

        text = auditer
        if unassignedAgent and not assignedAgent:
            text += f' unassigned the thread from {unassignedAgent}'
        elif assignedAgent and not unassignedAgent:
            text += f' assigned the thread to {assignedAgent}'
        elif assignedAgent and unassignedAgent:
            text += f' reassigned the thread from {unassignedAgent} to {assignedAgent}'
        else:
            text += ' updated the thread'
        return text

@dataclass
class StatusChange(MessageBase):
    newStatus: str = field(default=None)

    def __str__(self):
        return f"Thread status changed to {self.newStatus}"

@dataclass
class InboxChange(MessageBase):
    fromInboxId: str = field(default=None)
    toInboxId: str = field(default=None)

    def __str__(self):
        return f"Thread was moved from inbox {self.fromInboxId} to inbox {self.toInboxId}"

@dataclass
class MessageStatus:
    statusType: str # eg. "SENT"
    failureDetails: Optional[Dict] = None

@dataclass
class Message(MessageBase):
    subject: Optional[str] = None
    truncationStatus: Optional[str] = None # eg. TRUNCATED_TO_MOST_RECENT_REPLY or NOT_TRUNCATED
    inReplyToId: Optional[str] = None
    status: Optional[MessageStatus] = None
    direction: Optional[str] = None # OUTGOING or INCOMING

    def has_history(self) -> bool:
        return self.truncationStatus == "TRUNCATED_TO_MOST_RECENT_REPLY"

    def get_history(self) -> str:
        res = self.api.api_call('GET', f"/conversations/v3/conversations/threads/{self.conversationsThreadId}/messages/{self.id}/original-content")
        text = md(res.data['richText']) if res.data['richText'] else res.data['text']
        return remove_unsubscribe(text)

    def __str__(self):
        return f"MESSAGE FROM {self.senders[0].name or self.senders[0].actorId} at {self.createdAt.strftime('%Y-%m-%d %H:%M')}:\n{self.get_text()}"

@dataclass
class Conversation:
    results: List[MessageBase]
    paging: Dict

    @classmethod
    def from_dict(cls, data: dict, api: ApiClient):
        results = []
        message_class_map = {
            'MESSAGE': Message,
            'COMMENT': Comment,
            # 'WELCOME_MESSAGE': WelcomeMessage,
            'ASSIGNMENT': Assignment,
            # 'THREAD_STATUS_CHANGE': StatusChange,
            'INBOX_CHANGE': InboxChange,
        }

        for result in data['results']:
            message_type = result.get('type')
            message_class = message_class_map.get(message_type)
            if message_class:
                results.append(message_class.from_dict(result, api))

        return cls(results=results, paging=Paging.from_dict(data.get('paging', None)))