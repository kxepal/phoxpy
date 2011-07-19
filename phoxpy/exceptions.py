# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

class LisBaseException(Exception):
    """Base LIS exception"""
    code = None

class UnknownError(LisBaseException):
    """Exception for LIS error code #100"""
    code = 100

class RequestParsingError(LisBaseException):
    """Exception for LIS error code #200"""
    code = 200

class InvalidBuildNumber(LisBaseException):
    """Exception for LIS error code #220"""
    code = 220

class AccessDenied(LisBaseException):
    """Exception for LIS error code #400"""
    code = 400

class LicenseNotFound(LisBaseException):
    """Exception for LIS error code #401"""
    code = 401

class LicenseExpired(LisBaseException):
    """Exception for LIS error code #404"""
    code = 404

class TooManyLogins(LisBaseException):
    """Exception for LIS error code #406"""
    code = 406

class UnknownUser(LisBaseException):
    """Exception for LIS error code #500"""
    code = 500

class UnknownSession(LisBaseException):
    """Exception for LIS error code #501"""
    code = 501

class NotAuthorized(LisBaseException):
    """Exception for LIS error code #502"""
    code = 502

class AuthentificationError(LisBaseException):
    """Exception for LIS error code #504"""
    code = 504


exc_by_code = \
    dict([(cls.code, cls) for cls in LisBaseException.__subclasses__()])

def get_error_class(code):
    return exc_by_code.get(code, LisBaseException)

def handle_lis_error(func):
    """Decorator that looking for LIS error message and raises exception by
    associated error code"""
    def wrapper(*args, **kwargs):
        xmldata = func(*args, **kwargs)
        error = xmldata.find('error')
        if error is None:
            return xmldata
        code = error.attrib['code']
        descr = error.attrib.get('description', '')
        raise get_error_class(int(code))(descr.encode('utf-8'))
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

