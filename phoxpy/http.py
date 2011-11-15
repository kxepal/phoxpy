# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2011 Christopher Lenz, Dirkjan Ochtman, Matt Goodall
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Reworked and adapted version of couchdb-python project http module.
# <https://couchdb-python.googlecode.com/hg/couchdb/http.py>
#

import base64
import errno
import socket
import sys
import time
import urllib
from httplib import BadStatusLine, HTTPConnection, HTTPSConnection
from urlparse import urlsplit, urlunsplit
from threading import Lock
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = [
    'CHUNK_SIZE', 'RETRYABLE_ERRORS',
    'HTTPError', 'RedirectLimit',
    'ResponseBody', 'Session', 'Resource'
]

#: Nominal data chunk size to process by default
CHUNK_SIZE = 16 * 1024 * 1024

#: Frozen set of socket errors which will trigger retry request.
RETRYABLE_ERRORS = frozenset([
    errno.EPIPE, errno.ETIMEDOUT,
    errno.ECONNRESET, errno.ECONNREFUSED, errno.ECONNABORTED,
    errno.EHOSTDOWN, errno.EHOSTUNREACH,
    errno.ENETRESET, errno.ENETUNREACH, errno.ENETDOWN
])

class HTTPError(Exception):
    """Base class for errors based on HTTP status codes >= 400."""

class RedirectLimit(Exception):
    """Exception raised when a request is redirected more often than allowed
    by the maximum number of redirections.
    """

class ResponseBody(object):
    """Readonly file-like wrapper for http response data.

    :param resp: :class:`~httplib.HTTPResponse` instance.
    :param callback: Callable object.
    """
    def __init__(self, resp, callback):
        self.resp = resp
        self.callback = callback

    def __iter__(self):
        """Iterates over response data.

        If data transfer encoding is "chunked", than it would iterate over each
        line for each chunk in response. Otherwise it works like readlines
        method.

        Yields:
            Response data by lines.
        """
        if self.is_chunked_transfer():
            while not self.is_closed():
                chunks = int(self.readline().strip(), 16)
                if not chunks:
                    self.read(2) #crlf
                    self.resp.close()
                    self.callback()
                    break
                for line in self.read(chunks).splitlines():
                    yield line
                self.read(2) #crlf
        else:
            for line in self.readlines():
                yield line

    def read(self, size=None):
        """Read response data.

        :param size: Amount of data in bytes that should be readed.
                     ``None`` value means "read all at once".
        :type size: int

        :return: Data chunk.
        :rtype: str
        """
        bytes_data = self.resp.read(size)
        if size is None or len(bytes_data) < size:
            self.resp.close()
        return bytes_data

    def readline(self):
        """Reads one line from response data."""
        return self.resp.fp.readline()

    def readlines(self):
        """Yields response data line by line."""
        while not self.is_closed():
            yield self.readline()

    def close(self):
        """Closes wrapped response instance by reading all data to void."""
        while not self.resp.isclosed():
            self.read(CHUNK_SIZE)
        if self.callback is not None:
            self.callback()
            self.callback = None

    def is_chunked_transfer(self):
        """Check if response has chunked transfer encoding nature."""
        return self.resp.getheader('transfer-encoding') == 'chunked'

    def is_closed(self):
        """Check if response stream is closed."""
        return self.resp.isclosed()


class Session(object):
    """HTTP session holder.

    :param retry_delays: List of delay seconds before next try will be used.
    :type retry_delays: list of int

    :param max_redirects: Maximum number of redirects before
                          :exc:`~phoxpy.http.RedirectLimit` will be raised.
    :type max_redirects: int

    :param retryable_errors:
    :type retryable_errors: iterable
    """
    def __init__(self, retry_delays=None, max_redirects=5,
                 retryable_errors=RETRYABLE_ERRORS):
        self._conns = {}
        self._perm_redirects = {}
        self.lock = Lock()
        self.retry_delays = list(retry_delays or [0])
        self.max_redirects = max_redirects
        self.retryable_errors = set(retryable_errors)

    def _prerare_request(self, method, url, body, headers, credentials):
        """Prepare request options for future use."""
        assert isinstance(method, str)
        assert isinstance(url, str)

        if url in self._perm_redirects:
            url = self._perm_redirects[url]
        method = method.upper()

        if headers is None:
            headers = {}

        if not isinstance(body, basestring):
            if hasattr(body, '__call__'):
                body = body()
            if hasattr(body, 'read'):
                headers['Transfer-Encoding'] = 'chunked'
            elif isinstance(body, basestring):
                pass
            elif body is not None:
                raise TypeError('Invalid request body data %r' % body)
        if isinstance(body, basestring):
            headers['Content-Length'] = str(len(body))

        if credentials:
            basic_auth = 'Basic %s' % base64.b64encode('%s:%s' % credentials)
            headers['Authorization'] = basic_auth

        return method, url ,body, headers, credentials


    def request(self, method, url, body=None, headers=None, credentials=None,
                _num_redirects=0):
        """Send request to specified url.

        :param method: Request method (GET, POST, PUT etc.).
        :type method: str

        :param url: Target site URL.
        :type url: str

        :param body: Request body data. If body is file-like object then request
                     would be sent with `chunked` transfer encoding.
        :type body: str, file or callable object

        :param headers: HTTP headers dictionary.
        :type headers: dict

        :param credentials: Username and password pair used for basic auth.
        :type credentials: list, tuple

        :return: 3-element ``tuple`` of response status code (``int``),
                 http headers (``dict``) and response data.

                 Response data could be instance of
                 :class:`~StringIO.StringIO` or
                 :class:`~phoxpy.http.ResponseBody`
                 depending from ``CHUNK_SIZE`` variable and `Content-Length`
                 header values.
        :rtype: tuple
        """

        method, url, body, headers, credentials = \
            self._prerare_request(method, url, body, headers, credentials)
        
        path_query = urlunsplit(('', '') + urlsplit(url)[2:4] + ('',))

        conn = self._connect(url)
        retries = iter(self.retry_delays)
        while True:
            try:
                resp = self._send_request(conn, method,
                                          path_query, body, headers)
            except socket.error, err:
                self._try_retry(conn, err, retries)
                continue

            if resp.status in (301, 302, 303, 307):
                resp.read()
                self._cache_connection(url, conn)
                if _num_redirects > self.max_redirects:
                    raise RedirectLimit('Redirection limit (%s) exceeded'
                                        '' % self.max_redirects)
                location = resp.getheader('location')
                if resp.status == 301:
                    self._perm_redirects[url] = location
                elif resp.status == 303:
                    method = 'GET'
                return self.request(method, location, body, headers,
                                    _num_redirects=_num_redirects + 1)

            cache_connection = lambda: self._cache_connection(url, conn)
            return self._handle_response(method, resp, cache_connection)

    def _connect(self, url):
        """Create HTTP/HTTPS connection based on url.

        Args:
            url (str): URL with http(default if omitted) or https scheme.

        Returns:
            HTTPConnection or HTTPSConnection instance.

        Raises:
            ValueError: if scheme is different from http or https.
        """
        scheme, host = urlsplit(url, 'http', False)[:2]
        self.lock.acquire()
        try:
            conns = self._conns.setdefault(url, set([]))
            if conns:
                conn = conns.pop()
            else:
                if scheme == 'http':
                    cls = HTTPConnection
                elif scheme == 'https':
                    cls = HTTPSConnection
                else:
                    raise ValueError('%s is not a supported scheme' % scheme)
                conn = cls(host)
                conn.connect()
        finally:
            self.lock.release()
        return conn

    def _cache_connection(self, url, conn):
        """Stores active http/https connection to cache associated with url."""
        self.lock.acquire()
        try:
            self._conns.setdefault(url, set([])).add(conn)
        finally:
            self.lock.release()

    def _send_request(self, conn, method, path_query, body, headers):
        """Actually sends prepared request via active connection."""
        try:
            conn.putrequest(method, path_query, skip_accept_encoding=True)
            for header in headers:
                conn.putheader(header, headers[header])
            conn.endheaders()
            if body is not None:
                if isinstance(body, str):
                    conn.send(body)
                else:
                    while True:
                        chunk = body.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        conn.send(('%x\r\n' % len(chunk)) + chunk + '\r\n')
                    conn.send('0\r\n\r\n')
            return conn.getresponse()
        except BadStatusLine, err:
            if err.line == '' or err.line == "''":
                raise socket.error(errno.ECONNRESET)
            else:
                raise

    def _try_retry(self, conn, err, retries):
        """Checks if there could be one more shot."""
        ecode = err.args[0]
        if ecode not in self.retryable_errors:
            raise
        try:
            delay = retries.next()
        except StopIteration:
            # No more retries, raise last socket error.
            raise err
        time.sleep(delay)
        conn.close() # relay on autoopen connection property

    def _handle_response(self, method, resp, cache_connection):
        """Handles response to make final changes."""
        status = resp.status
        data = None
        streamed = False

        # Read the full response for empty responses so that the connection is
        # in good state for the next request
        if method == 'HEAD' or resp.getheader('content-length') == '0' or \
                status < 200 or status in (204, 304):
            resp.read()
            cache_connection()

        # Buffer small response bodies
        elif int(resp.getheader('content-length', sys.maxint)) < CHUNK_SIZE:
            data = resp.read()
            cache_connection()

        # For large or chunked response bodies, do not buffer the full body,
        # and instead return a minimal file-like object
        else:
            data = ResponseBody(resp, cache_connection)
            streamed = True

        # Handle errors
        if status >= 400:
            if method != 'HEAD':
                error = resp.read()
                cache_connection()
            else:
                error = ''
            raise HTTPError((status, error))

        if not streamed and data is not None:
            data = StringIO(data)

        return status, resp.msg, data


class Resource(object):
    """Provides methods to send request to HTTP resource.

    :param url: HTTP resource URL.
    :type url: str

    :param session: Custom :class:`~phoxpy.http.Session` instance.
                    If ``None`` new session will be created.

    :param headers: Default HTTP headers.
    :type headers: dict

    :param credentials: Username and password pair used for basic auth.
    :type credentials: list, tuple
    """
    def __init__(self, url, session=None, headers=None, credentials=None):
        self.url = url
        if session is None:
            session = Session()
        self.session = session
        self.credentials = credentials
        self.headers = headers or {}

    def __call__(self, *path):
        obj = type(self)(urljoin(self.url, *path), self.session)
        obj.credentials = self.credentials
        obj.headers = self.headers.copy()
        return obj

    def post(self, path=None, body=None, headers=None, **params):
        """Sends POST request to resource.

        :param path: Resource relative path.
        :type path: str

        :param body: Request body data. If body is file-like object then request
                     would be sent with `chunked` transfer encoding.
        :type body: str, file or callable object

        :param headers: HTTP headers dictionary.
        :type headers: dict

        :param params: Custom query parameters as keyword arguments.
            
        :return: 3-element ``tuple`` of response status code (``int``),
            http headers (``dict``) and response data.

            Response data could be instance of
            :class:`~StringIO.StringIO` or :class:`~phoxpy.http.ResponseBody`
            depending from ``CHUNK_SIZE`` constant and `Content-Length`
            header values.
        :rtype: tuple
        """
        return self._request('POST', path, body, headers, **params)

    def _request(self, method, path=None, body=None, headers=None, **params):
        all_headers = self.headers.copy()
        all_headers.update(headers or {})
        if path is not None:
            url = urljoin(self.url, path, **params)
        else:
            url = urljoin(self.url, **params)
        return self.session.request(method, url, body=body, headers=all_headers,
                                    credentials=self.credentials)


def quote(string, safe=''):
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    return urllib.quote(string, safe)

def urlencode(data):
    if isinstance(data, dict):
        data = data.items()
    params = []
    for name, value in data:
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        params.append((name, value))
    return urllib.urlencode(params)

def urljoin(base, *path, **query):
    if base and base.endswith('/'):
        base = base[:-1]
    retval = [base]

    # build the path
    path = '/'.join([''] + [quote(s) for s in path])
    if path:
        retval.append(path)

    # build the query string
    params = []
    for name, value in query.items():
        if type(value) in (list, tuple):
            params.extend([(name, i) for i in value if i is not None])
        elif value is not None:
            if value is True:
                value = 'true'
            elif value is False:
                value = 'false'
            params.append((name, value))
    if params:
        retval.extend(['?', urlencode(params)])

    return ''.join(retval)
