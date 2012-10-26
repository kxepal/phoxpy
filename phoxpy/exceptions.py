# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

class LisExceptionMeta(type):
    def __call__(cls, description=None):
        return super(LisExceptionMeta, cls).__call__(cls.code, description)

class LisBaseException(Exception):
    """Base LIS exception."""
    __metaclass__ = LisExceptionMeta
    code = None
    description = None

    def __init__(self, code, description=None):
        self.code = code
        self.description = description
        super(LisBaseException, self).__init__(description)

################################################################################
# System
################################################################################

class LisSystemError(LisBaseException):
    """Base exception for system errors."""

class UnknownError(LisSystemError):
    """Raises when something goes wrong. #100"""
    code = 100

class InvalidBuildNumber(LisSystemError):
    """Exception for LIS error code #220"""
    code = 220

################################################################################
# Database
################################################################################

class LisDatabaseError(LisBaseException):
    """Base exception for database errors."""

class HibernateError(LisDatabaseError):
    """Error in SQL query execution on server side. #103"""
    code = 103

################################################################################
# Requests
################################################################################

class LisRequestError(LisBaseException):
    """Base exception for request processing errors."""

class RequestParsingError(LisRequestError):
    """Couldn't parse XML data due to invalid format of it. #200"""
    code = 200

class NoProcessorError(LisRequestError):
    """No processor to handle request. #201"""
    code = 201

################################################################################
# Value errors
################################################################################

class LisValueError(LisBaseException, ValueError):
    """Base exception for value errors."""

class IncorrectDateFormat(LisValueError):
    """Datetime value has invalid format. #207"""
    code = 207

################################################################################
# License
################################################################################

class LisLicenseError(LisBaseException):
    """Base exception for auth related errors."""

class LicenseNotFound(LisLicenseError):
    """License not found. #401"""
    code = 401

class LicenseExpired(LisLicenseError):
    """License expired. #404"""
    code = 404

################################################################################
# Authentification
################################################################################

class LisAuthError(LisBaseException):
    pass

class UnknownUser(LisAuthError):
    """User not found in common list. #500"""
    code = 500

class UnknownSession(LisAuthError):
    """Request passed with invalid session number or expired one. #501"""
    code = 501

class NotAuthorized(LisAuthError):
    """Exception for LIS error code #502"""
    code = 502

class AuthentificationError(LisAuthError):
    """Invalid login name or password. #504"""
    code = 504

################################################################################
# Permissions
################################################################################

class LisAccessError(LisBaseException):
    pass

class AccessDeny(LisAccessError):
    """No permissions to execute requested operation. #400"""
    code = 400

################################################################################

_EXC_BY_CODE = {}
_stack = [LisBaseException]
while _stack:
    current = _stack.pop()
    for cls in current.__subclasses__():
        if cls.code is not None:
            _EXC_BY_CODE[cls.code] = cls
        _stack.append(cls)
del _stack

def get_error_class(code):
    return _EXC_BY_CODE.get(code, LisBaseException)
