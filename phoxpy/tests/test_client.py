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


if __name__ == '__main__':
    unittest.main()
