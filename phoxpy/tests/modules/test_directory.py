# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import types
import unittest
from phoxpy import client
from phoxpy.tests.lisserver import MockHttpSession, LisServer
from phoxpy.modules import directory

class DirectoryTestCase(unittest.TestCase):

    def setUp(self):
        server = LisServer()
        data = [{'id': '123', 'foo': 'bar'}, {'id': '456', 'foo': 'baz'},
                {'id': '789', 'foo': 'zoo'}, {'id': '42', 'foo': 'answer!'}]
        for item in data:
            server.db[item['id']] = item
        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        session.open('localhost', http_session=MockHttpSession(server))
        self.session = session
        self.server = server

    def test_list(self):
        items = directory.items(self.session)
        self.assertTrue(isinstance(items, types.GeneratorType))
        items = list(items)
        items_should_be = [('foo', '0'), ('bar', '1'), ('baz', '2')]
        self.assertEqual(sorted(items), sorted(items_should_be))

    def test_load_returns_generator(self):
        items = directory.load(self.session, 'foo')
        self.assertTrue(isinstance(items, types.GeneratorType))

    def test_load_all(self):
        items = list(directory.load(self.session, 'foo'))
        self.assertEqual(sorted(items), sorted(self.server.db.values()))

    def test_load_by_id(self):
        items = directory.load(self.session, 'foo', '456')
        self.assertEqual(items.next(), self.server.db['456'])
        try:
            item = items.next()
        except StopIteration:
            pass
        else:
            self.fail('Unexpectable item %r' % item)

    def test_load_by_ids(self):
        items = list(directory.load(self.session, 'foo', ['456', '42']))
        data = [self.server.db['456'], self.server.db['42']]
        self.assertEqual(sorted(data), sorted(items))

    def test_load_by_item(self):
        items = directory.load(self.session, 'foo', {'id': '42'})
        self.assertEqual(items.next(), self.server.db['42'])
        try:
            item = items.next()
        except StopIteration:
            pass
        else:
            self.fail('Unexpectable item %r' % item)

    def test_store(self):
        item = self.server.db['42']
        self.assertTrue('source' not in item)
        item['source'] = 'universe'
        id, version = directory.store(self.session, 'foo', item)
        self.assertEqual(id, item['id'])
        self.assertEqual(item, self.server.db['42'])

    def test_store_new(self):
        item = self.server.db['42']
        self.assertTrue('source' not in item)
        item['source'] = 'universe'
        id, version = directory.store(self.session, 'employee', item)
        self.assertEqual(id, item['id'])
        self.assertEqual(item, self.server.db['42'])

    def test_remove_by_id(self):
        version = directory.remove(self.session, 'foo', '42')
        self.assertTrue('42' in self.server.db)
        self.assertTrue('removed' in self.server.db['42'])
        self.assertTrue(self.server.db['42']['removed'])

    def test_remove_by_ids(self):
        version = directory.remove(self.session, 'foo', ['123', '456'])
        self.assertTrue(self.server.db['123']['removed'])
        self.assertTrue(self.server.db['456']['removed'])

    def test_remove_by_item(self):
        version = directory.remove(self.session, 'foo', {'id': '42', 'foo': 'bar'})
        self.assertTrue(self.server.db['42']['removed'])

    def test_remove_new(self):
        version = directory.remove(self.session, 'employee', '42')
        self.assertTrue(self.server.db['42']['removed'])

    def test_restore(self):
        self.assertTrue(not self.server.db['42'].get('removed', False))
        self.server.db['42']['removed'] = True
        assert directory.restore(self.session, 'foo', '42')

if __name__ == '__main__':
    unittest.main()
