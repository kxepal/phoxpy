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
from phoxpy.server import MockHttpSession, SimpleLISServer
from phoxpy.modules import options

class DirectoryTestCase(unittest.TestCase):

    def setUp(self):
        server = SimpleLISServer('4.2', '31415')
        server.ext_auth.add_license('foo-bar-baz')
        server.ext_auth.add_user('John', 'Doe')
        server.ext_opts.set('foo', 'bar')
        server.ext_opts.set('bar', 42)
        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        session.open('localhost', http_session=MockHttpSession(server))
        self.session = session
        self.server = server

    def test_load(self):
        data = options.load(self.session)
        self.assertTrue('foo' in data)
        self.assertEqual(data['foo'], 'bar')
        self.assertTrue('bar' in data)
        self.assertEqual(data['bar'], '42')
