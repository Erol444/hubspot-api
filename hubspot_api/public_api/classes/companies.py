import requests
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from hubspot_api.private_api.api_client import ApiClient

DEFAULT_PROPERTIES = [
    "email",
    "firstname",
    "hs_object_id",
    "lastname",
    "associatedcompanyid",
    "company",
    "website",
    "hubspot_owner_id",
    "lifecyclestage"
]
class Companies:
    def __init__(self, api: ApiClient):
        self.api = api

    def search(self, query: str) -> dict:
        """
        Search for companies by name or domain
        """
        url = "/crm/v3/objects/companies/search"
        body = {
            'query': query,
            "limit": 10,
            "properties": DEFAULT_PROPERTIES
        }
        return self.api.api_call("POST", url, data=body).data

    def get_by_id(self, company_id: str, params=None) -> dict:
        """
        Get a company by ID
        """
        url = f"/crm/v3/objects/companies/{company_id}"

        if params is None:
            params = {}
        if 'properties' not in params:
            params['properties'] = DEFAULT_PROPERTIES

        return self.api.api_call("GET", url, params=params).data