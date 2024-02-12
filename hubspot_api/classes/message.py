from typing import List, Dict
from datetime import datetime

class Message:
    """
    Message inside a thread (conversation). Can be either an email or a live chat message.
    Emails will have fromEmail / to / cc, but live chat messages will not.
    """
    def __init__(self, msg: Dict, recentHistory: Dict):
        self.raw = msg

        self.timestamp = datetime.fromtimestamp(msg["timestamp"] / 1000)
        try:
            self.fromEmail = msg['senders'][0]['deliveryIdentifier']['value']
        except:
            self.fromEmail = None

        self.text = msg['text']

        self.to = []
        self.cc = []
        # Check if self.raw has ['recipients']
        if self.raw['recipients'] is not None:
            for recipient in self.raw['recipients']:
                if recipient['recipientField'] == 'TO':
                    self.to.append(recipient['deliveryIdentifier']['value'])
                elif recipient['recipientField'] == 'CC':
                    self.cc.append(recipient['deliveryIdentifier']['value'])

        # From google groups
        unsubs = [
            """-- 
To unsubscribe from this group and stop receiving emails from it, send an email to""",
            """-- 
You received this message because you are subscribed to the""",
        ]
        for unsub in unsubs:
            if self.text.find(unsub) != -1:
                self.text = self.text[:self.text.find(unsub)]
        self.text = self.text.strip()

        try:
            self.fromName = msg['senders'][0]['name']
        except:
            try:
                for name in recentHistory['friendlyNameResults']:
                    email = (name['genericRecipient'] or name['genericSender'])['deliveryIdentifier']['value']
                    if email == self.fromEmail:
                        self.fromName = name['resolvedFriendlyName']
                        break
            except:
                self.fromName = None