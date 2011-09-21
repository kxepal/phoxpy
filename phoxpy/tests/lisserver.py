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
from phoxpy import mapping
from phoxpy import messages
from phoxpy.modules import directory

class MockHttpSession(object):

    def __init__(self, server=None):
        self.server = server or LisServer()

    def request(self, method, url, body=None, headers=None, credentials=None,
                _num_redirects=0):
        return 200, {}, StringIO(str(self.server.dispatch(body)))


class LisServer(object):

    def __init__(self, db=None):
        if db is None:
            db = {}
        self._db = db

    @property
    def db(self):
        return self._db

    def dispatch(self, xmlstr):
        root = xml.load(xmlstr)
        request_type = root.attrib['type'].replace('-', '_')
        return getattr(self, request_type)(root)

    def login(self, request):
        return messages.auth.AuthResponse(
            sessionid='12345', buildnumber='54321'
        )

    def logout(self, request):
        request = messages.PhoxRequest.wrap(request)
        return messages.PhoxResponse(
            buildnumber=request.buildnumber,
            sessionid=request.sessionid
        )

    def directory(self, request):
        request = directory.DirectoryLoad.wrap(request)
        elements = request.get('elements', [])
        data = {
            'sessionid': request.sessionid,
            'version': 0,
            request['name']: [
                self.db[item] for item in request['elements'] if item in self.db
            ] if elements else self.db.values()
        }
        return messages.PhoxResponse(**data)

    def _directory_save(self, request):
        data = {
            'sessionid': request.sessionid,
            'version': 0,
            'id': request['element']['id']
        }
        self.db[int(request['element']['id'])] = dict(request['element'].items())
        return messages.PhoxResponse(**data)

    def directory_save(self, request):
        request = directory.DirectorySave.wrap(request)
        return self._directory_save(request)

    def directory_save_new(self, request):
        request = directory.DirectorySaveNew.wrap(request)
        return self._directory_save(request)

    def directory_remove(self, request):
        request = directory.DirectoryRemove.wrap(request)
        for idx in request['ids']:
            self.db[idx]['removed'] = True
        # we have to return this one
        root = xml.Element('phox-response', sessionid=request['sessionid'])
        content = xml.Element('content')
        content.append(xml.Element('f', t='S', v='1'))
        root.append(content)
        return xml.dump(root)

    def directory_remove_new(self, request):
        request = directory.DirectoryRemoveNew.wrap(request)
        for idx in request['ids']:
            self.db[idx]['removed'] = True
        return messages.PhoxResponse(version='1')

    def directory_restore(self, request):
        request = directory.DirectoryRestore.wrap(request)
        for idx in request['ids']:
            self.db[idx]['removed'] = False
        return messages.PhoxResponse(version='1')

    def directory_versions(self, request):
        request = messages.PhoxRequest.wrap(request)
        class DirectoryList(messages.PhoxResponse):
            versions = mapping.ListField(
                mapping.ObjectField({
                    'name': mapping.TextField(),
                    'version': mapping.TextField()
                })
            )
        return DirectoryList(
            sessionid = request['sessionid'],
            versions = [{'name': 'foo', 'version': '0'},
                        {'name': 'bar', 'version': '1'},
                        {'name': 'baz', 'version': '2'},]
        )
