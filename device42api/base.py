from requests import Session, auth
from base64 import b64encode


class Required(object): pass


class Optional(object): pass


class Device42APIObjectException(Exception): pass


class Device42APIConnection(object):
    """.. _Device42APIClient:

    API abstraction class
    this object deals with the https request to the device42 service

    >>> api = device42api.Device42APIConnection(host='192.168.122.200', username='admin', password='changeme')

    * get(path='.../')  # everythin after /api/1.0/
    * __post_api__(path='.../', v='1.0', body=dict())   # v='1.0' or None
    * __put_api__(path='.../', body=dict()) # currently not used

    """

    def __init__(self, host=None, port=443, username=None, password=None, verify_ssl=False):
        self._host = 'https://{}:{}/api/'.format(host, port)
        self._macAddress = {}
        self._customers = {}
        self._buildings = {}
        self._racks = {}
        self._rooms = {}
        self._servicelevels = {}
        self._assets = {}
        self._ses = Session()
        self._verify = verify_ssl
        self._ses.auth = auth.HTTPBasicAuth(username, password)
        self._ses.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def url(self, path, v='1.0'):
        # if not path.startswith('patch_panel_ports') and not path.endswith('?follow=yes'):
        # unfortunately for this url path they API doesn't accept tailing '/'

        if not path.endswith('/'):
            path += '/'
        return self._host + v + '/' + path

    def get(self, path=None, v='1.0', args={}):
        r = self._ses.get(self.url(path, v), params=args)
        r.raise_for_status()
        return r.json()

    def post(self, path=None, v='1.0', json=None, data={}):
        #self._headers['content-type'] = 'application/x-www-form-urlencoded'
        r = self._ses.post(self.url(path, v), data=data, json=json)
        r.raise_for_status()
        return r.json()

    def put(self, path=None, v='1.0', json=None):
        r = self._ses.put(self.url(path, v), json=json)
        r.raise_for_status()
        return r.json()

    def delete(self, path=None, v='1.0', data={}):
        r = self._ses.put(self.url(path, v), params=data)
        r.raise_for_status()
        return r.json()


class Device42APIObject(object):
    """.. _Device42APIObject:

    basic Object representing a device42 API object,
    inherit from this one and implement at least:

    * save()
    * load()
    * get_json()

    """

    def __init__(self, json=None, parent=None, api=None):
        self.api = api
        self._json = json
        self.json = dict()
        self.parent = parent
        self._api_path = None
        self.custom_fields = []
        if self._json:
            for k in list(self._json.keys()):
                if k == 'custom_fields':
                    for c in self._json[k]:
                        self.custom_fields.append(CustomField(json=c, parent=self))
                setattr(self, k, self._json[k])
        else:
            self._json = dict()

    def save(self):
        raise Device42APIObjectException('need to implement save')

    def get_json(self):
        raise Device42APIObjectException('need to implement get_json')

    def load(self):
        raise Device42APIObjectException('need to implement load')

    def __get_json_validator__(self, keys=[]):
        for k in keys:
            v = getattr(self, k)
            if isinstance(v, Optional):  continue
            if k in self._json and self._json[k] != v:
                if not isinstance(v, int):
                    self.json[k] = str(v)
                else:
                    self.json[k] = v
            elif not k in self._json:
                if not isinstance(v, int):
                    self.json[k] = str(v)
                else:
                    self.json[k] = v
        for k in list(self._json.keys()):
            try:
                v = getattr(self, k)
                if isinstance(v, Optional):  continue
                if self._json[k] != v:
                    if not isinstance(v, int):
                        self.json[k] = str(v)
                    else:
                        self.json[k] = v
            except AttributeError:
                continue


class CustomField(Device42APIObject):
    """.. _CustomField:

    create CustomField

    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> b = device42api.Building(api=api)
    >>> b.name    = 'Building with CustomFields'
    >>> cf1 = device42api.CustomField(api=api)
    >>> cf1.key  = 'created'
    >>> cf1.type = 'date'
    >>> cf1.value = '2014-04-02'
    >>> cf1._api_path = 'building'
    >>> cf1.name = b.name
    >>> cf1.save()
    {'msg': ['custom key pair values added or updated', 1, 'Building with CustomFields'], 'code': 0}

    """

    def __init__(self, json=None, parent=None, api=None):
        self.name = Required()
        self.key = Required()
        self.type = Optional()  # default = Text, can be number, date fmt="yyyy-mm-dd"
        self.value = Optional()
        self.value2 = Optional()
        self.notes = Optional()
        super(CustomField, self).__init__(json, parent, api)

    def save(self):
        if self.api:
            rsp = self.api.put('custom_fields/%s/' % self._api_path, json=self.get_json())
            if isinstance(rsp, dict) and 'code' in rsp:
                if rsp['code'] == 0:
                    self._id = rsp['msg'][1]
            return rsp

    def get_json(self):
        for attr in ('name', 'key'):
            if isinstance(getattr(self, attr), Required):
                raise Device42APIObjectException('required Attribute "%s" not set' % attr)
        self.__get_json_validator__(('name', 'key', 'type', 'value', 'value2', 'notes'))
        return self.json


class History(Device42APIObject):
    """.. History:

    only representing the History as object

    .. note:: !!! can only be retrieved !!!


    >>> api = device42api.Device42API(host='127.0.0.1', username='admin', password='changeme')
    >>> for h in api.get_history():
    ...     print h
    2014-04-04T10:16:46.776Z Add/Change(API) admin building

    """

    def __init__(self, json=None, parent=None, api=None):
        self.action_time = None
        self.user = None
        self.action = None
        self.content_type = None
        super(History, self).__init__(json, parent, api)

    def __str__(self):
        return '%s %s %s %s' % (self.action_time, self.action, self.user, self.content_type)


__all__ = ["CustomField", "Optional", "Required", "Device42APIObjectException", "Device42APIConnection",
           "Device42APIObject", "History"]
