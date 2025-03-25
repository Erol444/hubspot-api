from .api_client import ApiClient
from .classes.meeting import Meeting
from .classes.company import Company

class Crm:
    def __init__(self, api: ApiClient):
        self.api = api
        self.meetings = Meeting(api)
        self.companies = Company(api)