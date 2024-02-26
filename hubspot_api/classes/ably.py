import requests
import json
import random

class Ably:
    """
    Ably.io is a service that provides real-time messaging. HubSpot uses it for their pub/sub messaging system, like conversation comments, or live chats.
    """
    def __init__(self, jsonStr: str):
        """
        Args:
            json (str): JSON string that was responded from /messages/v2/pubsub/token

        Example json str:

        {
            "capability": "{[\"prod.messages.CUSTOM-list-123123\"]}",
            "clientId": "AGENT-123123",
            "keyName": "t4K2dg.123123",
            "mac": "generated_hmac",
            "nonce": "6654632534341084",
            "timestamp": 1707993859138,
            "ttl": 0
        }
        """
        self.json = jsonStr
        self.data = json.loads(jsonStr)
        self.key = self.data['keyName']

        self.headers =  {
            'accept': 'application/json',
            'x-ably-version': '2',
            'ably-agent': 'ably-js/1.2.43 browser',
            'user-agent': 'HubSpotAndroid/3.54.1 (build:3.54.1; Android 11)',
            'x-hubspot-language': 'en',
            'accept-encoding': 'gzip',
            'content-type': 'application/json',
        }

        self.token = self.get_token()
        self.connKey = self.connect()

    def __get_rnd(self):
        return random.randint(10**15, 10**16 - 1)

    def get_token(self):
        response = requests.request("POST",
                                    f"https://hubspot-eu-rest.ably.io/keys/{self.key}/requestToken?rnd={self.__get_rnd()}",
                                    headers=self.headers,
                                    data=self.json
                                    )
        data = json.loads(response.text)
        return data['token']

    def connect(self) -> str:
        """
        Returns connection key
        """
        response = requests.request("GET",
                                    f"https://hubspot-eu-rest.ably.io/comet/connect?access_token={self.token}&stream=false&heartbeats=false&v=2&agent=ably-js%252F1.2.43%2520browser&rnd={self.__get_rnd()}",
                                    headers=self.headers
                                    )
        data = json.loads(response.text)
        return data[0]['connectionDetails']['connectionKey']

    def publish(self, data: dict):
        """
        Example data:
        [
            {
                "action": 15,
                "channel": "thread:v2:prod:messages:123:123:1",
                "messages": [
                    {
                        "data": "{}",
                        "id": "123123",
                        "name": "1"
                    }
                ],
                "msgSerial": 1
            }
        ]
        """
        response = requests.request("POST",
                         f"https://hubspot-eu-rest.ably.io/comet/{self.connKey}/send?access_token={self.token}&rnd={self.__get_rnd()}",
                         json=data,
                         headers=self.headers
                         )

        return response




