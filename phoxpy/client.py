# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy import xml
from phoxpy.exceptions import handle_lis_error
from phoxpy.http import Resource
from phoxpy.messages import AuthRequest, AuthResponse, PhoxRequest
from phoxpy.mapping import Message


class PhoxResource(Resource):
    """Specific resource for LIS server with native xml support."""
    def __init__(self, *args, **kwargs):
        super(PhoxResource, self).__init__(*args, **kwargs)
        self.headers.setdefault('Accept', 'text/html, */*')
        self.headers.setdefault('Content-Type', 'text/html')
        self.headers.setdefault('User-Agent', 'PhoxPy')

    def post_xml(self, path, body, headers=None, **params):
        """Send request to specified url.

        Args:
            path (str): Resource relative path.
            body (str, file-like, callable, Message): Request body data.
                If body is `callable` it would be call to extract value that
                needs to be sent.
                If body is `file-like` object, than request data would be sent
                by chunks sized by CHUNK_SIZE variable.
                If body is `str` it would be sent as is as regular request.
                If body is `Message` instance `__str__` method would be called
                to serialize object to xml source string.

        Kwargs:
            Custom query parameters.

        Returns:
            3-element tuple with response status code (int), headers (dict) and
            response data (xml.Element).
        """
        if isinstance(body, Message):
            body = str(body)
        status, headers, data = self.post(path, body, headers, **params)
        return status, headers, handle_lis_error(xml.load)(data.read())


class Session(object):
    """Represents LIS user session."""

    def __init__(self, login, password, client_id, **data):
        """Initialize Session instance.

        Args:
            login (str): Login name.
            password (str): Related password.
            client_id (str): License string.

        Kwargs:
            company (str): Company name.
            lab (str): Laboratory name.
            machine (str): Source computer name.
            session_code (int): Session code number.
            instance_count (int): Instance count number.
        """
        self._reqmsg = AuthRequest(
            login=login,
            password=password,
            client_id=client_id,
            **data
        )
        self._resmsg = AuthResponse('')
        self._resource = None

    def open(self, url, http_session=None):
        """Provides authorization and registration session on server

        Args:
            url (str): Server url.
            http_session (http.Session): Optional custom http session.

        Returns:
            self instance.
        """
        self._resource = PhoxResource(url, session=http_session)
        status, headers, data = self.request('', self._reqmsg)
        self._resmsg = AuthResponse.wrap(data)
        return self

    def request(self, path, data, headers=None, **params):
        """Makes single request to server.

        Args:
            path (str): Relative path from server url.
            data (mapping.Message):
            headers (dict): Custom HTTP headers.

        Kwargs:
            Custom query parameters.

        Returns:
            3-element tuple of http status, headers, data as xml.Element
            instance.
            See PhoxResource.post_xml method for more information.
        """
        return self._resource.post_xml(path, data, headers, **params)

    def close(self):
        """Closes current active session.
        
        Returns:
            True
        """
        assert self._resource is not None, 'Session has not been activated.'
        id, buildnumber = self.id, self._resmsg.buildnumber
        self.request('', PhoxRequest('logout', id, buildnumber))
        self._resmsg = AuthResponse('')
        return True

    def is_active(self):
        """Returns state of current session."""
        return bool(self.id)

    @property
    def id(self):
        """Session id number."""
        return self._resmsg.sessionid or None

    @property
    def departments(self):
        """List of department references which user is belong to."""
        return list(self._resmsg.departments)

    @property
    def hospitals(self):
        """List of hospital references which user is belong to."""
        return list(self._resmsg.hospitals)

    @property
    def employee(self):
        """Reference to Employee object."""
        return self._resmsg.employee

    @property
    def rights(self):
        """List of references to active permissions."""
        return list(self._resmsg.rights)

    @property
    def code(self):
        """Session code number."""
        return self._resmsg.session_code

    @property
    def server_version(self):
        """Server version string."""
        return self._resmsg.server_version

    @property
    def admin_mode(self):
        """Flag of admin mode usage."""
        return bool(self._resmsg.admin_mode)
