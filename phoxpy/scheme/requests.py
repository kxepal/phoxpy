# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.mapping import RefField, ObjectField, Mapping, IntegerField
from phoxpy.messages import PhoxRequestContent

__all__ = ['RequestInfo', 'RequestSamples']

class RequestInfo(PhoxRequestContent):
    """Content for request type ``request-info``."""
    request = RefField()


class RequestSamples(PhoxRequestContent):
    """Content for request type ``request-samples``."""
    request = RefField()


class PrintRequestOld(PhoxRequestContent):
    """Content for request type ``print-request-old``."""
    result = ObjectField(Mapping.build(
        request=RefField(),
        format=IntegerField()
    ))
