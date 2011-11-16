# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.messages import PhoxRequest

__all__ = ['OptionsGet']

class OptionsGet(PhoxRequest, 'options-get'):
    """Message for request type ``options-get``."""
