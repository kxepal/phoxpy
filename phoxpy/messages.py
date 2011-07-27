# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from random import randint
from phoxpy import xml
from phoxpy.mapping import BooleanField, IntegerField, ListField, LongField, \
                           GenericMapping, RefField, TextField


__all__ = ['Message', 'PhoxRequest', 'PhoxResponse',
           'AuthRequest', 'AuthResponse']

class Message(GenericMapping):
    """Base communication message mapping."""
    def __str__(self):
        raise NotImplementedError('Should be implemented for each message type')

    def unwrap(self, root=None):
        content = xml.Element('content')
        super(Message, self).unwrap(content)
        if root is not None:
            root.append(content)
            return root
        return content


class PhoxRequest(Message):
    """Base request message.

    :param msgtype: Message type.
    :type msgtype: str

    :param sessionid: Session id number.
    :type sessionid: str

    :param buildnumber: Client build number.
    :type buildnumber: str

    :param version: Server version number.
    :type version: str
    """
    def __init__(self, msgtype, sessionid=None, buildnumber=None, version=None,
                 **data):
        self._type = msgtype
        self._session_id = sessionid
        self._buildnumber = buildnumber
        self._version = version
        super(PhoxRequest, self).__init__(**data)

    def __str__(self):
        doctype = ('phox-request', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

    @property
    def type(self):
        """Request message type."""
        return self._type

    @property
    def sessionid(self):
        """Session id number for related request."""
        return self._session_id

    @property
    def buildnumber(self):
        return self._buildnumber

    @property
    def version(self):
        return self._version

    @classmethod
    def wrap(cls, xmlsrc, **defaults):
        return super(PhoxRequest, cls).wrap(xmlsrc.find('content'), **defaults)

    def unwrap(self):
        root = xml.Element('phox-request', type=self.type)
        if self.sessionid is not None:
            root.attrib['sessionid'] = self.sessionid
        if self.buildnumber is not None:
            root.attrib['buildnumber'] = self.buildnumber
        if self.version is not None:
            root.attrib['version'] = self.version
        return super(PhoxRequest, self).unwrap(root)


class PhoxResponse(Message):
    """Base phox response message. Used as answer on phox requests messages.

    :param sessionid: Session id.
    :type sessionid: str

    :param buildnumber: Build number.
    :type buildnumber: str
    """
    def __init__(self, sessionid=None, buildnumber=None, **data):
        self._session_id = sessionid
        self._buildnumber = buildnumber
        super(PhoxResponse, self).__init__(**data)

    def __str__(self):
        doctype = ('phox-response', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

    @property
    def sessionid(self):
        """Session id number for related response."""
        return self._session_id

    @property
    def buildnumber(self):
        return self._buildnumber

    @classmethod
    def wrap(cls, xmlsrc):
        root = xmlsrc.find('content/o')
        if root is None:
            root = xmlsrc.find('content')
        assert root is not None, xml.dump(xmlsrc)
        attrs = dict(xmlsrc.attrib.items())
        return super(PhoxResponse, cls).wrap(root, **attrs)

    def unwrap(self):
        root = xml.Element('phox-response')
        if self.sessionid is not None:
            root.attrib['sessionid'] = self.sessionid
        if self.buildnumber is not None:
            root.attrib['buildnumber'] = self.buildnumber
        content =  super(PhoxResponse, self).unwrap()
        if len(content):
            content.tag = 'o' # content => o
            content, obj = xml.Element('content'), content
            content.append(obj)
        root.append(content)
        return root


class AuthRequest(PhoxRequest):
    """Authentication request message.

    :param company: Company name.
    :type company: str

    :param lab: Laboratory name.
    :type lab: str

    :param login: Login name.
    :type login: str

    :param password: Related password.
    :type password: str

    :param machine: Client hostname.
    :type machine: str

    :param client_id: License string heavy binded to computer hardware.
    :type client_id: str

    :param session_code: Secret session code.
    :type session_code: int

    :param instance_count: Instance count.
    :type instance_count: int
    """
    company = TextField(default='')
    lab = TextField(default='')
    login = TextField()
    password = TextField()
    machine = TextField()
    client_id = TextField(name='clientId')
    session_code = IntegerField(name='sessionCode',
                                default=lambda: randint(10000, 20000))
    instance_count = IntegerField(name='instanceCount', default=0)

    def __init__(self, *args, **data):
        super(AuthRequest, self).__init__('login', *args, **data)


class AuthResponse(PhoxResponse):
    """Authentication response message.

    :param departments: List of department ids which user is belong to.
    :type departments: list

    :param hospitals: List of hospital ids which user is belong to.
    :type  hospitals: list

    :param rights: List of active permission ids.
    :type  rights: list

    :param employee: Referenced Employee object id.
    :type employee: int

    :param session_code: Session code number.
    :type session_code: int or long

    :param server_version: Server version string.
    :type server_version: str

    :param admin_mode: Flag of admin mode usage.
    :type admin_mode: bool
    """
    departments = ListField(RefField())
    hospitals = ListField(RefField())
    rights = ListField(RefField())
    employee = RefField()
    session_code = LongField(name='sessionCode')
    server_version = TextField(name='serverVersion')
    admin_mode = BooleanField(name='adminMode')
