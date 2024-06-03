from .crm_base import CrmBase

class Contact(CrmBase):
    object_name = 'contacts'
    default_properties = 'associatedcompanyid,jobtitle,country,photo,city,phone,mobilephone,emailwork_email'
    default_associations = 'meetings,deals'