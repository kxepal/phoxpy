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


class SessionTestCase(unittest.TestCase):

    def setUp(self):
        self.server = SimpleLISServer('4.2', '31415')
        self.server.ext_auth.add_license('foo-bar-baz')
        self.server.ext_auth.add_user('John', 'Doe')

    def test_login(self):
        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        self.assertFalse(session.is_active())
        session.open('localhost', http_session=MockHttpSession(self.server))
        self.assertTrue(session.is_active())

    def test_logout(self):
        session = client.Session(login='John', password='Doe',
                                 client_id='foo-bar-baz')
        self.assertFalse(session.is_active())
        session.open('localhost', http_session=MockHttpSession(self.server))
        self.assertTrue(session.is_active())
        session.close()
        self.assertFalse(session.is_active())


if __name__ == '__main__':
    unittest.main()
