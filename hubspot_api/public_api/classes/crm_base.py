from hubspot_api.public_api.api_client import ApiClient
from typing import Dict, Any, Union, List

class CrmBase:
    def __init__(self, api: ApiClient):
        self.api = api
        self.data: Dict[str, Any] = None

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

    def find_by(self, property_key: str, property_value: str) -> dict:
        """
        Find a company by a specific property
        """
        url = f"/crm/v3/objects/{self.object_name}/search"
        body = {
            "filterGroups": [
                {
                "filters": [
                    {
                    "propertyName": property_key,
                    "operator": "CONTAINS_TOKEN",
                    "value": property_value
                    }
                ]
                }
            ]
        }
        return self.api.api_call("POST", url, data=body).data

    def create(self, properties: dict) -> dict:
        """
        Create a company
        """
        url = f"/crm/v3/objects/{self.object_name}"
        return self.api.api_call("POST", url, data={'properties': properties}).data

    def get_by_id(self, object_id: Union[str, List[str]], params=None) -> dict:
        """
        Get a company by ID
        """
        if object_id is None:
            return None

        if params is None:
            params = {}
        if 'properties' not in params:
            params['properties'] = self.default_properties
        if 'associations' not in params:
            params['associations'] = self.default_associations

        if isinstance(object_id, list):
            url = f"/crm/v3/objects/{self.object_name}/batch/read"
            data= { "inputs": [{'id': id} for id in object_id], "properties": params['properties'] }
            self.data = self.api.api_call("POST", url, data=data).data
        else:
            url = f"/crm/v3/objects/{self.object_name}/{object_id}"
            self.data = self.api.api_call("GET", url, params=params).data

        return self.data

    def update(self, object_id: str, properties: dict) -> dict:
        """
        Update a company by ID
        """
        url = f"/crm/v3/objects/{self.object_name}/{object_id}"
        return self.api.api_call("PATCH", url, data={'properties': properties}).data

    @property
    def properties(self):
        if self.data:
            return self.data['properties']
        return None
