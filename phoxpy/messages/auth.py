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

class AuthRequest(PhoxRequest):
    """Authentication request message.

    :param client_id: License string heavy binded to computer hardware.
    :type client_id: str

    :param company: Company name.
    :type company: str

    :param instance_count: Instance count.
    :type instance_count: int

    :param lab: Laboratory name.
    :type lab: str

    :param login: Login name.
    :type login: str

    :param machine: Client hostname.
    :type machine: str
    
    :param password: Related password.
    :type password: str

    :param session_code: Secret session code.
    :type session_code: int
    """
    client_id = TextField(name='clientId')
    company = TextField(default='')
    instance_count = IntegerField(name='instanceCount', default=0)
    lab = TextField(default='')
    login = TextField()
    machine = TextField()
    password = TextField()
    session_code = IntegerField(name='sessionCode',
                                default=lambda: randint(10000, 20000))

    def __init__(self, **data):
        data['type'] = 'login'
        super(AuthRequest, self).__init__(**data)


class AuthResponse(PhoxResponse):
    """Authentication response message.

    :param admin_mode: Flag of admin mode usage.
    :type admin_mode: bool

    :param departments: List of department ids which user is belong to.
    :type departments: list

    :param employee: Referenced Employee object id.
    :type employee: int

    :param hospitals: List of hospital ids which user is belong to.
    :type  hospitals: list

    :param rights: List of active permission ids.
    :type  rights: list

    :param server_version: Server version string.
    :type server_version: str

    :param session_code: Session code number.
    :type session_code: int or long
    """
    admin_mode = BooleanField(name='adminMode')
    departments = ListField(RefField())
    employee = RefField()
    hospitals = ListField(RefField())
    rights = ListField(RefField())
    server_version = TextField(name='serverVersion')
    session_code = LongField(name='sessionCode')
