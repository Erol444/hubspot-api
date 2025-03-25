from hubspot_api.private_api.api_client import ApiClient
from .crm_base import CrmBase

class Company(CrmBase):
    object_name = "companies"
    default_properties = ["domain", "total_revenue", "website", "hubspot_owner_id", "lifecyclestage"]
    default_associations = []

    def get_total_revenue(self):
        """
        Get total revenue of the company
        """
        if self.properties is None:
            return None
        return self.properties.get('total_revenue', None)

    @classmethod
    def get_by_id(cls, api: ApiClient, company_id: str) -> 'Company':
        """
        Retrieve a Company instance by ID.
        """
        instance = cls(api)
        super(Company, instance).get_by_id(company_id)  # Explicitly call CrmBase's method
        return instance