# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
from phoxpy import client
from phoxpy.tests.lisserver import MockHttpSession

class SessionTestCase(unittest.TestCase):

    def setUp(self):
        self.session = MockHttpSession()

    def test_login(self):
        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        self.assertFalse(session.is_active())
        session.open('localhost', http_session=MockHttpSession())
        self.assertTrue(session.is_active())

    def test_logout(self):
        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        self.assertFalse(session.is_active())
        session.open('localhost', http_session=MockHttpSession())
        self.assertTrue(session.is_active())
        session.close()
        self.assertFalse(session.is_active())


class ServerTestCase(unittest.TestCase):

    def setUp(self):
        self.session = client.Session(login='John', password='Doe',
                                      client_id='foo-bar-baz')
        self.session.open('localhost', http_session=MockHttpSession())

    def test_getitem(self):
        server = client.Server()
        server.update(self.session)
        collection = server['foo']
        self.assertTrue(collection, client.Collection)
        self.assertEqual(collection.version, 0)

    def test_contains(self):
        server = client.Server()
        server.update(self.session)
        self.assertTrue('foo' in server)
        collection = server['foo']
        self.assertTrue(collection in server)

    def test_iter(self):
        server = client.Server()
        server.update(self.session)
        self.assertEqual(
            sorted(server),
            sorted(['foo', 'bar', 'baz'])
        )

    def test_items(self):
        server = client.Server()
        server.update(self.session)
        self.assertEqual(
            sorted(server.items()),
            sorted(zip(server.keys(), server.values()))
        )

    def test_update(self):
        server = client.Server()
        server.update(self.session)
        self.assertEqual(
            sorted(server.keys()),
            sorted(['foo', 'bar', 'baz'])
        )
        self.assertTrue(
            isinstance(server.values().next(), client.Collection)
        )
        self.assertEqual(
            sorted(map(lambda c: c.version, server.values())),
            sorted([0, 1, 2])

        )


if __name__ == '__main__':
    unittest.main()
