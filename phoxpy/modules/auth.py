# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from random import randint
from phoxpy.messages import PhoxRequest
from phoxpy.messages import  PhoxRequestContent, PhoxResponseContent
from phoxpy.mapping import (
    BooleanField, IntegerField, ListField, LongField, RefField, TextField
)

__all__ = ['AuthRequest', 'AuthResponse', 'login', 'logout']


class AuthRequest(PhoxRequestContent):
    """Authentication request message."""

    #: License string that heavy depended on host hardware.
    client_id = TextField(name='clientId')
    #: Company name.
    company = TextField(default='')
    #: Instance count.
    instance_count = IntegerField(name='instanceCount', default=0)
    #: Laboratory name.
    lab = TextField(default='')
    #: Login name.
    login = TextField()
    #: Client hostname.
    hostname = TextField(name='machine')
    #: Related password.
    password = TextField()
    #: Secret session code.
    session_code = IntegerField(name='sessionCode',
                                default=lambda: randint(10000, 20000))


class AuthResponse(PhoxResponseContent):
    """Authentication response message."""

    #: Flag of admin mode usage.
    admin_mode = BooleanField(name='adminMode')
    #: List of department ids which user is belong to.
    departments = ListField(RefField())
    #: Referenced Employee object id.
    employee = RefField()
    #: List of hospital ids which user is belong to.
    hospitals = ListField(RefField())
    #: List of active permission ids.
    rights = ListField(RefField())
    #: Server version string.
    server_version = TextField(name='serverVersion')
    #: Session code number.
    session_code = LongField(name='sessionCode')


def login(session, url=None):
    """Provides authentication for specified `session` instance.

    :param session: Session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param url: Custom server url. May be used to override `session` bounded
                one.
    :type url: str

    :return: Assigned session id number.
    """
    if url:
        session.bind_resource(url)
    session._userctx = session.request(
        body=session._credentials.to_message(type='login'),
        wrapper=AuthResponse)
    return session.id


def logout(session):
    """Closes session.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`
    """
    assert session.is_active(), 'Session is not activated.'
    session.request(body=PhoxRequest(type='logout'))
    session.userctx = AuthResponse()
