# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
import phoxpy.server.app as phoxpyd


class PhoxpydTestCase(unittest.TestCase):

    def setUp(self):
        phoxpyd.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        phoxpyd.app.config['TESTING'] = True
        self.app = phoxpyd.app.test_client()
