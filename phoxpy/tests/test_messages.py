# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
from StringIO import StringIO
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

    def test_to_xml_default_tag(self):
        class Post(messages.Message):
            ids = mapping.ListField(mapping.RefField())
        root = Post(ids=['1', '2', '3']).to_xml()
        self.assertEqual(root.tag, 'content')


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

    def test_to_python_should_containt_attrib_type(self):
        root = xml.Element('phox-request')
        root.append(xml.Element('content'))
        self.assertRaises(AssertionError, messages.PhoxRequest.to_python, root)

    def test_to_python(self):
        root = xml.Element('phox-request')
        root.attrib['type'] = 'foo'
        root.append(xml.Element('content'))
        req = xml.decode(root)
        self.assertEqual(req.type, 'foo')

    def test_to_python_stream(self):
        stream = xml.parse(StringIO('''<phox-request type="foo">
        <content><f n="bar" t="S" v="baz" /></content>
        </phox-request>'''))
        req = xml.decode(stream)
        self.assertEqual(req.type, 'foo')
        self.assertEqual(req['bar'], 'baz')

    def test_to_python_new_request_format(self):
        stream = xml.parse(StringIO('''<phox-request type="foo">
        <content><o><f n="bar" t="S" v="baz" /></o></content>
        </phox-request>'''))
        req = xml.decode(stream)
        self.assertEqual(req.type, 'foo')
        self.assertEqual(req['bar'], 'baz')

    def test_to_xml(self):
        msg = messages.PhoxRequest(type='foo', sessionid='bar',
                                   version='baz', buildnumber='zoo')
        data = msg.to_xml()
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

    def test_to_xml(self):
        msg = messages.PhoxResponse(sessionid='bar',  buildnumber='baz')
        data = msg.to_xml()
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
            '<content/>'
            '</phox-response>' % xml.ENCODING
        )

    def test_to_python_stream(self):
        stream = xml.parse(StringIO("<?xml version='1.0' encoding='utf-8'?>\n"
            '<!DOCTYPE phox-response SYSTEM "phox.dtd">\n'
            '<phox-response>'
            '<content><o n=""><s n="fbb">'
            '<f n="foo" v="foo" t="S"/>'
            '<f n="bar" v="bar" t="S"/>'
            '<f n="baz" v="baz" t="S"/>'
            '</s></o></content>'
            '</phox-response>'))
        msg = xml.decode(stream)
        self.assertEqual(sorted(['foo', 'bar', 'baz']), sorted(msg['fbb']))

    def test_to_python_with_named_o_tag(self):
        stream = xml.parse(StringIO("<?xml version='1.0' encoding='utf-8'?>\n"
            '<!DOCTYPE phox-response SYSTEM "phox.dtd">\n'
            '<phox-response>'
            '<content><o n=""><s n="fbb">'
            '<f n="foo" v="foo" t="S"/>'
            '<f n="bar" v="bar" t="S"/>'
            '<f n="baz" v="baz" t="S"/>'
            '</s></o></content>'
            '</phox-response>'))
        msg = xml.decode(stream)
        print msg
        self.assertEqual(sorted(['foo', 'bar', 'baz']), sorted(msg['fbb']))


class PhoxEventTestCase(unittest.TestCase):

    def test_to_xml(self):
        msg = messages.PhoxEvent(system='foo',  type='baz')
        data = msg.to_xml()
        self.assertEqual(data.tag, 'phox-event')

        self.assertTrue('system' in data.attrib)
        self.assertEqual(data.attrib['system'], 'foo')

        self.assertTrue('type' in data.attrib)
        self.assertEqual(data.attrib['type'], 'baz')

    def test_stringify(self):
        self.assertEqual(
            str(messages.PhoxEvent(type='foo', ids=[])).replace(' />', '/>'),
            "<?xml version='1.0' encoding='%s'?>\n"
            '<!DOCTYPE phox-event SYSTEM "phox.dtd">\n'
            '<phox-event type="foo">'
            '<content><o><s n="ids"/></o></content>'
            '</phox-event>' % xml.ENCODING
        )

if __name__ == '__main__':
    unittest.main()
