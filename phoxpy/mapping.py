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
"""Mapping to strict XML data scheme and help to decode it to Python objects
and encode vice versa."""

from itertools import islice
import copy
import datetime
from phoxpy import xml
from phoxpy.xmlcodec import Attribute, Reference, ObjectTag

__all__ = ['Field', 'BooleanField', 'IntegerField', 'LongField', 'FloatField',
           'TextField', 'DateTimeField', 'RefField', 'ListField', 'ObjectField',
           'Mapping', 'MappingTag']

class MetaField(type):

    def __init__(cls, *args, **kwargs):
        cls._pytypes = tuple()
        super(MetaField, cls).__init__(*args, **kwargs)

    def register(self, *pytypes):
        self._pytypes = pytypes


class Field(object):
    """Base field class.

    :param name: Field custom name.
    :type name: str

    :param default: Field default value if nothing was setted.
    :type default: unicode
    """
    __metaclass__ = MetaField

    def __init__(self, name=None, default=None):
        self.name = name
        self.default = default

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance._data.get(self.name)
        if value is not None:
            value = self._get_value(value)
        elif self.default is not None:
            default = self.default
            if hasattr(default, '__call__'):
                default = default()
            value = default
        return value

    def __set__(self, instance, value):
        if value is not None:
            value = self._set_value(value)
        instance._data[self.name] = value

    def _get_value(self, value):
        return unicode(value)

    def _set_value(self, value):
        return self._get_value(value)


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
    """Base class to construct complex data mappings.

    :param values: Keyword arguments mapped by fields.
    :type values: dict"""
    __metaclass__ = MetaMapping

    def __init__(self, **values):
        self._fields = self._fields.copy()
        self._data = {}
        for fieldname in self._fields:
            if fieldname in values:
                self[fieldname] = values.pop(fieldname)
            else:
                self[fieldname] = self[fieldname]
        self.update(values)

    def __getitem__(self, key):
        attrname, field = self._get_field(key)
        if field is None:
            raise KeyError(key)
        return field.__get__(self, None)

    def __setitem__(self, key, value):
        attrname, field = self._get_field(key)
        if field is None:
            field = self._set_field(key, value)
        field.__set__(self, value)

    def __delitem__(self, key):
        attrname, field = self._get_field(key)
        if field is None:
            raise KeyError(key)
        field.__set__(self, field.default)

    def __lt__(self, other):
        return self._asdict() < other

    def __le__(self, other):
        return self._asdict() <= other

    def __eq__(self, other):
        return self._asdict() == other

    def __ne__(self, other):
        return self._asdict() != other

    def __ge__(self, other):
        return self._asdict() >= other

    def __gt__(self, other):
        return self._asdict() > other

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        return self.keys()

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self._asdict())

    def _asdict(self):
        return dict(self.items())

    def _get_field(self, key):
        if key in self._fields:
            return key, self._fields[key]
        for name, field in self._fields.items():
            if field.name == key:
                return name, field
        return key, None

    def _set_field(self, name, value):
        field = gen_field_by_value(name, value)
        self._fields[name] = field
        self._data[name] = value
        return field

    def to_xml(self):
        return xml.encode(self)

    @classmethod
    def to_python(cls, xmlsrc):
        return cls.wrap(xml.decode(xmlsrc))

    @classmethod
    def build(cls, **d):
        """Creates AnonymousMapping type with specified fields."""
        fields = {}
        for attrname, attrval in d.items():
            if not attrval.name:
                attrval.name = attrname
            setattr(cls, attrname, attrval)
            fields[attrname] = attrval
        d['_fields'] = fields
        return type('AnonymousMapping', (cls,), d)

    @classmethod
    def wrap(cls, data):
        if isinstance(data, dict):
            return cls(**data)
        else:
            return cls.to_python(data)

    def unwrap(self):
        return self._data

    def copy(self):
        """Creates a new copy of mapping."""
        return type(self)(**copy.deepcopy(self._data))

    def get(self, key, default=None):
        """Returns data by `key` or `default` if missing."""
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        """Iterate over field names."""
        return self._data.iterkeys()

    def values(self):
        """Iterate over field values."""
        return self._data.itervalues()

    def items(self):
        """Iterate over field (name, value) pairs."""
        return self._data.iteritems()

    def setdefault(self, key, value):
        """Sets default value to specified field by name.

        :param key: Field name
        :type key: str

        :param value: Field valid value.

        :raises:
            :exc:`KeyError`: If field not found by `key` argument.
        """
        attrname, field = self._get_field(key)
        if field is None:
            raise KeyError(key)
        field.default = value
        self[key] = value

    def update(self, data):
        """Batch update fields data."""
        for key, value in data.items():
            self[key] = value


class MappingTag(ObjectTag):

    def encode(self, encode, name, value, **attrs):
        return super(MappingTag, self).encode(encode, name, value.unwrap())

xml.register_tag(MappingTag, Mapping)


class AttributeField(Field):
    """Field for Mapping attributes."""

    def _set_value(self, value):
        return Attribute(value)


class BooleanField(Field):
    """Mapping field for boolean values."""

    def _get_value(self, value):
        return bool(value)

    def _set_value(self, value):
        if not isinstance(value, bool):
            raise TypeError('Boolean value expected, got %r' % value)
        return super(BooleanField, self)._set_value(value)


class IntegerField(Field):
    """Mapping field for integer values."""

    def _get_value(self, value):
        return int(value)


class LongField(Field):
    """Mapping field for long integer values."""

    def _get_value(self, value):
        return long(value)


class FloatField(Field):
    """Mapping field for float values."""

    def _get_value(self, value):
        return float(value)


class TextField(Field):
    """Mapping field for string values."""

    def _set_value(self, value):
        if not isinstance(value, basestring):
            raise TypeError('String value expected, got %r' % value)
        if isinstance(value, str):
            value = unicode(value, 'utf-8')
        return super(TextField, self)._set_value(value)


class DateTimeField(Field):
    """Mapping field for storing date/time values."""

    def _get_value(self, value):
        return value

    def _set_value(self, value):
        if not isinstance(value, (datetime.datetime, datetime.date)):
            raise TypeError('Datetime value expected, got %r' % value)
        return super(DateTimeField, self)._set_value(value)


class RefField(Field):
    """Mapping field for storing object reference ids."""

    def _set_value(self, value):
        return Reference(value)


class ListField(Field):
    """Field type for sequences of other fields.

    :param field: Sequence item field instance.
    :type field: :class:`~phoxpy.mapping.Field`
    """

    def __init__(self, field, name=None, default=None):
        default = default or []
        if isinstance(field, Mapping):
            field = ObjectField(field)
        self.field = field
        super(ListField, self).__init__(name, default)

    class Proxy(list):
        def __init__(self, seq, field):
            list.__init__(self, seq)
            self.list = seq
            self.field = field

        def _to_python(self):
            return [self.field._get_value(item) for item in self.list]

        def __add__(self, other):
            obj = type(self)(self.list, self.field)
            obj.extend(other)
            return obj

        def __iadd__(self, other):
            self.extend(other)
            return self

        def __mul__(self, other):
            return type(self)(self.list * other, self.field)

        def __imul__(self, other):
            self.list *= other
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
            return self.field._get_value(self.list[index])

        def __setitem__(self, index, value):
            self.list[index] = self.field._set_value(value)

        def __delslice__(self, i, j):
            del self.list[i:j]

        def __getslice__(self, i, j):
            return ListField.Proxy(self.list[i:j], self.field)

        def __setslice__(self, i, j, seq):
            self.list[i:j] = [self.field._set_value(v) for v in seq]

        def __contains__(self, value):
            for item in self:
                if item == value:
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
            self.list.append(self.field._set_value(item))

        def count(self, value):
            return [i for i in self].count(value)

        def extend(self, other):
            self.list.extend([self.field._set_value(i) for i in other])

        def index(self, value, start=None, stop=None):
            start = start or 0
            for idx, item in enumerate(islice(self, start, stop)):
                if item == value:
                    return idx + start
            else:
                raise ValueError('%r not in list' % value)

        def insert(self, index, object):
            self.list.insert(index, self.field._set_value(object))

        def remove(self, value):
            for item in self:
                if item == value:
                    return self.list.remove(self.field._set_value(value))
            raise ValueError('Value %r not in list' % value)

        def pop(self, index=-1):
            return self.field._get_value(self.list.pop(index))

        def sort(self, cmp=None, key=None, reverse=False):
            vals = list(sorted(self, cmp, key, reverse))
            del self.list[:]
            for i in vals:
                self.append(i)

        # update docstrings from list
        for item in dir():
            if getattr(list, item, None) is None \
                or item in ['__module__', '__doc__']:
                continue
            func = eval(item)
            func.__doc__ = getattr(list, item).__doc__
        del func, item

    def _get_value(self, value):
        return self.Proxy(value, self.field)

    def _set_value(self, value):
        return [self.field._set_value(item) for item in value]


class ObjectField(Field):
    """Field type for nested objects in Mapping form."""
    def __init__(self, mapping, name=None, default=None):
        if isinstance(mapping, dict):
            mapping = Mapping.build(**mapping)
        self.mapping = mapping
        default = default or self.mapping
        super(ObjectField, self).__init__(name, default=default)

    def _get_value(self, value):
        if isinstance(value, dict):
            return self.mapping(**value)
        elif isinstance(value, self.mapping):
            return value
        else:
            return self.mapping(**dict(value.items()))

    def _set_value(self, value):
        if isinstance(value, dict):
            return self.mapping(**value)
        elif isinstance(value, self.mapping):
            return value
        else:
            raise TypeError('%s' % value)


AttributeField.register(Attribute)
BooleanField.register(bool)
IntegerField.register(int)
LongField.register(long)
FloatField.register(float)
TextField.register(str, unicode)
RefField.register(Reference)
DateTimeField.register(datetime.datetime, datetime.date)
ListField.register(tuple, list, set, frozenset)
ObjectField.register(dict, Mapping)

fields_by_pytype = dict([
    (pytype, fieldcls)
    for fieldcls in Field.__subclasses__()
    for pytype in fieldcls._pytypes
])

def guess_fieldcls_by_value(value):
    tval = type(value)
    maybe_right_field = None
    if tval in fields_by_pytype:
        return fields_by_pytype[tval]
    for fieldcls in Field.__subclasses__():
        for pytype in fieldcls._pytypes:
            if isinstance(value, pytype):
                maybe_right_field = fieldcls
    if maybe_right_field is not None:
        return maybe_right_field
    raise ValueError('Could not guess field for value %r' % value)

def gen_field_by_value(name, value):
    fieldcls = guess_fieldcls_by_value(value)
    if fieldcls is ListField:
        if value:
            itemfield = gen_field_by_value(None, value[0])
        else:
            itemfield = TextField()
        field = fieldcls(itemfield, name=name)
    elif fieldcls is ObjectField:
        field = fieldcls(Mapping.build(), name=name)
    else:
        field = fieldcls(name=name)
    return field
