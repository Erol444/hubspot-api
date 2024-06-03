
from hubspot_api.public_api.api_client import ApiClient

class Contact:
    def __init__(self, api: ApiClient, id: str):
        self.api = api
        self.id = id
        self.data = None


    def __get_data(self):
        if self.data:
            return self.data

        url = f"/crm/v3/objects/contacts/{self.id}"
        params = {
            'properties': 'associatedcompanyid,jobtitle,country,photo,city,phone,mobilephone,emailwork_email',
            'associations': 'meetings,deals,contacts'
        }
        self.data = self.api.api_call("GET", url, params=params).data
        return self.data

    @property
    def properties(self):
        return self.__get_data()['properties']

    def get_company(self) -> 'Company':
        """
        Get company associated with the contact
        """
        return self.api.get_company(self.properties['associatedcompanyid'])