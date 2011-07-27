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
from phoxpy.messages import Message, PhoxRequest, PhoxResponse,\
                            AuthRequest, AuthResponse


__all__ = ['PhoxResource', 'Session']

class PhoxResource(Resource):
    """Specific resource for LIS server with native xml support."""
    def __init__(self, *args, **kwargs):
        super(PhoxResource, self).__init__(*args, **kwargs)
        self.headers.setdefault('Accept', 'text/html, */*')
        self.headers.setdefault('Content-Type', 'text/html')
        self.headers.setdefault('User-Agent', 'PhoxPy')

    def post_xml(self, path, body, headers=None, **params):
        """Send request to specified url.

        :param path: Resource relative path.
        :type path: str

        :param body: Request body data.

                     If body is file-like object then request would be sent
                     with `chunked` transfer encoding.
                     
                     If body is :class:`~phoxpy.messages.Message` instance
                     it would be converted to string source by ``__str__``
                     method call.
        
        :type body: str, file, callable object
                    or :class:`~phoxpy.messages.Message` instance.

        :param headers: HTTP headers dictionary.
        :type headers: dict

        :param params: Custom query parameters as keyword arguments.

        :return: 3-element ``tuple``:
        
                 - response status code (``int``)
                 - http headers (``dict``)
                 - response data (:class:`~phoxpy.xml.Element`)

        :rtype: tuple
        """
        if isinstance(body, Message):
            body = str(body)
        status, headers, data = self.post(path, body, headers, **params)
        return status, headers, handle_lis_error(xml.load)(data.read())


class Session(object):
    """Represents LIS user session.

    :param login: Login name.
    :type login: str

    :param password: Related password.
    :type password: str

    :param client_id: License string heavy binded to computer hardware.
    :type client_id: str

    :param data: Custom keyword options.
                 See :class:`~phoxpy.messages.AuthRequest` for more information.
    """
    def __init__(self, login, password, client_id, **data):
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

        :param url: Server URL.
        :type url: str

        :param http_session: Optional custom HTTP session.
        :type http_session: :class:`~phoxpy.http.Session`

        :return: self
        """
        self._resource = PhoxResource(url, session=http_session)
        response = self.request('', self._reqmsg)
        self._resmsg = AuthResponse.wrap(response.unwrap())
        return self

    def request(self, path, data, headers=None, **params):
        """Makes single request to server.

        :param path: Resource relative path.
        :type path: str

        :param data: Request message instance.
        :type data: :class:`~phoxpy.messages.PhoxRequest`

        :param headers: HTTP headers dictionary.
        :type headers: dict

        :param params: Custom query parameters as keyword arguments.

        :return: Response message.
        :rtype: :class:`~phoxpy.messages.PhoxResponse`
        """
        return PhoxResponse.wrap(
            self._resource.post_xml(path, data, headers, **params)[2]
        )

    def close(self):
        """Closes current active session."""
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
