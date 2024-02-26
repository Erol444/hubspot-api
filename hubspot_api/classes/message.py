from typing import List, Dict
from datetime import datetime
from hubspot_api.api_client import ApiClient


def remove_unsubscribe(text: str) -> str:
    # From google groups
    unsubs = [
        """-- 
To unsubscribe from this group and stop receiving emails from it, send an email to""",
        """-- 
You received this message because you are subscribed to the""",
    ]
    for unsub in unsubs:
        if text.find(unsub) != -1:
            text = text[:text.find(unsub)]
    text = text.strip()
    return text

class Message:
    """
    Message inside a thread (conversation). Can be either an email or a live chat message.
    Emails will have fromEmail / to / cc, but live chat messages will not.
    """
    def __init__(self, msg: Dict, friendlyNames: Dict, threadId: int, api: ApiClient):
        self.raw = msg
        self.api = api

        self.id = msg['id'] # Message ID
        self.threadId = threadId

        self.timestamp = datetime.fromtimestamp(msg["timestamp"] / 1000)
        try:
            self.fromEmail = msg['senders'][0]['deliveryIdentifier']['value']
        except:
            self.fromEmail = None

        self.text = remove_unsubscribe(msg['text'])

        self.to = []
        self.cc = []
        # Check if self.raw has ['recipients']
        if self.raw['recipients']:
            for recipient in self.raw['recipients']:
                if 'recipientField' not in recipient:
                    continue
                if recipient['recipientField'] == 'TO':
                    self.to.append(recipient['deliveryIdentifier']['value'])
                elif recipient['recipientField'] == 'CC':
                    self.cc.append(recipient['deliveryIdentifier']['value'])

        try:
            self.fromName = msg['senders'][0]['name']
        except:
            try:
                for name in friendlyNames:
                    email = (name['genericRecipient'] or name['genericSender'])['deliveryIdentifier']['value']
                    if email == self.fromEmail:
                        self.fromName = name['resolvedFriendlyName']
                        break
            except:
                self.fromName = None

    def has_history(self) -> bool:
        """
        Check whether the message has a history (previous replies). Only relevant for first (oldest) message,
        as otherwise the history is always included.
        """
        metadata_list = list(filter(lambda x: x['@type'] == 'EMAIL_METADATA', self.raw['attachments']))
        if len(metadata_list) == 0:
            return False
        return metadata_list[0]['hasReplies']

    def get_history(self) -> str:
        """
        Get the message history (previous replies). Only relevant for first (oldest) message,
        as otherwise the history is always included.
        """
        response = self.api.api_call('GET',
                        f'/conversations-threads/v1/message/{self.threadId}/{self.id}',
                        params={'includeReplies': 'true', 'deletedFilter': 'NOT_DELETED'},
        )
        metadata = list(filter(lambda x: x['@type'] == 'EMAIL_METADATA', response.data['attachments']))[0]
        # We could also return richText with "previousRepliesHtml"
        text = metadata['previousRepliesPlainText']
        return remove_unsubscribe(text)