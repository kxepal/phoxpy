# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from cStringIO import StringIO
from phoxpy import xml
from phoxpy import messages

class MockHttpSession(object):

    def request(self, method, url, body=None, headers=None, credentials=None,
                _num_redirects=0):
        return 200, {}, StringIO(str(LisServer.dispatch(body)))

class LisServer(object):

    def dispatch(self, xmlsrc):
        request = xml.load(xmlsrc)
        return getattr(self, request.attrib['type'].replace('-', '_'))(request)

    def login(self, request):
        return messages.AuthResponse(sessionid='12345', buildnumber='54321')

    def logout(self, request):
        return messages.PhoxResponse(
            buildnumber=request.attrib['buildnumber'],
            sessionid=request.attrib['sessionid']
        )

LisServer = LisServer()
