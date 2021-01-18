from .base import *
from .content import *
from .containers import *
from .ipam import *
from .commercial import *


class Device42API(Device42APIConnection):
    """.. _Device42API:
    
    API abstraction class
    this object deals with the https request to the device42 service
    
    >>> api = device42api.Device42API(host='192.168.122.200', username='admin', password='changeme')
    >>> for r in api.get_rack():
    ...     print r
    ...
    TestRack1
    TestRack2
    
    low level methods:
    
    * get(path='.../')  # everythin after /api/1.0/
    * __post_api__(path='.../', v='1.0', body=dict())   # v='1.0' or None
    * __put_api__(path='.../', body=dict()) # currently not used
    
    """

    def __init__(self, host=None, port=443, username=None, password=None, verify_ssl=False, noInit=False):
        super(Device42API, self).__init__(host, port, username, password, verify_ssl)
        self._macAddress = {}
        self._customers = {}
        self._buildings = {}
        self._racks = {}
        self._rooms = {}
        self._servicelevels = {}
        self._assets = {}

        if noInit:      return
        try:
            self.get_building()
            self.get_customer()
            self.get_rack()
            self.get_room()
            self.get_service_level()
        except Exception as e:
            print((str(e)))

    def get_macid_byAddress(self, macaddress=None, reload=False):
        """return IPAM_macaddress object from API if found otherwise False
        
        >>> api.get_macid_byAddress('11:11:11:11:22:01')
        <device42api.IPAM_macaddress object at 0x26a0a50>
        >>> api.get_macid_byAddress('11:11:11:11:22:01').macaddress_id
        3
        
        """
        if not self._macAddress or reload:
            for m in self.get('macs/')['macaddresses']:
                mac = IPAM_macaddress(json=m, parent=self, api=self)
                self._macAddress[mac.macaddress] = mac
        return self._macAddress.get(macaddress, False)

    def get_pdu_models(self):
        """return all PDU models from device42
        
        >>> api.get_pdu_models()
        [<device42api.PDU_Model object at 0x26a0bd0>]
        >>> for m in api.get_pdu_models():
        ...     print m
        ... 
        pdu_model 1 ports 8 type NEMA 5-15R
        
        """
        pdum = []
        for r in self.get('pdu_models/')['pdu_models']:
            pdum.append(PDU_Model(json=r, parent=self, api=self))
        return pdum

    def get_rack(self, name=None, building=None, room=None, reload=True):
        """return all racks from device42
        
        >>> api.get_rack('TestRack1')
        [<device42api.Rack object at 0x26a0dd0>]
        >>> for r in api.get_rack():
        ...     for d in r.devices.values():
        ...             print u'device: %s id: %s' % (d.name, d.device_id)
        ... 
        device: Test Device id: 1
        >>>
        >>> api.get_rack(room='Test Room')
        
        """
        if not self._racks or reload:
            for r in self.get('racks/')['racks']:
                ra = Rack(json=r, parent=self, api=self)
                self._racks[ra.name] = ra

        if name is None and building is None and room is None:
            return list(self._racks.values())
        if name and building is None and room is None:
            return [r for r in self.racks if r.name == name]

        racks = []
        if building:
            for r in self._racks:
                if room is None:
                    if r.building == building:
                        if not name or name == r.name:
                            racks.append(r)
                elif r.building == building and r.room == room:
                    if not name or r.name == name:
                        racks.append(r)
        elif room:
            for r in list(self._racks.values()):
                if r.room != room:
                    continue
                if name is None:
                    racks.append(r)
                elif name == r.name:
                    racks.append(r)
        return racks

    def get_asset(self, name=None, reload=False):
        """return all assets from device42
        
        >>> api.get_asset()
        [<device42api.Asset object at 0x26a0b50>, <device42api.Asset object at 0x26a8450>]
        >>> for a in api.get_assets():
        ...     print a, a.asset_id
        ... 
        <device42api.Asset object at 0x26aaa50> 1
        <device42api.Asset object at 0x26a8590> 2
        >>> api.get_asset('Asset with CustomFields')
        <device42api.Asset object at 0x1c5e410>
        
        """
        if self._assets == {} or reload:
            for a in self.get('assets/')['assets']:
                ass = Asset(json=a, parent=self, api=self)
                ass.load()
                self._assets[ass.id] = ass
        if name:
            assets = []
            for a in list(self._assets.values()):
                if a.name == name:  assets.append(a)
            return assets
        return list(self._assets.values())

    def get_patch_panels(self):
        """return all patch panels from device42, use get_assets and validate patch_panel_model_id field
        
        >>> api.get_patch_panels()
        [<device42api.Asset object at 0x26b2450>]
        >>> for p in api.get_patch_panels():
        ...     print p, p.asset_id
        ... 
        <device42api.Asset object at 0x26a8150> 2
        
        """
        panels = []
        for a in self.get_assets():
            if a.type != 'Patch Panel': continue
            panels.append(a)
        return panels

    def get_patch_panel_modules(self):
        """return all patch panels from device42, use get_assets and validate patch_panel_model_id field
        
        >>> api.get_patch_panels()
        [<device42api.Asset object at 0x26b2450>]
        >>> for p in api.get_patch_panels():
        ...     print p, p.asset_id
        ... 
        <device42api.Asset object at 0x26a8150> 2
        
        """
        modules = []
        for m in self.get('patch_panel_models'):
            modules.append(PatchPanelModule(json=m, parent=self, api=self))
        return modules

    def get_customer(self, name=None, reload=False):
        """return Customer object from API if found otherwise False
        
        >>> api.get_customer('device42 Support')
        <device42api.Customer object at 0x1887a10>
        >>> api.get_customer('unknown')
        False
        >>> for con in api.get_customer('device42 Support').Contacts:
        ...    print con
        {'phone': '111-111-111', 'address': 'Helpdesk Office 1', 'type': 'Helpdesk', 'email': 'helpdesk@device42.com', 'name': 'Helpdesk1'}
        
        """
        if self._customers == {} or reload:
            for c in self.get('customers/')['Customers']:
                cu = Customer(json=c, parent=self, api=self)
                self._customers[cu.name] = cu
        return self._customers.get(name, False)

    def get_building(self, name=None, reload=False):
        """return Building object from API if found otherwise False
        
        >>> api.get_building('device42 Support')
        <device42api.Building object at 0x1887d90>
        >>> api.get_building('White House - Oval Office')
        False
        
        """
        if self._buildings == {} or reload:
            for c in self.get('buildings/')['buildings']:
                b = Building(json=c, parent=self, api=self)
                self._buildings[b.name] = b
        return self._buildings.get(name, False)

    def get_room(self, name=None, reload=False):
        """return Room object from API if found otherwise False
        
        >>> api.get_room('device42 Support')
        <device42api.Building object at 0x1887d90>
        >>> api.get_room('Oval Office')
        False
        
        """
        if self._rooms == {} or reload:
            for c in self.get('rooms/')['rooms']:
                r = Room(json=c, parent=self, api=self)
                self._rooms[r.name] = r
        return self._rooms.get(name, False)

    def get_service_level(self, name=None, reload=False):
        """return ServiceLevel object from API if found otherwise False
        
        >>> api.get_service_level('Production')
        <device42api.ServiceLevel object at 0x1aa4310>
        >>> print api.get_service_level('Production')
        Production(1)
        
        """
        if self._servicelevels == {} or reload:
            for c in self.get('service_level/'):
                r = ServiceLevel(json=c, parent=self, api=self)
                self._servicelevels[r.name] = r
        if name:
            return self._servicelevels.get(name, False)
        return self._servicelevels

    def get_history(self):
        """return History records from API
        
        >>> for h in api.get_history():
        ...     print h
        2014-04-04T10:16:46.776Z Add/Change(API) admin building
        
        """
        for h in self.get('history/'):
            yield History(json=h, parent=self, api=self)

    def get_device(self, name=None, device_id=None, serial=None):
        """return the Device from the API classified by
        
        * name
        * device_id
        * serial
        
        .. attention:: return by name isn't working with device names including spaces (or anything which requires quoting) as the API always responses with 404 NOT FOUND. You're seeing this error because you have DEBUG Enabled in your settings
        
        """
        device = Device(parent=self, api=self)
        if name:
            device_id = self.get('devices/name/%s/?follow=yes' % name)['id']
            if device_id:
                device.device_id = device_id
                device.load()
                return device
            return False
        elif device_id:
            device.device_id = device_id
            device.load()
            return device
        elif serial:
            device_id = self.get('devices/serial/%s' % serial)
            if device_id:
                device.device_id = device_id
                device.load()
                return device
            return False
        return False
