from .api_client import ApiClient
from .classes.meetings import Meetings
from .classes.companies import Companies

class Crm:
    def __init__(self, api: ApiClient):
        self.api = api
        self.meetings = Meetings(api)
        self.companies = Companies(api)