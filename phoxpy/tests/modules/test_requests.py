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
from phoxpy.modules import requests

class RequestsTestCase(unittest.TestCase):

    def setUp(self):
        server = SimpleLISServer('4.2', '31415')
        server.ext_auth.add_license('foo-bar-baz')
        server.ext_auth.add_user('John', 'Doe')
        server.ext_reqs.set({'id': 'foo', 'data': 1})
        server.ext_reqs.set({'id': 'bar', 'data': 2})

        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        session.open('localhost', http_session=MockHttpSession(server))
        self.session = session
        self.server = server

    def test_load(self):
        req = requests.load(self.session, 'foo')
        self.assertEqual(req['data'], 1)

    def test_load_shares_no_header_info(self):
        req = requests.load(self.session, 'foo')
        self.assertTrue('sessionid' not in req)
        self.assertTrue('buildnumber' not in req)

    def test_select_all(self):
        items = requests.select(self.session)
        self.assertEqual(
            sorted(list(self.server.ext_reqs.db.values())),
            sorted(list(items))
        )

    def test_changes(self):
        items = requests.changes(self.session, 123)
        self.assertTrue(isinstance(items, types.GeneratorType))
        foo = items.next()
        self.assertEqual('foo', foo['id'])
        self.assertEqual('bar', items.next()['id'])
        self.server.ext_reqs.set({'id': 'bar', 'data': 5}, 10)
        self.server.ext_reqs.set({'id': 'foo', 'data': 4}, 9999999999L)
        foo_new = items.next()
        self.assertEqual('foo', foo_new['id'])

if __name__ == '__main__':
    unittest.main()
