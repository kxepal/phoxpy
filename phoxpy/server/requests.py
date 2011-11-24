# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import time
from random import randint
from phoxpy.messages import PhoxResponse
from phoxpy.messages import requests
from phoxpy.messages import journal
from phoxpy.server.main import ServerExtension, request_type

__all__ = ['RequestsExt']

class RequestsExt(ServerExtension):

    def set(self, item, timestamp=None):
        assert isinstance(item, dict)
        if 'id' not in item:
            item['id'] = str(randint(1, 10000))
        item['timestamp'] = timestamp or int(time.time())
        self.db[item['id']] = item

    @request_type(requests.RequestInfo)
    def handle_request_info(self, request):
        return PhoxResponse(**self.db.get(request['request'], {}))

    @request_type(journal.RegistrationJournalRequest)
    def handle_registration_journal(self, request):
        data = []
        for item in self.db.values():
            emit = True
            if request.filter.last_timestamp:
                if request.filter.last_timestamp > item['timestamp']:
                    emit = False
            if emit:
                data.append(item)
        return PhoxResponse(Request=data)

