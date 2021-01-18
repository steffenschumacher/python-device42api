from .base import *


class Asset(Device42APIObject):
    """.. _Asset:

    create Asset object

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> a = device42api.Asset(api=api)
    >>> a.type = 'AC' # AC,Breaker Panel,Cable Modem,DMARC,Fabric Extender,Fax Machine,Filler Panel,Monitor,Patch Panel
                      # Patch Panel Module,Projector,Scanner,Shredder,Software,Speaker Phone,TAP Module
    >>> a.serial_no = '1234567890'
    >>> a.vendor = 'Test'
    >>> a.building = 'TestBuilding'
    >>> a.room = 'Test Room'
    >>> a.rack_id = 80
    >>> a.start_at = 1
    >>> a.save()
    {'msg': ['asset added/edited.', 1, ''], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.type = Required()
        self.name = Optional()
        self.service_level = Optional()
        self.serial_no = Optional()
        self.asset_no = Optional()
        self.customer_id = Optional()
        self.location = Optional()
        self.notes = Optional()
        self.building = Optional()
        self.vendor = Optional()
        self.imagefile_id = Optional()
        self.contract_id = Optional()
        self.rack_id = Optional()
        self.building = Optional()
        self.room = Optional()
        self.rack = Optional()
        self.row = Optional()
        self.start_at = Optional()
        self.size = Optional()
        self.orientation = Optional()
        self.depth = Optional()
        self.patch_panel_model_id = Optional()
        self.numbering_start_from = Optional()
        self.asset_contracts = []
        self.asset_purchases = []
        if json and 'asset' in json:
            super(Asset, self).__init__(json['asset'], parent, api)
        else:
            super(Asset, self).__init__(json, parent, api)
        self._api_path = 'assets'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.asset_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        if isinstance(self.type, Required):
            raise Device42APIObjectException('required Attribute "type" not set')
        self.__get_json_validator__(
            ('type', 'name', 'service_level', 'serial_no', 'asset_no', 'customer_id', 'location',
             'notes', 'building', 'vendor', 'imagefile_id', 'contract_id', 'rack_id',
             'building', 'room', 'rack', 'row', 'start_at', 'size', 'orientation',
             'depth', 'patch_panel_model_id', 'numbering_start_from'))
        return self.json

    def load(self):
        """get entries for asset from API

        """
        if self.api:
            json = self.api.get('assets/%s' % self.asset_id)
            for k in list(json.keys()):
                if json[k] != None:
                    setattr(self, k, json[k])
            self._json = json

    def add_customField(self, cf=None):
        """add custom Fields to the object

        >>> asset = api.get_asset('Rack with CustomFields')[0]
        >>> cf = device42api.CustomField(api=api)
        >>> cf.key      = 'used_since'
        >>> cf.type     = 'date'
        >>> cf.value    = '2014-04-02'
        >>> asset.add_customField(cf)
        {'msg': ['custom key pair values added or updated', 15, 'Asset with CustomFields - AC'], 'code': 0}

        """
        if not isinstance(cf, CustomField): raise Device42APIObjectException('need CustomField instance')
        cf._api_path = 'asset'
        cf.name = self.name
        cf.id = self.asset_id
        rsp = cf.save()
        if isinstance(rsp, dict) and 'code' in rsp:
            if rsp['code'] == 0:
                self.custom_fields.append(cf)
        return rsp


class Device(Device42APIObject):
    """.. _Device:

    create Device object

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> d = device42api.Device(api=api)
    >>> d.name = 'TestDevice'
    >>> d.serial_no = 'Ab123asd' # serial number must follow certain structure ???
    >>> d.hardware = 'Generic Hardware 1U'
    >>> d.in_service = 'yes'
    >>> d.type = 'physical'
    >>> d.service_level = 'production'
    >>> d.os = 'RHEL Server'
    >>> d.osver = 6.5
    >>> d.memory = 16.000
    >>> d.cpucount = 80
    >>> d.cpucore = 8
    >>> d.notes = 'my special device'
    >>> d.save()
    {'msg': ['device added or updated', 156, 'TestDevice', True, True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.serial_no = Optional()
        self.asset_no = Optional()
        self.manufacturer = Optional()
        self.hardware = Optional()
        self.is_it_switch = False
        self.is_it_virtual_host = False
        self.is_it_blade_host = False
        self.in_service = False
        self.type = Optional()  # values are physical, virtual, blade, cluster, or other
        self.service_level = Optional()
        self.virtual_host = Optional()
        self.blade_host = Optional()
        self.slot_no = Optional()
        self.storage_room_id = Optional()
        self.storage_room = Optional()
        self.os = Optional()
        self.osver = Optional()
        self.memory = Optional()
        self.cpucount = Optional()
        self.cpupower = Optional()
        self.cpucore = Optional()
        self.hddcount = Optional()
        self.hddsize = Optional()
        self.hddraid = Optional()
        self.hddraid_type = Optional()
        self.mac_addresses = []
        self.ip_addresses = []
        self.devices = Optional()
        self.appcomps = Optional()
        self.customer = Optional()
        self.contract = Optional()
        self.aliases = Optional()
        self.notes = Optional()
        self.uuid = Optional()
        if json:
            super(Device, self).__init__(json['device'], parent, api)
            self._json = json
        else:
            super(Device, self).__init__(json, parent, api)
            self._json = dict()
        self._api_path = 'device'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, v=None, body=self.get_json())
            # {'msg': ['device added or updated', 3, 'Test Device 2', True, True], 'code': 0}
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.device_id = rsp['msg'][1]
            return rsp

    def load(self):
        """
        get entries for asset from API

        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> d = device42api.Device(api=api)
        >>> d.device_id = 156
        >>> d.load()
        >>> d.name, d.serial_no
        ('TestDevice', 'Ab123asd')

        """
        if self.api:
            json = self.api.get('devices/id/%s/?follow=yes' % self.device_id)
            # fix size changed during iteration with hack hw_model
            json['hardware'] = ''
            for k in list(json.keys()):
                if k == 'ip_addresses':
                    ipaddresses = []
                    for i in json['ip_addresses']:
                        ip = IPAM_ipaddress(json=i, parent=self, api=self.api)
                        ip.load()
                        ipaddresses.append(ip)
                    self.ip_addresses = ipaddresses
                elif k == 'mac_addresses':
                    for m in json['mac_addresses']:
                        # it might be None
                        if m:
                            self.mac_addresses.append(self.api.get_macid_byAddress(m['mac']))
                elif k == 'hw_model':
                    setattr(self, 'hardware', json[k])
                    # hack as hardware is returned as hw_model
                    json['hardware'] = json[k]
                else:
                    if json[k] != None:
                        setattr(self, k, json[k])
            self._json = json

    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException('required Attribute "name" not set')
        self.__get_json_validator__(('name', 'serial_no', 'asset_no', 'manufacturer', 'hardware', 'type',
                                     'service_level', 'virtual_host', 'blade_host', 'slot_no',
                                     'storage_room_id', 'storage_room', 'os', 'osver', 'memory', 'cpucount', 'cpupower',
                                     'cpucore',
                                     'hddcount', 'hddsize', 'hddraid', 'hddraid_type', 'devices', 'appcomps',
                                     'customer', 'contract', 'aliases', 'notes', 'is_it_switch', 'is_it_virtual_host',
                                     'is_it_blade_host', 'uuid'))
        return self.json

    def add_mac(self, macAddress=None, port_name=None):
        """.. _Device.add_mac:

        adds a macAddress to the device (if new macAddress will be created)

        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> d = device42api.Device(api=api)
        >>> d.device_id = 1
        >>> d.load()
        >>> d.add_mac('00:00:00:00:00:02', 'eth1')
        {'msg': ['mac address successfully added/updated', 2, '00:00:00:00:00:02', True, True], 'code': 0}

        """
        mc = IPAM_macaddress(api=self.api)
        mc.macaddress = macAddress
        if port_name:
            mc.port_name = port_name
        mc.device = self
        rsp = mc.save()
        if rsp['msg'][-2]:
            mc.macaddress_id = rsp['msg'][1]
            self.mac_addresses.append(mc)
            return True
        return rsp

    def add_ip(self, ipAddress=None, macAddress=None):
        """.. _Device.add_ip:

        adds an ipAddress to the device

        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> racks = api.get_rack()
        >>> racks[0].devices.keys()
        [1.0]
        >>> d = racks[0].devices[1.0]
        >>> len(d.mac_addresses)
        1
        >>> d.add_ip('2.2.2.2') # if macAddress is ommited and only one macAddress is in device this one will be used
        {'msg': ['mac address successfully added/updated', 2, '00:00:00:00:00:02', True, True], 'code': 0}
        >>> for ip in d.ip_addresses:
        ...     print ip.ipaddress
        1.1.1.1
        2.2.2.2

        """
        ip = IPAM_ipaddress(api=self.api)
        ip.ipaddress = ipAddress
        if macAddress:
            ip.macaddress = macAddress
        elif len(self.mac_addresses) == 1:
            ip.macaddress = self.mac_addresses[0].macaddress
        ip.device = self.name
        ip.type = 'static'
        rsp = ip.save()
        if rsp['msg'][-2]:
            ip.ipaddress_id = rsp['msg'][1]
            self.ip_addresses.append(ip)
            return True
        return rsp

    def __str__(self):
        return '%s' % self.name

    def add_customField(self, cf=None):
        """add custom Fields to the object

        .. note: CustomFieldDevice is needed as the path in the API changes for this particular object

        >>> device = api.get_device(device_id=1)
        >>> cf = device42api.CustomFieldDevice(api=api)
        >>> cf.key      = 'used_since'
        >>> cf.type     = 'date'
        >>> cf.value    = '2014-04-02'
        >>> device.add_customField(cf)
        {'msg': ['custom key pair values added or updated', 1, 'Device with CustomFields'], 'code': 0}

        """
        if not isinstance(cf, CustomFieldDevice): raise Device42APIObjectException('need CustomField instance')
        cf.name = self.name
        rsp = cf.save()
        if isinstance(rsp, dict) and 'code' in rsp:
            if rsp['code'] == 0:
                self.custom_fields.append(cf)
        return rsp


class CustomFieldDevice(CustomField):
    """.. _CustomFieldDevice:

    .. hint:: special handling as API path changes for device custom fields

    """

    def __init__(self, json=None, parent=None, api=None):
        super(CustomFieldDevice, self).__init__(json, parent, api)
        self._api_path = 'device/custom_field'

    def save(self):
        if self.api:
            rsp = self.api.put(self._api_path, json=self.get_json())
            if isinstance(rsp, dict) and 'code' in rsp:
                if rsp['code'] == 0:
                    self._id = rsp['msg'][1]
            return rsp


class Hardware(Device42APIObject):
    """.. _Hardware:

    create Hardware object

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> h = device42api.Hardware(api=api)
    >>> h.name = 'TestHardware'
    >>> h.type = 1  # 1=Regular,2=Blade,3=Other
    >>> h.size = 1
    >>> h.depth = 1 # 1=Full,2=Half
    >>> h.notes = 'my test hardware'
    >>> h.save()
    {'msg': ['hardware model added or updated', 25, 'TestHardware', True, True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.type = Optional()  # 1=Regular,2=Blade,3=Other
        self.size = Optional()
        self.depth = Optional()  # 2 = Half depth or empty, 1 = Full depth
        self.blade_size = Optional()  # 1=Full Height,2=Half Height,3=Double Half Height,4=Double Full Height
        self.part_no = Optional()
        self.watts = Optional()
        self.spec_url = Optional()
        self.manufacturer = Optional()
        self.front_image_id = Optional()
        self.back_image_id = Optional()
        self.notes = Optional()
        super(Hardware, self).__init__(json, parent, api)
        self._api_path = 'hardwares'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.hardware_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException('required Attribute "name" not set')
        self.__get_json_validator__(('name', 'type', 'size', 'depth', 'blade_size', 'part_no', 'watts', 'spec_url',
                                     'manufacturer', 'front_image_id',
                                     'back_image_id', 'notes'))
        return self.json


class PDU_Model(Device42APIObject):
    """.. _PDU_Model:

    only representing the PDU Models as object

    .. note:: !!! since there's no API call to create/update these can only be retrieved !!!


    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> models = api.get_pdu_models()
    >>> for m in models:
    ...     print m
    pdu_model 1 ports 8 type NEMA 5-15R

    """

    def __init__(self, json=None, parent=None, api=None):
        super(PDU_Model, self).__init__(json, parent, api)
        self.ports = getattr(self, 'ports in pdu model')

    def __str__(self):
        pdu_port_count, pdu_port_type = 0, []
        for p in self.ports:
            pdu_port_count += p['pdu_port_count']
            pdu_port_type.append(p['pdu_port_type'])
        return 'pdu_model %s ports %s type %s' % (self.pdu_model_id, pdu_port_count, ','.join(pdu_port_type))


class PDU(Device42APIObject):
    """.. _PDU:

    create Rack object

    .. note:: !!! the PDU Model needs to exist an unfortunatley there's no API call to create it !!!


    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> pdu_models = api.get_pdu_models()
    >>> p = device42api.PDU(api=api)
    >>> p.name = 'Test PDU'
    >>> p.pdu_id = 1
    >>> p.rack_id = 80
    >>> p.device = 156
    >>> p.notes = 'Test PDU Test Device'
    >>> p.where = 'left'
    >>> p.start_at = 1
    >>> p.save()
    {'msg': '{\'pdu\': [u"Model PDU with pk u\'1\' does not exist."]}', 'code': 1}

    .. note:: !!! that might be an API bug ? updating after adding it in the GUI works


    >>> p.save()
    {'msg': ['PDU Rack Info successfully added/edited.', 1, 'PDU Test'], 'code': 0}
    >>> r = api.get_rack()
    >>> r[0].pdus
    [{'start_at': 1.0, 'name': 'PDU Test', 'orientation': 'Front', 'pdu_id': 1, 'depth': 'Full Depth', 'where': 'Left', 'size': 1.0}]

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.pdu_id = Optional()
        self.rack_id = Optional()
        self.device = Optional()
        self.notes = Optional()
        self.where = Optional()  # values: left, right, above, below or mounted.
        self.start_at = Optional()
        self.orientation = Optional()
        if json and 'pdu' in json:
            super(PDU, self).__init__(json['pdu'], parent, api)
        else:
            super(PDU, self).__init__(json, parent, api)
        self._api_path = 'pdus'

    def save(self):
        if self.api:
            if self.rack_id != Optional():
                rsp = self.api.__post_api__('%s/rack/' % self._api_path, body=self.get_json())
            else:
                rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.pdu_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException('required Attribute "name" not set')
        self.__get_json_validator__(
            ('name', 'pdu_id', 'rack_id', 'device', 'notes', 'where', 'start_at', 'orientation'))
        return self.json


class PatchPanel(Device42APIObject):
    """.. _PatchPanel:

    create PatchPanel

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> cp = device42api.PatchPanel(api=api)
    >>> p = api.get_patch_panels()[0]
    >>> mac = api.get_macid_byAddress('00:00:00:00:00:01')
    >>> cp.patch_panel_id = p.asset_id
    >>> cp.number = 1
    >>> cp.mac_id = mac.address_id
    >>> cp.get_json()
    {'patch_panel_id': 2, 'mac_id': 1, 'number': 1}
    >>> cp.save()
    {'msg': ['patch port details edited successfully.', 1, 'Test Panel: 1'], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.patch_panel_id = Required()
        self.number = Required()
        self.mac_id = Required()
        self.device_id = Required()
        self.device = Required()
        self.switchport_id = Optional()
        self.switch = Optional()
        self.switchport = Optional()
        self.patch_panel_port_id = Optional()
        self.label = Optional()
        self.obj_label1 = Optional()
        self.obj_label2 = Optional()
        self.back_connection_id = Optional()
        self.back_switchport_id = Optional()
        self.back_switch = Optional()
        self.back_switchport = Optional()
        self.cable_type = Optional()
        super(PatchPanel, self).__init__(json, parent, api)
        self._api_path = 'patch_panel_ports'

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.patch_panel_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        for attr in ('patch_panel_id', 'number'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException('required Attribute "%s" not set' % attr)
        if isinstance(self.mac_id, Required) and \
                (isinstance(self.device_id, Required) or isinstance(self.device), Required):
            raise Device42APIObjectException('required Attribute mac_id or device_id or device')
        elif not isinstance(self.mac_id, Required):
            if isinstance(self.device_id, Required):    self.device_id = Optional()
            if isinstance(self.device, Required):       self.device = Optional()
        if not isinstance(self.device, Required) or not isinstance(self.device_id, Required):
            if isinstance(self.mac_id, Required):       self.mac_id = Optional()
            for attr in ('device', 'device_id'):
                if isinstance(getattr(self, attr), Optional):   continue
        self.__get_json_validator__(('patch_panel_id', 'number', 'mac_id', 'device', 'device_id', 'switchport_id',
                                     'switch', 'switchport', 'patch_panel_port_id', 'label',
                                     'obj_label1', 'obj_label2', 'back_connection_id', 'back_switchport_id',
                                     'back_switch', 'back_switchport', 'cable_type'))
        return self.json


class PatchPanelModule(Device42APIObject):
    """.. _PatchPanelModule:

    only representing the Patch Panel Modules as object

    .. note:: !!! since there's no API call to create/update these can only be retrieved !!!


    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> modules = api.get_patch_panel_modules()
    >>> for m in modules:
    ...     print m
    Test Panel Singular port_type=RJ45 ports_in_row=12 ports=24

    """

    def __init__(self, json=None, parent=None, api=None):
        super(PatchPanelModule, self).__init__(json, parent, api)

    def __str__(self):
        if self._json != {}:
            return '%s %s port_type=%s ports_in_row=%s ports=%s' % (self.name, self.type, self.port_type,
                                                                    self.number_of_ports_in_row, self.number_of_ports)
        return ''
