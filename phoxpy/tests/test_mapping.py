# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
import datetime
import unittest

from phoxpy import xml
from phoxpy import mapping


class FieldTestCase(unittest.TestCase):

    def test_init_default(self):
        f = mapping.Field()
        self.assertTrue(hasattr(f, 'name'))
        self.assertTrue(hasattr(f, 'default'))
        self.assertEqual(f.name, None)
        self.assertEqual(f.default, None)

    def test_init_with_custom_name(self):
        f = mapping.Field(name='foo')
        self.assertTrue(f.name, 'foo')

    def test_init_with_custom_default_value(self):
        f = mapping.Field(default='foo')
        self.assertTrue(f.default, 'foo')

    def test_default_getter(self):
        f = mapping.Field()
        elem = xml.Element('foo')
        elem.attrib['v'] = 'bar'
        self.assertEqual(f.to_python(elem), 'bar')

    def test_default_setter(self):
        f = mapping.Field()
        elem = f.to_xml('foo')
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], 'foo')

    def test_missed_name_attribute_for_nonamed_fields(self):
        f = mapping.Field()
        elem = f.to_xml('foo')
        self.assertTrue('n' not in elem.attrib)

    def test_name_attribute_for_named_fields(self):
        f = mapping.Field('foo')
        elem = f.to_xml('bar')
        self.assertTrue('n' in elem.attrib)
        self.assertTrue(elem.attrib['n'], 'foo')

    def test_setter_fail_for_non_string_values(self):
        f = mapping.Field()
        self.assertRaises(TypeError, f.to_xml, 42)

    def test_callable_default_value(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(default=lambda: 'foobar')
        self.assertEqual(Dummy().field, 'foobar')


class BooleanFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = mapping.BooleanField()

    def test_get_value_true(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'true'
        self.assertEqual(self.field.to_python(elem), True)

    def test_get_value_false(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'false'
        self.assertEqual(self.field.to_python(elem), False)

    def test_fail_to_get_invalid_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'foobar'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_set_correct_type_attrib(self):
        value = self.field.to_xml(True)
        self.assertEqual(value.attrib.get('t'), 'B')

    def test_set_value_true(self):
        value = self.field.to_xml(True)
        self.assertEqual(value.attrib.get('v'), 'true')

    def test_set_value_false(self):
        value = self.field.to_xml(False)
        self.assertEqual(value.attrib.get('v'), 'false')

    def test_fail_to_set_invalid_value(self):
        self.assertRaises(TypeError, self.field.to_xml, None)


class IntegerFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = mapping.IntegerField()

    def test_get_correct_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '42'
        self.assertEqual(self.field.to_python(elem), 42)

    def test_get_float_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '3.14'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_fail_to_get_invalid_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'foobar'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_set_correct_type_attrib(self):
        value = self.field.to_xml(42)
        self.assertEqual(value.attrib.get('t'), 'I')

    def test_set_correct_value(self):
        value = self.field.to_xml(42)
        self.assertEqual(value.attrib.get('v'), '42')

    def test_fail_to_set_invalid_value(self):
        self.assertRaises(TypeError, self.field.to_xml, 3.14)


class LongFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = mapping.LongField()

    def test_get_correct_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '100500'
        self.assertEqual(self.field.to_python(elem), 100500)

    def test_get_float_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '3.14'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_fail_get_invalid_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'foobar'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_set_correct_type_attrib(self):
        value = self.field.to_xml(100500L)
        self.assertEqual(value.attrib.get('t'), 'L')

    def test_set_correct_value(self):
        value = self.field.to_xml(100500L)
        self.assertEqual(value.attrib.get('v'), '100500')

    def test_fail_set_invalid_value(self):
        self.assertRaises(TypeError, self.field.to_xml, 3.14)


class FloatFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = mapping.FloatField()

    def test_get_correct_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '3.14'
        self.assertEqual(self.field.to_python(elem), 3.14)

    def test_get_int_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '42'
        self.assertEqual(self.field.to_python(elem), 42)

    def test_fail_get_invalid_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'foobar'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_set_correct_type_attrib(self):
        value = self.field.to_xml(3.14)
        self.assertEqual(value.attrib.get('t'), 'F')

    def test_set_correct_value(self):
        value = self.field.to_xml(3.14)
        self.assertEqual(value.attrib.get('v'), '3.14')

    def test_fail_set_invalid_value(self):
        self.assertRaises(TypeError, self.field.to_xml, 100500L)


class TextFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = mapping.TextField()

    def test_get_correct_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'Hello, World!'
        self.assertEqual(self.field.to_python(elem), 'Hello, World!')

    def test_get_unicode_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = u'Привет, Мир!'
        self.assertEqual(self.field.to_python(elem), u'Привет, Мир!')

    def test_set_correct_type_attrib(self):
        value = self.field.to_xml('foobar')
        self.assertEqual(value.attrib.get('t'), 'S')

    def test_set_correct_value(self):
        value = self.field.to_xml('foobar')
        self.assertEqual(value.attrib.get('v'), 'foobar')

    def test_set_unicode_value(self):
        value = self.field.to_xml(u'фывапро')
        self.assertEqual(value.attrib.get('v'), u'фывапро')

    def test_fail_set_nonascii_bytestring_value(self):
        self.assertRaises(ValueError, self.field.to_xml, 'фывапро')

    def test_fail_set_invalid_value(self):
        self.assertRaises(TypeError, self.field.to_xml, None)


class DateTimeFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = mapping.DateTimeField()

    def test_get_correct_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '14.02.2009 02:31:30'
        self.assertEqual(
            self.field.to_python(elem),
            datetime.datetime(2009, 02, 14, 02, 31, 30)
        )

    def test_fail_get_invalid_format_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = '2009.02.14T02:31:30'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_fail_get_invalid_value(self):
        elem = xml.Element('f')
        elem.attrib['v'] = 'foobar'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_set_correct_type_attrib(self):
        value = self.field.to_xml(datetime.datetime(2009, 02, 14, 02, 31, 30))
        self.assertEqual(value.attrib.get('t'), 'D')

    def test_set_correct_value(self):
        value = self.field.to_xml(datetime.datetime(2009, 02, 14, 02, 31, 30))
        self.assertEqual(value.attrib.get('v'), '14.02.2009 02:31:30')

    def test_fail_set_invalid_value(self):
        self.assertRaises(TypeError, self.field.to_xml, '14.02.2009 02:31:30')


class RefFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = mapping.RefField()

    def test_get_correct_value(self):
        elem = xml.Element('r')
        elem.attrib['i'] = '42'
        self.assertEqual(self.field.to_python(elem), 42)

    def test_fail_get_float_value(self):
        elem = xml.Element('r')
        elem.attrib['i'] = '3.14'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_fail_get_invalid_value(self):
        elem = xml.Element('r')
        elem.attrib['i'] = 'foobar'
        self.assertRaises(ValueError, self.field.to_python, elem)

    def test_setter_creates_specific_xml_element(self):
        elem = self.field.to_xml(42)
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'r')
        self.assertTrue('i' in elem.attrib)
        self.assertEqual(elem.attrib['i'], '42')

    def test_fail_to_set_invalid_value(self):
        self.assertRaises(TypeError, self.field.to_xml, 3.14)


class ListFieldTestCase(unittest.TestCase):

    def test_setter_creates_specific_xml_element(self):
        f = mapping.ListField(mapping.Field())
        elem = f.to_xml([])
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')
        self.assertEqual(len(elem), 0)

    def test_set_list_creates_child_elements(self):
        f = mapping.ListField(mapping.Field())
        elem = f.to_xml(['a', 'b', 'c'])
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')
        self.assertEqual(len(elem), 3)
        self.assertEqual(elem[0].attrib['v'], 'a')
        self.assertEqual(elem[1].attrib['v'], 'b')
        self.assertEqual(elem[2].attrib['v'], 'c')

    def test_set_any_iterable(self):
        class Iterable(object):
            def __init__(self, queue):
                self.queue = queue

            def __iter__(self):
                return self

            def next(self):
                if self.queue:
                    return self.queue.pop(0)
                else:
                    raise StopIteration

        f = mapping.ListField(mapping.Field())
        elem = f.to_xml(Iterable(['a', 'b', 'c']))
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')
        self.assertEqual(len(elem), 3)
        self.assertEqual(elem[0].attrib['v'], 'a')
        self.assertEqual(elem[1].attrib['v'], 'b')
        self.assertEqual(elem[2].attrib['v'], 'c')

    def test_fail_set_not_iterable(self):
        f = mapping.ListField(mapping.Field())
        self.assertRaises(TypeError, f.to_xml, 42)

    def test_getter_returns_list_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.Field())
        obj = Dummy()
        self.assertTrue(isinstance(obj.numbers, mapping.ListField.Proxy))
        self.assertTrue(isinstance(obj.numbers, list))

    def test_default_list_field(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField(), default=[1, 2])
        obj = Dummy()
        self.assertEqual(obj.numbers, [1, 2])
        obj.numbers.append(3)
        self.assertEqual(obj.numbers, [1, 2, 3])

    def test_proxy_delitem(self):
        class Dummy(mapping.Mapping):
            values = mapping.ListField(mapping.Field())
        obj = Dummy(values=['foo', 'bar'])
        del obj.values[0]
        self.assertEqual(len(obj.values), 1)
        self.assertEqual(obj.values[0], 'bar')

    def test_proxy_append(self):
        class Dummy(mapping.Mapping):
            values = mapping.ListField(mapping.Field())
        obj = Dummy(values=['foo', 'bar'])
        obj.values.append('baz')
        self.assertEqual(len(obj.values), 3)
        self.assertEqual(obj.values[2], 'baz')

    def test_proxy_extend(self):
        class Dummy(mapping.Mapping):
            values = mapping.ListField(mapping.Field())
        obj = Dummy(values=['foo', 'bar'])
        obj.values.extend(['baz', 'zaz'])
        self.assertEqual(len(obj.values), 4)
        self.assertEqual(obj.values[3], 'zaz')

    def test_proxy_contains(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[i for i in range(5)])
        self.assertTrue(3 in obj.numbers)
        self.assertTrue(6 not in obj.numbers)

    def test_proxy_count(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        self.assertEqual(1, obj.numbers.count(1.0))
        self.assertEqual(0, obj.numbers.count(3.0))

    def test_proxy_index(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        self.assertEqual(0, obj.numbers.index(1.0))

    def test_proxy_index_range(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        self.assertEqual(1, obj.numbers.index(2.0, 1, 2))

    def test_fail_proxy_index_for_nonexisted_element(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        self.assertRaises(ValueError, obj.numbers.index, 5.0)

    def test_fail_proxy_index_negative_start(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        self.assertRaises(ValueError, obj.numbers.index, 2.0, -1 ,3)

    def test_proxy_insert(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        obj.numbers.insert(0, 0.0)
        self.assertEqual(0.0, obj.numbers[0])

    def test_proxy_remove(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        obj.numbers.remove(1.0)
        obj.numbers.remove(2.0)
        self.assertEqual(len(obj.numbers), 1)
        self.assertEqual(obj.numbers[0], 2.5)

    def test_fail_proxy_remove_missing(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers=[1.0, 2.0, 2.5])
        self.assertRaises(ValueError, obj.numbers.remove, 5.0)

    def test_proxy_pop(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy()
        obj.numbers = [1.0, 1.5, 2.0]
        self.assertEqual(obj.numbers.pop(), 2.0)
        self.assertEqual(len(obj.numbers), 2)
        self.assertEqual(obj.numbers.pop(0), 1.0)

    def test_proxy_slices(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy()
        obj.numbers = [i for i in range(5)]
        ll = obj.numbers[1:3]
        self.assertEqual(len(ll), 2)
        self.assertEqual(ll[0], 1)
        obj.numbers[2:4] = [i for i in range(6, 8)]
        self.assertEqual(obj.numbers[2], 6)
        self.assertEqual(obj.numbers[4], 4)
        self.assertEqual(len(obj.numbers), 5)
        del obj.numbers[3:]
        self.assertEquals(len(obj.numbers), 3)

    def test_proxy_sort(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.ListField(mapping.IntegerField()))
        obj = Dummy(numbers=[[4, 2], [2, 3], [0, 1]])
        obj.numbers.sort()
        self.assertEqual(obj.numbers, [[0, 1], [2, 3], [4, 2]])

    def test_proxy_lt(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj.numbers < [4, 5, 6])

    def test_proxy_lt_with_other_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj1 = Dummy(numbers=[1, 2, 3])
        obj2 = Dummy(numbers=[4, 5, 6])
        self.assertTrue(obj1.numbers < obj2.numbers)

    def test_proxy_le(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj.numbers <= [1, 2, 3])

    def test_proxy_le_with_other_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj1 = Dummy(numbers=[1, 2, 3])
        obj2 = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj1.numbers <= obj2.numbers)

    def test_proxy_eq(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj.numbers == [1, 2, 3])

    def test_proxy_eq_with_other_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj1 = Dummy(numbers=[1, 2, 3])
        obj2 = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj1.numbers == obj2.numbers)

    def test_proxy_ne(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj.numbers != [4, 5, 6])

    def test_proxy_ne_with_other_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj1 = Dummy(numbers=[1, 2, 3])
        obj2 = Dummy(numbers=[4, 5, 6])
        self.assertTrue(obj1.numbers != obj2.numbers)

    def test_proxy_ge(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj.numbers >= [1, 2, 3])

    def test_proxy_ge_with_other_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj1 = Dummy(numbers=[1, 2, 3])
        obj2 = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj1.numbers >= obj2.numbers)

    def test_proxy_gt(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        self.assertTrue(obj.numbers > [0, 1, 2])

    def test_proxy_gt_with_other_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj1 = Dummy(numbers=[1, 2, 3])
        obj2 = Dummy(numbers=[0, 1, 2])
        self.assertTrue(obj1.numbers > obj2.numbers)

    def test_proxy_add(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        l = obj.numbers + [4, 5, 6]
        self.assertEqual(l, [1, 2, 3, 4, 5, 6])
        self.assertTrue(isinstance(l, mapping.ListField.Proxy))
        self.assertTrue(obj.numbers is not l)

    def test_proxy_add_other_proxy(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj1 = Dummy(numbers=[1, 2, 3])
        obj2 = Dummy(numbers=[4, 5, 6])
        l = obj1.numbers + obj2.numbers
        self.assertEqual(l, [1, 2, 3, 4, 5, 6])

    def test_proxy_iadd(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        obj.numbers += [4, 5, 6]
        self.assertEqual(obj.numbers, [1, 2, 3, 4, 5, 6])

    def test_proxy_mul(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        l = obj.numbers * 2
        self.assertEqual(l, [1, 2, 3, 1, 2, 3])
        self.assertTrue(isinstance(l, mapping.ListField.Proxy))
        self.assertTrue(obj.numbers is not l)
        self.assertEqual(obj.numbers, [1, 2, 3])

    def test_proxy_mul_one(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        l = obj.numbers * 1
        self.assertEqual(l, [1, 2, 3])

    def test_proxy_mul_zero(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        l = obj.numbers * 0
        self.assertEqual(l, [])
        self.assertTrue(isinstance(l, mapping.ListField.Proxy))

    def test_proxy_imul(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        obj.numbers *= 2
        self.assertEqual(obj.numbers, [1, 2, 3, 1, 2, 3])

    def test_proxy_imul_one(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        obj.numbers *= 1
        self.assertEqual(obj.numbers, [1, 2, 3])

    def test_proxy_imul_zero(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        obj.numbers *= 0
        self.assertEqual(obj.numbers, [])


class MappingTestCase(unittest.TestCase):

    def test_getitem(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field()
        obj = Dummy(field='hello')
        self.assertEqual(obj['field'], 'hello')

    def test_getitem_custom_name(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(name='foo')
        obj = Dummy(field='hello')
        self.assertEqual(obj['foo'], 'hello')

    def test_getitem_default_value_with_custom_name(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(name='foo', default='bar')
        obj = Dummy()
        self.assertEqual(obj['field'], 'bar')
        self.assertEqual(obj['foo'], 'bar')

    def test_getitem_unknown_name(self):
        self.assertRaises(KeyError, mapping.Mapping().__getitem__, 'foo')

    def test_setitem_unknown_name(self):
        self.assertRaises(KeyError, mapping.Mapping().__setitem__, 'foo', 'bar')

    def test_setitem(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field()
        obj = Dummy(field='hello')
        obj['field'] = 'world'
        self.assertEqual(obj.field, 'world')

    def test_setitem_custom_name(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(name='foo')
        obj = Dummy(field='hello')
        obj['foo'] = 'world'
        self.assertEqual(obj.field, 'world')

    def test_delitem(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field()
        obj = Dummy(field='hello')
        del obj['field']
        self.assertEqual(obj.field, None)

    def test_delitem_custom_name(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(name='foo')
        obj = Dummy(field='hello')
        del obj['foo']
        self.assertEqual(obj.field, None)

    def test_copy(self):
        class Dummy(mapping.Mapping):
            foo = mapping.Field()
            bar = mapping.IntegerField()
            baz = mapping.ListField(mapping.RefField())
        obj = Dummy(foo='test', bar=42, baz=[1, 2, 3])
        new = obj.copy()
        self.assertTrue(obj is not new)
        self.assertEqual(obj.foo, new['foo'])
        self.assertEqual(obj.bar, new['bar'])
        self.assertEqual(obj.baz, new['baz'])

    def test_copy_doesnt_keeps_refs_for_mutables(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers=[1, 2, 3])
        new = obj.copy()
        self.assertEqual(obj.numbers, new.numbers)
        obj.numbers.append(4)
        self.assertNotEqual(obj.numbers, new.numbers)

    def test_wrap_single_node(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        root = xml.Element('content')
        numbers = xml.Element('s', n='numbers')
        numbers.append(xml.Element('f', v='1'))
        numbers.append(xml.Element('f', v='2'))
        numbers.append(xml.Element('f', v='3'))
        root.append(numbers)
        obj = Dummy.wrap(root)
        self.assertEqual(obj.numbers, [1, 2, 3])

    def test_wrap_tree(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
            text = mapping.TextField(name='story')
        root = xml.Element('root')
        numbers = xml.Element('s', n='numbers')
        numbers.append(xml.Element('f', v='1'))
        numbers.append(xml.Element('f', v='2'))
        numbers.append(xml.Element('f', v='3'))
        root.append(numbers)
        root.append(xml.Element('f', n='story', v='lorem...'))
        tree = xml.ElementTree(root)
        obj = Dummy.wrap(tree)
        self.assertEqual(obj.numbers, [1, 2, 3])
        self.assertEqual(obj.text, 'lorem...')

    def test_wrap_with_defaults(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
            text = mapping.TextField(name='story')
        root = xml.Element('content')
        numbers = xml.Element('s', n='numbers')
        numbers.append(xml.Element('f', v='1'))
        numbers.append(xml.Element('f', v='2'))
        numbers.append(xml.Element('f', v='3'))
        root.append(numbers)
        data = {
            'text': 'lorem...'
        }
        obj = Dummy.wrap(root, **data)
        self.assertEqual(obj.numbers, [1, 2, 3])
        self.assertEqual(obj.text, 'lorem...')

    def test_fail_wrap_with_invalid_defaults(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
            text = mapping.TextField(name='story')
        root = xml.Element('s', n='numbers')
        root.append(xml.Element('f', v='1'))
        root.append(xml.Element('f', v='2'))
        root.append(xml.Element('f', v='3'))
        data = {
            'missed': 'lorem...'
        }
        self.assertRaises(ValueError, Dummy.wrap, root, kwargs=data)

    def test_fail_wrap_invalid_source(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        self.assertRaises(TypeError, Dummy.wrap, [1, 2, 3])

    def test_fail_wrap_unnamed_node(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
            text = mapping.TextField(name='story')
        root = xml.Element('root')
        numbers = xml.Element('s', n='numbers')
        numbers.append(xml.Element('f', v='1'))
        numbers.append(xml.Element('f', v='2'))
        numbers.append(xml.Element('f', v='3'))
        root.append(numbers)
        root.append(xml.Element('f', v='lorem...'))
        self.assertRaises(ValueError, Dummy.wrap, root)

    def test_fail_wrap_unnamed_nodes_in_tree(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
            text = mapping.TextField(name='story')
        root = xml.Element('root')
        numbers = xml.Element('s', n='numbers')
        numbers.append(xml.Element('f', v='1'))
        numbers.append(xml.Element('f', v='2'))
        numbers.append(xml.Element('f', v='3'))
        root.append(numbers)
        root.append(xml.Element('f', v='lorem...'))
        tree = xml.ElementTree(root)
        self.assertRaises(ValueError, Dummy.wrap, tree)

    def test_keys(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField()
            bar = mapping.ListField(mapping.IntegerField())
            baz = mapping.ObjectField(mapping.Mapping.build())
        obj = Dummy()
        keys = obj.keys()
        self.assertTrue(hasattr(keys, 'next'))
        self.assertEqual(sorted(list(keys)), sorted(['foo', 'bar', 'baz']))

    def test_values(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField()
            bar = mapping.ListField(mapping.IntegerField())
            baz = mapping.ObjectField(mapping.Mapping.build(
                zoo = mapping.TextField()
            ))
        obj = Dummy(foo='foo', bar=[42], baz={'zoo': 'boo'})
        values = obj.values()
        self.assertTrue(hasattr(values, 'next'))
        self.assertEqual(
            sorted(list(values)),
            sorted(['foo', [42], {'zoo': 'boo'}])
        )

    def test_items(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField(default='bar')
        obj = Dummy()
        items = obj.items()
        self.assertTrue(hasattr(items, 'next'))
        self.assertEqual(list(items), [('foo', 'bar')])

    def test_setdefault(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField()
        obj = Dummy()
        obj.setdefault('foo', 'bar')
        self.assertEqual(obj.foo, 'bar')

    def test_setdefault_custom_name(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField(name='baz')
        obj = Dummy()
        obj.setdefault('baz', 'bar')
        self.assertEqual(obj.foo, 'bar')
        self.assertEqual(obj['baz'], 'bar')

    def test_update(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField()
            bar = mapping.ListField(mapping.IntegerField())
            baz = mapping.ObjectField(mapping.Mapping.build(
                zoo = mapping.TextField()
            ))
        obj = Dummy()
        obj.update(dict(foo='foo', bar=[42], baz={'zoo': 'boo'}))
        self.assertEqual(
            sorted(list(obj.values())),
            sorted(['foo', [42], {'zoo': 'boo'}])
        )

    def test_get(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField(default='bar')
        obj = Dummy()
        self.assertEqual(obj.get('foo'), 'bar')

    def test_get_default(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField(default='bar')
        obj = Dummy()
        self.assertEqual(obj.get('bar', 'baz'), 'baz')

    def test_contains(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField(default='bar')
        obj = Dummy()
        self.assertTrue('foo' in obj)
        self.assertTrue('bar' not in obj)

    def test_iter(self):
        class Dummy(mapping.Mapping):
            foo = mapping.TextField(default='bar')
            baz = mapping.IntegerField(default=42)
        obj = Dummy()
        self.assertEqual(sorted(iter(obj)), sorted(obj.keys()))


class GenericMappingTestCase(unittest.TestCase):

    def test_setdefault(self):
        class Dummy(mapping.GenericMapping):
            foo = mapping.TextField()
        obj = Dummy()
        obj.setdefault('baz', 'bar')
        self.assertEqual(obj['baz'], 'bar')

    def test_add_new_fields_via_constructor(self):
        obj = mapping.GenericMapping(foo='bar')
        self.assertTrue(isinstance(obj._fields['foo'], mapping.TextField))
        self.assertEqual(obj['foo'], 'bar')

    def test_add_new_fields_via_dict_interface(self):
        class Post(mapping.GenericMapping):
            foo = mapping.TextField()
        obj = Post(foo='bar')
        obj['bar'] = 'baz'
        self.assertTrue(isinstance(obj._fields['bar'], mapping.TextField))
        self.assertEqual(obj['bar'], 'baz')

    def test_add_list_field(self):
        obj = mapping.GenericMapping()
        obj['foo'] = ['bar', 'baz']
        self.assertTrue(isinstance(obj._fields['foo'], mapping.ListField))
        self.assertEqual(obj['foo'], ['bar', 'baz'])

    def test_add_object_field(self):
        obj = mapping.GenericMapping()
        obj['foo'] = {'bar': 'baz'}
        self.assertTrue(isinstance(obj._fields['foo'], mapping.ObjectField))
        self.assertEqual(obj['foo'], {'bar': 'baz'})

    def test_list_with_text_field_as_default(self):
        obj = mapping.GenericMapping()
        obj['foo'] = []
        self.assertTrue(isinstance(obj._fields['foo'], mapping.ListField))
        obj['foo'] = ['bar', 'baz']
        self.assertEqual(obj['foo'], ['bar', 'baz'])
        self.assertRaises(TypeError, obj.__setitem__, 'foo', [1, 2, 3])

    def test_fail_map_unknown_type(self):
        obj = mapping.GenericMapping()
        self.assertRaises(TypeError, obj.__setitem__, 'foo', object())
        self.assertRaises(TypeError, obj.__setitem__, 'foo', [object()])

    def test_wrap(self):
        class Post(mapping.Mapping):
            author = mapping.TextField(default='foo')
            content = mapping.TextField(default='bar')
            posted_at = mapping.DateTimeField(
                            default=datetime.datetime(2010, 2, 14, 2, 31, 30)
                        )
        post = Post()
        obj = mapping.GenericMapping.wrap(post.unwrap(xml.Element('root')))
        self.assertEqual(obj['author'], post.author)
        self.assertEqual(obj['content'], post.content)
        self.assertEqual(obj['posted_at'], post.posted_at)

    def test_wrap_list_field(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        dummy = Dummy(numbers=[1, 2, 3])
        obj = mapping.GenericMapping.wrap(dummy.unwrap(xml.Element('dummy')))
        self.assertEqual(obj['numbers'], dummy.numbers)

    def test_wrap_empty_list(self):
        root = xml.Element('root')
        root.append(xml.Element('s', n='foo'))
        obj = mapping.GenericMapping.wrap(root)
        self.assertEqual(obj['foo'], [])
        obj['foo'].append('bar')
        self.assertEqual(obj['foo'], ['bar'])
        self.assertRaises(TypeError, obj['foo'].append, 42)

    def test_wrap_object(self):
        root = xml.Element('root')
        obj = xml.Element('o', n='foo')
        obj.append(xml.Element('f', n='bar', t='S', v='baz'))
        root.append(obj)
        dummy = mapping.GenericMapping.wrap(root)
        self.assertEqual(dummy['foo']['bar'], 'baz')

    def test_fail_wrap_unknown_field(self):
        root = xml.Element('root')
        root.append(xml.Element('f', t='U', n='foo'))
        self.assertRaises(ValueError, mapping.GenericMapping.wrap, root)

        root = xml.Element('root')
        root.append(xml.Element('foo', t='bar', n='baz'))
        self.assertRaises(ValueError, mapping.GenericMapping.wrap, root)

    def test_fail_wrap_unnamed_field(self):
        root = xml.Element('root')
        root.append(xml.Element('f', t='I'))
        self.assertRaises(ValueError, mapping.GenericMapping.wrap, root)


class ObjectFieldTestCase(unittest.TestCase):

    def test_convert_xml_nodes_to_mapping(self):
        field = mapping.ObjectField(mapping.Mapping.build(
            text = mapping.TextField(),
            numbers = mapping.ListField(mapping.IntegerField())
        ))
        root = xml.Element('o')
        root.append(xml.Element('f', n='text', v='foobar'))
        numbers = xml.Element('s', n='numbers')
        numbers.append(xml.Element('f', v='1'))
        numbers.append(xml.Element('f', v='2'))
        numbers.append(xml.Element('f', v='3'))
        root.append(numbers)
        res = field.to_python(root)
        self.assertEqual(res.text, 'foobar')
        self.assertEqual(res.numbers, [1, 2, 3])

    def test_init_from_dict(self):
        field = mapping.ObjectField({
            'text': mapping.TextField(),
            'numbers': mapping.ListField(mapping.IntegerField())
        })
        root = xml.Element('o')
        root.append(xml.Element('f', n='text', v='foobar'))
        numbers = xml.Element('s', n='numbers')
        numbers.append(xml.Element('f', v='1'))
        numbers.append(xml.Element('f', v='2'))
        numbers.append(xml.Element('f', v='3'))
        root.append(numbers)
        res = field.to_python(root)
        self.assertEqual(res.text, 'foobar')
        self.assertEqual(res.numbers, [1, 2, 3])

    def test_setter_creates_specific_xml_element(self):
        field = mapping.ObjectField(mapping.Mapping.build(
            text = mapping.TextField(),
            numbers = mapping.ListField(mapping.IntegerField())
        ), name='baz')
        elem = field.to_xml({'text': 'foobar', 'numbers': [1, 2, 3]})
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'o')
        self.assertEqual(elem.attrib['n'], 'baz')

    def test_fail_set_invalid_value(self):
        field = mapping.ObjectField(mapping.Mapping.build(
            text = mapping.TextField(),
            numbers = mapping.ListField(mapping.IntegerField())
        ), name='baz')
        self.assertRaises(TypeError, field.to_xml, [1, 2, 42])


if __name__ == '__main__':
    unittest.main()
