# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import hashlib
import phoxpy.xmlcodec # TODO: import recursion WHY?
from phoxpy import http
from phoxpy import xml
from phoxpy.messages import Message, PhoxRequest, PhoxResponse
from phoxpy.messages.auth import AuthRequest, AuthResponse

__all__ = ['PhoxResource', 'Session']

md5 = lambda s: hashlib.md5(s).hexdigest()

class PhoxResource(http.Resource):
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

                     If body is :class:`~phoxpy.xml.Element` it will be
                     converted to string source.

        :type body: str, file, callable object, :class:`~phoxpy.xml.Element`
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
        elif isinstance(body, xml.ElementType):
            body = xml.dump(body)
        status, headers, data = self.post(path, body, headers, **params)
        return status, headers, xml.parse(data)


class Session(object):
    """Represents LIS user session.

    :param login: Login name.
    :type login: str

    :param password: Related password.
    :type password: str

    :param client_id: License string heavy binded to computer hardware.
    :type client_id: str

    :param secure: Activate "secure auth" mode. This should work for modern
                   LIS server (since 38776), but wouldn't with old ones.
                   However, you should know, that "secure auth" is not much more
                   than sending password not as is, but as his md5 hash.
                   This means that Bob still able to capture your traffic and
                   hack your account simply by passing password hash.
    :type secure: bool

    :param data: Custom keyword options.
                 See :class:`~phoxpy.messages.AuthRequest` for more information.
    """
    def __init__(self, login, password, client_id, secure=False, **data):
        if secure:
            password = md5(password)

        self._credentials = AuthRequest(login=login,
                                        password=password,
                                        client_id=client_id,
                                        **data)
        self._userctx = AuthResponse()
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
        self._userctx = self.request(body=self._credentials,
                                     wrapper=AuthResponse)
        return self

    def request(self, path='', body=None, headers=None, wrapper=None, **params):
        """Makes single request to server.

        :param path: Resource relative path.
        :type path: str

        :param body: Request message instance or xml data.
        :type body: :class:`~phoxpy.messages.PhoxRequest`,
                    :class:`~phox.xml.Element`,
                    str

        :param headers: HTTP headers dictionary.
        :type headers: dict

        :param wrapper: Callable object that will wrap XML data into Python
                        object.
        :type wrapper: callable

        :param params: Custom query parameters as keyword arguments.

        :return: Response message.
        """
        self.sign(body)
        if wrapper is None:
            wrapper = PhoxResponse
        if hasattr(wrapper, 'to_python'):
            wrapper = wrapper.to_python
        return wrapper(
            self._resource.post_xml(path, body, headers, **params)[2]
        )

    def sign(self, message):
        """Signs :class:`~phox.messages.Message` instance by setting session id
        to header information.
        """
        if isinstance(message, Message):
            message.sessionid = self.id
        elif isinstance(message, xml.ElementType):
            message.attrib['sessionid'] = self.id
        elif message is not None:
            raise TypeError('Invalid message %r' % message)

    def close(self):
        """Closes current active session."""
        assert self.is_active(), 'Session has not been activated.'
        self.request(body=PhoxRequest(type='logout'))
        self._userctx = AuthResponse()
        return True

    def is_active(self):
        """Returns state of current session."""
        return bool(self.id)

    def _get_id(self):
        """Session id number."""
        return self._userctx.sessionid or None

    def _set_id(self, value):
        self._userctx.sessionid = value

    id = property(_get_id, _set_id)

    @property
    def userctx(self):
        return self._userctx.unwrap()
