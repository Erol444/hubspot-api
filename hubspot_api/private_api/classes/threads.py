from typing import List, Dict
import json
import uuid
from datetime import datetime

from hubspot_api.private_api.api_client import ApiClient
from .agents import Agent
from .message import Message
from .ably import Ably
import re
import time

class Thread:
    def __init__(self, id: int, api: ApiClient):
        self.api = api
        self.id = id

        # Will get filled in from read_details
        self.subject = None
        self.status = None
        self.channel = None
        self.assigned_agent = None
        self.timestamp = None

        self.details: Dict = None
        self.ably: Ably = None

    @staticmethod
    def from_dict(data: dict, api: ApiClient):
        if 'threadId' in data:
            t = Thread(data['threadId'], api)
            # From v2/threadlist
            emailMetadata = data['latestMessagePreview']['emailMetadata']
            t.subject = emailMetadata['subject'] if emailMetadata else None
            t.status = data['status']
            t.channel = data['originalGenericChannelId']
            try:
                t.assigned_agent = data['assignee']['agentId']
            except:
                t.assigned_agent = None
            t.timestamp = datetime.fromtimestamp(data['latestMessageTimestamp'] / 1000)
        else:
            t = Thread(data['objectKey']['threadId'], api)
            t.subject = data['subject']
            t.status = data['threadStatus']
            # 1002 = email, 1000 = chat (no subject)
            t.channel = data['genericChannelId']
            try:
                t.assigned_agent = data['objectPropertyMap']['0-11']['hs_assigned_agent_id']
            except:
                t.assigned_agent = None
            t.timestamp = datetime.fromtimestamp(data['latestMessageTimestamp'] / 1000)
        return t

    @staticmethod
    def from_id(data: dict, api: ApiClient):
        t = Thread(data['id'], api)
        # t.subject = data['subject']
        t.status = data['threadStatus']
        # 1002 = email, 1000 = chat (no subject)
        t.channel = data['originalGenericChannelId']
        t.timestamp = datetime.fromtimestamp(data['latestMessageTimestamp'] / 1000)
        return t

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

    def _create_ably(self):
        # First get ably.io token
        data = {
            "threadIds": [str(self.id)],
        }
        response = self.api.api_call('PUT',
                          f'/messages/v2/pubsub/token',
                          data = data
                        )

        self.ably = Ably(response.text)

    def comment(self, rich_text, plain_text):
        """
        Comment on the thread. You can pass HTML text, and tag an agent (assignee) in the text like f"Hey @{assigneeObject}, can you check this?"

        Returns True if the comment was successful
        """
        if not rich_text or not plain_text: # Empty string
            return False

        if self.ably is None:
            self._create_ably()

        if self.details is None:
            self.read_details()

        channel = list(filter(lambda x: x['type'] == 'THREAD_PRIVATE', self.details['channels']))[0]

        tag_users = re.findall(r'<strong.*?data-user-id=\"(.*?)\"', rich_text)
        tag_users = [int(x) for x in tag_users]
        userId = self.api.login.userId

        randomId = uuid.uuid4().hex

        msg_data = {
            "@type":"THREAD_COMMENT",
            "sender": {
                "@type":"AGENT_SENDER",
                "id":userId
            },
            "senders": [
                {
                    "actorId":f"A-{userId}",
                    "deliveryIdentifier": None,
                    "senderField": None,
                    "name":None
                }
            ],
            "timestamp": int(time.time() * 1000),
            "text": plain_text,
            "richText": rich_text,
            "hasMore":False,
            "id": randomId,
            "status":{
                "messageStatus":"SENT",
                "timestamp":None,
                "sendFailure":None
            },
            "attachments":[
                {
                    "@type":"MENTIONS",
                    "userIds": tag_users
                }
            ],
            "messageDeletedStatus":"NOT_DELETED",
            "clientType":"MOBILE",
            "genericChannelId":None
        }
        data = [
            {
                "action": 15,
                "channel": channel['name'],
                "messages": [
                    {
                        "data": json.dumps(msg_data),
                        "id": randomId,
                        "name": "1"
                    }
                ],
                "msgSerial": 1
            }
        ]
        res = self.ably.publish(data)
        return res.status_code == 201

    def associate_with_contact(self, contact_id: int):
        """
        Associate the thread with a contact
        """
        randomId = uuid.uuid4().hex
        if self.ably is None:
            self._create_ably()

        {
            "@type": "CONTACT_ASSOCIATION",
            "id": "48150f19-8e61-45fd-8df8-85daaf66399e",
            "timestamp": 1733418168347,
            "echo": False,
            "messageDeletedStatus": "NOT_DELETED",
            "attachments": [],
            "senders": [
                {
                    "actorId": "S-hubspot",
                    "type": "ACTOR_ID"
                }
            ],
            "newVid": 85551,
            "threadId": 9107376366,
            "ablyTs": 1733418168347,
            "clientType": "API"
        }

        data = [
            {
                "action": 15,
                "messages": [
                    {
                        "id": "48150f19-8e61-45fd-8df8-85daaf66399e",
                        "clientId": "API-default",
                        "data": json.dumps(msg_data),
                        "name": "1"
                    }
                ]
            }
        ]
        pass
        

    def read_details(self) -> Dict:
        """
        Get the details of the thread
        """
        response = self.api.api_call('GET',
                          f'/messages/v2/threadlist/member/{self.id}/details',
                          params={'expectedResponseType':'WRAPPER_V2', 'includeDeletedHistory':False, 'historyLimit':100},
                        )

        # Write to conversation_details.json
        with open(f'conversation_details.json', 'w', encoding='utf-8') as file:
            file.write(response.text)
        self.details = response.data
        metadata = response.data['latestMessagePreview']['emailMetadata']
        self.subject = metadata['subject'] if metadata else None
        self.status = response.data['status']
        self.channel = response.data['genericChannelsUsed'][0]['genericChannelId']
        if response.data['assignee'] is not None:
            self.assigned_agent = response.data['assignee']['agentId']
        self.timestamp = response.data['latestMessageTimestamp']
        return self.details

    def assign(self, assignee: Agent):
        """
        Assign the thread to an agent. If the agent is None, it will be unassigned.
        """
        data = {
            "actorId": f"A-{assignee.userId}" if assignee is not None else None,
            "assignmentMethod": "API_AGENT_MANUAL",
            "shouldReassign": True,
            "shouldStartThreadIfStartable": False
        }
        response = self.api.api_call('POST',
            f'/conversations-assignments/v1/assignments/{self.id}',
            data=data
        )
        print(response.status_code, response.text)

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
        Gets all messages in the thread. First message in the list is the oldest one.
        """
        data = self.read_details()

        messages: List[Message] = []
        for msg in data['recentHistory']['messages']['results']:
            if msg['@type'] in ['THREAD_STATUS_UPDATE', 'CONTEXT_UPDATE', 'CRM_OBJECT_LIFECYCLE_UPDATE', 'TYPICAL_RESPONSE_TIME', 'INITIAL_MESSAGE']:
                continue
            elif msg['@type'] in ['COMMON_MESSAGE']:
                messages.append(Message(msg, data['recentHistory']['friendlyNameResults'], self.id, api=self.api))
            else:
                print('Unknown type', msg['@type'])

        # Reorder messages
        messages.sort(key=lambda x: x.timestamp)
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