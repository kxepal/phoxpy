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
from itertools import repeat, islice, izip
from phoxpy import xml

__all__ = ['Field', 'BooleanField', 'IntegerField', 'LongField', 'FloatField',
           'TextField', 'DateTimeField', 'RefField', 'ListField', 'ObjectField',
           'Mapping']

class Field(object):
    """Base field class.

    :param name: Field custom name.
    :type name: str

    :param default: Field default value if nothing was setted.
    :type default: unicode
    """
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
        if instance._data.get(self.name) is not None:
            instance._root.remove(instance._data[self.name])
        if value is not None:
            value = self.to_xml(value)
            instance._root.append(value)
        instance._data[self.name] = value

    def to_python(self, node):
        """xml element => unicode

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: Node attribute ``v`` value as is.
        :rtype: unicode

        >>> field = Field(name='foo')
        >>> elem = xml.Element('foo', v='bar')
        >>> field.to_python(elem)
        'bar'
        """
        return node.attrib['v']

    def to_xml(self, value):
        """unicode => xml element

        :param value: Unicode or utf-8 encoded string.
        :type value: basestring

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = Field(name='foo')
        >>> elem = field.to_xml('bar')
        >>> elem.tag
        'f'
        >>> elem.attrib['n']
        'foo'
        >>> elem.attrib['v']
        'bar'
        """
        if not isinstance(value, basestring):
            raise TypeError('Unicode value excepted, got %r' % value)
        if not isinstance(value, unicode):
            value = unicode(value)
        elem = xml.Element('f')
        if self.name:
            elem.attrib['n'] = self.name
        elem.attrib['v'] = value
        return elem


class AttributeField(Field):
    """Field for Mapping attributes.

    >>> class Post(Mapping):
    ...   foo = AttributeField()
    ...   bar = AttributeField(default='baz')
    >>> post = Post(foo='zoo')
    >>> post.foo
    u'zoo'
    >>> post['bar'] == post.bar == 'baz'
    True
    >>> elem = post.unwrap(xml.Element('root'))
    >>> elem.attrib.get('foo')
    'zoo'
    >>> elem.attrib.get('bar')
    'baz'
    """
    def __set__(self, instance, value):
        if instance._data.get(self.name) is not None:
            del instance._root.attrib[self.name]
        if value is not None:
            value = self.to_xml(value)
            instance._root.attrib[self.name] = value
        instance._data[self.name] = value

    def to_python(self, value):
        return value

    def to_xml(self, value):
        return unicode(value)


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
    :type values: dict

    :raises: :exc:`ValueError`: If no fields available to assign passed value.

    >>> class Post(Mapping):
    ...   foo = TextField()
    ...   bar = IntegerField()
    ...   baz = BooleanField(default=False)
    >>> post = Post(foo='zoo', bar=42)
    >>> post.foo
    'zoo'
    >>> post['bar'] == post.bar == 42
    True
    >>> post.baz
    False
    >>> post['baz'] = True
    >>> post.baz
    True
    """
    __metaclass__ = MetaMapping

    def __init__(self, **values):
        self._fields = self._fields.copy()
        self._root = xml.Element('root')
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

    def __contains__(self, item):
        if isinstance(item, basestring):
            return item in self._fields or item in self._data
        else:
            return item in list(self._root)

    def __iter__(self):
        return self.keys()

    def _to_python(self):
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
        if self._data.get(name) is not None:
            self._root.remove(self._data[name])
        elem = field.to_xml(value)
        self._data[name] = elem
        self._root.append(elem)
        return field

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
    def wrap(cls, xmlelem, **defaults):
        """Wrap :class:`~phoxpy.xml.Element` or :class:`~phoxpy.xml.ElementTree`
        instance and map elements to related fields by name.
        """
        if not isinstance(xmlelem, (xml.ElementType, xml.ElementTreeType)):
            raise TypeError('Invalid xml data %r' % xmlelem)
        if isinstance(xmlelem, xml.ElementTreeType):
            root = xmlelem.getroot()
        else:
            root = xmlelem
        instance = cls(**defaults)
        for idx in range(len(root)):
            elem = root[idx]
            fname = elem.attrib.get('n')
            if fname is None:
                raise ValueError('Unnamed node %s' % elem)
            elif fname in instance._fields:
                instance[fname] = instance._fields[fname].to_python(elem)
            else:
                for field in instance._fields.values():
                    if field.name == fname:
                        instance[fname] = field.to_python(elem)
                        break
                else:
                    field = gen_field_by_xmlelem(elem)
                    value = field.to_python(elem)
                    instance[field.name] = value
        for key, value in root.attrib.items():
            if key in instance._fields:
                instance[key] = instance._fields[key].to_python(value)
            elif key not in ['n', 't', 'i']:
                field = AttributeField(name=key)
                value = field.to_python(value)
                instance[field.name] = value
        return instance

    def unwrap(self, xmlelem):
        """Unwraps mapping instance to XML object."""
        for idx in range(len(self._root)):
            xmlelem.append(copy.deepcopy(self._root[idx]))
        xmlelem.attrib.update(self._root.attrib.items())
        return xmlelem

    def copy(self):
        """Creates a shallow copy of mapping."""
        return type(self).wrap(copy.deepcopy(self._root))

    def get(self, key, default=None):
        """Returns data by `key` or `default` if missing."""
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        """Iterate over field names."""
        for key in self._fields:
            yield key

    def values(self):
        """Iterate over field values."""
        for node in self._root:
            yield self._fields[node.attrib['n']].to_python(node)

    def items(self):
        """Iterate over field (name, value) pairs."""
        return izip(self.keys(), self.values())

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


class BooleanField(Field):
    """Mapping field for boolean values."""
    def to_python(self, node):
        """xml element => bool

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: ``True`` for `true` attribute value or ``False`` for `false`.
        :rtype: bool

        :raises:
            :exc:`ValueError`: If ``v`` attribute value couldn't be decoded
            to ``bool``.

        >>> field = BooleanField()
        >>> elem = xml.Element('foo', v='false')
        >>> field.to_python(elem)
        False
        >>> elem = xml.Element('foo', v='true')
        >>> field.to_python(elem)
        True
        """
        value = node.attrib['v']
        if value == 'true':
            return True
        elif value == 'false':
            return False
        raise ValueError(value)

    def to_xml(self, value):
        """bool => xml element

        :param value: Boolean value.
        :type value: bool

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = BooleanField()
        >>> elem = field.to_xml(False)
        >>> elem.attrib['t']
        'B'
        >>> elem.attrib['v']
        'false'
        >>> elem = field.to_xml(True)
        >>> elem.attrib['v']
        'true'
        """
        if not isinstance(value, bool):
            raise TypeError('Boolean value expected, got %r' % value)
        elem = super(BooleanField, self).to_xml('true' if value else 'false')
        elem.attrib['t'] = 'B'
        return elem


class IntegerField(Field):
    """Mapping field for integer values."""
    def to_python(self, node):
        """xml element => int

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: Integer value.
        :rtype: int

        >>> field = IntegerField()
        >>> elem = xml.Element('foo', v='42')
        >>> field.to_python(elem)
        42
        """
        return int(node.attrib['v'])

    def to_xml(self, value):
        """int => xml element

        :param value: Integer value.
        :type value: int

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = IntegerField()
        >>> elem = field.to_xml(42)
        >>> elem.attrib['t']
        'I'
        >>> elem.attrib['v']
        '42'
        """
        if not isinstance(value, int):
            raise TypeError('Integer value expected, got %r' % value)
        elem = super(IntegerField, self).to_xml(str(value))
        elem.attrib['t'] = 'I'
        return elem


class LongField(Field):
    """Mapping field for long integer values."""
    def to_python(self, node):
        """xml element => long

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: Long integer value.
        :rtype: long

        >>> field = LongField()
        >>> elem = xml.Element('foo', v='100500')
        >>> field.to_python(elem)
        100500L
        """
        return long(node.attrib['v'])

    def to_xml(self, value):
        """int or long => xml element

        :param value: Integer or long integer value.
        :type value: int or long

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = LongField()
        >>> elem = field.to_xml(100500L)
        >>> elem.attrib['t']
        'L'
        >>> elem.attrib['v']
        '100500'
        """
        if not isinstance(value, (int, long)):
            raise TypeError('Integer or long value expected, got %r' % value)
        elem = super(LongField, self).to_xml(str(value).rstrip('L'))
        elem.attrib['t'] = 'L'
        return elem


class FloatField(Field):
    """Mapping field for float values."""
    def to_python(self, node):
        """xml element => float

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: Float value.
        :rtype: float

        >>> field = FloatField()
        >>> elem = xml.Element('foo', v='3.14')
        >>> print round(field.to_python(elem), 2)
        3.14
        """
        return float(node.attrib['v'])

    def to_xml(self, value):
        """float => xml element

        :param value: Float value.
        :type value: float

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = FloatField()
        >>> elem = field.to_xml(3.14)
        >>> elem.attrib['t']
        'F'
        >>> elem.attrib['v']
        '3.14'
        """
        if not isinstance(value, float):
            raise TypeError('Float value expected, got %r' % value)
        elem = super(FloatField, self).to_xml(str(value))
        elem.attrib['t'] = 'F'
        return elem


class TextField(Field):
    """Mapping field for string values."""
    def __init__(self, encoding=None, name=None, default=None):
        self.encoding = encoding
        super(TextField, self).__init__(name, default)

    def to_python(self, node):
        """xml element => unicode

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: Node attribute ``v`` value as is.
        :rtype: unicode

        >>> field = TextField()
        >>> elem = xml.Element('foo', v='bar')
        >>> field.to_python(elem)
        'bar'
        """
        return node.attrib['v']

    def to_xml(self, value):
        """unicode => xml element

        :param value: Unicode or utf-8 encoded string.
        :type value: basestring

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = TextField()
        >>> elem = field.to_xml('bar')
        >>> elem.attrib['t']
        'S'
        >>> elem.attrib['v']
        'bar'
        """
        if not isinstance(value, basestring):
            raise TypeError('String value expected, got %r' % value)
        elem = super(TextField, self).to_xml(value)
        elem.attrib['t'] = 'S'
        return elem


class DateTimeField(Field):
    """Mapping field for storing date/time values."""
    def __init__(self, fmt=None, name=None, default=None):
        self.format = fmt or '%d.%m.%Y %H:%M:%S'
        super(DateTimeField, self).__init__(name, default)

    def to_python(self, node):
        """xml element => datetime

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: Python datetime object.
        :rtype: :class:`datetime.datetime`

        >>> field = DateTimeField()
        >>> elem = xml.Element('foo', v='14.02.2010 02:31:30')
        >>> field.to_python(elem)
        datetime.datetime(2010, 2, 14, 2, 31, 30)
        """
        return datetime.datetime.strptime(node.attrib['v'], self.format)

    def to_xml(self, value):
        """datetime => xml element

        :param value: Python datetime object.
        :type value: :class:`datetime.datetime`

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = DateTimeField()
        >>> elem = field.to_xml(datetime.datetime(2010, 2, 14, 2, 31, 30))
        >>> elem.attrib['t']
        'D'
        >>> elem.attrib['v']
        '14.02.2010 02:31:30'
        """
        if not isinstance(value, (datetime.datetime, datetime.date)):
            raise TypeError('Datetime value expected, got %r' % value)
        elem = super(DateTimeField, self).to_xml(value.strftime(self.format))
        elem.attrib['t'] = 'D'
        return elem


class RefField(Field):
    """Mapping field for storing object reference ids."""
    def to_python(self, node):
        """xml element => int

        :param node: XML element. Should contains ``v`` attribute.
        :type node: :class:`~phoxpy.xml.Element`

        :return: Integer value.
        :rtype: int

        >>> field = RefField()
        >>> elem = xml.Element('foo', i='42')
        >>> field.to_python(elem)
        42
        """
        return int(node.attrib['i'])

    def to_xml(self, value):
        """int => xml element

        :param value: Integer value.
        :type value: int

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = RefField()
        >>> elem = field.to_xml(42)
        >>> elem.tag
        'r'
        >>> elem.attrib['i']
        '42'
        """
        if not isinstance(value, int):
            raise TypeError('Integer value expected, got %r' % value)
        elem = xml.Element('r')
        if self.name:
            elem.attrib['n'] = self.name
        elem.attrib['i'] = str(value)
        return elem


class ListField(Field):
    """Field type for sequences of other fields.

    :param field: Sequence item field instance.
    :type field: :class:`~phoxpy.mapping.Field`
    """
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
                attribs = dict(elem.attrib.items())
                elem.clear()
                elem.attrib.update(attribs)
            elif other > 1:
                for seq in repeat(self, other - 1):
                    val.extend(seq)
            return val

        def __imul__(self, other):
            if other < 1:
                attribs = dict(self.list.attrib.items())
                self.list.clear()
                self.list.attrib.update(attribs)
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
            return bool(len(self.list))

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

        def index(self, value, start=None, stop=None):
            start = start or 0
            for idx, node in enumerate(islice(self.list, start, stop)):
                if self.field.to_python(node) == value:
                    return idx + start
            else:
                raise ValueError('%r not in list' % value)

        def insert(self, index, object):
            self.list.insert(index, self.field.to_xml(object))

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
            attribs = dict(self.list.attrib.items())
            self.list.clear()
            self.list.attrib.update(attribs)
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

    def __init__(self, field, name=None, default=None):
        default = default or []
        self.field = field
        super(ListField, self).__init__(name, default)

    def to_python(self, node):
        """Converts XML element to list-like object.

        :param node: XML element.
        :type node: :class:`~phoxpy.xml.Element`

        :return: List-like object.
        :rtype: :class:`~phoxpy.mapping.ListField.Proxy`

        >>> field = ListField(IntegerField())
        >>> elem = xml.Element('s')
        >>> elem.append(xml.Element('f', v='1'))
        >>> elem.append(xml.Element('f', v='2'))
        >>> elem.append(xml.Element('f', v='3'))
        >>> res = field.to_python(elem)
        >>> res[0]
        1
        >>> res
        [1, 2, 3]
        """
        return self.Proxy(node, self.field)

    def to_xml(self, value):
        """Converts Python iterable object to XML element.

        :param value: Iterable object.

        :return: XML element instance.
        :rtype: :class:`~phoxpy.xml.Element`

        >>> field = ListField(IntegerField())
        >>> elem = field.to_xml([1, 2, 3])
        >>> elem.tag
        's'
        >>> elem[0].attrib['v'], elem[1].attrib['v'], elem[2].attrib['v']
        ('1', '2', '3')
        """
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
    """Field type for nested objects in Mapping form."""
    def __init__(self, mapping, name=None, default=None):
        default = default or {}
        if isinstance(mapping, dict):
            mapping = Mapping.build(**mapping)
        self.mapping = mapping
        super(ObjectField, self).__init__(name, default=default.copy)

    def to_python(self, node):
        return self.mapping.wrap(node)

    def to_xml(self, value):
        if isinstance(value, Mapping):
            value = dict(value.items())
        if not isinstance(value, dict):
            raise TypeError('Mapping or dict value expected, got %r' % value)
        root = xml.Element('o')
        if self.name:
            root.attrib['n'] = self.name
        self.mapping(**value).unwrap(root)
        return root

#: Mapping between Python types and Field classes.
FIELDS_BY_PYTYPE = {
    bool: BooleanField,
    int: IntegerField,
    long: LongField,
    float: FloatField,
    str: TextField,
    unicode: TextField,
    datetime.datetime: DateTimeField,
    list: ListField,
    ListField.Proxy: ListField,
    dict: ObjectField
}

FIELDS_BY_XML_ATTRS = {
    BooleanField: ('f', {'t': 'B'}),
    IntegerField: ('f', {'t': 'I'}),
    LongField: ('f', {'t': 'L'}),
    FloatField: ('f', {'t': 'F'}),
    TextField: ('f', {'t': 'S'}),
    DateTimeField: ('f', {'t': 'D'}),
    RefField: ('r', {}),
    ListField: ('s', {}),
    ObjectField: ('o', {}),
}

def gen_field_by_value(name, value):
    if isinstance(value, Mapping):
        value = dict(value.items())
    fieldcls = FIELDS_BY_PYTYPE.get(type(value), None)
    if fieldcls is None:
        raise TypeError('Could not map value %r (%s) to any known field'
                        '' % (value, type(value)))
    if fieldcls is ListField:
        if value:
            itemfield = gen_field_by_value(None, value[0])
        else:
            itemfield = FIELDS_BY_PYTYPE[str]()
        field = fieldcls(itemfield, name=name)
    elif fieldcls is ObjectField:
        field = fieldcls(Mapping.build(), name=name)
    else:
        field = fieldcls(name=name)
    return field

def gen_field_by_xmlelem(elem):
    for fieldcls, value in FIELDS_BY_XML_ATTRS.items():
        tagname, attrs = value
        if elem.tag != tagname:
            continue
        if not attrs:
            break
        for key, value in attrs.items():
            if key in elem.attrib and elem.attrib[key] != value:
                break
        else:
            break
    else:
        raise ValueError('Unable map element %s' % xml.dump(elem))
    fname = elem.attrib.get('n', '')
    if fieldcls is ListField:
        if len(elem):
            return fieldcls(gen_field_by_xmlelem(elem[0]), name=fname)
        else:
            return fieldcls(TextField(), name=fname)
    elif fieldcls is ObjectField:
        return fieldcls(Mapping.build(), name=fname)
    else:
        return fieldcls(name=fname)
