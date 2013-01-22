# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

# special Python objects that could be extracted from XML data
# why in this module? to solve import recursions

class Attribute(unicode):
    """Sentinel unicode value that marks value to help serialize it back to
    XML attribute."""


class Reference(unicode):
    """Sentinel unicode value that marks value for RefField to help serialize it
    back to XML without losing information about their kind."""
