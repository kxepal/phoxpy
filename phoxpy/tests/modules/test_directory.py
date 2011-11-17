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
from phoxpy.server import MockHttpSession, SimpleLISServer
from phoxpy.modules import directory

class DirectoryTestCase(unittest.TestCase):

    def setUp(self):
        server = SimpleLISServer('4.2', '31415')
        server.ext_auth.add_license('foo-bar-baz')
        server.ext_auth.add_user('John', 'Doe')
        server.ext_dirs.add('foo',
            {'foo': 'bar'}, {'foo': 'baz'}, {'foo': 'zoo'},
            {'id': '42', 'foo': 'answer!'}, {'id': '3.14', 'foo': 'oof'}
        )
        server.ext_dirs.add('abc',
            {'id': '1', 'foo': 'a'}, {'id': '2', 'foo': 'b'},
            {'id': '3', 'foo': 'c'},
        )
        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        session.open('localhost', http_session=MockHttpSession(server))
        self.session = session
        self.server = server
        self.db = server.ext_dirs

    def test_list(self):
        items = directory.items(self.session)
        self.assertTrue(isinstance(items, types.GeneratorType))
        items = list(items)
        items_should_be = [('foo', 5), ('abc', 3)]
        self.assertEqual(sorted(items), sorted(items_should_be))

    def test_load_returns_generator(self):
        items = directory.load(self.session, 'foo')
        self.assertTrue(isinstance(items, types.GeneratorType))

    def test_load_all(self):
        items = list(directory.load(self.session, 'foo'))
        self.assertEqual(
            sorted(items),
            sorted(self.db['foo'].values())
        )

    def test_load_by_id(self):
        items = directory.load(self.session, 'foo', '42')
        self.assertEqual(items.next(), self.db['foo']['42'])
        try:
            item = items.next()
        except StopIteration:
            pass
        else:
            self.fail('Unexpectable item %r' % item)

    def test_load_by_ids(self):
        items = list(directory.load(self.session, 'foo', ['42', '3.14']))
        data = [self.db['foo']['42'], self.db['foo']['3.14']]
        self.assertEqual(sorted(data), sorted(items))

    def test_load_by_item(self):
        items = directory.load(self.session, 'foo', {'id': '42'})
        self.assertEqual(items.next(), self.db['foo']['42'])
        try:
            item = items.next()
        except StopIteration:
            pass
        else:
            self.fail('Unexpectable item %r' % item)

    def test_load_not_removed(self):
        self.db['foo']['42']['removed'] = True
        items = list(directory.load(self.session, 'foo', ['42', '3.14']))
        self.assertEqual(items, [self.db['foo']['3.14']])

    def test_load_removed(self):
        self.db['foo']['42']['removed'] = True
        items = directory.load(self.session, 'foo', ['42', '3.14'], removed=True)
        data = [self.db['foo']['42'], self.db['foo']['3.14']]
        self.assertEqual(sorted(items), sorted(data))

    def test_store(self):
        item = self.db['foo']['42']
        self.assertTrue('source' not in item)
        item['source'] = 'universe'
        id, version = directory.store(self.session, 'foo', item)
        self.assertEqual(id, item['id'])
        self.assertEqual(item, self.db['foo']['42'])

    def test_store_new(self):
        self.db.add('employee', {'id': '42'})
        item = self.db['employee']['42']
        self.assertTrue('source' not in item)
        item['source'] = 'universe'
        id, version = directory.store(self.session, 'employee', item)
        self.assertEqual(id, item['id'])
        self.assertEqual(item, self.db['employee']['42'])

    def test_remove_by_id(self):
        old_version = self.db['foo'].version
        version = directory.remove(self.session, 'foo', '42')
        self.assertTrue('42' in self.db['foo'])
        self.assertTrue('removed' in self.db['foo']['42'])
        self.assertTrue(self.db['foo']['42']['removed'])
        self.assertEqual(version, self.db['foo'].version)
        self.assertEqual(old_version + 1, version)

    def test_remove_by_ids(self):
        old_version = self.db['foo'].version
        version = directory.remove(self.session, 'foo', ['42', '3.14'])
        self.assertTrue(self.db['foo']['42']['removed'])
        self.assertTrue(self.db['foo']['3.14']['removed'])
        self.assertEqual(version, self.db['foo'].version)
        self.assertEqual(old_version + 2, version)

    def test_remove_by_item(self):
        directory.remove(self.session, 'foo', {'id': '42', 'foo': 'bar'})
        self.assertTrue(self.db['foo']['42']['removed'])

    def test_remove_new(self):
        self.db.add('employee', {'id': '42'})
        directory.remove(self.session, 'employee', '42')
        self.assertTrue(self.db['employee']['42']['removed'])

    def test_restore(self):
        self.assertTrue(not self.db['foo']['42'].get('removed', False))
        self.db['foo']['42']['removed'] = True
        assert directory.restore(self.session, 'foo', '42')
        self.assertTrue(not self.db['foo']['42'].get('removed', False))

    def test_changes(self):
        feed = directory.changes(self.session)
        self.assertTrue(isinstance(feed, types.GeneratorType))
        data = [feed.next(), feed.next()]
        self.assertEqual(sorted([('foo', 5), ('abc', 3)]), sorted(data))
        self.db['abc'].set({'foo': 'bar'})
        self.assertEqual(('abc', 4), feed.next())

    def test_specific_changes(self):
        feed = directory.changes(self.session, init_versions={'foo': 2})
        self.assertEqual(('foo', 5), feed.next())

if __name__ == '__main__':
    unittest.main()
