# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy import exceptions
from phoxpy import xml
from phoxpy.xmlcodec import PhoxDecoder
from phoxpy.mapping import MetaMapping, Mapping, AttributeField, \
                           PhoxMappingEncoder

__all__ = ['Message', 'PhoxRequest', 'PhoxResponse']

class Message(Mapping):
    """Base communication message mapping."""

    # Unique session id. Sets automatically after successful auth.
    sessionid = AttributeField()

    def __str__(self):
        raise NotImplementedError('Should be implemented for each message type')

    @classmethod
    def to_python(cls, xmlsrc):
        return xml.decode(xmlsrc, PhoxMessageDecoder)

    def to_xml(self):
        return xml.encode(self, PhoxMessageEncoder)


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
        # TODO: fix decoder workaround
        def to_python(cls, xmlsrc):
            class LocalPhoxMessageDecoder(PhoxMessageDecoder):
                def decode_phox_request(self, stream, endelem):
                    headers = dict(endelem.attrib.items())
                    data = self.decode(stream)
                    data.update(headers)
                    return cls(**data)
            return xml.decode(xmlsrc, LocalPhoxMessageDecoder)
        if cls._request_type is not None:
            data['type'] = cls._request_type
        cls.to_python = classmethod(to_python)
        return super(MetaPhoxRequest, cls).__call__(*args, **data)


class PhoxRequest(Message):
    """Base request message."""
    __metaclass__ = MetaPhoxRequest

    #: Request type.
    type = AttributeField()
    #: Build number. Should be same as server one.
    buildnumber = AttributeField()
    #: Server version.
    version = AttributeField()

    def __init__(self, **kwargs):
        super(PhoxRequest, self).__init__(**kwargs)
        assert self.type is not None

    def __str__(self):
        doctype = ('phox-request', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.to_xml(), doctype=doctype)


class PhoxResponse(Message):
    """Base phox response message. Used as answer on phox requests messages."""

    #: Server build number.
    buildnumber = AttributeField()

    def __str__(self):
        doctype = ('phox-response', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.to_xml(), doctype=doctype)


class PhoxMessageDecoder(PhoxDecoder):
    """Decoder for LIS specific messages."""

    def __init__(self, *args, **kwargs):
        super(PhoxMessageDecoder, self).__init__(*args, **kwargs)
        self.handlers.update({
            ('content', ()): self.decode_content,
            ('error', ()): self.decode_error,
            ('phox-request', ()): self.decode_phox_request,
            ('phox-response', ()): self.decode_phox_response,
        })

    def decode_error(self, stream, endelem):
        event, elem = stream.next()
        assert event == 'end' and elem is endelem
        code = elem.attrib['code']
        descr = elem.attrib.get('description', '')
        raise exceptions.get_error_class(int(code))(descr.encode('utf-8'))

    def decode_content(self, stream, endelem):
        if len(endelem) == 1 and endelem[0].tag == 'o':
            event, endelem = stream.next()
            result = self.decode_object_field(stream, endelem)
            stream.next() # fire `o` tag closing event
            return result
        return self.decode_object_field(stream, endelem)

    def decode_phox_request(self, stream, endelem):
        cls = PhoxRequest
        headers = dict(endelem.attrib.items())
        data = self.decode(stream)
        data.update(headers)
        return cls(**data)

    def decode_phox_response(self, stream, endelem):
        cls = PhoxResponse
        headers = dict(endelem.attrib.items())
        data = self.decode(stream)
        data.update(headers)
        return cls(**data)


class PhoxMessageEncoder(PhoxMappingEncoder):
    """Encoder for LIS specific messages to XML data."""

    def __init__(self, *args, **kwargs):
        super(PhoxMessageEncoder, self).__init__(*args, **kwargs)
        self.handlers.update({
            Message: self.encode_message,
            PhoxRequest: self.encode_phox_request,
            PhoxResponse: self.encode_phox_response,
        })

    def encode_message(self, name, value):
        content = self.encode(value._asdict())
        content.tag = 'content'
        return content

    def encode_phox_request(self, name, value):
        elem = self.encode(value._asdict())
        root = xml.Element('phox-request')

        root.attrib.update(elem.attrib.items())
        elem.attrib.clear()

        elem.tag = 'content'
        root.append(elem)
        return root

    def encode_phox_request_new(self, name, value):
        root = self.encode_phox_response(value)
        root.tag = 'phox-request'
        return root

    def encode_phox_response(self, name, value):
        elem = self.encode(value._asdict())
        root = xml.Element('phox-response')

        root.attrib.update(elem.attrib.items())
        elem.attrib.clear()

        content = xml.Element('content')
        content.append(elem)
        root.append(content)
        return root
