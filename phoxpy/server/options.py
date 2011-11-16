# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.messages import PhoxResponse
from phoxpy.messages import options
from phoxpy.server.main import ServerExtension, request_type

__all__ = ['OptionsExt']

class OptionsExt(ServerExtension):

    def set(self, key, value):
        self.db[key] = str(value)

    def remove(self, key):
        del self.db[key]

    @request_type(options.OptionsGet)
    def handle_options_get(self, request):
        data = {'': [{'code': key, 'value': value}
                     for key, value in self.db.items()]}
        return PhoxResponse(
            sessionid=request.sessionid,
            **data
        )
