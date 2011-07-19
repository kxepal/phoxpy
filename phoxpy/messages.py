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
from phoxpy.mapping import Message
from phoxpy.mapping import BooleanField, IntegerField, ListField, LongField, \
                           RefField, TextField


class PhoxMessage(Message):
    """Base phox message class"""
    def __str__(self):
        raise NotImplementedError('should be implemented for each message type')


class PhoxRequest(PhoxMessage):
    """Base phox request message. Used for data requests."""
    def __init__(self, msgtype, sessionid=None, buildnumber=None, version=None,
                 **data):
        """Initialize PhoxRequest instance.

        Args:
            msgtype (str): Message type.
            session_id (str): Session id number.
            buildnumber (str): LIS client build number.
            version (str): LIS server version number.

        Kwargs:
            Message fields values.
        """
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
        return self._type

    @property
    def sessionid(self):
        return self._session_id

    @property
    def buildnumber(self):
        return self._buildnumber

    @property
    def version(self):
        return self._version

    def unwrap(self):
        root = xml.Element('phox-request', type=self.type)
        if self.sessionid is not None:
            root.attrib['sessionid'] = self.sessionid
        if self.buildnumber is not None:
            root.attrib['buildnumber'] = self.buildnumber
        if self.version is not None:
            root.attrib['version'] = self.version
        return super(PhoxRequest, self).unwrap(root)


class PhoxResponse(PhoxMessage):
    """Base phox response message. Used as answer on phox requests messages."""
    def __init__(self, sessionid=None, buildnumber=None, **data):
        """Initialize PhoxResponse instance.

        Args:
            session_id (str): Session id number.
            buildnumber (str): LIS client build number.

        Kwargs:
            Message fields values.
        """
        self._session_id = sessionid
        self._buildnumber = buildnumber
        super(PhoxResponse, self).__init__(**data)

    def __str__(self):
        doctype = ('phox-response', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

    @property
    def sessionid(self):
        return self._session_id

    @property
    def buildnumber(self):
        return self._buildnumber

    def unwrap(self):
        root = xml.Element('phox-response')
        if self.sessionid is not None:
            root.attrib['sessionid'] = self.sessionid
        if self.buildnumber is not None:
            root.attrib['buildnumber'] = self.buildnumber
        return super(PhoxResponse, self).unwrap(root)


class AuthRequest(PhoxRequest):
    """Authentication request message."""
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

    @classmethod
    def wrap(cls, xmlsrc, **defaults):
        root = xml.ElementTree(xmlsrc.find('content'))
        return super(AuthRequest, cls).wrap(root, **defaults)


class AuthResponse(PhoxResponse):
    """Authentication response message."""
    departments = ListField(RefField())
    hospitals = ListField(RefField())
    rights = ListField(RefField())
    employee = RefField()
    session_code = LongField(name='sessionCode')
    server_version = TextField(name='serverVersion')
    admin_mode = BooleanField(name='adminMode')

    @classmethod
    def wrap(cls, xmlsrc):
        attrs = dict(xmlsrc.attrib.items())
        root = xml.ElementTree(xmlsrc.find('content/o'))
        return super(AuthResponse, cls).wrap(root, **attrs)

    def unwrap(self):
        # rewrite phox-response/content/data to phox-response/content/o/data
        root = super(AuthResponse, self).unwrap()
        root[0].tag = 'o'
        newroot = xml.Element(root.tag)
        newroot.attrib.update(dict(root.attrib.items()))
        root.attrib.clear()
        root.tag = 'content'
        newroot.append(root)
        return newroot

