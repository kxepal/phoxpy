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
from phoxpy import xmlcodec

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
#: Default XML decoder :class:`~phoxpy.xmlcodec.PhoxDecoder`.
DEFAULT_DECODER = xmlcodec.PhoxDecoder()
#: Default XML encoder :class:`~phoxpy.xmlcodec.PhoxEncoder`.
DEFAULT_ENCODER = xmlcodec.PhoxEncoder(lambda *a, **k: Element(*a, **k))
#: Type of :class:`~phoxpy.xml.Element` realization.
ElementType = type(xml.Element('x'))
#: Type of :class:`~phoxpy.xml.ElementTree` realization.
ElementTreeType = type(xml.ElementTree(xml.Element('x')))
#: Default XML encoding.
ENCODING = 'Windows-1251' # there is 2011 year, but we still have to use
                          # something not like utf-8

def decode(xmlsrc, cls=None, handlers=None):
    """Decodes xml source to Python object.

    :param xmlsrc: XML data source.

    :param cls: Custom decoder class. Uses :class:`~phoxpy.xmlcodec.PhoxDecoder`
                by default.
    :type cls: :class:`~phoxpy.xmlcodec.Decoder`

    :param handlers: Custom handlers for xml element.
    :type handlers: dict
    """
    if isinstance(xmlsrc, basestring):
        stream = parse(StringIO(xmlsrc))
    elif isinstance(xmlsrc, ElementType):
        stream = parse(StringIO(dump(xmlsrc)))
    elif isinstance(xmlsrc, ElementTreeType):
        stream = parse(StringIO(dump(xmlsrc.getroot())))
    elif hasattr(xmlsrc, 'read'):
        stream = parse(xmlsrc)
    else:
        stream = xmlsrc
    decoder = DEFAULT_DECODER
    if cls is not None or handlers is not None:
        kwargs = {}
        if handlers is not None:
            kwargs['handlers'] = handlers
        if cls is None:
            cls = xmlcodec.PhoxDecoder
        decoder = cls(**kwargs)
    return decoder.decode(stream)

def encode(data, cls=None, handlers=None):
    """Encodes Python object to XML object.

    :param data: Python object.

    :param cls: Custom encoder class. Uses :class:`~phoxpy.xmlcodec.PhoxEncoder`
                by default.
    :type cls: :class:`~phoxpy.xmlcodec.Encoder`

    :param handlers: Custom handlers for xml element.
    :type handlers: dict

    :return: :class:`~phoxpy.xml.Element` instance.
    """
    encoder = DEFAULT_ENCODER
    if cls is not None or handlers is not None:
        kwargs = {}
        if handlers is not None:
            kwargs['handlers'] = handlers
        if cls is None:
            cls = xmlcodec.PhoxEncoder
        encoder = cls(Element, **kwargs)
    return encoder.encode(data)

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
            # clean up to reduce memory footprint
            # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/#listing4
            elem.clear()
            if not hasattr(elem, 'getprevious'):
                continue
            while elem.getprevious() is not None:
                del elem.getparent()[0]

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
