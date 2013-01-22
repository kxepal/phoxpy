# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import inspect
from phoxpy import exceptions
from phoxpy import xml


def request_type(message):
    def decorator(func, _message=message):
        def wrapper(self, xmlsrc):
            return func(self, _message.to_python(xmlsrc))
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper._is_handler = True
        return wrapper
    return decorator

class ServerExtension(object):

    _version = '0.0'
    _buildnumber = '00000'

    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db

    @property
    def build_number(self):
        return self._buildnumber

    @property
    def server_version(self):
        return self._version


class BaseLisServer(object):

    def __init__(self, version, buildnumber):
        self._db = {}
        self._handlers = {}
        self._version = version
        self._buildnumber = buildnumber
        ServerExtension._version = version
        ServerExtension._buildnumber = buildnumber

    @property
    def db(self):
        return self._db

    def dispatch(self, xmlstr):
        root = xml.load(xmlstr)
        assert 'type' in root.attrib
        request_type = root.attrib['type'].replace('-', '_')
        handler = 'handle_' + request_type
        if handler not in self._handlers:
            raise exceptions.NoProcessorError(handler)
        return self._handlers[handler](root)

    @property
    def build_number(self):
        return self._buildnumber

    @property
    def server_version(self):
        return self._version

    def extend(self, namespace, extension):
        dbleaf = self.db[namespace] = {}
        instance = extension(dbleaf)
        setattr(self, 'ext_' + namespace, instance)
        for name, member in inspect.getmembers(instance):
            if not name.startswith('handle_'):
                continue
            if not hasattr(member, '_is_handler'):
                return
            self._handlers[name] = member


