# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
"""An abstraction layer over various ElementTree-based XML modules."""

import sys

__all__ = ['ENCODING','ElementType', 'ElementTreeType',
           'Element', 'ElementTree', 'use', 'dump', 'load']

_using = None
_initialized = False
_Element = None
_ElementTree = None
_load = None
_dump = None
#: Type of :class:`~phoxpy.xml.Element` realization.
ElementType = None
#: Type of :class:`~phoxpy.xml.ElementTree` realization.
ElementTreeType = None
#: Default XML encoding.
ENCODING = 'Windows-1251' # there is 2011 year, but we still have to use
                          # something not like utf-8

def use(module):
    """Set the XML library that should be used by specifying a known module
    name.

    Currently supports next XML modules:

     - ``lxml.etree``: http://lxml.de
     - ``xml.etree.ElementTree``: This is the version of
       :mod:`~xml.etree.ElementTree` that is bundled with the Python standard
       library since version 2.5. `cElementTree` realization
       is prefered, but `ElementTree` could be used too.
     - ``cElementTree``: http://effbot.org/zone/celementtree.htm
     - ``elementtree.ElementTree``: http://effbot.org/zone/element-index.htm

    :param module: The name of the XML library module to use or the module
                   object itself.
    :type module: str or module

    :raises:
        :exc:`ValueError`: If specified module is unsupported.
    """
    global _using, _initialized
    if not isinstance(module, basestring):
        module = module.__name__
    if module not in ('lxml.etree', 'xml.etree.ElementTree', 'cElementTree',
                      'xml.etree.cElementTree', 'elementtree.ElementTree'):
        raise ValueError('Unsupported XML module %s' % module)
    _using = module
    _initialized = False

def should_initialize_first(func):
    def wrapper(*args, **kwargs):
        if not _initialized:
            _initialize()
        return func(*args, **kwargs)
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper

@should_initialize_first
def Element(name, *args, **kwargs):
    """Proxy to ``Element`` factory of used etree module."""
    return _Element(name, *args, **kwargs)

@should_initialize_first
def ElementTree(node):
    """Proxy to ``ElementTree`` factory of used etree module."""
    return _ElementTree(node)

@should_initialize_first
def load(s):
    """Load xml source string to :class:`~phoxpy.xml.Element` instance."""
    return _load(s)

@should_initialize_first
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

def _initialize():
    global _initialized, _using, _load, _dump, _Element, _ElementTree

    def use_lxml():
        global ElementType, ElementTreeType

        import lxml.etree as xml
        ElementType = type(xml.Element('x'))
        ElementTreeType = type(xml.ElementTree(xml.Element('x')))
        return xml

    def use_stdlib_cetree():
        global ElementType, ElementTreeType

        try:
            # TODO: invent better way to resolve xml module import problem
            sys.path.reverse()
            xml = __import__('xml.etree.cElementTree', fromlist=['xml.etree'])
        finally:
            sys.path.reverse()

        ElementType = type(xml.Element('x'))
        ElementTreeType = type(xml.ElementTree(xml.Element('x')))
        return xml

    def use_stdlib_etree():
        global ElementType, ElementTreeType

        try:
            sys.path.reverse()
            xml = __import__('xml.etree.ElementTree', fromlist=['xml.etree'])
        finally:
            sys.path.reverse()

        ElementType = type(xml.Element('x'))
        ElementTreeType = xml.ElementTree
        return xml

    def use_cetree():
        global ElementType, ElementTreeType

        import cElementTree as xml

        ElementType = type(xml.Element('x'))
        ElementTreeType = type(xml.ElementTree(xml.Element('x')))
        return xml

    def use_etree():
        global ElementType, ElementTreeType

        import elementtree.ElementTree as xml

        ElementType = type(xml.Element('x'))
        ElementTreeType = xml.ElementTree
        return xml

    modules = [
        ('lxml.etree', use_lxml),
        ('xml.etree.cElementTree', use_stdlib_cetree),
        ('xml.etree.ElementTree', use_stdlib_etree),
        ('cElementTree', use_cetree),
        ('elementtree.ElementTree', use_etree),
    ]
    if _using is None:
        for name, use in modules:
            try:
                module = use()
            except ImportError:
                continue
            else:
                _using = name
                break
        else:
            raise ImportError('No one of these modules could be used: "%s"'
                              '' % '", "'.join(dict(modules).keys()))
    else:
        module = dict(modules).get(_using)()
        if module is None:
            raise ValueError('Unsupported module %r' % _using)
    _load = module.fromstring
    _dump = module.tostring
    _Element = module.Element
    _ElementTree = module.ElementTree

    _initialized = True
