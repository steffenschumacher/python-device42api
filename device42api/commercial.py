from .base import *


class ServiceLevel(Device42APIObject):
    """.. _ServiceLevel:

    only representing the ServiceLevels as object

    .. note:: !!! since there's no API call to create/update these can only be retrieved !!!


    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> sl = api.get_service_level('Production')
    >>> print sl
    Production(1)
    >>> for sl in api.get_service_level():
    ...     print sl
    QA
    Development
    Production

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = None
        self.id = None
        super(ServiceLevel, self).__init__(json, parent, api)

    def __str__(self):
        return '%s(%s)' % (self.name, self.id)


class Customer(Device42APIObject):
    """.. _Customer:

    create Customer

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> c = device42api.Customer(api=api)
    >>> c.name = 'device42 Support'
    >>> c.contact_info = 'device42 Support Team'
    >>> c.save()
    {'msg': ['Customer added or updated.', 1, 'device42 Support', True, True], 'code': 0}

    .. note:: to get Contact details ready you need to switch to the GUI and create the appropriate type definitions ...

    >>> c = device42api.Customer(api.get_customer('device42 Support'), api=api)
    >>> c.customer  = c.name
    >>> c.name      = 'Helpdesk'
    >>> c.type      = 'Helpdesk' # this needs to be created in the GUI there's no API call for it
    >>> c.email     = 'helpdesk@device42.com'
    >>> c.phone     = '111-111-111'
    >>> c.address   = 'Helpdesk Office Building 1'
    >>> c.save()
    {'msg': ['customer contact record added/updated successfully', 1, 'Helpdesk1'], 'code': 0}


    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.contact_info = Optional()
        self.notes = Optional()
        self.type = Optional()  # Contact type, must already exist.
        self.customer = Optional()  # Customer name.
        self.email = Optional()  # Text field.
        self.phone = Optional()  # Text field.
        self.address = Optional()  # Text field.
        super(Customer, self).__init__(json, parent, api)
        self._api_path = 'customers'

    def save(self):
        if self.api:
            if not isinstance(self.customer, Optional):
                rsp = self.api.__post_api__('%s/contacts/' % self._api_path, body=self.get_json())
            else:
                rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.customer_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        for attr in ('name',):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException('required Attribute "%s" not set' % getattr(self, attr))
        self.__get_json_validator__(('name', 'contact_info', 'notes', 'type', 'customer', 'email', 'phone', 'address'))
        return self.json

    def add_customField(self, cf=None):
        if not isinstance(cf, CustomField): raise Device42APIObjectException('need CustomField instance')
        cf._api_path = 'customer'
        cf.name = self.name
        rsp = cf.save()
        if isinstance(rsp, dict) and 'code' in rsp:
            if rsp['code'] == 0:
                self.custom_fields.append(cf)
        return rsp
