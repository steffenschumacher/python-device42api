from .base import *


class IPAM_macaddress(Device42APIObject):
    """.. _IPAM_macaddress:

    create IPAM macaddress
    these objects are returned if you fetch devices with configured macAddresses, manual adding a mac Address to a device
    as follows ...

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> i = device42api.IPAM_macaddress(api=api)
    >>> i.macaddress = '00:11:22:33:44:55'
    >>> i.port_name = 'eth0'
    >>> i.device = 'Test Device'
    >>> i.get_json()
    {'device': 'Test Device', 'macaddress': '00:11:22:33:44:55', 'port_name': 'eth0'}
    >>> i.save()
    {'msg': ['mac address successfully added/updated', 1, '00:11:22:33:44:55', True, True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.macaddress = Required()
        self.port_name = Optional()  # Interface name.
        self.override = False  # Value can be smart, no, or yes. See notice below.
        self.vlan_id = Optional()  # GET VLAN IDs or UI Tools > Export > VLAN
        self.device = Optional()
        super(IPAM_macaddress, self).__init__(json, parent, api)
        self._api_path = 'macs'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.mac_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        if isinstance(self.macaddress, Required):
            raise Device42APIObjectException('required Attribute "macaddress" not set')
        self.__get_json_validator__(('macaddress', 'port_name', 'vlan_id', 'device'))
        return self.json


class IPAM_ipaddress(Device42APIObject):
    """.. _IPAM_ipaddress:

    create IPAM ipaddress
    these objects are returned if you fetch devices with configured macAddresses, manual adding a mac Address to a device
    as follows ...

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> i = device42api.IPAM_ipaddress(api=api)
    >>> i.ipaddress = '1.1.1.1' # 127.0.0.1 is not supported and will lead to {'msg': 'list index out of range', 'code': 1}
    >>> i.macaddress = '00:11:22:33:44:55'
    >>> i.device = 'Test Device'
    >>> i.type = 'static' # static or dhcp
    >>> i.get_json()
    {'device': 'Test Device', 'macaddress': '00:11:22:33:44:55', 'ipaddress': '1.1.1.1', 'type': 'static'}
    >>> i.save()
    {'msg': ['ip added or updated', 1, '1.1.1.1', True, True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.ipaddress = Required()
        self.tag = Optional()  # label for the interface
        self.subnet = Optional()
        self.macaddress = Optional()
        self.device = Optional()
        self.type = Optional()  # Could be static, dhcp or reserved
        self.notes = Optional()
        self.vrf_group_id = Optional()  # Added in v5.1.2. ID of the VRF group you want this IP to be associated with.
        self.vrf_group = Optional()  # Name of the VRF group you want this IP to be associated with. Processed only if vrf_group_id is not present in the arguments.
        self.available = False  # If yes - then IP is marked as available and device and mac address associations are cleared. Added in v5.7.2
        self.clear_all = False  # If yes - then IP is marked as available and device and mac address associations are cleared. Also notes and lable fields are cleared. Added in v5.7.2
        super(IPAM_ipaddress, self).__init__(json, parent, api)
        self._api_path = 'ip'
        if json and self.__dict__.get('ip', False):
            self.ipaddress = self.ip

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, v=None, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.ip_id = rsp['msg'][1]
            return rsp

    def save_dnsRecord(self, nameserver=None, ttl=86400):
        """saves the A DNS record for the device and the IP

        .. note:: I've not added any DNS logic as the API and GUI suffer support and I'm anoyed if implementing this over and over. Since I didn't want to introduce dependencies to other python Modules there's no logic in here

        .. attention:: the DNS Zones must exist and need to be created through the GUI

        >>> d = api.get_device('TestDevice')
        >>> # since the device doesn't carry a valid FQDN set it accordingly !
        >>> d.name = 'testdevice.localdomain'
        testdevice.localdomain
        >>> i = d.ip_address[0]
        >>> i.ipaddress
        1.1.1.1
        >>> i.save_dnsRecord()
        [{'msg': ['DNS record added/updated successfully', 1, 'testdevice.localdomain'], 'code': 0},
         {'msg': ['DNS record added/updated successfully', 2, '1.1.1.1.in-addr.arpa'], 'code': 0}]

        .. attention:: when changing the parent device in any way remember that there's no logic which removes the old entries, so you end up with multiple entries for the address

        >>> d = api.get_device('TestDevice')
        >>> d.name = 'testdevice2.localdomain'
        >>> i = d.ip_address[0]
        >>> i.save_dnsRecord()
        [{'msg': ['DNS record added/updated successfully', 3, 'testdevice2.localdomain'], 'code': 0},
         {'msg': ['DNS record added/updated successfully', 4, '1.1.1.1.in-addr.arpa'], 'code': 0}]

        """
        d = IPAM_DNSRecord(api=self.api)
        d.name = self.parent.name
        d.domain = '.'.join(d.name.split('.')[1:])
        d.type = 'A'
        if nameserver:
            d.nameserver = nameserver
        d.content = self.ipaddress
        d.ttl = int(ttl)
        rsp = d.save()
        rev = self.ipaddress.split('.')
        rev.reverse()
        r = IPAM_DNSRecord(api=self.api)
        r.name = '%s.in-addr.arpa' % '.'.join(rev)
        r.domain = '.'.join(r.name.split('.')[1:])
        r.type = 'PTR'
        if nameserver:
            r.nameserver = nameserver
        r.content = self.parent.name
        r.ttl = int(ttl)
        rsp2 = r.save()
        return [rsp, rsp2]

    def get_json(self):
        if isinstance(self.ipaddress, Required):
            raise Device42APIObjectException('required Attribute "ipaddress" not set')
        self.__get_json_validator__(('ipaddress', 'tag', 'subnet', 'macaddress', 'device', 'type'))
        return self.json

    def load(self):
        """ there's nothing to be loaded for now"""
        return True


class IPAM_subnet(Device42APIObject):
    """.. _IPAM_subnet:

    create IPAM subnet

    >>> api = device42api.Device42API(host='192.168.122.102', username='admin', password='admin')
    >>> sub = device42api.IPAM_subnet(api=api)
    >>> sub.network = '1.1.1.0'
    >>> sub.mask_bits = 24
    >>> sub.name    = 'Home Servers'
    >>> sub.gateway = '1.1.1.254'
    >>> sub.save()
    {'msg': ['subnet successfully added/updated', 1, 'Home Servers-1.1.1.0/24'], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.network = Required()
        self.mask_bits = Required()
        self.vrf_group_id = Optional()
        self.name = Optional()
        self.description = Optional()
        self.number = Optional()
        self.gateway = Optional()
        self.range_begin = Optional()
        self.range_end = Optional()
        self.parent_vlan_id = Optional()
        self.customer_id = Optional()
        self.customer = Optional()
        self.notes = Optional()
        super(IPAM_subnet, self).__init__(json, parent, api)
        self._api_path = 'subnets'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.subnet_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        for attr in ('network', 'mask_bits'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException('required Attribute "%s" not set' % getattr(self, attr))
        self.__get_json_validator__(('network', 'mask_bits', 'vrf_group_id', 'name', 'description', 'number', 'gateway',
                                     'range_begin', 'range_end', 'parent_vlan_id', 'customer_id', 'customer'))
        return self.json


class IPAM_vlan(Device42APIObject):
    """.. _IPAM_vlan:

    create IPAM subnet

    >>> v = device42api.IPAM_vlan(api=api)
    >>> v.number = 1
    >>> v.name = 'Default VLAN'
    >>> v.save()
    {'msg': ['vlan successfully added', 1, 'Default VLAN', True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.number = Required()
        self.name = Optional()
        self.description = Optional()
        self.switch_id = Optional()
        self.switches = Optional()
        self.notes = Optional()
        super(IPAM_vlan, self).__init__(json, parent, api)
        self._api_path = 'vlans'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.vlan_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        if isinstance(self.number, Required):
            raise Device42APIObjectException('required Attribute "number" not set')
        self.__get_json_validator__(('number', 'name', 'description', 'switch_id', 'switches', 'notes'))
        return self.json


class IPAM_switchport(Device42APIObject):
    """.. _IPAM_switchport:

    create IPAM switchport

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> sp = device42api.IPAM_switchport(api=api)
    >>> sp.port = 1
    >>> sp.vlan_ids = '1'
    >>> sp.description = 'Test Port'
    >>> sp.up = 'yes'
    >>> sp.up_admin = 'no'
    >>> sp.count = 'yes'
    >>> sp.save()
    {'msg': ['switchport successfully added/updated', 7, '1'], 'code': 0}

    .. attention:: !!! API Bug !!! even with the switchport_id given the API adds a new port

    >>> sp.get_json()
    {'switchport_id': 7, 'port': 7}
    >>> sp.save()
    {'msg': ['switchport successfully added/updated', 9, '7'], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.port = Required()
        self.switch = Optional()
        self.description = Optional()
        self.type = Optional()
        self.vlan_ids = Optional()  # only one integer item in reality API bug ?
        self.up = Optional()
        self.up_admin = Optional()
        self.count = Optional()
        self.remote_port_id = Optional()
        self.remote_device = Optional()
        self.remote_port = Optional()
        self.notes = Optional()
        self.switchport_id = Optional()
        super(IPAM_switchport, self).__init__(json, parent, api)
        self._api_path = 'switchports'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.switchport_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        if isinstance(self.port, Required):
            raise Device42APIObjectException('required Attribute "port" not set')
        self.__get_json_validator__(('port', 'switch', 'description', 'type', 'vlan_ids', 'up', 'up_admin', 'count',
                                     'remote_port_id', 'remote_device', 'remote_port', 'notes', 'switchport_id'))
        return self.json


class IPAM_switch(Device42APIObject):
    """.. _IPAM_switch:

    create IPAM switch
    postponed

    """

    def __init__(self, json=None, parent=None, api=None):
        self.device = Required()
        self.device_id = Optional()
        self.switch_template_id = Required()
        self.notes = Optional()
        super(IPAM_switch, self).__init__(json, parent, api)
        self._api_path = 'vlans'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.switch_template_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        for attr in ('device', 'switch_template_id'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException('required Attribute "%s" not set' % getattr(self, attr))
        self.__get_json_validator__(('device', 'switch_template_id', 'device_id', 'notes'))
        return self.json


class IPAM_DNSRecord(Device42APIObject):
    """.. _IPAM_DNSRecord:

    create IPAM DNSRecord

    .. note:: the API and the device42 logic in the Backend don't provide sanity checking of DNS syntax/recomendations for data, in addition to the problem of validation, the DNS Zone needs to be created through the GUI

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> i = device42api.IPAM_DNSRecord(api=api)
    >>> i.domain     = 'localdomain'
    >>> i.type       = 'CNAME'
    >>> i.nameserver = '127.0.0.1'
    >>> i.name       = 'localhost'
    >>> i.content    = '127.0.0.1'
    >>> i.ttl        = 86400
    >>> i.save()
    {'msg': ['DNS record added/updated successfully', 1, 'localhost'], 'code': 0}
    >>> i2 = device42api.IPAM_DNSRecord(api=api)
    >>> i2.domain     = 'localdomain'
    >>> i2.nameserver = '127.0.0.1'
    >>> i2.name       = 'localhost'
    >>> i2.content    = '127.0.0.2'
    >>> i2.ttl        = 86400
    >>> i2.type       = 'CNAME'
    >>> i2.save()
    {'msg': ['DNS record added/updated successfully', 2, 'localhost'], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.domain = Required()
        self.type = Required()  # SOA, NS, MX, A, AAAA, CNAME, PTR, TXT, SPF, SRV, CERT, DNSKEY, DS, KEY, NSEC, RRSIG, HINFO, LOC, NAPTR, RP, AFSDB, SSHFP
        self.nameserver = Optional()
        self.name = Optional()
        self.content = Optional()
        self.prio = Optional()
        self.ttl = Optional()
        super(IPAM_DNSRecord, self).__init__(json, parent, api)
        self._api_path = 'dns/records'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.mac_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        for attr in ('domain', 'type'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException('required Attribute "%s" not set' % attr)
        self.__get_json_validator__(('domain', 'type', 'nameserver', 'name', 'content', 'prio', 'ttl'))
        return self.json
