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
from phoxpy import xml


class XMLTestsMixIn(object):

    def test_create_element(self):
        elem = xml.Element('foo')
        self.assertTrue(hasattr(elem, 'tag'))
        self.assertEqual(elem.tag, 'foo')

    def test_create_element_with_attrs(self):
        elem = xml.Element('foo', bar='baz')
        self.assertTrue(hasattr(elem, 'attrib'))
        self.assertTrue('bar' in elem.attrib)
        self.assertEqual(elem.attrib['bar'], 'baz')

    def test_element_type(self):
        elem = xml.Element('foo')
        self.assertTrue(isinstance(elem, xml.ElementType))

    def test_create_element_tree(self):
        elem = xml.Element('foo')
        tree = xml.ElementTree(elem)
        self.assertEqual(tree.getroot(), elem)

    def test_element_tree_type(self):
        elem = xml.Element('foo')
        tree = xml.ElementTree(elem)
        self.assertTrue(isinstance(tree, xml.ElementTreeType))

    def test_dump_element(self):
        elem = xml.Element('foo', bar='baz')
        xmltext = xml.dump(elem)
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='%s'?>\n"
            '<foo bar="baz" />' % xml.ENCODING
        )

    def test_dump_element_with_custom_encoding(self):
        elem = xml.Element('foo')
        elem.append(xml.Element('bar'))
        elem.append(xml.Element('baz'))
        xmltext = xml.dump(elem, encoding='utf-8')
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='utf-8'?>\n"
            "<foo><bar /><baz /></foo>"
        )

    def test_dump_element_tree(self):
        elem = xml.Element('foo')
        elem.append(xml.Element('bar'))
        elem.append(xml.Element('baz'))
        xmltext = xml.dump(xml.ElementTree(elem), encoding='Windows-1251')
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='Windows-1251'?>\n"
            "<foo><bar /><baz /></foo>"
        )

    def test_dump_with_doctype(self):
        elem = xml.Element('foo')
        xmltext = xml.dump(elem, doctype=('request', 'SYSTEM', 'schema.dtd'))
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='%s'?>\n"
            '<!DOCTYPE request SYSTEM "schema.dtd">\n'
            "<foo />" % xml.ENCODING
        )

    def test_load(self):
        root = xml.load('<foo><bar/><baz></baz></foo>')
        self.assertTrue(isinstance(root, xml.ElementType))
        self.assertEqual(root.tag, 'foo')

    def test_load_with_xml_declaration(self):
        root = xml.load("<?xml version='1.0' encoding='utf-8'?>\n"
                        "<foo><bar/><baz/></foo>")
        self.assertTrue(isinstance(root, xml.ElementType))
        self.assertEqual(root.tag, 'foo')

    def test_load_with_doctype(self):
        root = xml.load("<?xml version='1.0' encoding='Windows-1251'?>\n"
                        '<!DOCTYPE request SYSTEM "schema.dtd">\n'
                        "<foo bar='baz'/>")
        self.assertTrue(isinstance(root, xml.ElementType))
        self.assertEqual(root.tag, 'foo')
        self.assertEqual(root.attrib['bar'], 'baz')

    def test_load_dump_load(self):
        root = xml.load(xml.dump(xml.load(
            "<?xml version='1.0' encoding='Windows-1251'?>\n"
            '<!DOCTYPE request SYSTEM "schema.dtd">\n'
            "<foo bar='baz'/>"),
            encoding='Windows-1251', doctype=('request', 'SYSTEM', 'schema.dtd')
        ))
        self.assertTrue(isinstance(root, xml.ElementType))
        self.assertEqual(root.tag, 'foo')
        self.assertEqual(root.attrib['bar'], 'baz')

    def test_parse(self):
        fobj = StringIO('''<?xml version='1.0' encoding='utf-8'?>
            <foo><bar />something<baz><!--comment--><boo>42</boo></baz></foo>
        ''')
        stream = xml.parse(fobj)
        expected_output = [
            ('start', 'foo'),
            ('start', 'bar'),
            ('end', 'bar'),
            ('start', 'baz'),
            ('start', 'boo'),
            ('end', 'boo'),
            ('end', 'baz'),
            ('end', 'foo'),
        ]
        for idx, item in enumerate(stream):
            event, elem = item
            tagname = elem.tag
            self.assertEqual(expected_output[idx], (event, tagname))
        

class CElementTreeTestCase(unittest.TestCase, XMLTestsMixIn):

    def setUp(self):
        xml.use('cElementTree')


class ElementTreeTestCase(unittest.TestCase, XMLTestsMixIn):

    def setUp(self):
        xml.use('elementtree.ElementTree')

class StdlibCElementTreeTestCase(unittest.TestCase, XMLTestsMixIn):

    def setUp(self):
        xml.use('xml.etree.cElementTree')


class StdlibElementTreeTestCase(unittest.TestCase, XMLTestsMixIn):

    def setUp(self):
        xml.use('xml.etree.ElementTree')


class LxmlTestCase(unittest.TestCase, XMLTestsMixIn):

    def setUp(self):
        xml.use('lxml.etree')

    def test_dump_element(self):
        elem = xml.Element('foo', bar='baz')
        xmltext = xml.dump(elem)
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='%s'?>\n"
            '<foo bar="baz"/>' % xml.ENCODING
        )

    def test_dump_element_with_custom_encoding(self):
        elem = xml.Element('foo')
        elem.append(xml.Element('bar'))
        elem.append(xml.Element('baz'))
        xmltext = xml.dump(elem, encoding='utf-8')
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='utf-8'?>\n"
            "<foo><bar/><baz/></foo>"
        )

    def test_dump_element_tree(self):
        elem = xml.Element('foo')
        elem.append(xml.Element('bar'))
        elem.append(xml.Element('baz'))
        xmltext = xml.dump(xml.ElementTree(elem), encoding='utf-8')
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='utf-8'?>\n"
            "<foo><bar/><baz/></foo>"
        )

    def test_dump_with_doctype(self):
        elem = xml.Element('foo')
        xmltext = xml.dump(elem, doctype=('request', 'SYSTEM', 'schema.dtd'))
        self.assertEqual(
            xmltext,
            "<?xml version='1.0' encoding='%s'?>\n"
            '<!DOCTYPE request SYSTEM "schema.dtd">\n'
            "<foo/>" % xml.ENCODING
        )


if __name__ == '__main__':
    unittest.main()
