# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
from phoxpy import exceptions
from phoxpy import xml

class ExceptionsTestCase(unittest.TestCase):

    def test_handle_error_message(self):
        def gen_message():
            return xml.load(
                '<content><error code="500" description="foo" /></content>'
            )
        try:
            exceptions.handle_lis_error(gen_message)()
        except Exception, err:
            self.assertTrue(isinstance(err, exceptions.UnknownUser))
            self.assertEqual(err.args[0], 'foo')

    def test_skip_normal_messages(self):
        def gen_message():
            return xml.load(
                '<content><foo bar="baz"/></content>'
            )
        exceptions.handle_lis_error(gen_message)()

    def test_undescriptable_error(self):
        def gen_message():
            return xml.load(
                '<content><error code="500"/></content>'
            )
        try:
            exceptions.handle_lis_error(gen_message)()
        except Exception, err:
            self.assertTrue(isinstance(err, exceptions.UnknownUser))
            self.assertEqual(err.args[0], '')


if __name__ == '__main__':
    unittest.main()
