# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
"""An abstraction layer over various ElementTree-based XML modules."""

import lxml.etree as xml
from StringIO import StringIO

__all__ = ['ENCODING', 'DEFAULT_DECODER', 'DEFAULT_ENCODER',
           'Element', 'ElementTree', 'ElementType', 'ElementTreeType',
           'use', 'dump', 'load', 'parse',
           'decode', 'encode']

_using = 'lxml'
_initialized = True
_Element = xml.Element
_ElementTree = xml.ElementTree
_load = xml.fromstring
_dump = xml.tostring
_parse = xml.iterparse
#: Type of :class:`~phoxpy.xml.Element` realization.
ElementType = type(xml.Element('x'))
#: Type of :class:`~phoxpy.xml.ElementTree` realization.
ElementTreeType = type(xml.ElementTree(xml.Element('x')))
#: Default XML encoding.
ENCODING = 'Windows-1251' # there is 2011 year, but we still have to use
                          # something not like utf-8

_TAGS = {}
_TAGS_BY_TYPE = {}
_TAGS_BY_PYTYPE = {}

def register_tag(tag, *pytypes):
    """Registers new XML element codec.

    :param tag: :class:`~phoxpy.xmlcodec.Tag` class or his subclass
    :param pytypes: Python types which will be associated with.
    """
    tag = tag()
    if tag.tagname not in _TAGS:
        _TAGS[tag.tagname] = tag
    if tag.typeattr is not None:
        _TAGS_BY_TYPE[tag.typeattr] = tag
    for pytype in pytypes:
        _TAGS_BY_PYTYPE[pytype] = tag

def make_stream(xmlsrc):
    """Wraps XML source to generator of events and XML element instances."""
    if isinstance(xmlsrc, basestring):
        stream = parse(StringIO(xmlsrc))
    elif hasattr(xmlsrc, 'read'):
        stream = parse(xmlsrc)
    elif isinstance(xmlsrc, ElementType):
        stream = parse(StringIO(_dump(xmlsrc)))
    else:
        stream = xmlsrc
    return stream

def decode(xmlsrc):
    """Decodes xml source to Python object.

    :param xmlsrc: XML data source.

    +-------------------------------------+----------------------------+-------+
    | XML Tag                             | Python type                | Notes |
    +=====================================+============================+=======+
    | tag: f; no attribs; no childs       | :class:`unicode`           |       |
    +-------------------------------------+----------------------------+-------+
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
    stream = make_stream(xmlsrc)
    for obj in decode_stream(stream):
        return obj

def decode_stream(stream):
    """Decodes elements of xml stream.

    :param stream: XML parser's stream which emits pair of
                   event and :class:`~phoxpy.xml.Element` instances.
    :type: generator

    :yields: Decoded value.
    """
    for event, elem in stream:
        yield decode_elem(stream, elem)

def decode_elem(stream, elem):
    """Decodes single XML element by calling his decoding handler.

    :param stream: XML parser's stream which emits pair of
                   event and :class:`~phoxpy.Element` instances.
    :type stream: generator

    :param elem: XML element instance to process.
    :type elem: :class:`~phoxpy.xml.Element

    :return: Decoded value

    :raises: :exc:`ValueError` if no decoders available for passed `elem`.
    """
    if 't' in elem.attrib and elem.attrib['t'] in _TAGS_BY_TYPE:
        value = _TAGS_BY_TYPE[elem.attrib['t']].decode(decode_elem, stream, elem)
    elif elem.tag in _TAGS:
        value = _TAGS[elem.tag].decode(decode_elem, stream, elem)
    else:
        raise ValueError('unknown elem %r' % elem)
    return value

def encode(obj, **attrs):
    """Encodes Python object to XML object.

    :param obj: Python object.
    :param attrs: Custom XML attributes.

    :return: :class:`~phoxpy.xml.Element` instance.

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
    return encode_elem(None, obj, **attrs)

def encode_elem(name, obj, **attrs):
    """Encodes Python object to XML element with `name` and custom `attrs` as
    attributes.

    :param name: XML element `name`. If element should be nonames
                 (e.g. items of lists) ``None`` value should be explicitly
                 passed.
    :type name: unicode

    :param obj: Python object of any type.

    :param attrs: Key-value mapping for custom XML element attributes.
    """
    def get_type_rating(tval, cls, score=10):
        if tval is cls:
            return score
        rates = []
        for base in cls.__bases__:
            rates.append(get_type_rating(tval, base, score-1))
        if rates:
            return sorted(rates)[-1]
    tobj = type(obj)
    if obj is None:
        func = _TAGS['f'].encode
    elif tobj in _TAGS_BY_TYPE:
        func = _TAGS_BY_TYPE[tobj].encode
    elif isinstance(obj, dict):
        func = _TAGS['o'].encode
    elif isinstance(obj, (tuple, list, set, frozenset)): # TODO: check for __iter__
        func = _TAGS['s'].encode
    else:
        maybe_right_handlers = []
        for pytype, handler in _TAGS_BY_PYTYPE.items():
            if isinstance(obj, pytype):
                rate = get_type_rating(pytype, tobj)
                if rate is not None:
                    maybe_right_handlers.append((rate, handler))
        if not maybe_right_handlers:
            raise TypeError('unknown handler for %r' % obj)
        maybe_right_handlers.sort()
        func =  maybe_right_handlers[-1][1].encode
    return func(encode_elem, name, obj, **attrs)

def Element(name, *args, **kwargs):
    """Proxy to ``Element`` factory of used etree module."""
    return _Element(name, *args, **kwargs)

def ElementTree(node):
    """Proxy to ``ElementTree`` factory of used etree module."""
    return _ElementTree(node)

def load(s):
    """Load xml source string to :class:`~phoxpy.xml.Element` instance."""
    return _load(s)

def parse(fileobj):
    """Parse file like object with xml data yielding events (`start` and `end`)
    and elements. When `end` event occurred, emitted element cleaned up with all
    attributes, inner nodes and siblings.

    :param fileobj: File-like object.

    :yields: 2-element tuple of event name and :class:`~phoxpy.xml.Element`
             instance.
    """
    for event, elem in _parse(fileobj, ('start', 'end')):
        yield event, elem
        if event == 'end':
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            del elem

def dump(xmlsrc, doctype=None, encoding=None):
    """Dump module with very limited support of doctype setting
    and force xml declaration definition.

    :param xmlsrc: XML object.
    :type xmlsrc: :class:`~phoxpy.xml.Element`
                  or :class:`~phoxpy.xml.ElementTree`

    :param doctype: 3-element ``tuple`` with name, identifier and dtd filename.
    :type doctype: tuple or list

    :param encoding: Custom document encoding.
    :type encoding: str

    :return: XML source string.
    :rtype: str
    """
    if encoding is None:
        encoding = ENCODING or 'utf-8'
    xml_declaration = \
    "<?xml version='1.0' encoding='%s'?>\n" % encoding
    if doctype:
        doctype = '<!DOCTYPE %s %s "%s">\n' % doctype
    else:
        doctype = ''
    if isinstance(xmlsrc, ElementTreeType):
        xmlsrc = xmlsrc.getroot()
    xmlstr = _dump(xmlsrc, encoding=encoding)
    if encoding.lower() not in ('us-ascii', 'utf-8'):
        xmlstr = ''.join(xmlstr.split('\n', 1)[1])
    return ''.join([xml_declaration, doctype, xmlstr])
