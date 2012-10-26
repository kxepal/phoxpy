# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
from phoxpy.messages import PhoxRequest
import phoxpy.server.app as phoxpyd

class PhoxpydTestCase(unittest.TestCase):

    def setUp(self):
        phoxpyd.app.config['TESTING'] = True
        self.app = phoxpyd.app.test_client()

    def test_get_phox(self):
        rv = self.app.get('/phox')
        self.assertTrue('It works!' in rv.data)

    def test_require_payload(self):
        rv = self.app.post('/phox')
        self.assertEqual(rv.status_code, 400)

    def test_require_valid_xml(self):
        rv = self.app.post('/phox', data='foo')
        self.assertEqual(rv.status_code, 500)

    def test_require_message_type(self):
        rv = self.app.post('/phox', data='<phox-request />')
        self.assertEqual(rv.status_code, 500)

        rv = self.app.post('/phox',
                           data='<phox-request><content/></phox-request>')
        self.assertEqual(rv.status_code, 500)

    def test_not_allow_empty_type(self):
        rv = self.app.post('/phox',
                           data='<phox-request type=""><content/></phox-request>')
        self.assertEqual(rv.status_code, 400)

    def test_fail_on_unknown_type(self):
        rv = self.app.post('/phox', data=str(PhoxRequest(type='fooo')))
        self.assertEqual(rv.status_code, 400)

    def test_pass_phox_type(self):
        rv = self.app.post('/phox', data=str(PhoxRequest(type='phox')))
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('It works!' in rv.data)


if __name__ == '__main__':
    unittest.main()
