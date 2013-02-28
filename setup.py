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
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    # http://wiki.python.org/moin/Distutils/Cookbook/AutoPackageDiscovery
    import os

    def is_package(path):
        return (
            os.path.isdir(path) and
            os.path.isfile(os.path.join(path, '__init__.py'))
        )

    def find_packages(path='.', base=""):
        """ Find all packages in path """
        packages = {}
        for item in os.listdir(path):
            dir = os.path.join(path, item)
            if is_package( dir ):
                if base:
                    module_name = "%(base)s.%(item)s" % vars()
                else:
                    module_name = item
                packages[module_name] = dir
                packages.update(find_packages(dir, module_name))
        return packages

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

    install_requires = ['lxml'],
    test_suite = 'phoxpy.tests',
    zip_safe = True,

    packages = find_packages(),
)
