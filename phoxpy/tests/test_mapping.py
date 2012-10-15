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

    def test_callable_default_value(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(default=lambda: 'foobar')
        self.assertEqual(Dummy().field, 'foobar')


class AttributeFieldTestCase(unittest.TestCase):

    def test_object_attribute(self):
        class Dummy(mapping.Mapping):
            foo = mapping.ObjectField(mapping.Mapping.build(
                bar = mapping.AttributeField()
            ))
        obj = Dummy()
        obj['foo'] = {'bar': 'baz'}
        self.assertEqual(obj.foo.bar, 'baz')


class BooleanTestCase(unittest.TestCase):

    def setUp(self):
        class Dummy(mapping.Mapping):
            field = mapping.BooleanField()
        self.Dummy = Dummy

    def test_get_value(self):
        obj = self.Dummy(field=False)
        self.assertEqual(obj.field, False)

    def test_set_value(self):
        obj = self.Dummy()
        obj.field = True
        self.assertEqual(obj.field, True)


class IntegerTestCase(unittest.TestCase):

    def setUp(self):
        class Dummy(mapping.Mapping):
            field = mapping.IntegerField()
        self.Dummy = Dummy

    def test_get_value(self):
        obj = self.Dummy(field=42)
        self.assertEqual(obj.field, 42)

    def test_set_value(self):
        obj = self.Dummy()
        obj.field = 42
        self.assertEqual(obj.field, 42)


class LongFieldTestCase(unittest.TestCase):

    def setUp(self):
        class Dummy(mapping.Mapping):
            field = mapping.LongField()
        self.Dummy = Dummy

    def test_get_value(self):
        obj = self.Dummy(field=100500)
        self.assertEqual(obj.field, 100500L)

    def test_set_value(self):
        obj = self.Dummy()
        obj.field = 100500
        self.assertEqual(obj.field, 100500L)


class FloatFieldTestCase(unittest.TestCase):

    def setUp(self):
        class Dummy(mapping.Mapping):
            field = mapping.FloatField()
        self.Dummy = Dummy

    def test_get_value(self):
        obj = self.Dummy(field=3.14)
        self.assertEqual(obj.field, 3.14)

    def test_set_value(self):
        obj = self.Dummy()
        obj.field = 3.14
        self.assertEqual(obj.field, 3.14)

    def test_set_int_value(self):
        obj = self.Dummy()
        obj.field = 42
        self.assertEqual(obj.field, 42.0)


class TextFieldTestCase(unittest.TestCase):

    def setUp(self):
        class Dummy(mapping.Mapping):
            field = mapping.TextField()
        self.Dummy = Dummy

    def test_get_value(self):
        obj = self.Dummy(field='foo')
        self.assertEqual(obj.field, u'foo')

    def test_set_value(self):
        obj = self.Dummy()
        obj.field = u'привет'
        self.assertEqual(obj.field, u'привет')

    def test_set_utf8_value(self):
        obj = self.Dummy()
        obj.field = u'привет'.encode('utf-8')
        self.assertEqual(obj.field, u'привет')

    def test_fail_set_non_utf8_value(self):
        obj = self.Dummy()
        try:
            obj.field = u'привет'.encode('cp1251')
        except UnicodeDecodeError:
            pass
        else:
            self.fail('%s expected' % UnicodeDecodeError)

    def test_fail_set_non_string_value(self):
        obj = self.Dummy()
        try:
            obj.field = object()
        except TypeError:
            pass
        else:
            self.fail('%s expected' % TypeError)


class DatetimeTestCase(unittest.TestCase):

    def setUp(self):
        class Dummy(mapping.Mapping):
            field = mapping.DateTimeField()
        self.Dummy = Dummy
        self.datetime = datetime.datetime(2009, 2, 13, 23, 31, 30)
        self.date = datetime.datetime(2009, 2, 13)

    def test_get_value(self):
        obj = self.Dummy(field=self.datetime)
        self.assertEqual(obj.field, self.datetime)

    def test_set_value(self):
        obj = self.Dummy()
        obj.field = self.datetime
        self.assertEqual(obj.field, self.datetime)

    def test_get_date_value(self):
        obj = self.Dummy(field=self.datetime)
        self.assertEqual(obj.field, self.datetime)

    def test_set_date_value(self):
        obj = self.Dummy()
        obj.field = self.datetime
        self.assertEqual(obj.field, self.datetime)

class ListFieldTestCase(unittest.TestCase):

    def test_getter_returns_list(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.Field())
        obj = Dummy()
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
        obj = Dummy(numbers= [i for i in range(5)])
        self.assertTrue(3 in obj.numbers)
        self.assertTrue(6 not in obj.numbers)

    def test_proxy_count(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers= [1.0, 2.0, 2.5])
        self.assertEqual(1, obj.numbers.count(1.0))
        self.assertEqual(0, obj.numbers.count(3.0))

    def test_proxy_index(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers= [1.0, 2.0, 2.5])
        self.assertEqual(0, obj.numbers.index(1.0))

    def test_proxy_index_range(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.FloatField())
        obj = Dummy(numbers= [1.0, 2.0, 2.5])
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
        obj = Dummy(numbers= [[4, 2], [2, 3], [0, 1]])
        obj.numbers.sort()
        self.assertEqual(obj.numbers, [[0, 1], [2, 3], [4, 2]])

    def test_proxy_lt(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers= [1, 2, 3])
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
        obj = Dummy(numbers= [1, 2, 3])
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
        obj = Dummy(numbers= [1, 2, 3])
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
        obj = Dummy(numbers= [1, 2, 3])
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
        obj = Dummy(numbers= [1, 2, 3])
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
        obj = Dummy(numbers= [1, 2, 3])
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
        self.assertTrue(isinstance(l, list))
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
        self.assertTrue(isinstance(l, list))
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
        self.assertTrue(isinstance(l, list))

    def test_proxy_imul(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers= [1, 2, 3])
        obj.numbers *= 2
        self.assertEqual(obj.numbers, [1, 2, 3, 1, 2, 3])

    def test_proxy_imul_one(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers= [1, 2, 3])
        obj.numbers *= 1
        self.assertEqual(obj.numbers, [1, 2, 3])

    def test_proxy_imul_zero(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.IntegerField())
        obj = Dummy(numbers= [1, 2, 3])
        obj.numbers *= 0
        self.assertEqual(obj.numbers, [])

    def test_proxy_mapping_wrap(self):
        class Dummy(mapping.Mapping):
            numbers = mapping.ListField(mapping.ObjectField(mapping.Mapping.build(
                positive = mapping.ListField(mapping.IntegerField()),
                negative = mapping.ListField(mapping.IntegerField()),
            )))
        obj = Dummy()
        obj.numbers.append({'positive': [1, 2, 3], 'negative': [-1, -2, -3]})
        self.assertTrue(isinstance(obj.numbers[0], mapping.Mapping))
        self.assertEqual(obj.numbers[0].positive, [1, 2, 3])


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
        self.assertEqual(obj['foo'], 'bar')

    def test_getitem_unknown_name(self):
        self.assertRaises(KeyError, mapping.Mapping().__getitem__, 'foo')

    def test_getitem_none_value(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(name='foo')
        obj = Dummy()
        self.assertEqual(obj['foo'], None)

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

    def test_setitem_none_value(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(name='foo')
        obj = Dummy()
        self.assertEqual(obj['foo'], None)

    def test_delitem(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field()
        obj = Dummy(field='hello')
        del obj['field']
        self.assertEqual(obj.field, None)

    def test_delitem_custom_name(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(name='foo')
        obj = Dummy()
        obj.field = 'hello'
        del obj['foo']
        self.assertEqual(obj.field, None)

    def test_delitem_sets_default_value(self):
        class Dummy(mapping.Mapping):
            field = mapping.Field(default='foo')
        obj = Dummy()
        obj.field = 'bar'
        del obj['field']
        self.assertEqual(obj.field, 'foo')

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

    def test_init_custom_field(self):
        class Dummy(mapping.Mapping):
            pass
        obj = Dummy(foo='bar')
        self.assertEqual(obj['foo'], 'bar')

    def test_set_custom_field(self):
        class Dummy(mapping.Mapping):
            pass
        obj = Dummy(foo={'bar': 'baz'})
        self.assertEqual(obj['foo'], {'bar': 'baz'})
        self.assertEqual(obj['foo']['bar'], 'baz')

    def test_set_custom_complex_field(self):
        class Dummy(mapping.Mapping):
            pass
        obj = Dummy()
        obj['foo'] = [{'bar': 'baz'}, {'boo': 42}]
        self.assertEqual(obj['foo'][0], {'bar': 'baz'})
        self.assertEqual(obj['foo'][1], {'boo': 42})

    def test_del_custom_field(self):
        class Dummy(mapping.Mapping):
            pass
        obj = Dummy()
        self.assertRaises(KeyError, obj.__getitem__, 'foo')
        obj['foo'] = [1, 2, 42]
        self.assertEqual(obj['foo'][2], 42)
        del obj['foo']
        self.assertTrue('foo' not in obj)

    def test_convert_to_dict(self):
        class Dummy(mapping.Mapping):
            boo = mapping.AttributeField()
        obj = Dummy(foo='bar', baz=3.14, zoo=[1, 2, 3], boo='test')
        self.assertEqual(
            obj._asdict(),
            {'foo': 'bar', 'baz': 3.14, 'zoo': [1, 2, 3], 'boo': 'test'}
        )

    def test_to_xml_with_nested_mapping(self):
        class Foo(mapping.Mapping):
            bar = mapping.TextField()
        class Dummy(mapping.Mapping):
            foo = mapping.ObjectField(Foo)
        obj = Dummy()
        obj.foo.bar = 'baz'
        obj.to_xml()

    def test_wrap_dict(self):
        class Dummy(mapping.Mapping):
            boo = mapping.IntegerField()
        obj = Dummy.wrap({'boo': 42, 'foo': 'ehlo'})
        self.assertEqual(obj.boo, 42)
        self.assertEqual(obj['foo'], 'ehlo')

    def test_wrap_mapping(self):
        class Dummy(mapping.Mapping):
            boo = mapping.IntegerField()
        class Funny(mapping.Mapping):
            foo = mapping.TextField()
        obj = Dummy.wrap({'boo': 42, 'foo': 'ehlo'})
        obj2 = Funny.wrap(obj)
        self.assertEqual(obj2['boo'], 42)
        self.assertEqual(obj2.foo, 'ehlo')

    def test_wrap_fail(self):
        class Dummy(mapping.Mapping):
            boo = mapping.IntegerField()
        self.assertRaises(TypeError, Dummy.wrap, 42)
        self.assertRaises(TypeError, Dummy.wrap, None)
        self.assertRaises(TypeError, Dummy.wrap, [])


class ObjectFieldTestCase(unittest.TestCase):

    def test_fail_set_invalid_value(self):
        field = mapping.ObjectField(mapping.Mapping.build(
            text = mapping.TextField(),
            numbers = mapping.ListField(mapping.IntegerField())
        ), name='baz')
        self.assertRaises(TypeError, field._set_value, [1, 2, 42])

    def test_with_mapping(self):
        class Dummy(mapping.Mapping):
            foo = mapping.ObjectField(mapping.Mapping.build(
                bar = mapping.TextField()
            ))
        obj = Dummy()
        obj.foo.bar = 'baz'
        self.assertEqual(obj.foo.bar, 'baz')
        self.assertEqual(obj['foo']['bar'], 'baz')

    def test_item_assigment(self):
        class Dummy(mapping.Mapping):
            foo = mapping.ObjectField(mapping.Mapping.build(
                bar=mapping.IntegerField()
            ))
        obj = Dummy()
        obj.foo.bar = 42
        self.assertEqual(obj['foo']['bar'], 42)
        obj['foo']['bar'] = 24
        self.assertEqual(obj.foo.bar, 24)

    def test_dynamic_item_assigment(self):
        class Dummy(mapping.Mapping):
            foo = mapping.ObjectField(mapping.Mapping.build())
        obj = Dummy()
        obj.foo['bar'] = 42
        self.assertEqual(obj['foo']['bar'], 42)
        obj['foo']['bar'] = 24
        self.assertEqual(obj['foo']['bar'], 24)

    def test_dynamic_object_item_assigment(self):
        class Dummy(mapping.Mapping):
            pass
        obj = Dummy(foo={})
        obj['foo']['bar'] = 42
        self.assertTrue('bar' in obj['foo'])
        self.assertEqual(obj['foo']['bar'], 42)


if __name__ == '__main__':
    unittest.main()
