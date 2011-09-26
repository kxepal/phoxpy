# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
from phoxpy import mapping
from phoxpy import messages
from phoxpy import xml


class MessageTestCase(unittest.TestCase):

    def test_generic_message(self):
        self.assertTrue(isinstance(messages.Message(), mapping.Mapping))

    def test_abstract_to_string_serialization(self):
        class Post(messages.Message):
            ids = mapping.ListField(mapping.RefField())
        self.assertRaises(NotImplementedError, str, Post(ids=[1, 2, 3]))

    def test_session_id(self):
        msg = messages.Message(sessionid='bar')
        self.assertEqual(msg.sessionid, 'bar')
        msg.sessionid = 'baz'
        self.assertEqual(msg.sessionid, 'baz')

    def test_unwrap_default_tag(self):
        class Post(messages.Message):
            ids = mapping.ListField(mapping.RefField())
        root = Post(ids=['1', '2', '3']).unwrap()
        self.assertEqual(root.tag, 'content')

    def test_unwrap_sets_content_tag(self):
        class Post(messages.Message):
            ids = mapping.ListField(mapping.RefField())
        foo = xml.Element('foo')
        root = Post(ids=['foo', 'bar', 'baz']).unwrap(foo)
        self.assertEqual(root.tag, 'foo')
        self.assertEqual(root[0].tag, 'content')


class PhoxRequestTestCase(unittest.TestCase):

    def test_set_type(self):
        msg = messages.PhoxRequest(type='foo')
        self.assertEqual(msg.type, 'foo')

    def test_is_phoxmsg_instance(self):
        msg = messages.PhoxRequest(type='foo')
        self.assertTrue(isinstance(msg, messages.Message))

    def test_buildnumber(self):
        msg = messages.PhoxRequest(type='foo', buildnumber='bar')
        self.assertEqual(msg.buildnumber, 'bar')

    def test_version(self):
        msg = messages.PhoxRequest(type='foo', version='bar')
        self.assertEqual(msg.version, 'bar')

    def test_wrap_should_containt_attrib_type(self):
        root = xml.Element('phox-request')
        root.append(xml.Element('content'))
        self.assertRaises(AssertionError, messages.PhoxRequest.wrap, root)

    def test_wrap(self):
        root = xml.Element('phox-request')
        root.attrib['type'] = 'foo'
        root.append(xml.Element('content'))
        req = messages.PhoxRequest.wrap(root)
        self.assertEqual(req.type, 'foo')

    def test_unwrap(self):
        msg = messages.PhoxRequest(type='foo', sessionid='bar',
                                   version='baz', buildnumber='zoo')
        data = msg.unwrap()
        self.assertEqual(data.tag, 'phox-request')

        self.assertTrue('type' in data.attrib)
        self.assertEqual(data.attrib['type'], 'foo')

        self.assertTrue('sessionid' in data.attrib)
        self.assertEqual(data.attrib['sessionid'], 'bar')

        self.assertTrue('buildnumber' in data.attrib)
        self.assertEqual(data.attrib['buildnumber'], 'zoo')

        self.assertTrue('version' in data.attrib)
        self.assertEqual(data.attrib['version'], 'baz')

    def test_stringify(self):
        self.assertEqual(
            str(messages.PhoxRequest(type='foo')).replace(' />', '/>'),
            "<?xml version='1.0' encoding='%s'?>\n"
            '<!DOCTYPE phox-request SYSTEM "phox.dtd">\n'
            '<phox-request type="foo">'
            '<content/>'
            '</phox-request>' % xml.ENCODING
        )


class PhoxResponseTestCase(unittest.TestCase):

    def test_is_phoxmsg_instance(self):
        msg = messages.PhoxResponse()
        self.assertTrue(isinstance(msg, messages.Message))

    def test_buildnumber(self):
        msg = messages.PhoxResponse(buildnumber='bar')
        self.assertEqual(msg.buildnumber, 'bar')

    def test_unwrap(self):
        msg = messages.PhoxResponse(sessionid='bar',  buildnumber='baz')
        data = msg.unwrap()
        self.assertEqual(data.tag, 'phox-response')

        self.assertTrue('sessionid' in data.attrib)
        self.assertEqual(data.attrib['sessionid'], 'bar')

        self.assertTrue('buildnumber' in data.attrib)
        self.assertEqual(data.attrib['buildnumber'], 'baz')

    def test_stringify(self):
        self.assertEqual(
            str(messages.PhoxResponse()).replace(' />', '/>'),
            "<?xml version='1.0' encoding='%s'?>\n"
            '<!DOCTYPE phox-response SYSTEM "phox.dtd">\n'
            '<phox-response>'
            '<content><o/></content>'
            '</phox-response>' % xml.ENCODING
        )


if __name__ == '__main__':
    unittest.main()
