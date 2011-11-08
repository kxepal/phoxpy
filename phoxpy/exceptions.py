# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

class LisExceptionMeta(type):
    def __call__(cls, description):
        return super(LisExceptionMeta, cls).__call__(cls.code, description)

class LisBaseException(Exception):
    """Base LIS exception."""
    __metaclass__ = LisExceptionMeta
    code = None
    description = None

    def __init__(self, code, description):
        self.code = code
        self.description = description
        super(LisBaseException, self).__init__(description)

################################################################################
# System
################################################################################

class LisSystemError(LisBaseException):
    """Base exception for system errors."""

class UnknownError(LisSystemError):
    """Exception for LIS error code #100"""
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
    """Exception for LIS error code #103"""
    code = 103

################################################################################
# Requests
################################################################################

class LisRequestError(LisBaseException):
    """Base exception for request processing errors."""

class RequestParsingError(LisRequestError):
    """Exception for LIS error code #200"""
    code = 200

class NoProcessorError(LisRequestError):
    """Exception for LIS error code #201"""
    code = 201

################################################################################
# Value errors
################################################################################

class LisValueError(LisBaseException, ValueError):
    """Base exception for value errors."""

class IncorrectDateFormat(LisValueError):
    """Exception for LIS error code #207"""
    code = 207

################################################################################
# Authentification
################################################################################

class LisAuthError(LisBaseException):
    """Base exception for auth related errors."""

class AccessDenied(LisAuthError):
    """Exception for LIS error code #400"""
    code = 400

class LicenseNotFound(LisAuthError):
    """Exception for LIS error code #401"""
    code = 401

class LicenseExpired(LisAuthError):
    """Exception for LIS error code #404"""
    code = 404

class TooManyLogins(LisAuthError):
    """Exception for LIS error code #406"""
    code = 406

class UnknownUser(LisAuthError):
    """Exception for LIS error code #500"""
    code = 500

class UnknownSession(LisAuthError):
    """Exception for LIS error code #501"""
    code = 501

class NotAuthorized(LisAuthError):
    """Exception for LIS error code #502"""
    code = 502

class AuthentificationError(LisAuthError):
    """Exception for LIS error code #504"""
    code = 504

################################################################################

_EXC_BY_CODE = dict([
    (cls.code, cls)
    for cls in LisBaseException.__subclasses__()
    if cls.code is not None])

def get_error_class(code):
    return _EXC_BY_CODE.get(code, LisBaseException)
