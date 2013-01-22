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
from types import GeneratorType
from . import exceptions
from . import xml
from .mapping import Mapping
from .messages import Content, PhoxEvent, PhoxRequest, PhoxResponse
from .xmlobjects import Attribute, Reference


class BaseCodec(object):
    """Base XML element codec."""
    __slots__ = ()
    #: XML tag name to handle.
    tagname = None
    #: XML stored value type marker.
    typemarker = None

    @classmethod
    def to_python(cls, xmlsrc):
        """Shortcut to :meth:`decode`.

        :param xmlsrc: XML data source.
        :type xmlsrc: str, file-like object or :class:`~phoxpy.xml.Element`
                      instance.

        :return: Python object depended on decoding logic.
        """
        stream = xml.make_stream(xmlsrc)
        event, elem = stream.next()
        return cls().decode(xml.decode_elem, stream, elem)

    @classmethod
    def to_xml(cls, obj, **kwargs):
        """Shortcut to :meth:`encode`.

        :param obj: Python object.

        :return: :class:`~phoxpy.xml.Element` instance.
        """
        kwargs.setdefault('name', None)
        return cls().encode(xml.encode_elem, value=obj, **kwargs)

    def decode(self, decode, stream, curelem):
        """Decodes XML element to Python object.

        :param decode: Element decoding handler.
        :type decode: callable

        :param stream: XML event-element pairs generator.
        :type stream: generator
        
        :param curelem: Current decoded XML element.
        :type curelem: :class:`~phoxpy.xml.Element`

        :raises: :exc:`AssertionError` if emitted by `stream` event is not
                 ``"end"`` for same element as `curelem` one.

        :return: `str` or `None` if ``v`` attribute missed.
        """
        for event, elem in stream:
            assert elem is curelem and event == 'end', (event, elem, curelem)
            value = elem.attrib.get('v')
            return value

    def encode(self, encode, name=None, value=None, **attrs):
        """Encodes Python object to XML element."""
        elem = xml.Element(self.tagname)
        if name is not None:
            elem.attrib['n'] = name
        if value is not None:
            elem.attrib['v'] = unicode(value)
        if self.typemarker is not None:
            elem.attrib['t'] = self.typemarker
        elem.attrib.update(attrs)
        return elem


class FallbackCodec(BaseCodec):
    """Fallback codec for cases when there is suitable codecs for decodec
    or encoded object.

    >>> FallbackCodec.to_python('<foo />')  #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> FallbackCodec.to_xml(object())      #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...
    """


    def decode(self, decode, stream, curelem):
        raise ValueError('unable to decode element %r' % curelem)

    def encode(self, encode, name=None, value=None, **attrs):
        raise ValueError('unable to encode object %r' % value)


class FieldCodec(BaseCodec):
    """Base codec for primitive types that described by `f` named XML tag."""
    __slots__ = ()
    tagname = 'f'


class BooleanCodec(FieldCodec):
    """Codec for :class:`bool` type.

    >>> BooleanCodec.to_python('<f t="B" v="false" />')
    False
    >>> BooleanCodec.to_python('<f t="B" v="true" />')
    True
    >>> elem = BooleanCodec.to_xml(False)
    >>> elem.tag
    'f'
    >>> elem.attrib['t']
    'B'
    >>> elem.attrib['v']
    'false'
    """
    __slots__ = ()
    typemarker = 'B'

    def decode(self, decode, stream, curelem):
        value = super(BooleanCodec, self).decode(decode, stream, curelem)
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            raise ValueError('Invalid boolean value')

    def encode(self,encode, name, value, **attrs):
        value = 'true' if value else 'false'
        return super(BooleanCodec, self).encode(encode, name, value, **attrs)


class IntegerCodec(FieldCodec):
    """Codec for :class:`int` type.

    >>> IntegerCodec.to_python('<f t="I" v="42" />')
    42
    >>> elem = IntegerCodec.to_xml(42)
    >>> elem.tag
    'f'
    >>> elem.attrib['t']
    'I'
    >>> elem.attrib['v']
    '42'
    """
    __slots__ = ()
    typemarker = 'I'

    def decode(self, decode, stream, curelem):
        value = super(IntegerCodec, self).decode(decode, stream, curelem)
        return int(value)


class LongIntegerCodec(FieldCodec):
    """Codec for :class:`long` type.

    >>> LongIntegerCodec.to_python('<f t="L" v="42" />')
    42L
    >>> elem = LongIntegerCodec.to_xml(42L)
    >>> elem.tag
    'f'
    >>> elem.attrib['t']
    'L'
    >>> elem.attrib['v']
    '42'
    """
    __slots__ = ()
    typemarker = 'L'

    def decode(self, decode, stream, curelem):
        value = super(LongIntegerCodec, self).decode(decode, stream, curelem)
        return long(value)


class FloatCodec(FieldCodec):
    """Codec for :class:`float` type.

    >>> str(round(FloatCodec.to_python('<f t="F" v="3.14" />'), 2))
    '3.14'
    >>> elem = FloatCodec.to_xml(3.14)
    >>> elem.tag
    'f'
    >>> elem.attrib['t']
    'F'
    >>> elem.attrib['v']
    '3.14'
    """
    __slots__ = ()
    typemarker = 'F'

    def decode(self, decode, stream, curelem):
        value = super(FloatCodec, self).decode(decode, stream, curelem)
        return float(value)

class StringCodec(FieldCodec):
    """Codec for :class:`str` and :class:`unicode` types.

    >>> StringCodec.to_python('<f t="S" v="foo" />')
    'foo'
    >>> elem = StringCodec.to_xml('foo')
    >>> elem.tag
    'f'
    >>> elem.attrib['t']
    'S'
    >>> elem.attrib['v']
    'foo'
    """
    __slots__ = ()
    typemarker = 'S'


class DateTimeCodec(FieldCodec):
    """Codec for :class:`datetime.datetime` type.

    >>> DateTimeCodec.to_python('<f t="D" v="14.02.2009 02:31:30" />')
    datetime.datetime(2009, 2, 14, 2, 31, 30)
    >>> elem = DateTimeCodec.to_xml(datetime.datetime(2009,2,14,2,31,30))
    >>> elem.tag
    'f'
    >>> elem.attrib['t']
    'D'
    >>> elem.attrib['v']
    '14.02.2009 02:31:30'
    """
    __slots__ = ()
    typemarker = 'D'

    def decode(self, decode, stream, curelem):
        value = super(DateTimeCodec, self).decode(decode, stream, curelem)
        return datetime.datetime.strptime(value, '%d.%m.%Y %H:%M:%S')

    def encode(self, encode, name, value, **attrs):
        value = value.strftime('%d.%m.%Y %H:%M:%S')
        return super(DateTimeCodec, self).encode(encode, name, value, **attrs)


class ReferenceCodec(BaseCodec):
    """Codec for :class:`~phoxpy.xmlcodec.Reference` type.

    >>> ReferenceCodec.to_python('<r i="42"/>')
    u'42'
    >>> elem = ReferenceCodec.to_xml(Reference('42'))
    >>> elem.tag
    'r'
    >>> elem.attrib['i']
    '42'
    """
    __slots__ = ()
    tagname = 'r'

    def decode(self, decode, stream, curelem):
        for event, elem in stream:
            assert elem is curelem and event == 'end', (event, elem)
            return Reference(elem.attrib['i'])

    def encode(self, encode, name=None, value=None, **attrs):
        attrs['i'] = unicode(value)
        return super(ReferenceCodec, self).encode(encode, name, **attrs)


class ListCodec(BaseCodec):
    """Codec for items sequence.

    >>> xmlsrc = '<s><f t="I" v="1"/><f t="I" v="2"/><f t="I" v="3"/></s>'
    >>> obj = ListCodec.to_python(xmlsrc)
    >>> obj     #doctest: +ELLIPSIS
    <generator object at 0x...>
    >>> list(obj)
    [1, 2, 3]
    >>> elem = ListCodec.to_xml([1, 2, 3])
    >>> elem.tag
    's'
    >>> len(elem)
    3
    """
    __slots__ = ()
    tagname = 's'

    def decode(self, decode, stream, curelem):
        for event, elem in stream:
            if event == 'start':
                yield decode(stream, elem)
            if event == 'end':
                assert elem is curelem
                break

    def encode(self, encode, name=None, value=None, **attrs):
        elem = super(ListCodec, self).encode(encode, name, **attrs)
        for item in value:
            elem.append(encode(None, item))
        return elem


class ObjectCodec(BaseCodec):
    """Codec for key-value mappings."""
    __slots__ = ()
    tagname = 'o'

    def decode(self, decode, stream, curelem):
        data = {}
        for event, elem in stream:
            if event == 'start':
                if not 'n' in elem.attrib:
                    raise ValueError('Unnamed element %s: attribute `n`'
                                     ' expected (%s)' % (elem, elem.attrib))
                key = elem.attrib['n']
                value = decode(stream, elem)
                if isinstance(value, GeneratorType):
                    value = list(value)
                data[key] = value
            if event == 'end':
                assert elem is curelem, (elem, curelem)
                for key, value in elem.attrib.items():
                    if key in ['n', 't', 'v']:
                        continue
                    assert key not in data, 'name collision with attibute %r' % key
                    data[key] = Attribute(value)
                break
        return data

    def encode(self, encode, name=None, value=None, **attrs):
        elem = super(ObjectCodec, self).encode(encode, name, **attrs)
        for key, value in value.items():
            if value is None:
                continue
            if isinstance(value, Attribute):
                elem.attrib[key] = value
            else:
                elem.append(encode(key, value))
        return elem


class ContentCodec(ObjectCodec):
    """Special codec for `content` tag."""
    __slots__ = ()
    tagname = 'content'

    def decode(self, decode, stream, curelem):
        if len(curelem) == 1:
            child = curelem[0]
            if child.tag == 'o':
                event, endelem = stream.next()
                result = super(ContentCodec, self).decode(decode, stream, endelem)
                stream.next() # fire `o` tag closing event
                return result
        return super(ContentCodec, self).decode(decode, stream, curelem)

    def encode(self, encode, name, value, **attrs):
        elem = xml.encode_elem(name, value.unwrap(), **attrs)
        container = xml.Element('content')
        if len(elem):
            container.append(elem)
        container.attrib.update(dict(elem.attrib.items()))
        elem.attrib.clear()
        return container


class PhoxMessageCodec(ObjectCodec):
    """Codec for Phox :class:`~phoxpy.messages.Message` instances."""
    __slots__ = ()
    wrapper = None

    def decode(self, decode, stream, curelem):
        header = dict(map(lambda i: (i[0], Attribute(i[1])),
                          curelem.attrib.items()))

        data = xml.decode(stream)
        instance = self.wrapper(**header)

        instance.content = data
        return instance

    def encode(self, encode, name=None, value=None, **attrs):
        root = super(PhoxMessageCodec, self).encode(encode, name, value, **attrs)
        if len(root):
            root[0].attrib.pop('n', None) # strip content name
        return root


class PhoxRequestCodec(PhoxMessageCodec):
    """Codec for :class:`~phoxpy.messages.PhoxRequest` messages."""
    __slots__ = ()
    tagname = 'phox-request'
    wrapper = PhoxRequest

    def encode(self, encode, name=None, value=None, **attrs):
        root = super(PhoxRequestCodec, self).encode(encode, name, value, **attrs)
        if len(root):
            content = root[0]
            if len(content):
                root.remove(content)
                obj = content[0]
                obj.tag = 'content'
                del content
                root.append(obj)
        return root


class PhoxResponseCodec(PhoxMessageCodec):
    """Codec for :class:`~phoxpy.messages.PhoxResponse` messages."""
    __slots__ = ()
    tagname = 'phox-response'
    wrapper = PhoxResponse


class PhoxEventCodec(PhoxMessageCodec):
    """Codec for :class:`~phoxpy.messages.PhoxEvent` messages."""
    __slots__ = ()
    tagname = 'phox-event'
    wrapper = PhoxEvent


class PhoxErrorCodec(ContentCodec):
    """Codec for LIS errors and :exc:`~phoxpy.exception.LisBaseException`."""
    __slots__ = ()
    tagname = 'error'

    def decode(self, decode, stream, curelem):
        event, elem = stream.next()
        assert event == 'end' and elem is curelem
        code = elem.attrib['code']
        descr = elem.attrib.get('description', '')
        raise exceptions.get_error_class(int(code))(descr.encode('utf-8'))

    def encode(self, encode, name, value, **attrs):
        elem = xml.Element('error')
        elem.attrib['code'] = value.code and str(value.code) or ''
        elem.attrib['description'] = value.description or ''
        return elem


class DirectoryResponseCodec(PhoxResponseCodec):
    """Optimized :class:`~phoxpy.xmlcodec.PhoxResponceCodec` for handling
    loaded directories. General fix is to prevent unfolding generator inside of
    root object.
    """

    def decode(self, decode, stream, prevelem):
        def next_tag_should_be(stream, expected_event, expected_tag):
            for event, elem in stream:
                assert event == expected_event, (event, expected_event)
                assert elem.tag == expected_tag, (elem.tag, expected_tag)
                return event, elem
        header = dict(map(lambda i: (i[0], Attribute(i[1])),
                          prevelem.attrib.items()))
        data = {}

        next_tag_should_be(stream, 'start', 'content')
        next_tag_should_be(stream, 'start', 'o')

        event, elem = next_tag_should_be(stream, 'start', 'f')
        attrs = dict(elem.attrib.items())
        data[attrs['n']] = decode(stream, elem)

        event, elem = next_tag_should_be(stream, 'start', 's')
        attrs = dict(elem.attrib.items())
        data[attrs['n']] = decode(stream, elem)

        instance = self.wrapper(**header)

        instance.content = data

        return instance

xml.register_fallback_codec(FallbackCodec)
xml.register_codec(FieldCodec, type(None))
xml.register_codec(BooleanCodec, bool)
xml.register_codec(IntegerCodec, int)
xml.register_codec(LongIntegerCodec, long)
xml.register_codec(FloatCodec, float)
xml.register_codec(StringCodec, str,  unicode)
xml.register_codec(ReferenceCodec, Reference)
xml.register_codec(DateTimeCodec, datetime.date, datetime.datetime)
xml.register_codec(ReferenceCodec, Reference)
xml.register_codec(ListCodec, tuple, list, set, frozenset)
xml.register_codec(ObjectCodec, dict, Mapping)
xml.register_codec(ContentCodec, Content)
xml.register_codec(PhoxRequestCodec, PhoxRequest)
xml.register_codec(PhoxResponseCodec, PhoxResponse)
xml.register_codec(PhoxEventCodec, PhoxEvent)
xml.register_codec(PhoxErrorCodec, exceptions.LisBaseException)
