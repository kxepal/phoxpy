# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy import xml
from phoxpy.mapping import MetaMapping, Mapping, AttributeField

__all__ = ['Message', 'PhoxRequest', 'PhoxResponse']

class Message(Mapping):
    """Base communication message mapping.

    :param sessionid: Session id.
    :type sessionid: str
    """
    sessionid = AttributeField()

    def __str__(self):
        raise NotImplementedError('Should be implemented for each message type')

    def unwrap(self, root=None, content=None):
        if root is None:
            root = xml.Element('content')
        elif content is None:
            content = xml.Element('content')
            root.append(content)
        return super(Message, self).unwrap(root, content)


class MetaPhoxRequest(MetaMapping):

    def __new__(mcs, name, bases, data):
        reqtype = None
        bases = list(bases)
        for idx, base in enumerate(bases):
            if isinstance(base, str):
                reqtype = bases.pop(idx)
                break
        data['_request_type'] = reqtype
        return super(MetaPhoxRequest, mcs).__new__(mcs, name, tuple(bases), data)

    def __call__(cls, *args, **data):
        if cls._request_type is not None:
            data['type'] = cls._request_type
        return super(MetaPhoxRequest, cls).__call__(*args, **data)


class PhoxRequest(Message):
    """Base request message.

    :param type: Message type.
    :type type: str

    :param buildnumber: Client build number.
    :type buildnumber: str

    :param version: Server version number.
    :type version: str
    """
    __metaclass__ = MetaPhoxRequest

    type = AttributeField()
    buildnumber = AttributeField()
    version = AttributeField()

    def __init__(self, **data):
        super(PhoxRequest, self).__init__(**data)
        assert self.type is not None

    def __str__(self):
        doctype = ('phox-request', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

    @classmethod
    def wrap_xmlelem(cls, xmlelem, defaults):
        defaults.update(xmlelem.attrib)
        assert 'type' in defaults
        root = xmlelem.find('content')
        assert root is not None
        return super(PhoxRequest, cls).wrap_xmlelem(root, defaults)

    @classmethod
    def wrap_stream(cls, stream, defaults):
        event, elem = stream.next()
        assert event == 'start' and elem.tag == 'phox-request'
        defaults.update(dict(elem.attrib.items()))
        assert 'type' in defaults
        return super(PhoxRequest, cls).wrap_stream(stream, defaults)

    def unwrap(self):
        root = xml.Element('phox-request')
        content = xml.Element('content')
        root.append(content)
        return super(PhoxRequest, self).unwrap(root, content)


class PhoxResponse(Message):
    """Base phox response message. Used as answer on phox requests messages.

    :param buildnumber: Build number.
    :type buildnumber: str
    """

    buildnumber = AttributeField()

    def __str__(self):
        doctype = ('phox-response', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.unwrap(), doctype=doctype)

    @classmethod
    def wrap_xmlelem(cls, xmlelem, defaults):
        root = xmlelem.find('content/o')
        assert root is not None, xml.dump(xmlsrc)
        defaults.update(xmlelem.attrib.items())
        return super(PhoxResponse, cls).wrap_xmlelem(root, defaults)

    @classmethod
    def wrap_stream(cls, stream, defaults):
        event, elem = stream.next()
        assert event == 'start' and elem.tag == 'phox-response'
        defaults.update(elem.attrib.items())
        event, elem = stream.next()
        assert event == 'start' and elem.tag == 'content'
        return super(PhoxResponse, cls).wrap_stream(stream, defaults)

    def unwrap(self):
        root = xml.Element('phox-response')
        content = xml.Element('content')
        obj = xml.Element('o')
        content.append(obj)
        root.append(content)
        return super(PhoxResponse, self).unwrap(root, obj)
