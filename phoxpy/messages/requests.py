# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.mapping import RefField
from phoxpy.messages import Message, PhoxRequest

__all__ = ['RequestInfo', 'RequestSamples']

class RequestInfo(PhoxRequest, 'request-info'):
    """Message for request type ``request-info``."""
    class Content(Message.Content):
        request = RefField()


class RequestSamples(PhoxRequest, 'request-samples'):
    """Message for request type ``request-samples``."""
    class Content(Message.Content):
        request = RefField()


