# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""Operates with user session."""

from flask import Blueprint, request, Response, session, abort
from flask.globals import current_app as app
from phoxpy.scheme.auth import AuthResponse

session = Blueprint('session', __name__,)

@session.route('/login', methods=['POST'])
def login():
    if session.id:
        pass
    msg = request.phoxmsg
    if not validate_license(msg['license']):
        abort(401, 'invalid license')
    if not validate_credentials(msg['login'], msg['password']):
        abort(401, 'invalid username or password')
    resp = Response(

    )
    resp.headers['Content-Type'] = 'application/xml'
    return resp

@session.route('/logout', methods=['POST'])
def logout():
    msg = request.phoxmsg



def validate_license(license):
    pass

def validate_credentials(username, password):
    pass

pass
