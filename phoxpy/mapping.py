# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Based on ideas of couchdb-python mapping module.
# <https://couchdb-python.googlecode.com/hg/couchdb/mapping.py>
#
"""Mapping from raw XML data structures to Python objects and vice versa."""
import copy
import datetime
from itertools import repeat, izip
from phoxpy import xml

__all__ = ['Field', 'BooleanField', 'IntegerField', 'LongField', 'FloatField',
           'TextField', 'DateTimeField', 'RefField', 'ListField', 'ObjectField',
           'Mapping', 'Message']

class Field(object):

    def __init__(self, name=None, default=None):
        self.name = name
        self.default = default

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance._data.get(self.name)
        if value is not None:
            value = self.to_python(value)
        elif self.default is not None:
            default = self.default
            if hasattr(default, '__call__'):
                default = default()
            value = default
        return value

    def __set__(self, instance, value):
        if value is not None:
            value = self.to_xml(value)
        instance._data[self.name] = value

    def to_python(self, node):
        return node.attrib['v']

    def to_xml(self, value):
        if not isinstance(value, basestring):
            raise TypeError('Unicode value excepted, got %r' % value)
        if not isinstance(value, unicode):
            value = unicode(value)
        elem = xml.Element('f')
        if self.name:
            elem.attrib['n'] = self.name
        elem.attrib['v'] = value
        return elem


class MetaMapping(type):

    def __new__(mcs, name, bases, data):
        fields = {}
        for base in bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)
        for attrname, attrval in data.items():
            if isinstance(attrval, Field):
                if not attrval.name:
                    attrval.name = attrname
                fields[attrname] = attrval
        if '_fields' not in data:
            data['_fields'] = fields
        else:
            data['_fields'].update(fields)
        return type.__new__(mcs, name, bases, data)


class Mapping(object):
    __metaclass__ = MetaMapping

    def __init__(self, **values):
        self._data = {}
        for fieldname in self._fields:
            if fieldname in values:
                setattr(self, fieldname, values.pop(fieldname))
            else:
                setattr(self, fieldname, getattr(self, fieldname))
        if values:
            raise ValueError('Unexpected kwargs found: %r' % values)

    def __getitem__(self, item):
        if item in self._fields:
            field = self._fields[item]
            return field.to_python(self._data[field.name])
        elif item in self._data:
            for field in self._fields.values():
                if field.name == item:
                    return field.to_python(self._data[item])
        else:
            raise KeyError('Unknown field %r' % item)

    def __setitem__(self, key, value):
        if key in self._fields:
            field = self._fields[key]
            self._data[field.name] = field.to_xml(value)
        elif key in self._data:
            for field in self._fields.values():
                if field.name == key:
                    self._data[field.name] = field.to_xml(value)
                    break
        else:
            raise KeyError('Unknown field %r' % key)

    def __delitem__(self, key):
        self._data[key] = None

    def __lt__(self, other):
        return self._to_python() < other

    def __le__(self, other):
        return self._to_python() <= other

    def __eq__(self, other):
        return self._to_python() == other

    def __ne__(self, other):
        return self._to_python() != other

    def __ge__(self, other):
        return self._to_python() >= other

    def __gt__(self, other):
        return self._to_python() > other

    def _to_python(self):
        return dict(self.items())

    @classmethod
    def build(cls, **d):
        fields = {}
        for attrname, attrval in d.items():
            if not attrval.name:
                attrval.name = attrname
            setattr(cls, attrname, attrval)
            fields[attrname] = attrval
        d['_fields'] = fields
        return type('AnonymousMapping', (cls,), d)

    @classmethod
    def wrap(cls, xmlsrc, **defaults):
        if not isinstance(xmlsrc, (xml.ElementType, xml.ElementTreeType)):
            raise TypeError('Invalid xml data %r' % xmlsrc)
        instance = cls(**defaults)
        if isinstance(xmlsrc, xml.ElementType):
            xmlsrc = xml.ElementTree(xmlsrc)
        for node in xmlsrc.getroot():
            if not 'n' in node.attrib:
                xmlstr = xml.dump(xmlsrc)
                raise ValueError('Unnamed field %r\n%s' % (xmlsrc, xmlstr))
            instance._data[node.attrib['n']] = node
        return instance

    def unwrap(self, root):
        for node in self._data.values():
            if isinstance(node, Mapping):
                root.append(node.unwrap())
            elif node is not None:
                root.append(node)
        return root

    def copy(self):
        instance = type(self)()
        for name, node in self._data.items():
            instance._data[name] = copy.deepcopy(node)
        return instance

    def keys(self):
        for key in self._data:
            yield key

    def values(self):
        for key in self._data:
            yield self[key]

    def items(self):
        return izip(self.keys(), self.values())

    def setdefault(self, key, value):
        if key in self._fields:
            field = self._fields[key]
            field.default = value
            if self._data[key] is None:
                self[key] = value
        elif key in self._data:
            for field in self._fields.values():
                if field.name == key:
                    field.default = value
                    if self._data[key] is None:
                        self[key] = value
        else:
            raise KeyError('Unknown field %r' % key)

    def update(self, data):
        for key, value in data.items():
            self[key] = value



class BooleanField(Field):

    def to_python(self, node):
        value = node.attrib['v']
        if value == 'true':
            return True
        elif value == 'false':
            return False
        raise ValueError(value)

    def to_xml(self, value):
        if not isinstance(value, bool):
            raise TypeError('Boolean value expected, got %r' % value)
        elem = super(BooleanField, self).to_xml('true' if value else 'false')
        elem.attrib['t'] = 'B'
        return elem


class IntegerField(Field):

    def to_python(self, node):
        return int(node.attrib['v'])

    def to_xml(self, value):
        if not isinstance(value, int):
            raise TypeError('Integer value expected, got %r' % value)
        elem = super(IntegerField, self).to_xml(str(value))
        elem.attrib['t'] = 'I'
        return elem


class LongField(Field):

    def to_python(self, node):
        return long(node.attrib['v'])

    def to_xml(self, value):
        if not isinstance(value, (int, long)):
            raise TypeError('Integer or long value expected, got %r' % value)
        elem = super(LongField, self).to_xml(str(value).rstrip('L'))
        elem.attrib['t'] = 'L'
        return elem


class FloatField(Field):

    def to_python(self, node):
        """Returns """
        return float(node.attrib['v'])

    def to_xml(self, value):
        if not isinstance(value, float):
            raise TypeError('Float value expected, got %r' % value)
        elem = super(FloatField, self).to_xml(str(value))
        elem.attrib['t'] = 'F'
        return elem


class TextField(Field):

    def __init__(self, encoding=None, name=None, default=None):
        self.encoding = encoding
        super(TextField, self).__init__(name, default)

    def to_python(self, node):
        return node.attrib['v']

    def to_xml(self, value):
        if not isinstance(value, basestring):
            raise TypeError('String value expected, got %r' % value)
        elem = super(TextField, self).to_xml(value)
        elem.attrib['t'] = 'S'
        return elem


class DateTimeField(Field):

    def __init__(self, fmt=None, name=None, default=None):
        self.format = fmt or '%d.%m.%Y %H:%M:%S'
        super(DateTimeField, self).__init__(name, default)

    def to_python(self, node):
        return datetime.datetime.strptime(node.attrib['v'], self.format)

    def to_xml(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError('Datetime value expected, got %r' % value)
        elem = super(DateTimeField, self).to_xml(value.strftime(self.format))
        elem.attrib['t'] = 'D'
        return elem


class RefField(Field):

    def to_python(self, node):
        return int(node.attrib['i'])

    def to_xml(self, value):
        if not isinstance(value, int):
            raise TypeError('Integer value expected, got %r' % value)
        elem = xml.Element('r')
        if self.name:
            elem.attrib['n'] = self.name
        elem.attrib['i'] = str(value)
        return elem


class ListField(Field):

    class Proxy(list):
        def __init__(self, seq, field):
            list.__init__(self, seq)
            self.list = seq
            self.field = field

        def _to_python(self):
            return [self.field.to_python(i) for i in self.list]

        def __add__(self, other):
            elem = copy.deepcopy(self.list)
            proxy = ListField(self.field).to_python(elem)
            proxy.extend(other)
            return proxy

        def __iadd__(self, other):
            self.extend(other)
            return self

        def __mul__(self, other):
            elem = copy.deepcopy(self.list)
            val = ListField(self.field).to_python(elem)
            if other < 1:
                elem.clear()
            elif other > 1:
                for seq in repeat(self, other - 1):
                    val.extend(seq)
            return val

        def __imul__(self, other):
            if other < 1:
                self.list.clear()
            elif other > 1:
                for seq in repeat(list(self), other - 1):
                    self.extend(seq)
            return self

        def __lt__(self, other):
            return self._to_python() < other

        def __le__(self, other):
            return self._to_python() <= other

        def __eq__(self, other):
            return self._to_python() == other

        def __ne__(self, other):
            return self._to_python() != other

        def __ge__(self, other):
            return self._to_python() >= other
    
        def __gt__(self, other):
            return self._to_python() > other

        def __repr__(self):
            return '<ListProxy %s %r>' % (self.list, list(self))

        def __str__(self):
            return str(self.list)

        def __unicode__(self):
            return unicode(self.list)

        def __delitem__(self, index):
            del self.list[index]

        def __getitem__(self, index):
            return self.field.to_python(self.list[index])

        def __setitem__(self, index, value):
            self.list[index] = self.field.to_xml(value)

        def __delslice__(self, i, j):
            del self.list[i:j]

        def __getslice__(self, i, j):
            return ListField.Proxy(self.list[i:j], self.field)

        def __setslice__(self, i, j, seq):
            self.list[i:j] = [self.field.to_xml(v) for v in seq]

        def __contains__(self, value):
            for item in self.list:
                if self.field.to_python(item) == value:
                    return True
            return False

        def __iter__(self):
            for index in range(len(self)):
                yield self[index]

        def __len__(self):
            return len(self.list)

        def __nonzero__(self):
            return bool(self.list)

        def __reduce__(self):
            return self.list.__reduce__()

        def __reduce_ex__(self, *args, **kwargs):
            return self.list.__reduce_ex__(*args, **kwargs)

        def append(self, item):
            self.list.append(self.field.to_xml(item))

        def count(self, value):
            return [i for i in self].count(value)

        def extend(self, other):
            if hasattr(self.list, 'extend'):
                self.list.extend([self.field.to_xml(i) for i in other])
            else:
                for item in other:
                    self.append(item)

        def index(self, item):
            for idx, node in enumerate(self.list):
                if self.field.to_python(node) == item:
                    return idx
            else:
                raise ValueError('%r not in list' % item)

        def insert(self, idx, item):
            self.list.insert(idx, self.field.to_xml(item))

        def remove(self, value):
            for node in self.list:
                if self.field.to_python(node) == value:
                    return self.list.remove(node)
            raise ValueError('Value %r not in list' % value)

        def pop(self, index=-1):
            elem = self.list[index]
            value = self.field.to_python(elem)
            self.list.remove(elem)
            return value

        def sort(self, cmp=None, key=None, reverse=False):
            vals = list(sorted(self, cmp, key, reverse))
            self.list.clear()
            for i in vals:
                self.append(i)

    def __init__(self, field, name=None, default=None):
        default = default or []
        self.field = field
        super(ListField, self).__init__(name, default)

    def to_python(self, node):
        return self.Proxy(node, self.field)

    def to_xml(self, value):
        try:
            iter(value)
        except TypeError:
            raise TypeError('Iterable value expected, got %r' % value)
        elem = xml.Element('s')
        if self.name:
            elem.attrib['n'] = self.name
        for item in value:
            elem.append(self.field.to_xml(item))
        return elem


class ObjectField(Field):

    def __init__(self, mapping, name=None, default=None):
        default = default or {}
        if isinstance(mapping, dict):
            mapping = Mapping.build(**mapping)
        self.mapping = mapping
        super(ObjectField, self).__init__(name, default=default.copy)

    def to_python(self, node):
        return self.mapping.wrap(xml.ElementTree(node))

    def to_xml(self, value):
        if isinstance(value, Mapping):
            value = value._data
        if not isinstance(value, dict):
            raise TypeError('Mapping or dict value expected, got %r' % value)
        root = xml.Element('o')
        if self.name:
            root.attrib['n'] = self.name
        self.mapping(**value).unwrap(root)
        return root
