# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy import xml
from phoxpy.mapping import GenericMapping


__all__ = ['Message', 'PhoxRequest', 'PhoxResponse']

class Message(GenericMapping):
    """Base communication message mapping.

    :param sessionid: Session id.
    :type sessionid: str
    """
    def __init__(self, sessionid=None, **data):
        self._session_id = sessionid
        super(Message, self).__init__(**data)

    def __str__(self):
        raise NotImplementedError('Should be implemented for each message type')

    def _get_sessionid(self):
        """Session id number."""
        return self._session_id

    def _set_sessionid(self, value):
        if value is not None and not isinstance(value, basestring):
            raise TypeError('Invalid value type %r' % type(value))
        self._session_id = value

    sessionid = property(_get_sessionid, _set_sessionid)

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
        self._buildnumber = buildnumber
        self._version = version
        super(PhoxRequest, self).__init__(sessionid, **data)

    def __str__(self):
        doctype = ('phox-request', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

    @property
    def type(self):
        """Request message type."""
        return self._type

    @property
    def buildnumber(self):
        return self._buildnumber

    @property
    def version(self):
        return self._version

    @classmethod
    def wrap(cls, xmlsrc, **defaults):
        defaults.setdefault('msgtype', xmlsrc.attrib['type'])
        defaults.setdefault('sessionid', xmlsrc.attrib.get('sessionid'))
        defaults.setdefault('buildnumber', xmlsrc.attrib.get('buildnumber'))
        defaults.setdefault('version', xmlsrc.attrib.get('version'))
        req = super(PhoxRequest, cls).wrap(xmlsrc.find('content'), **defaults)
        return req

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
        self._buildnumber = buildnumber
        super(PhoxResponse, self).__init__(sessionid, **data)

    def __str__(self):
        doctype = ('phox-response', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

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
