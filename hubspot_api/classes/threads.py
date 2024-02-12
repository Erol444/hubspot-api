from typing import List, Dict
import json
import uuid
from datetime import datetime
from hubspot_api.api_client import ApiClient
from .assignee import Assignee
from .message import Message

class Thread:
    def __init__(self, raw: Dict, api: ApiClient):
        self.raw = raw
        self.api = api

        self.id = raw['objectKey']['threadId']
        self.subject = raw['subject']
        self.status = raw['threadStatus']
        # 1002 = email, 1000 = chat (no subject)
        self.channel = raw['genericChannelId']
        self.details = None

        try:
            self.assigned_agent = raw['objectPropertyMap']['0-11']['hs_assigned_agent_id']
        except:
            self.assigned_agent = None

        self.inboxId = raw['objectPropertyMap']['0-11']['hs_inbox_id']
        self.timestamp = datetime.fromtimestamp(raw['latestMessageTimestamp'] / 1000)

    def close(self) -> bool:
        """
        Close the thread
        """
        response = self.api.api_call('PUT',
                          f'/conversations-threads/v1/threads/{self.id}/status',
                          params={'portalId': self.api.portalId},
                          data={"status": "ENDED"},
                        )
        return response.status_code == 200

    def read_details(self) -> Dict:
        """
        Get the details of the thread
        """
        response = self.api.api_call('GET',
                          f'/messages/v2/threadlist/member/{self.id}/details',
                          params={'expectedResponseType':'WRAPPER_V2', 'includeDeletedHistory':False, 'historyLimit':100},
                        )

        self.details = json.loads(response.text)
        return self.details

    def assign(self, assignee: Assignee):
        """
        Assign the thread to an agent
        """
        data = {
            "actorId": f"A-{assignee.userId}",
            "assignmentMethod": "API_AGENT_MANUAL",
            "shouldReassign": True,
            "shouldStartThreadIfStartable": False
        }
        response = self.api.api_call('POST',
            f'/conversations-assignments/v1/assignments/{self.id}',
            data=data
        )
        print(response, response.text)

    def spam(self, deleteContact: bool = True):
        data = {
            "contactDeletion": deleteContact,
            "filtered": True,
            "filteringType": "SPAM"
        }
        response = self.api.api_call('POST',
                        f'/messages/v2/filtering/status/{self.id}',
                        data=data
        )
        print("thead marked as spam, response:", response.text, response.status_code)

    def read_messages(self) -> List[Message]:
        """
        Get all messages in the thread
        """
        data = self.read_details()

        with open(f'get_conversation.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4))

        messages: List[Message] = []
        for msg in data['recentHistory']['messages']['results']:
            if msg['@type'] in ['THREAD_STATUS_UPDATE', 'CONTEXT_UPDATE', 'CRM_OBJECT_LIFECYCLE_UPDATE', 'TYPICAL_RESPONSE_TIME', 'INITIAL_MESSAGE']:
                continue
            elif msg['@type'] in ['COMMON_MESSAGE']:
                messages.append(Message(msg, data['recentHistory']))
            else:
                print('Unknown type', msg['@type'])

        return messages

    def send_message(self, text: str):
        if self.details is None:
            self.read_details()

        metadata = self.details['latestMessagePreview']['emailMetadata']
        conn_addr = metadata['connectedAccountAddress']

        to = metadata['to']
        # Remove our own email from the list
        to = [x for x in to if '<' not in x and '>' not in x]
        to.append(metadata['from']['email'])

        req_body = {
            "appendSignature": True,
            "associations": [
            ],
            "attachments": [],
            "bcc": [],
            "cc": metadata['cc'],
            "connectedAccountAddress": conn_addr,
            "conversationMessageId": uuid.uuid4().hex,
            "from": {
                "email": conn_addr
            },
            "html": text,
            "inReplyToCmId": self.details['latestMessagePreview']['previewMessageId'],
            "inReplyToDisposition": "REPLY",
            "includeChatHistory": False,
            "isForward": False,
            "plainText": text,
            "subject": self.details['latestMessagePreview']['emailMetadata']['subject'],
            "to": to
        }

        for id in self.details['associatedTicketIds']:
            req_body['associations'].append(
            {
                "id": id,
                "type": "TICKET"
            })

        response = self.api.api_call('POST', f'/conversations-email/v1/send/{self.id}', data=req_body)
        return response.status_code == 200