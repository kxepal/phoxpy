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
        if value is not None:
            value = self.to_xml(value)
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
        self._data = {}
        for fieldname in self._fields:
            if fieldname in values:
                setattr(self, fieldname, values.pop(fieldname))
            else:
                setattr(self, fieldname, getattr(self, fieldname))
        if values:
            raise ValueError('Unexpected kwargs found: %r' % values)

    def __getitem__(self, item):
        field = self._get_field(item)
        return field.to_python(self._data[field.name])

    def __setitem__(self, key, value):
        field = self._get_field(key)
        self._data[field.name] = field.to_xml(value)

    def __delitem__(self, key):
        field = self._get_field(key)
        self._data[field.name] = None

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

    def _get_field(self, key):
        if key in self._fields:
            return self._fields[key]
        elif key in self._data:
            for field in self._fields.values():
                if field.name == key:
                    return field
        else:
            raise KeyError('Unknown field %r' % key)

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
    def wrap(cls, xmlsrc, **defaults):
        """Wrap :class:`~phoxpy.xml.Element` or :class:`~phoxpy.xml.ElementTree`
        instance and map elements to related fields by name.
        """
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
        """Unwraps mapping instance to XML object.

        :param root: Root xml node.
        :type root: :class:`~phoxpy.xml.Element`
        """
        for node in self._data.values():
            if isinstance(node, Mapping):
                root.append(node.unwrap())
            elif node is not None:
                root.append(node)
        return root

    def copy(self):
        """Creates a shallow copy of mapping."""
        instance = type(self)()
        for name, node in self._data.items():
            instance._data[name] = copy.deepcopy(node)
        return instance

    def keys(self):
        """Iterate over field names."""
        for key in self._data:
            yield key

    def values(self):
        """Iterate over field values."""
        for key in self._data:
            yield self[key]

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
        field = self._get_field(key)
        field.default = value
        if self._data[key] is None:
            self[key] = value

    def update(self, data):
        """Batch update fields data."""
        for key, value in data.items():
            self[key] = value


class GenericMapping(Mapping):
    """Generic mapping provides more flexible scheme construction
    with on fly field creation.

    >>> class Post(GenericMapping):
    ...   pass
    >>> post = Post(foo='zoo', bar=42, baz=False)
    >>> post['foo']
    'zoo'
    >>> post['bar']
    42
    >>> post['baz']
    False
    """
    def __init__(self, **values):
        self._fields = dict(self._fields)
        self._data = {}
        for fieldname in self._fields:
            if fieldname in values:
                setattr(self, fieldname, values.pop(fieldname))
            elif hasattr(self, fieldname):
                setattr(self, fieldname, getattr(self, fieldname))
        for name, value in values.items():
            self[name] = value

    def __setitem__(self, key, value):
        if not (key in self._fields or key in self._data):
            self._set_field(key, value)
        super(GenericMapping, self).__setitem__(key, value)

    def _gen_field(self, key, value):
        fieldcls = FIELDS_BY_PYTYPE.get(type(value), None)
        if fieldcls is None:
            raise TypeError('Could not map value %r (%s) to any known field'
                            '' % (value, type(value)))
        if fieldcls is ListField:
            if value:
                item = value[0]
                itemfield = FIELDS_BY_PYTYPE.get(type(item), None)
                if itemfield is None:
                    raise TypeError('Could not map value %r (%s) to any'
                                    ' known field' % (item, type(item)))
            else:
                itemfield = FIELDS_BY_PYTYPE[str]
            field = fieldcls(itemfield(), name=key)
        elif fieldcls is ObjectField:
            d = {}
            for key, item in value.items():
                d[key] = self._gen_field(key, item)
            field = fieldcls(GenericMapping.build(**d), name=key)
        else:
            field = fieldcls(name=key)
        return field

    def _set_field(self, key, value):
        field = self._gen_field(key, value)
        self._fields[key] = field
        self._data[key] = field.to_xml(value)

    def setdefault(self, key, value):
        """Sets default value to specified field by name."""
        if not (key in self._fields or key in self._data):
            self._set_field(key, value)
        super(GenericMapping, self).setdefault(key, value)


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
        if not isinstance(value, datetime.datetime):
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
            self.list.clear()
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
    dict: ObjectField
}
