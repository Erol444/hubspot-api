from .classes.message import Message
from .classes.threads import Thread
from .conversations import Conversations
from .login import Login
from .api_client import ApiClient

from typing import Callable

class HubSpotApi:
    def __init__(self, email: str, password: str, verification_code_cb: Callable):
        self.login = Login(email, password, verification_code_cb)
        self.api_client = ApiClient(login=self.login)

        self.conversations = Conversations(self.api_client)

        # We could add support for other HubSpot modules (contacts, deals, etc.), but those work as expected
        # with their public API. Only Conversations are in "BETA", and have been for over a year now.