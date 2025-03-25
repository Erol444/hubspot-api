from .crm_base import CrmBase
from .company import Company
from .contact import Contact
from hubspot_api.private_api.api_client import ApiClient

class Deal(CrmBase):
    object_name = "deals"
    default_properties = ""
    default_associations = "contact,company"

    @property
    def properties(self):
        return self.__get_data()["properties"]

    @classmethod
    def get_by_id(cls, api: ApiClient, deal_id: str) -> 'Deal':
        """
        Retrieve a Contact instance by ID.
        """
        instance = cls(api)
        super(Deal, instance).get_by_id(deal_id)# Explicitly call CrmBase's method
        return instance

    def get_associated_company_id(self) -> str:
        try:
            for result in self.data["associations"]["companies"]["results"]:
                if result["type"] == "deal_to_company":
                    return result["id"]
        except KeyError:
            pass
        return None

    def get_associated_contact_id(self) -> str:
        try:
            for result in self.data["associations"]["contacts"]["results"]:
                if result["type"] == "deal_to_contact":
                    return result["id"]
        except KeyError:
            pass
        return None

    def get_company(self) -> Company:
        """
        Get company associated with the contact
        """
        return Company.get_by_id(self.api, self.get_associated_company_id())

    def get_contact(self) -> Contact:
        """
        Get contact associated with the deal
        """
        return Contact.get_by_id(self.api, self.get_associated_contact_id())

    def add_association(self, target_object_name, target_object_id):
        url = f"/crm/v4/objects/{self.object_name}/{self.data['properties']['hs_object_id']}/associations/{target_object_name}/{target_object_id}"
        if target_object_name != "company":
            raise ValueError(
                f"Only company associations are supported, not {target_object_name}"
            )

        data = [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}]
        return self.api.api_call("PUT", url, data=data)
