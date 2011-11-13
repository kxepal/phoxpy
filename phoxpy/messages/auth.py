# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from random import randint
from phoxpy.messages import PhoxRequest, PhoxResponse
from phoxpy.mapping import BooleanField, IntegerField, ListField, LongField, \
                           RefField, TextField

__all__ = ['AuthRequest', 'AuthResponse']

class AuthRequest(PhoxRequest, 'login'):
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


class AuthResponse(PhoxResponse):
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
