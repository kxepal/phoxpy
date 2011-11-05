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
from phoxpy import xmlcodec

class XMLDecodeTestCase(unittest.TestCase):

    def test_decode_boolean_false(self):
        value = xml.decode('<f t="B" v="false" />')
        self.assertEqual(value, False)

    def test_decode_boolean_true(self):
        value = xml.decode('<f t="B" v="true" />')
        self.assertEqual(value, True)

    def test_fail_decode_invalid_boolean(self):
        self.assertRaises(ValueError, xml.decode, '<f t="B" v="foo" />')

    def test_decode_int(self):
        value = xml.decode('<f t="I" v="42" />')
        self.assertEqual(value, 42)

    def test_decode_long(self):
        value = xml.decode('<f t="L" v="100500" />')
        self.assertEqual(value, 100500L)

    def test_decode_float(self):
        value = xml.decode('<f t="F" v="3.14" />')
        self.assertEqual(value, 3.14)

    def test_decode_text(self):
        value = xml.decode('<f t="S" v="привет, world!" />')
        self.assertEqual(value, u'привет, world!')

    def test_decode_date(self):
        value = xml.decode('<f t="D" v="14.02.2009 02:30:31" />')
        self.assertEqual(value, datetime.datetime(2009, 2, 14, 2, 30, 31))
        
    def test_decode_reference(self):
        value = xml.decode('<r i="42" />')
        self.assertTrue(isinstance(value, xmlcodec.Reference))
        self.assertEqual(value, '42')

    def test_decode_sequence(self):
        value = xml.decode('<s><f t="I" v="1"/><f t="I" v="2"/><f t="I" v="3"/></s>')
        self.assertTrue(isinstance(value, list))
        self.assertEqual(value, [1, 2, 3])

    def test_decode_empty_sequence(self):
        value = xml.decode('<s/>')
        self.assertTrue(isinstance(value, list))
        self.assertEqual(value, [])

    def test_decode_object(self):
        value = xml.decode('<o><f n="foo" t="I" v="42"/><f n="bar" t="S" v="baz"/></o>')
        self.assertTrue(isinstance(value, dict))
        self.assertEqual(value, {'foo': 42, 'bar': 'baz'})

    def test_decode_empty_object(self):
        value = xml.decode('<o/>')
        self.assertTrue(isinstance(value, dict))
        self.assertEqual(value, {})

    def test_decode_complex(self):
        value = xml.decode('''<s>
        <o></o>
        <o>
            <s n="foo"><r i="foo"/><r i="bar"/><r i="baz"/></s>
            <s n="zoo">
                <o><s n="bar"><r i="bar"/><r i="baz"/></s></o>
                <o><s n="baz"><r i="baz"/></s></o>
            </s>
        </o></s>
        ''')
        self.assertEqual(value, [
            {},
            {'foo': [xmlcodec.Reference('foo'),
                     xmlcodec.Reference('bar'),
                     xmlcodec.Reference('baz')],
             'zoo': [
                 {'bar': [xmlcodec.Reference('bar'),
                          xmlcodec.Reference('baz')]},
                 {'baz': [xmlcodec.Reference('baz')]}
             ]}
        ])

    def test_decode_object_with_attributes(self):
        value = xml.decode('<o id="test"><f n="foo" t="S" v="bar"/></o>')
        self.assertTrue('id' in value)
        self.assertTrue(isinstance(value['id'], xmlcodec.Attribute))
        self.assertEqual(value['id'], 'test')

    def test_decode_object_with_attributes(self):
        value = xml.decode('<o id="test"><f n="foo" t="S" v="bar"/></o>')
        self.assertTrue('id' in value)
        self.assertTrue(isinstance(value['id'], xmlcodec.Attribute))
        self.assertEqual(value['id'], 'test')

    def test_fail_decode_unnamed_object_item(self):
        self.assertRaises(ValueError, xml.decode, '<o><s/></o>')

    def test_fail_decode_if_collision_occurs(self):
        self.assertRaises(AssertionError,
                          xml.decode, 
                          '<o id="test"><f n="id" t="S" v="bar"/></o>')

    def test_fail_decode_unknown(self):
        self.assertRaises(ValueError, xml.decode, '<foo/>')


class XMLEncodeTestCase(unittest.TestCase):

    def test_encode_none(self):
        self.assertRaises(TypeError, xml.encode, None)

    def test_encode_false(self):
        elem = xml.encode(False)
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('t' in elem.attrib)
        self.assertEqual(elem.attrib['t'], 'B')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], 'false')

    def test_encode_true(self):
        elem = xml.encode(True)
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('t' in elem.attrib)
        self.assertEqual(elem.attrib['t'], 'B')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], 'true')

    def test_encode_int(self):
        elem = xml.encode(42)
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('t' in elem.attrib)
        self.assertEqual(elem.attrib['t'], 'I')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], '42')

    def test_encode_long(self):
        elem = xml.encode(100500L)
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('t' in elem.attrib)
        self.assertEqual(elem.attrib['t'], 'L')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], '100500')

    def test_encode_float(self):
        elem = xml.encode(3.14)
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('t' in elem.attrib)
        self.assertEqual(elem.attrib['t'], 'F')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], '3.14')

    def test_encode_string(self):
        elem = xml.encode('foo')
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('t' in elem.attrib)
        self.assertEqual(elem.attrib['t'], 'S')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], 'foo')

    def test_encode_ref(self):
        elem = xml.encode(xmlcodec.Reference('foo'))
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'r')
        self.assertTrue('i' in elem.attrib)
        self.assertEqual(elem.attrib['i'], 'foo')

    def test_encode_ref_id(self):
        elem = xml.encode(xmlcodec.Reference(42))
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'r')
        self.assertTrue('i' in elem.attrib)
        self.assertEqual(elem.attrib['i'], '42')

    def test_encode_datetime(self):
        elem = xml.encode(datetime.datetime(2009, 2, 14, 2, 31, 30))
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'f')
        self.assertTrue('t' in elem.attrib)
        self.assertEqual(elem.attrib['t'], 'D')
        self.assertTrue('v' in elem.attrib)
        self.assertEqual(elem.attrib['v'], '14.02.2009 02:31:30')
        
    def test_encode_empty_list(self):
        elem = xml.encode(list())
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')
        self.assertEqual(len(elem), 0)

    def test_encode_list(self):
        elem = xml.encode(['foo', 42, 'baz'])
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')
        self.assertEqual(len(elem), 3)

        item = elem[0]
        self.assertEqual(item.tag, 'f')
        self.assertEqual(item.attrib['v'], 'foo')

        item = elem[1]
        self.assertEqual(item.tag, 'f')
        self.assertEqual(item.attrib['v'], '42')

        item = elem[2]
        self.assertEqual(item.tag, 'f')
        self.assertEqual(item.attrib['v'], 'baz')

    def test_encode_tuple(self):
        elem = xml.encode(tuple())
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')

    def test_encode_set(self):
        elem = xml.encode(set(list([1,2,3])))
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')

    def test_encode_frozenset(self):
        elem = xml.encode(frozenset(list([1,2,3])))
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 's')

    def test_encode_object(self):
        elem = xml.encode({'foo': 'bar'})
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'o')
        item = elem[0]
        self.assertTrue('n' in item.attrib)
        self.assertEqual(item.attrib['n'], 'foo')
        self.assertTrue('t' in item.attrib)
        self.assertEqual(item.attrib['t'], 'S')
        self.assertTrue('v' in item.attrib)
        self.assertEqual(item.attrib['v'], 'bar')

    def test_encode_object_with_attribs(self):
        elem = xml.encode({'id': xmlcodec.Attribute('foo'), 'bar': 'baz'})
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'o')
        self.assertTrue('id' in elem.attrib)
        self.assertEqual(elem.attrib['id'], 'foo')
        
    def test_encode_object_skips_none_values(self):
        elem = xml.encode({'id': None, 'foo': 'bar'})
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'o')
        self.assertEqual(len(elem), 1)
        self.assertEqual(elem[0].attrib['v'], 'bar')

    def test_encode_inherited_item(self):
        class Dummy(dict):
            pass
        item = Dummy({'id': xmlcodec.Attribute('foo'), 'bar': 'baz'})
        elem = xml.encode(item)
        self.assertTrue(isinstance(elem, xml.ElementType))
        self.assertEqual(elem.tag, 'o')
        self.assertTrue('id' in elem.attrib)
        self.assertEqual(elem.attrib['id'], 'foo')



if __name__ == '__main__':
    unittest.main()
