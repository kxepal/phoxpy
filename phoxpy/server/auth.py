# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import hashlib
from random import randint
from phoxpy import exceptions
from phoxpy.messages import PhoxRequest, PhoxResponse
from phoxpy.messages import auth
from phoxpy.server.main import ServerExtension, request_type

__all__ = ['AuthExt']

md5 = lambda s: hashlib.md5(s).hexdigest()

class AuthExt(ServerExtension):

    def __init__(self, db):
        db.update({
            'licenses': set([]),
            'users': {},
            'sessions': set([])
        })
        super(AuthExt, self).__init__(db)

    def get_session_id(self):
        return str(randint(10000, 50000))

    def add_license(self, key):
        self.db['licenses'].add(key)

    def add_user(self, login, password, secure=False):
        if secure:
            password = md5(password)
        self.db['users'][login] = password

    @request_type(auth.AuthRequest)
    def handle_login(self, request):
        if request.client_id not in self.db['licenses']:
            raise exceptions.LicenseNotFound(request.client_id)

        if request.instance_count is None:
            raise exceptions.LisBaseException(654)

        if request.login not in self.db['users']:
            raise exceptions.UnknownUser()

        if self.db['users'][request.login] != request.password:
            raise exceptions.AuthentificationError()

        sessionid = self.get_session_id()
        self.db['sessions'].add(sessionid)

        return auth.AuthResponse(
            sessionid=sessionid,
            buildnumber=self.build_number,
            version=self.server_version
        )

    @request_type(PhoxRequest)
    def handle_logout(self, request):
        if request.sessionid not in self.db['sessions']:
            raise exceptions.UnknownSession()

        self.db['sessions'].remove(request.sessionid)

        return PhoxResponse(sessionid=request.sessionid)
