
from .crm_base import CrmBase
from .company import Company
from hubspot_api.private_api.api_client import ApiClient

class Contact(CrmBase):
    object_name = 'contacts'
    default_properties = 'firstname,lastname,associatedcompanyid,jobtitle,country,photo,city,phone,mobilephone,email,work_email'
    default_associations = 'meetings,deals'

    @classmethod
    def get_by_id(cls, api: ApiClient, contact_id: str) -> 'Contact':
        """
        Retrieve a Contact instance by ID.
        """
        instance = cls(api)
        super(Contact, instance).get_by_id(contact_id)  # Explicitly call CrmBase's method
        return instance
    
    @classmethod
    def create_contact(cls, api: ApiClient, properties: dict) -> 'Contact':
        """
        Create a new contact
        """
        instance = cls(api)
        data = super(Contact, instance).create(properties)
        instance.data = data
        return instance

    @classmethod
    def find_by_email(cls, api: ApiClient, email: str, create_otherwise: bool = False) -> 'Contact':
        """
        Find contact by email
        """
        instance = cls(api)
        res = super(Contact, instance).find_by('email', email)
        if res['total'] == 0:
            if create_otherwise:
                return cls.create(api, {'email': email})
            return None
        else:
            instance.data = res['results'][0]
            return instance

    def get_company(self) -> Company:
        """
        Get company associated with the contact
        """
        return Company.get_by_id(self.api, self.properties['associatedcompanyid'])