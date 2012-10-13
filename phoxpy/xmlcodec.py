# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
"""XML decoder/encoder for phox.dtd schema."""

import datetime
from phoxpy import xml

__all__ = ['Attribute', 'Reference', 'Decoder', 'Encoder',
           'PhoxDecoder', 'PhoxEncoder']

class Attribute(unicode):
    """Sentinel unicode value that marks value to help serialize it back to
    XML attribute."""


class Reference(unicode):
    """Sentinel unicode value that marks value for RefField to help serialize it
    back to XML without losing information about their kind."""


class Tag(object):

    __slots__ = ()
    tagname = None
    typeattr = None

    def decode(self, decode, stream, prevelem):
        for event, elem in stream:
            assert elem is prevelem and event == 'end', (event, elem)
            value = elem.attrib.get('v')
            return value

    def encode(self, encode, name=None, value=None, **attrs):
        elem = xml.Element(self.tagname)
        if name is not None:
            elem.attrib['n'] = name
        if value is not None:
            elem.attrib['v'] = unicode(value)
        if self.typeattr is not None:
            elem.attrib['t'] = self.typeattr
        elem.attrib.update(attrs)
        return elem

class Field(Tag):

    __slots__ = ()
    tagname = 'f'

    def encode(self, encode, name, value, **attrs):
        return super(Field, self).encode(encode, name, value, **attrs)


class BooleanField(Field):

    __slots__ = ()
    typeattr = 'B'

    def decode(self, decode, stream, prevelem):
        value = super(BooleanField, self).decode(decode, stream, prevelem)
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            raise ValueError('Invalid boolean value')

    def encode(self,encode, name, value, **attrs):
        value = 'true' if value else 'false'
        return super(BooleanField, self).encode(encode, name, value, **attrs)


class IntegerField(Field):

    __slots__ = ()
    typeattr = 'I'

    def decode(self, decode, stream, prevelem):
        value = super(IntegerField, self).decode(decode, stream, prevelem)
        return int(value)


class LongIntegerField(Field):

    __slots__ = ()
    typeattr = 'L'

    def decode(self, decode, stream, prevelem):
        value = super(LongIntegerField, self).decode(decode, stream, prevelem)
        return long(value)


class FloatField(Field):

    __slots__ = ()
    typeattr = 'F'

    def decode(self, decode, stream, prevelem):
        value = super(FloatField, self).decode(decode, stream, prevelem)
        return float(value)

class StringField(Field):

    __slots__ = ()
    typeattr = 'S'


class DateTimeField(Field):

    __slots__ = ()
    typeattr = 'D'

    def decode(self, decode, stream, prevelem):
        value = super(DateTimeField, self).decode(decode, stream, prevelem)
        return datetime.datetime.strptime(value, '%d.%m.%Y %H:%M:%S')

    def encode(self, encode, name, value, **attrs):
        value = value.strftime('%d.%m.%Y %H:%M:%S')
        return super(DateTimeField, self).encode(encode, name, value, **attrs)


class ReferenceField(Tag):

    __slots__ = ()
    tagname = 'r'

    def decode(self, decode, stream, prevelem):
        for event, elem in stream:
            assert elem is prevelem and event == 'end', (event, elem)
            return Reference(elem.attrib['i'])

    def encode(self, encode, name=None, value=None, **attrs):
        attrs['i'] = unicode(value)
        return super(ReferenceField, self).encode(encode, name, **attrs)


class ListField(Tag):

    __slots__ = ()
    tagname = 's'

    def decode(self, decode, stream, prevelem):
        data = []
        for event, elem in stream:
            if event == 'start':
                data.append(decode(stream, elem))
            if event == 'end':
                assert elem is prevelem
                break
        return data

    def encode(self, encode, name=None, value=None, **attrs):
        elem = super(ListField, self).encode(name, **attrs)
        for item in value:
            elem.append(encode(None, item))
        return elem


class ObjectField(Tag):

    __slots__ = ()
    tagname = 'o'

    def decode(self, decode, stream, prevelem):
        data = {}
        for event, elem in stream:
            if event == 'start':
                if not 'n' in elem.attrib:
                    raise ValueError('Unnamed element %s: attribute `n`'
                                     ' expected (%s)' % (elem, elem.attrib))
                key = elem.attrib['n']
                data[key] = decode(stream, elem)
            if event == 'end':
                assert elem is prevelem, (elem, prevelem)
                for key, value in elem.attrib.items():
                    if key in ['n', 't', 'v']:
                        continue
                    assert key not in data, 'name collision with attibute %r' % key
                    data[key] = Attribute(value)
                break
        return data


    def encode(self, encode, name=None, value=None, **attrs):
        elem = super(ObjectField, self).encode(name, **attrs)
        for key, value in value.items():
            if value is None:
                continue
            if isinstance(value, Attribute):
                elem.attrib[key] = value
            else:
                elem.append(encode(key, value))
        return elem


xml.register_field(Field, type(None))
xml.register_field(BooleanField, bool)
xml.register_field(IntegerField, int)
xml.register_field(LongIntegerField, long)
xml.register_field(FloatField, float)
xml.register_field(StringField, str,  unicode)
xml.register_field(ReferenceField, Reference)
xml.register_field(DateTimeField, datetime.date, datetime.datetime)
xml.register_field(ReferenceField, Reference)
xml.register_field(ListField, tuple, list, set, frozenset)
xml.register_field(ObjectField, dict)
