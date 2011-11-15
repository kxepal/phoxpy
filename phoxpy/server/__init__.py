# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.server.main import BaseLisServer


class SimpleLISServer(BaseLisServer):
    """Simple mock LIS server."""
    def __init__(self, *args, **kwargs):
        super(SimpleLISServer, self).__init__(*args, **kwargs)
