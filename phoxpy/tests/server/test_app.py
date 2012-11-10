# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from . import PhoxpydTestCase
from phoxpy import exceptions
from phoxpy.messages import PhoxRequest
from phoxpy.xmlcodec import PhoxResponseCodec

class CommonTestCase(PhoxpydTestCase):

    def test_get_phox(self):
        rv = self.app.get('/phox')
        self.assertTrue('It works!' in rv.data)

    def test_require_payload(self):
        rv = self.app.post('/phox')
        self.assertEqual(rv.status_code, 400)

    def test_require_valid_xml(self):
        rv = self.app.post('/phox', data='foo')
        self.assertEqual(rv.status_code, 400)

    def test_require_message_type(self):
        rv = self.app.post('/phox', data='<phox-request />')
        self.assertEqual(rv.status_code, 400)

        rv = self.app.post('/phox',
                           data='<phox-request><content/></phox-request>')
        self.assertEqual(rv.status_code, 400)

    def test_not_allow_empty_type(self):
        rv = self.app.post('/phox',
                           data='<phox-request type=""><content/></phox-request>')
        self.assertEqual(rv.status_code, 400)

    def test_return_unknown_session_error_if_session_id_missed(self):
        rv = self.app.post('/phox', data=str(PhoxRequest(type='phox')))
        self.assertEqual(rv.status_code, 200)
        self.assertRaises(exceptions.NotAuthorized,
                          PhoxResponseCodec.to_python, rv.data)
