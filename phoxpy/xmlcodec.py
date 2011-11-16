# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
""""""

import datetime

__all__ = ['Attribute', 'Reference', 'Decoder', 'Encoder',
           'PhoxDecoder', 'PhoxEncoder']

class Attribute(unicode):
    """Sentinel unicode value that marks value to help serialize it back to
    XML attribute."""


class Reference(unicode):
    """Sentinel unicode value that marks value for RefField to help serialize it
    back to XML without losing information about their kind."""


class Decoder(object):
    """Base abstract decoder."""
    def decode(self, *args, **kwargs):
        """Abstract decode method."""
        raise NotImplementedError


class Encoder(object):
    """Base abstract encoder."""
    def encode(self, *args, **kwargs):
        """Abstract encode method."""
        raise NotImplementedError


class PhoxDecoder(Decoder):
    """XML decoder based on RosLabSystems protocol.

    +-------------------------------------+----------------------------+-------+
    | XML Tag                             | Python type                | Notes |
    +=====================================+============================+=======+
    | tag: f; attribs: t="B"; no childs   | :class:`bool`              | \(1)  |
    +-------------------------------------+----------------------------+-------+
    | tag: f; attribs: t="I"; no childs   | :class:`int`               |       |
    +-------------------------------------+----------------------------+-------+
    | tag: f; attribs: t="L"; no childs   | :class:`long`              |       |
    +-------------------------------------+----------------------------+-------+
    | tag: f; attribs: t="F"; no childs   | :class:`float`             |       |
    +-------------------------------------+----------------------------+-------+
    | tag: f; attribs: t="S"; no childs   | :class:`unicode`           |       |
    +-------------------------------------+----------------------------+-------+
    | tag: f; attribs: t="D"; no childs   | :class:`datetime.datetime` | \(2)  |
    +-------------------------------------+----------------------------+-------+
    | tag: r; no childs                   | :class:`Reference`         |       |
    +-------------------------------------+----------------------------+-------+
    | tag: s                              | :class:`list`              |       |
    +-------------------------------------+----------------------------+-------+
    | tag: o                              | :class:`dict`              | \(3)  |
    +-------------------------------------+----------------------------+-------+

    Notes:

    (1)
        Valid values are: ``false`` and ``true` or ValueError raises otherwise.

    (2)
        Datetime value has format ``%d.%m.%Y %H:%M:%S``.

    (3)
        May has additional attributes that would be decoded as
        :class:`Attribute` instances.

    For ``f`` tags value is searched in ``v`` attribute.
    """
    def __init__(self, default=None, handlers=None):
        self.handlers = {
            ('f', (('t', 'B'),)): self.decode_boolean_field,
            ('f', (('t', 'I'),)): self.decode_integer_field,
            ('f', (('t', 'L'),)): self.decode_long_field,
            ('f', (('t', 'F'),)): self.decode_float_field,
            ('f', (('t', 'S'),)): self.decode_text_field,
            ('f', (('t', 'D'),)): self.decode_datetime_field,
            ('r', ()): self.decode_ref_field,
            ('s', ()): self.decode_list_field,
            ('o', ()): self.decode_object_field,
        }
        if default is not None:
            self.decode_default = default
        if handlers is not None:
            self.handlers.update(handlers)

    def get_handler(self, elem):
        maybe_right_handler = None
        for tagname, attrs in self.handlers:
            if elem.tag != tagname:
                continue
            for key, value in attrs:
                if key not in elem.attrib:
                    break
                if elem.attrib[key] != value:
                    break
            else:
                maybe_right_handler = self.handlers[(tagname, attrs)]
        if maybe_right_handler is None:
            return self.decode_default
        return maybe_right_handler

    def decode(self, stream):
        """Decodes elements xml stream, produced by :func:`phoxpy.xml.parse`
        to Python object."""
        for event, elem in stream:
            return self.get_handler(elem)(stream, elem)

    def decode_default(self, stream, elem):
        raise ValueError('Unable to decode elem %s %s' % (elem, elem.attrib))

    def decode_field(self, stream, endelem):
        for event, elem in stream:
            assert elem is endelem and event == 'end', (event, elem)
            return elem.attrib['v']

    def decode_boolean_field(self, stream, endelem):
        value = self.decode_field(stream, endelem)
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            raise ValueError('Invalid boolean value')

    def decode_integer_field(self, stream, endelem):
        value = self.decode_field(stream, endelem)
        return int(value)

    def decode_long_field(self, stream, endelem):
        value = self.decode_field(stream, endelem)
        return long(value)

    def decode_float_field(self, stream, endelem):
        value = self.decode_field(stream, endelem)
        return float(value)

    def decode_text_field(self, stream, endelem):
        value = self.decode_field(stream, endelem)
        return value

    def decode_datetime_field(self, stream, endelem):
        value = self.decode_field(stream, endelem)
        return datetime.datetime.strptime(value, '%d.%m.%Y %H:%M:%S')

    def decode_ref_field(self, stream, endelem):
        for event, elem in stream:
            assert elem is endelem and event == 'end', (event, elem)
            return Reference(elem.attrib['i'])

    def decode_list_field(self, stream, endelem):
        data = []
        for event, elem in stream:
            if event == 'start':
                data.append(self.get_handler(elem)(stream, elem))
            if event == 'end':
                assert elem is endelem
                break
        return data

    def decode_object_field(self, stream, endelem):
        data = {}
        for event, elem in stream:
            if event == 'start':
                if not 'n' in elem.attrib:
                    raise ValueError('Unnamed element %s: attribute `n`'
                                     ' expected (%s)' % (elem, elem.attrib))
                key = elem.attrib['n']
                data[key] = self.get_handler(elem)(stream, elem)
            if event == 'end':
                assert elem is endelem, (elem, endelem)
                for key, value in elem.attrib.items():
                    if key in ['n', 't', 'v']:
                        continue
                    assert key not in data, \
                        'Collision: key %r is already in data %s' % (key, data)
                    data[key] = Attribute(value)
                break
        return data


class PhoxEncoder(Encoder):
    """Encoder for Python objects to RosLabSystems XML protocol.

    +-----------------------------+------------------------------------+-------+
    | Python type                 | XML tag                            | Notes |
    +=============================+====================================+=======+
    | :func:`bool`                | tag: f; attribs: t="B"             | \(1)  |
    +-----------------------------+------------------------------------+-------+
    | :func:`int`                 | tag: f; attribs: t="I"             |       |
    +-----------------------------+------------------------------------+-------+
    | :func:`long`                | tag: f; attribs: t="L"             |       |
    +-----------------------------+------------------------------------+-------+
    | :func:`float`               | tag: f; attribs: t="F"             |       |
    +-----------------------------+------------------------------------+-------+
    | :func:`str`,                | tag: f; attribs: t="S"             |       |
    | :func:`unicode`             |                                    |       |
    +-----------------------------+------------------------------------+-------+
    | :class:`datetime.date`,     | tag: f; attribs: t="D"             | \(2)  |
    | :class:`datetime.datetime`  |                                    |       |
    +-----------------------------+------------------------------------+-------+
    | :func:`list`, :class:`set`, | tag: s                             |       |
    | :func:`tuple`,              |                                    |       |
    | :class:`frozenset`          |                                    |       |
    +-----------------------------+------------------------------------+-------+
    | :class:`dict`               | tag: o                             |       |
    +-----------------------------+------------------------------------+-------+
    | :class:`Reference`          | tag: r                             |       |
    +-----------------------------+------------------------------------+-------+
    | :class:`Attribute`          | sets attribute to related tag      |       |
    +-----------------------------+------------------------------------+-------+

    Notes:

    (1)
        Valid values are: false, true or ValueError will be raised otherwise.

    (2)
        Datetime value would be formatted as ``%d.%m.%Y %H:%M:%S``.

    For ``f`` tags value stores  in ``v`` attribute.
    """
    def __init__(self, elemcls, default=None, handlers=None):
        self.Element = elemcls
        self.handlers = {
            bool: self.encode_boolean_field,
            int: self.encode_integer_field,
            long: self.encode_long_field,
            float: self.encode_float_field,
            str: self.encode_text_field,
            unicode: self.encode_text_field,
            datetime.date: self.encode_datetime_field,
            datetime.datetime: self.encode_datetime_field,
            Reference: self.encode_ref_field,
            set: self.encode_list_field,
            frozenset: self.encode_list_field,
            tuple: self.encode_list_field,
            list: self.encode_list_field,
            dict: self.encode_object_field,
        }
        if default is not None:
            self.encode_default = default
        if handlers is not None:
            self.handlers.update(handlers)

    def get_handler(self, value):
        tval = type(value)
        if tval in self.handlers:
            return self.handlers[tval]
        maybe_right_handlers = []
        for pytype, handler in self.handlers.items():
            if isinstance(value, pytype):
                if pytype in tval.__bases__:
                    maybe_right_handlers.append((10, handler))
                else:
                    maybe_right_handlers.append((1, handler))
        if not maybe_right_handlers:
            return self.encode_default
        maybe_right_handlers.sort()
        return maybe_right_handlers[-1][1]

    def encode(self, value):
        """Encodes to Python object :class:`phoxpy.xml.Element`."""
        return self.get_handler(value)(None, value)

    def encode_default(self, name, value):
        raise TypeError('Unable to encode %r' % value)

    def encode_value(self, tagname, name, value, **attribs):
        elem = self.Element(tagname)
        if name is not None:
            elem.attrib['n'] = name
        if value is not None:
            elem.attrib['v'] = unicode(value)
        elem.attrib.update(attribs)
        return elem

    def encode_boolean_field(self, name, value, **attribs):
        attribs['t'] = 'B'
        value = 'true' if value else 'false'
        return self.encode_value('f', name, value, **attribs)

    def encode_integer_field(self, name, value, **attribs):
        attribs['t'] = 'I'
        return self.encode_value('f', name, value, **attribs)

    def encode_long_field(self, name, value, **attribs):
        attribs['t'] = 'L'
        return self.encode_value('f', name, value, **attribs)

    def encode_float_field(self, name, value, **attribs):
        attribs['t'] = 'F'
        return self.encode_value('f', name, value, **attribs)

    def encode_text_field(self, name, value, **attribs):
        attribs['t'] = 'S'
        return self.encode_value('f', name, value, **attribs)

    def encode_datetime_field(self, name, value, **attribs):
        attribs['t'] = 'D'
        value = value.strftime('%d.%m.%Y %H:%M:%S')
        return self.encode_value('f', name, value, **attribs)

    def encode_ref_field(self, name, value, **attribs):
        attribs['i'] = unicode(value)
        return self.encode_value('r', name, None, **attribs)

    def encode_list_field(self, name, value, **attribs):
        elem = self.encode_value('s', name, None, **attribs)
        for item in value:
            elem.append(self.get_handler(item)(None, item))
        return elem

    def encode_object_field(self, name, value, **attribs):
        elem = self.encode_value('o', name, None, **attribs)
        for key, item in value.items():
            if item is None:
                continue
            if isinstance(item, Attribute):
                elem.attrib[key] = item
            else:
                elem.append(self.get_handler(item)(key, item))
        return elem
