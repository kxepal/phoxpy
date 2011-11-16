# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from random import randint
from phoxpy import xml
from phoxpy import messages
from phoxpy import exceptions
from phoxpy.messages import directory
from phoxpy.server.main import ServerExtension, request_type

__all__ = ['DirectoryExt', 'DirectoryItem']

class DirectoryItem(object):

    def __init__(self, name, *items):
        db = self._db = {}
        db['name'] = name
        db['version'] = 0
        db['items'] = {}
        for item in items:
            self.update(item)

    def __getitem__(self, item):
        return self.db['items'][item]

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, item):
        return item in self.db['items']

    def keys(self):
        return self.db['items'].keys()

    def values(self):
        return self.db['items'].values()

    def items(self):
        return self.db['items'].items()

    def get(self, id_or_item):
        if isinstance(id_or_item, dict):
            idx = id_or_item['id']
        else:
            idx = id_or_item
        return self.db['items'][idx]

    def set(self, item):
        assert isinstance(item, dict)
        if 'id' not in item:
            item['id'] = str(randint(1, 10000))
        self.db['items'][item['id']] = item
        self.db['version'] += 1
        return item['id'], self.version

    def update(self, idx, **values):
        item = self.get(idx)
        item.update(values)
        return self.set(item)

    @property
    def db(self):
        return self._db

    @property
    def name(self):
        return self._db['name']

    @property
    def version(self):
        return self._db['version']


class DirectoryExt(ServerExtension):

    def __getitem__(self, item):
        return self.db[item]

    def __iter__(self):
        return iter(self.db)

    def add(self, name, *items):
        assert name not in self.db
        self.db[name] = DirectoryItem(name)
        return self.update(name, *items)

    def get(self, name):
        if name not in self.db:
            raise exceptions.LisBaseException(name)
        return self.db[name]

    def items(self):
        return self.db.items()

    def update(self, name, *items):
        dirdb = self.get(name)
        for item in items:
            dirdb.set(item)

    @request_type(directory.DirectoryVersions)
    def handle_directory_versions(self, request):
        return messages.PhoxResponse(
            sessionid=request.sessionid,
            versions=[
                {'name': key, 'version': dirdb.version}
                for key, dirdb in self.items()
            ]
        )

    @request_type(directory.DirectoryLoad)
    def handle_directory(self, request):
        ids = request.get('elements', [])

        dirdb = self.get(request.name)

        if ids:
            items = [dirdb.get(idx) for idx in ids if idx in dirdb]
        else:
            items = dirdb.values()
        data = {
            'version': dirdb.version,
            dirdb.name: items
        }

        return messages.PhoxResponse(
            sessionid = request.sessionid,
            buildnumber = request.buildnumber,
            **data
        )

    def _directory_save(self, request):
        item = request.element.unwrap()
        dirdb = self.get(request.directory)
        idx, version = dirdb.set(item)

        return messages.PhoxResponse(
            sessionid=request.sessionid,
            buildnumber=request.buildnumber,
            id=idx,
            version=version
        )

    @request_type(directory.DirectorySave)
    def handle_directory_save(self, request):
        return self._directory_save(request)

    @request_type(directory.DirectorySaveNew)
    def handle_directory_save_new(self, request):
        return self._directory_save(request)

    @request_type(directory.DirectoryRemove)
    def handle_directory_remove(self, request):
        dirdb = self.get(request.directory)
        version = dirdb.version
        for idx in request.ids:
            _, version = dirdb.update(idx, removed=True)
        # we have to return this one
        root = xml.Element('phox-response', sessionid=request['sessionid'])
        content = xml.Element('content')
        content.append(xml.Element('f', t='S', v=str(version)))
        root.append(content)
        return xml.dump(root)

    @request_type(directory.DirectoryRemoveNew)
    def handle_directory_remove_new(self, request):
        dirdb = self.get(request.directory)
        version = dirdb.version
        for idx in request['ids']:
            _, version = dirdb.update(idx, removed=True)
        return messages.PhoxResponse(version=version)

    @request_type(directory.DirectoryRestore)
    def handle_directory_restore(self, request):
        dirdb = self.get(request.directory)
        version = dirdb.version
        for idx in request['ids']:
            _, version = dirdb.update(idx, removed=False)
        return messages.PhoxResponse(version=version)
