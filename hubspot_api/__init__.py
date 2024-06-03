from typing import Callable

class PrivateApi:
    def __init__(self, email: str, password: str, verification_code_cb: Callable):
        from .private_api.conversations import Conversations
        from .private_api.api_client import ApiClient
        from .private_api.login import Login
        self.login = Login(email, password, verification_code_cb)
        self.api_client = ApiClient(login=self.login)

        self.conversations = Conversations(self.api_client)

        # We could add support for other HubSpot modules (contacts, deals, etc.), but those work as expected
        # with their public API. Only Conversations are in "BETA", and have been for over a year now.

class Api:
    def __init__(self, api_key: str):
        """
        This class is used to access the public API of HubSpot.

        :param api_key: Your HubSpot API key, like 'pat-eu1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
        """
        from .public_api.conversations import Conversations
        from .public_api.crm import Crm
        from .public_api.api_client import ApiClient
        self.api_client = ApiClient(api_key)
        self.conversations = Conversations(self.api_client)
        self.crm = Crm(self.api_client)