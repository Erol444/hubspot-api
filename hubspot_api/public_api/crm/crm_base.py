from hubspot_api.public_api.api_client import ApiClient

class CrmBase:
    def __init__(self, api: ApiClient):
        self.api = api
        self.data = None

    def search(self, query: str) -> dict:
        """
        Search for companies by name or domain
        """
        url = f"/crm/v3/objects/{self.object_name}/search"
        body = {
            'query': query,
            "limit": 10,
            "properties": self.default_properties
        }
        return self.api.api_call("POST", url, data=body).data

    def get_by_id(self, obj_id: str, params=None) -> dict:
        """
        Get a company by ID
        """
        url = f"/crm/v3/objects/{self.object_name}/{obj_id}"

        if params is None:
            params = {}
        if 'properties' not in params:
            params['properties'] = self.default_properties
        if 'associations' not in params:
            params['associations'] = self.default_associations

        self.data = self.api.api_call("GET", url, params=params).data
        return self.data


    @property
    def properties(self):
        if self.data:
            return self.data['properties']
        return self.data['properties']