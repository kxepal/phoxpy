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
from phoxpy import mapping

class MockHttpSession(object):

    def request(self, method, url, body=None, headers=None, credentials=None,
                _num_redirects=0):
        return 200, {}, StringIO(str(LisServer.dispatch(body)))


class LisServer(object):

    def dispatch(self, xmlsrc):
        request = messages.PhoxRequest.wrap(xml.load(xmlsrc))
        return getattr(self, request.type.replace('-', '_'))(request)

    def login(self, request):
        return messages.AuthResponse(sessionid='12345', buildnumber='54321')

    def logout(self, request):
        return messages.PhoxResponse(
            buildnumber=request.buildnumber,
            sessionid=request.sessionid
        )

    def directory_versions(self, request):
        class DirectoryList(messages.PhoxResponse):
            versions = mapping.ListField(
                mapping.ObjectField({
                    'name': mapping.TextField(),
                    'version': mapping.TextField()
                })
            )
        return DirectoryList(
            sessionid = request.sessionid,
            versions = [{'name': 'foo', 'version': '0'},
                        {'name': 'bar', 'version': '1'},
                        {'name': 'baz', 'version': '2'},]
        )

LisServer = LisServer()
'''
implement Server and Collection classes.

Server class would operate directly with LIS server to request or
retrieve data by custom complex queries. Current implementation adds
support of retrieving information about available collections and
their versions.

Collection class would operate with cached data providing single API
to access them and store them within different backend databases.
Currently this feature not implemented, but CouchDB and SQLite support
will be out of the box.
'''
