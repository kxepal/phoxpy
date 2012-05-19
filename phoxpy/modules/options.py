# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.messages.options import OptionsGet

__all__ = ['load']

def load(session):
    """Loads global config options.
    
    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`
    
    :return: Config options as is.
    :rtype: dict
    """
    resp = session.request(body=OptionsGet())
    config = {}
    for item in resp['']: # unnamed sequence
        config[item['code']] = item['value']
    return config
