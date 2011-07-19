# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
from phoxpy import messages
from phoxpy import xml

class PhoxMessageTestCase(unittest.TestCase):

    def test_abstract_string_serialization(self):
        self.assertRaises(NotImplementedError, str, messages.PhoxMessage())


class PhoxRequestTestCase(unittest.TestCase):

    def test_set_type(self):
        msg = messages.PhoxRequest('foo')
        self.assertEqual(msg.type, 'foo')

    def test_is_phoxmsg_instance(self):
        msg = messages.PhoxRequest('foo')
        self.assertTrue(isinstance(msg, messages.PhoxMessage))

    def test_session_id(self):
        msg = messages.PhoxRequest('foo', sessionid='bar')
        self.assertEqual(msg.sessionid, 'bar')

    def test_read_only_session_id(self):
        msg = messages.PhoxRequest('foo', sessionid='bar')
        self.assertRaises(AttributeError, setattr, msg, 'sessionid', 'baz')

    def test_buildnumber(self):
        msg = messages.PhoxRequest('foo', buildnumber='bar')
        self.assertEqual(msg.buildnumber, 'bar')

    def test_read_only_buildnumber(self):
        msg = messages.PhoxRequest('foo', buildnumber='bar')
        self.assertRaises(AttributeError, setattr, msg, 'buildnumber', 'baz')

    def test_version(self):
        msg = messages.PhoxRequest('foo', version='bar')
        self.assertEqual(msg.version, 'bar')

    def test_read_only_version(self):
        msg = messages.PhoxRequest('foo', version='bar')
        self.assertRaises(AttributeError, setattr, msg, 'version', 'baz')

    def test_unwrap(self):
        msg = messages.PhoxRequest('foo', sessionid='bar',
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
            str(messages.PhoxRequest('foo')),
            "<?xml version='1.0' encoding='%s'?>\n"
            '<!DOCTYPE phox-request SYSTEM "phox.dtd">\n'
            '<phox-request type="foo">'
            '<content />'
            '</phox-request>' % xml.ENCODING
        )


class PhoxResponseTestCase(unittest.TestCase):

    def test_is_phoxmsg_instance(self):
        msg = messages.PhoxResponse()
        self.assertTrue(isinstance(msg, messages.PhoxMessage))

    def test_session_id(self):
        msg = messages.PhoxResponse(sessionid='bar')
        self.assertEqual(msg.sessionid, 'bar')

    def test_read_only_session_id(self):
        msg = messages.PhoxResponse(sessionid='bar')
        self.assertRaises(AttributeError, setattr, msg, 'sessionid', 'baz')

    def test_buildnumber(self):
        msg = messages.PhoxResponse(buildnumber='bar')
        self.assertEqual(msg.buildnumber, 'bar')

    def test_read_only_buildnumber(self):
        msg = messages.PhoxResponse(buildnumber='bar')
        self.assertRaises(AttributeError, setattr, msg, 'buildnumber', 'baz')

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
            str(messages.PhoxResponse()),
            "<?xml version='1.0' encoding='%s'?>\n"
            '<!DOCTYPE phox-response SYSTEM "phox.dtd">\n'
            '<phox-response>'
            '<content />'
            '</phox-response>' % xml.ENCODING
        )


if __name__ == '__main__':
    unittest.main()
