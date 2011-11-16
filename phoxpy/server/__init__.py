# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from cStringIO import StringIO
from phoxpy.server.auth import AuthExt
from phoxpy.server.directory import DirectoryExt
from phoxpy.server.options import OptionsExt
from phoxpy.server.main import BaseLisServer

class MockHttpSession(object):

    def __init__(self, server=None):
        self.server = server or SimpleLISServer('0.0', '00000')

    def request(self, method, url, body=None, headers=None, credentials=None,
                _num_redirects=0):
        return 200, {}, StringIO(str(self.server.dispatch(body)))


class SimpleLISServer(BaseLisServer):
    """Simple mock LIS server."""
    def __init__(self, *args, **kwargs):
        super(SimpleLISServer, self).__init__(*args, **kwargs)
        self.extend('auth', AuthExt)
        self.extend('dirs', DirectoryExt)
        self.extend('opts', OptionsExt)
