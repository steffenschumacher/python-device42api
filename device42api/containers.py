from .base import *
from .content import Device, Asset


class Building(Device42APIObject):
    """.. _Building:

    create Building object

    >>> api = Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> b = Building(api=api)
    >>> b.name    = 'Test Building'
    >>> b.address = 'somewhere in the city'
    >>> b.notes   = 'destruction ongoing, leave the building immediatley'
    >>> b.save()
    {'msg': ['Building added/updated successfully', 3, 'TestBuilding', True, True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.address = Optional()
        self.contact_name = Optional()
        self.contact_phone = Optional()
        self.notes = Optional()
        super(Building, self).__init__(json, parent, api)
        self._api_path = 'buildings'

    def add_customField(self, cf=None):
        """add custom Fields to the object

        >>> b = api.get_building('Building with CustomFields')
        >>> cf = device42api.CustomField(api=api)
        >>> cf.key      = 'bldid'
        >>> cf.value    = 23
        >>> cf.value2   = 44
        >>> cf.notes    = 'Building ids: 23,44'
        >>> b.add_customField(cf)
        {'msg': ['custom key pair values added or updated', 3, 'Building with CustomFields'], 'code': 0}

        """
        if not isinstance(cf, CustomField): raise Device42APIObjectException('need CustomField instance')
        cf._api_path = 'building'
        cf.name = self.name
        rsp = cf.save()
        if isinstance(rsp, dict) and 'code' in rsp:
            if rsp['code'] == 0:
                self.custom_fields.append(cf)
        return rsp

    def __str__(self):
        return '%s %s' % (self.name, self.address)

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.building_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        if isinstance(self.name, Required):
            raise Device42APIObjectException('required Attribute "name" not set')
        self.__get_json_validator__(('name', 'address', 'contact_name', 'contact_phone', 'notes'))
        return self.json


class Room(Device42APIObject):
    """.. _Room:

    create Room object

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> r = device42api.Room(api=api)
    >>> r.name      = 'Test Room'
    >>> r.building  = 'Test Building'
    >>> r.building_id = 3
    >>> r.notes     = 'coffee corner for sysadmins'
    >>> r.save()
    {'msg': ['Room added/updated successfully', 2, 'Test Room', True, True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.building_id = Required()
        self.building = Required()
        self.notes = Optional()
        self.assets = []
        self.devices = []
        self.racks = []
        super(Room, self).__init__(json, parent, api)
        self._api_path = 'rooms'

    def __str__(self):
        return '%s %s' % (self.name)

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.room_id = rsp['msg'][1]
            return rsp

    def add_customField(self, cf=None):
        """add custom Fields to the object

        >>> room = api.get_room('Room with CustomFields')
        >>> cf = device42api.CustomField(api=api)
        >>> cf.key      = 'used_since'
        >>> cf.value    = '2014-04-02'
        >>> cf.type     = 'date'
        >>> room.add_customField(cf)
        {'msg': ['custom key pair values added or updated', 3, 'Room with CustomFields @ Building with CustomFields'], 'code': 0}

        """
        if not isinstance(cf, CustomField): raise Device42APIObjectException('need CustomField instance')
        cf._api_path = 'room'
        cf.name = self.name
        cf.id = self.room_id
        rsp = cf.save()
        if isinstance(rsp, dict) and 'code' in rsp:
            if rsp['code'] == 0:
                self.custom_fields.append(cf)
        return rsp

    def load(self):
        """get entries for room from API

        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> r = device42api.Room(api=api)
        >>> r.room_id = 2
        >>> r.load()
        >>> r.notes
        'coffee corner for sysadmins'
        >>> r.building
        'TestBuilding'

        """
        if self.api:
            json = self.api.get('rooms/%s' % self.room_id)
            for k in list(json.keys()):
                if k == 'devices':
                    for d in json[k]:
                        d = Device(json=d, parent=self, api=self.api)
                        d.load()
                        self.devices.append(d)
                elif k == 'racks':
                    for r in json[k]:
                        r = Rack(json=r, parent=self, api=self.api)
                        r.load()
                        self.racks.append(r)
                elif k == 'assets':
                    for a in json[k]:
                        a = Asset(json=a, parent=self, api=self.api)
                        a.load()
                        self.assets.append(a)
                else:
                    if json[k]:
                        setattr(self, k, json[k])
            self._json = json

    def get_json(self):
        for attr in ('name', 'building_id', 'building'):
            if isinstance(getattr(self, attr), Required):
                if attr == 'building_id' and isinstance(self.building, Required):
                    raise Device42APIObjectException('required Attribute "building_id" or Attribute "building" not set')
                elif attr == 'building' and isinstance(self.building_id, Required):
                    raise Device42APIObjectException('required Attribute "building_id" or Attribute "building" not set')
                elif attr == 'name':
                    raise Device42APIObjectException('required Attribute "name" not set')
        self.__get_json_validator__(('name', 'building', 'building_id', 'notes'))
        return self.json


class Rack(Device42APIObject):
    """.. _Rack:

    create Rack object

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> r = device42api.Rack(api=api)
    >>> r.name = 'TestRack1'
    >>> r.size = 42
    >>> r.room = 'Test Room'
    >>> r.building = 'TestBuilding'
    >>> r.room_id = 2
    >>> r.numbering_start_from_botton = 'no'
    >>> r.notes = 'my personal rack'
    >>> r.save()
    {'msg': ['rack added/updated.', 80, 'TestRack1', True, True], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.size = Required()
        self.room = Required()
        self.building = Optional()
        self.room_id = Optional()
        self.numbering_start_from_bottom = Optional()
        self.first_number = Optional()
        self.row = Optional()
        self.manufacturer = Optional()
        self.notes = Optional()
        self.assets = {}
        self.devices = {}

        if json and 'rack' in json:
            super(Rack, self).__init__(json['rack'], parent, api)
        else:
            super(Rack, self).__init__(json, parent, api)
        self._api_path = 'racks'
        if self.assets != {}:
            assets = {}
            for a in self.assets:
                aa = assets.get(a['start_at'], False)
                if not aa:
                    aa = Asset(json=a, parent=self, api=self.api)
                assets[a['start_at']] = aa
            self.assets = assets
        if self.devices != {}:
            devices = {}
            for d in self.devices:
                dd = devices.get(d['start_at'], False)
                if not dd:
                    dd = Device(json=d, parent=self, api=self.api)
                devices[d['start_at']] = dd
            self.devices = devices

    def __str__(self):
        return '%s' % self.name

    def get_assets(self):
        order = list(self.assets.keys())
        if self.numbering_start_from_bottom == 'no':
            order.sort()
        else:
            order.reverse()
        for k in order:
            yield self.assets[k]

    def get_devices(self):
        order = list(self.devices.keys())
        if self.numbering_start_from_bottom == 'no':
            order.sort()
        else:
            order.reverse()
        for k in order:
            yield self.devices[k]

    def add_device(self, device=None, start_at='auto'):
        """.. _Rack.add_device:

        add's a device to the rack starting at given position "start_at=xxx" or auto for next possible free slot

        >>> # if created you need to set the rack_id first
        >>> hw  = device42api.Hardware(api=api)
        >>> hw.name, hw.type, hw.size, hw.depth = 'Generic Hardware 1U', 1, 1, 1
        >>> h.save()
        >>> dev = device42api.Device(api=api)
        >>> dev.name = 'Test Device'
        >>> dev.hardware = 'Generic Hardware 1U'
        >>> dev.save()
        >>> r.rack_id = 80
        >>> r.add_device(dev, start_at=1)
        {'msg': ['device added or updated in the rack', 1, '[1.0] - TestRack1 -Test Room'], 'code': 0}

        """
        body = dict(device=device.name, rack_id=self.rack_id, start_at=start_at)
        rsp = self.api.__post_api__('device/rack', body=body)
        if isinstance(rsp, dict) and 'msg' in rsp:
            if rsp['msg'][-2]:
                self.load()
        return rsp

    def save(self):
        if self.api:
            rsp = self.api.__post_api__('%s/' % self._api_path, body=self.get_json())
            if isinstance(rsp, dict) and 'msg' in rsp:
                if rsp['msg'][-2]:
                    self.rack_id = rsp['msg'][1]
            return rsp

    def get_json(self):
        for attr in ('name', 'size', 'room'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException('required Attribute "%s" not set' % attr)
        self.__get_json_validator__(
            ('name', 'size', 'room', 'building', 'room_id', 'numbering_start_from_bottom', 'first_number',
             'row', 'manufacturer', 'notes'))
        return self.json

    def load(self):
        """get entries for rack from API

        >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
        >>> r = device42api.Rack(api=api)
        >>> r.rack_id = 80
        >>> r.load()
        >>> r.name, r.notes
        ('TestRack1', 'my personal rack')
        >>> r.devices
        {32.0: <device42api.Device object at 0x991cd0>, 36.0: <device42api.Device object at 0x991b50>, 6.0: <device42api.Device object at 0x9097d0>, 40.0: <device42api.Device object at 0x994d50>, 45.0: <device42api.Device object at 0x994f10>, 28.0: <device42api.Device object at 0x991b10>}

        """
        if self.api:
            json = self.api.get('racks/%s' % self.rack_id)
            for k in list(json.keys()):
                if k == 'devices':
                    for d in json[k]:
                        start_at = d['start_at']
                        d = Device(json=d, parent=self, api=self.api)
                        d.load()
                        self.devices[start_at] = d
                elif k == 'assets':
                    for a in json[k]:
                        start_at = a['start_at']
                        a = Asset(json=a, parent=self, api=self.api)
                        a.load()
                        self.assets[start_at] = a
                else:
                    if json[k]:
                        setattr(self, k, json[k])
            self._json = json

    def add_customField(self, cf=None):
        """add custom Fields to the object

        >>> rack = api.get_rack('Rack with CustomFields')[0]
        >>> cf = device42api.CustomField(api=api)
        >>> cf.key      = 'used_since'
        >>> cf.type     = 'date'
        >>> cf.value    = '2014-04-02'
        >>> rack.add_customField(cf)
        {'msg': ['custom key pair values added or updated', 3, 'Rack with CustomFields (in Room with CustomFields @ Building with CustomFields)'], 'code': 0}

        """
        if not isinstance(cf, CustomField): raise Device42APIObjectException('need CustomField instance')
        cf._api_path = 'rack'
        cf.name = self.name
        cf.id = self.rack_id
        rsp = cf.save()
        if isinstance(rsp, dict) and 'code' in rsp:
            if rsp['code'] == 0:
                self.custom_fields.append(cf)
        return rsp
