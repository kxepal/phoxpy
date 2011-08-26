# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy import xml
from phoxpy.mapping import GenericMapping, AttributeField


__all__ = ['Message', 'PhoxRequest', 'PhoxResponse']

class Message(GenericMapping):
    """Base communication message mapping.

    :param sessionid: Session id.
    :type sessionid: str
    """
    sessionid = AttributeField()

    def __str__(self):
        raise NotImplementedError('Should be implemented for each message type')

    def unwrap(self, root=None):
        content = xml.Element('content')
        super(Message, self).unwrap(content)
        if root is not None:
            root.attrib.update(content.attrib.items())
            content.attrib.clear()
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
    type = AttributeField()
    buildnumber = AttributeField()
    version = AttributeField()

    def __init__(self, type, **data):
        super(PhoxRequest, self).__init__(type=type, **data)
        assert self.type is not None

    def __str__(self):
        doctype = ('phox-request', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

    @classmethod
    def wrap(cls, xmlsrc, **defaults):
        defaults.setdefault('type', xmlsrc.attrib['type'])
        defaults.setdefault('sessionid', xmlsrc.attrib.get('sessionid'))
        defaults.setdefault('buildnumber', xmlsrc.attrib.get('buildnumber'))
        defaults.setdefault('version', xmlsrc.attrib.get('version'))
        req = super(PhoxRequest, cls).wrap(xmlsrc.find('content'), **defaults)
        return req

    def unwrap(self):
        return super(PhoxRequest, self).unwrap(xml.Element('phox-request'))


class PhoxResponse(Message):
    """Base phox response message. Used as answer on phox requests messages.

    :param sessionid: Session id.
    :type sessionid: str

    :param buildnumber: Build number.
    :type buildnumber: str
    """

    buildnumber = AttributeField()

    def __str__(self):
        doctype = ('phox-response', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

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
