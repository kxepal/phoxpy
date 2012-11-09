#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'phoxpy',
    version = '0.3-dev',
    description = 'Python client to Laboratory Information System',
    long_description = \
"""This is a Python library that implements protocol and base operations with
RosLabSystems Laboratory Information System software.""",
    author = 'Alexander Shorin',
    author_email = 'kxepal@gmail.com',
    license = 'BSD',
    url = 'http://code.google.com/p/phoxpy/',

    install_requires = ['lxml', 'flask', 'flask-sqlalchemy'],
    test_suite = 'phoxpy.tests',
    zip_safe = True,

    packages = ['phoxpy', 'phoxpy.tests'],
)
