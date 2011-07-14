# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import os
import unittest
import warnings

def suite():
    suite = unittest.TestSuite()
    warnings.simplefilter('always')
    for root, dirs, files in os.walk(os.path.dirname(__file__)):
        for file in files:
            if not (file.startswith('test_') and file.endswith('.py')):
                continue
            name = file.split('.')[0]
            try:
                mod = __import__(name)
            except ImportError:
                warnings.warn('Unable to run tests from module %s'
                              '' % os.path.join(root, file), ImportWarning)
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(mod))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
