# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import errno
import httplib as _httplib
import socket
import unittest
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from phoxpy import http

http.CHUNK_SIZE = 16 * 1024 # reduce chunk size

class DummyHTTPConnection(object):
    def __init__(self, *args, **kwargs):
        self.headers = {}
        self.data = []
        self.request = None

    def putrequest(self, *args, **kwargs):
        self.request = args, kwargs

    def putheader(self, key, value):
        self.headers[key] = value

    def endheaders(self):
        pass

    def send(self, data):
        self.data.append(data)

    def connect(self):
        pass

    def getresponse(self):
        return DummyHttpResponse(200, ''.join(self.data), self.headers)

    @property
    def chunks_sent(self):
        return len(self.data)

    @property
    def was_data_sent(self):
        return bool(self.data)

    def close(self):
        pass


class DummyHTTPSConnection(DummyHTTPConnection):
    pass


class DummyHttpResponse(object):
    def __init__(self, status, data='', headers=None):
        self.status = status
        self.datalen = len(data)
        self.fp = StringIO(data)
        headers = headers or {}
        self.msg = dict([(k.lower(), v) for k, v in headers.items()])

    def read(self, buf=None):
        if buf is None:
            return self.fp.read()
        else:
            return self.fp.read(buf)

    def getheader(self, header, default=None):
        return self.msg.get(header.lower(), default)

    def isclosed(self):
        return self.fp.tell() == self.datalen

    def close(self):
        self.fp.read()


class Chain(object):

    def __init__(self, *funcs):
        self.chain = list(funcs)

    def __call__(self, *args, **kwargs):
        return self.chain.pop(0)(*args, **kwargs)


_resp= lambda *a, **k: lambda *v, **w: DummyHttpResponse(*a, **k)

# emulation of request chains
_HTTP_RESPONSES = {
    'perm_redirect': Chain(
        _resp(301, '', {'location': 'localhost/new_location'}),
        _resp(200, 'OK', {'foo': 'bar'})
    ),
    'see_other': Chain(
        _resp(303, '', {'location': 'localhost/new_location'}),
        _resp(200, 'OK', {'foo': 'bar'})
    ),
    'use_proxy': Chain(
        _resp(305, '', {'location': 'localhost/new_location'}),
        _resp(200, 'OK', {'foo': 'bar'})
    ),
    'temp_redirect': Chain(
        _resp(307, '', {'location': 'localhost/new_location'}),
        _resp(200, 'OK', {'foo': 'bar'})
    ),
    'chunked': _resp(200,
        '\r\n'.join(['\r\n'.join([hex(len(c)), c])
                     for c in ['foo', 'bar', 'baz', '']]),
        {'Transfer-Encoding': 'chunked'}
    ),
    'not_found': _resp(404, 'Not Found'),
    'server_error': _resp(500, 'Server error'),

    'head': _resp(200, ''),
    'small_data': _resp(
        200, ''.join(map(str, range(128))),
        {'Content-Length': '128'}
    ),
    'large_data': _resp(
        200, ''.join(map(str, xrange(http.CHUNK_SIZE * 2))),
        {'Content-Length': str(http.CHUNK_SIZE * 2)}
    )
}
del _resp


class HelpersTestCase(unittest.TestCase):

    def test_urljoin(self):
        """should join url base with path chunk via slash"""
        url = http.urljoin('base', 'chunk')
        self.assertEqual(url, 'base/chunk')

    def test_urljoin_strip_base_trail_slash(self):
        """should strip trailing slash from url base before joining"""
        url = http.urljoin('base/', 'chunk')
        self.assertEqual(url, 'base/chunk')

    def test_urljoin_multiple_chunks(self):
        """shoul join multiple path chunks with url base"""
        url = http.urljoin('base', *map(str, range(10)))
        self.assertEqual(url, 'base/0/1/2/3/4/5/6/7/8/9')

    def test_urljoin_escape_chars_in_chunk(self):
        """should escape characters in chunks, even slash"""
        url = http.urljoin('base', '/chunk')
        self.assertEqual(url, 'base/%2Fchunk')

    def test_urljoin_query_params(self):
        """should join keyword arguments as query parameters to url base"""
        url = http.urljoin('base', test='passed', answer=42)
        self.assertEqual(url, 'base?test=passed&answer=42')

    def test_urljoin_query_boolean_params(self):
        """should convert boolean parameter values to lowercase"""
        url = http.urljoin('base', active=True, foo=False)
        self.assertEqual(url, 'base?active=true&foo=false')

    def test_urljoin_query_list_params(self):
        """should convert list to se"""
        url = http.urljoin('base', foo=['bar', 'baz'])
        self.assertEqual(url, 'base?foo=bar&foo=baz')

    def test_quote(self):
        self.assertEqual(http.quote('/test=&passed'), '%2Ftest%3D%26passed')

    def test_quote_unicode_chunk(self):
        self.assertEqual(http.quote(u'/test=&passed'), '%2Ftest%3D%26passed')


class ResourceTestCase(unittest.TestCase):

    def test_basic_initialize(self):
        res = http.Resource('http://localhost')
        self.assertTrue(hasattr(res, 'url'))
        self.assertTrue(hasattr(res, 'session'))
        self.assertTrue(hasattr(res, 'headers'))
        self.assertTrue(hasattr(res, 'credentials'))

        self.assertEqual(res.url, 'http://localhost')
        self.assertTrue(isinstance(res.session, http.Session))
        self.assertEqual(res.headers, {})
        self.assertEqual(res.credentials, None)

    def test_call_extends_url(self):
        res = http.Resource('http://localhost')
        new_res = res('path')
        self.assertEqual(new_res.url, 'http://localhost/path')
        self.assertEqual(res.url, 'http://localhost')

    def test_call_copies_headers(self):
        res = http.Resource('http://localhost', headers={'foo': 'bar'})
        new_res = res('/path')
        self.assertEqual(res.headers, new_res.headers)
        self.assertTrue(res.headers is not new_res.headers)

    def test_post_request(self):
        class DummySession(object):
            def request(self, method, url, body, headers, *args, **kwargs):
                return method, url, body, headers

        res = http.Resource('http://localhost', session=DummySession())
        method, url, body, headers = res.post(
            'path', 'foobar', headers={'bar': 'baz'}, test='pas&sed'
        )
        self.assertEqual(method, 'POST')
        self.assertEqual(url, 'http://localhost/path?test=pas%26sed')
        self.assertEqual(body, 'foobar')
        self.assertEqual(headers, {'bar': 'baz'})


class SessionTestCase(unittest.TestCase):

    def setUp(self):
        http.HTTPConnection = DummyHTTPConnection
        http.HTTPSConnection = DummyHTTPSConnection

    def tearDown(self):
        http.HTTPConnection = _httplib.HTTPConnection
        http.HTTPSConnection = _httplib.HTTPSConnection


class SessionConnectionTestCase(SessionTestCase):

    def test_make_http_connection(self):
        session = http.Session()
        conn = session._connect('http://localhost')
        self.assertTrue(isinstance(conn, http.HTTPConnection))

    def test_make_https_connection(self):
        session = http.Session()
        conn = session._connect('https://localhost')
        self.assertTrue(isinstance(conn, http.HTTPSConnection))

    def test_fail_make_connection_for_unknown_scheme(self):
        session = http.Session()
        self.assertRaises(ValueError, session._connect, 'foo://bar')

    def test_reuse_connection_for_same_url(self):
        url = 'http://localhost'
        session = http.Session()
        conn1 = session._connect(url)
        session._cache_connection(url, conn1)
        conn2 = session._connect(url)
        self.assertTrue(conn1 is conn2)

    def test_make_new_connection_for_same_url_if_old_one_is_in_used(self):
        url = 'http://localhost'
        session = http.Session()
        conn1 = session._connect(url)
        conn2 = session._connect(url)
        session._cache_connection(url, conn1)
        session._cache_connection(url, conn2)
        self.assertTrue(conn1 is not conn2)
        self.assertEqual(len(session._conns), 1)

class SessionPrepareRequestTestCase(SessionTestCase):

    def test_prepare(self):
        session = http.Session()
        res = session._prerare_request('GET', 'foo', None, None, None)
        method, url, body, headers, credentials = res
        self.assertTrue(body is None)
        self.assertTrue(isinstance(headers, dict))
        self.assertTrue(credentials is None)

    def test_perm_redirect(self):
        session = http.Session()
        session._perm_redirects['foo'] = 'bar'
        res = session._prerare_request('GET', 'foo', None, None, None)
        method, url, body, headers, credentials = res
        self.assertEqual(url, 'bar')

    def test_uppercase_method(self):
        session = http.Session()
        res = session._prerare_request('get', 'foo', None, None, None)
        method, url, body, headers, credentials = res
        self.assertEqual(method, 'GET')

    def test_none_body(self):
        session = http.Session()
        res = session._prerare_request('GET', 'foo', None, None, None)
        method, url, body, headers, credentials = res
        self.assertTrue('Content-Length' not in headers)

    def test_text_body(self):
        session = http.Session()
        res = session._prerare_request('GET', '', 'foo-bar-baz', None, None)
        method, url, body, headers, credentials = res
        self.assertEqual(body, 'foo-bar-baz')
        self.assertTrue('Content-Length' in headers)
        self.assertEqual(headers['Content-Length'], str(len(body)))

    def test_file_body(self):
        body = StringIO('foo-bar-baz')
        session = http.Session()
        res = session._prerare_request('GET', '', body, None, None)
        method, url, body, headers, credentials = res
        self.assertTrue(isinstance(body, type(StringIO(''))))
        self.assertTrue('Transfer-Encoding' in headers)
        self.assertEqual(headers['Transfer-Encoding'], 'chunked')

    def test_callable_body(self):
        body = lambda: str(42)
        session = http.Session()
        res = session._prerare_request('GET', '', body, None, None)
        method, url, body, headers, credentials = res
        self.assertEqual(body, '42')

    def test_fail_unknown_body(self):
        body = lambda: object()
        session = http.Session()
        self.assertRaises(TypeError, session._prerare_request,
                          'GET', 'foo', body, None, None)

    def test_credentials(self):
        session = http.Session()
        res = session._prerare_request('GET', 'foo', '', None, ('bar', 'baz'))
        method, url, body, headers, credentials = res
        self.assertTrue('Authorization' in headers)
        self.assertEqual(headers['Authorization'], 'Basic YmFyOmJheg==')


class SessionHandleResponseTestCase(SessionTestCase):

    def test_head_request(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(200, '', {'foo': 'bar'})
        status, headers, data = session._handle_response(
            'HEAD', resp, cache_connection
        )
        self.assertEqual(callback, ['hit'])
        self.assertTrue(resp.isclosed())

    def test_zero_content_length(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(200, '', {'Content-Length': '0'})
        status, headers, data = session._handle_response(
            'GET', resp, cache_connection
        )
        self.assertEqual(callback, ['hit'])
        self.assertTrue(resp.isclosed())

    def test_status_1xx(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(100, 'foo-bar')
        status, headers, data = session._handle_response(
            'GET', resp, cache_connection
        )
        self.assertEqual(callback, ['hit'])
        self.assertTrue(resp.isclosed())

    def test_status_204(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(204, '')
        status, headers, data = session._handle_response(
            'GET', resp, cache_connection
        )
        self.assertEqual(callback, ['hit'])
        self.assertTrue(resp.isclosed())

    def test_status_304(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(304, 'foo-bar')
        status, headers, data = session._handle_response(
            'GET', resp, cache_connection
        )
        self.assertEqual(callback, ['hit'])
        self.assertTrue(resp.isclosed())

    def test_small_response(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(200, 'foo-bar', {'Content-Length': '7'})
        status, headers, data = session._handle_response(
            'GET', resp, cache_connection
        )
        self.assertEqual(callback, ['hit'])
        self.assertTrue(resp.isclosed())
        self.assertTrue(isinstance(data, type(StringIO(''))))

    def test_large_response(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(200, '-' * http.CHUNK_SIZE)
        status, headers, data = session._handle_response(
            'GET', resp, cache_connection
        )
        self.assertEqual(callback, [])
        self.assertTrue(isinstance(data, http.ResponseBody))

    def test_small_response_with_missed_content_length(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(200, 'foo')
        status, headers, data = session._handle_response(
            'GET', resp, cache_connection
        )
        self.assertEqual(callback, [])
        self.assertTrue(isinstance(data, http.ResponseBody))

    def test_fail_for_400_http_status(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(404, 'foo')
        try:
            session._handle_response('GET', resp, cache_connection)
        except Exception, err:
            self.assertTrue(isinstance(err, http.HTTPError))
            self.assertEqual(err.args[0], (404, 'foo'))
            self.assertEqual(callback, ['hit'])

    def test_head_method_request_got_http_error_status_code(self):
        callback = []
        cache_connection = lambda: callback.append('hit')
        session = http.Session()
        resp = DummyHttpResponse(404, 'foo')
        try:
            session._handle_response('HEAD', resp, cache_connection)
        except Exception, err:
            self.assertTrue(isinstance(err, http.HTTPError))
            self.assertEqual(err.args[0], (404, ''))
            self.assertEqual(callback, ['hit'])


class SessionRequestsTestCase(SessionTestCase):

    def test_handle_perm_redirect(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['perm_redirect']
        status, headers, data = session.request('GET', 'base/redirect')
        self.assertEqual(status, 200)
        self.assertEqual(data.read(), 'OK')

    def test_handle_see_other_redirect(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['see_other']
        status, headers, data = session.request('GET', 'base/redirect')
        self.assertEqual(status, 200)
        self.assertEqual(data.read(), 'OK')

    def test_handle_temp_redirect(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['temp_redirect']
        status, headers, data = session.request('GET', 'base/redirect')
        self.assertEqual(status, 200)
        self.assertEqual(data.read(), 'OK')

    def test_fail_when_maximum_redirect_reached(self):
        def make_request(self, *args, **kwargs):
            return DummyHttpResponse(307, '', {'location': 'base/resource'})
        session = http.Session()
        session._send_request = make_request
        self.assertRaises(http.RedirectLimit, session.request,
                          'GET', 'base/redirect')

    def test_rethrow_4xx_http_error(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['not_found']
        self.assertRaises(http.HTTPError, session.request, 'GET', 'base/404')

    def test_rethrow_5xx_http_error(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['server_error']
        self.assertRaises(http.HTTPError, session.request, 'GET', 'base/500')

    def test_raise_http_error_with_message_from_response_body(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['not_found']
        try:
            session.request('GET', 'base/location')
        except http.HTTPError, err:
            self.assertEqual(err.args[0][1], 'Not Found')

    def test_return_none_response_body_for_head_requests(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['head']
        self.assertEqual(session.request('HEAD', 'base/res')[2], None)

    def test_wrap_small_responses_with_stringio(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['small_data']
        self.assertTrue(
            isinstance(session.request('GET', 'base/res')[2], type(StringIO('')))
        )

    def test_wrap_large_responses_with_reponse_body(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['large_data']
        self.assertTrue(
            isinstance(session.request('GET', 'base/res')[2], http.ResponseBody)
        )

    def test_read_chunked_response(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['chunked']
        status, headers, data = session.request('GET', 'base/res')
        self.assertTrue(isinstance(data, http.ResponseBody))
        self.assertEqual(list(data), ['foo', 'bar', 'baz'])

    def test_chunked_response_could_read_once(self):
        session = http.Session()
        session._send_request = _HTTP_RESPONSES['chunked']
        status, headers, data = session.request('GET', 'base/res')
        self.assertTrue(isinstance(data, http.ResponseBody))
        self.assertEqual(list(data), ['foo', 'bar', 'baz'])
        self.assertEqual(list(data), [])

    def test_make_request_with_empty_body(self):
        session = http.Session()
        conn = DummyHTTPConnection(data='OK')
        resp = session._send_request(conn, 'GET', '/foo/bar?baz=true', None, {})
        self.assertTrue(not conn.was_data_sent)
        self.assertEqual(resp.read(), '')

    def test_make_request_with_string_data(self):
        session = http.Session()
        conn = DummyHTTPConnection(data='OK')
        resp = session._send_request(conn, 'GET', '/foo/bar', 'ping', {'a': 'b'})
        self.assertTrue(conn.was_data_sent)
        self.assertEqual(resp.read(), 'ping')
        self.assertEqual(resp.getheader('a'), 'b')

    def test_make_chunked_request(self):
        session = http.Session()
        data = StringIO('xx' * (http.CHUNK_SIZE))
        headers = {'Transfer-Encoding': 'chunked'}
        conn = DummyHTTPConnection(data='OK')
        session._send_request(conn, 'POST', '/foo/bar', data, headers)
        self.assertEqual(conn.chunks_sent, 3)

    def test_raise_econnreset_for_emtpy_response(self):
        def getresponse():
            raise _httplib.BadStatusLine('')
        session = http.Session()
        conn = DummyHTTPConnection()
        conn.getresponse = getresponse
        try:
            session._send_request(conn, 'GET', '/foo/bar', None, {})
        except socket.error, err:
            self.assertEqual(err.args[0], errno.ECONNRESET)
        else:
            self.fail('Socket error %r expected' % errno.ECONNRESET)

    def test_raise_econnreset_for_emtpy_string_response(self):
        def getresponse():
            raise _httplib.BadStatusLine("''")
        session = http.Session()
        conn = DummyHTTPConnection()
        conn.getresponse = getresponse
        try:
            session._send_request(conn, 'GET', '/foo/bar', None, {})
        except socket.error, err:
            self.assertEqual(err.args[0], errno.ECONNRESET)
        else:
            self.fail('Socket error %r expected' % errno.ECONNRESET)

    def test_retry_request_if_retryable_socket_error_raised(self):
        for error in http.RETRYABLE_ERRORS:
            def getresponse(_=[]):
                if not _:
                    _.append(True)
                    raise socket.error(error)
                else:
                    return _HTTP_RESPONSES['small_data']()
            session = http.Session()
            conn = DummyHTTPConnection()
            conn.getresponse = getresponse
            session._conns['/foo/bar'] = set([conn])
            session.request('GET', '/foo/bar', None, {})

    def test_fail_for_too_many_retries(self):
        for error in http.RETRYABLE_ERRORS:
            def getresponse():
                raise socket.error(error)
            session = http.Session()
            conn = DummyHTTPConnection()
            conn.getresponse = getresponse
            session._conns['/foo/bar'] = set([conn])
            self.assertRaises(socket.error, session.request,
                              'GET', '/foo/bar', None, {})


class ResponseBodyTestCase(unittest.TestCase):

    def test_read_all_data(self):
        """should read all data at once"""
        rbody = http.ResponseBody(
            DummyHttpResponse(200, 'foo-bar-baz'),
            lambda: None
        )
        self.assertEqual(rbody.read(), 'foo-bar-baz')

    def test_read_chunk(self):
        """should read data by sized chunks"""
        rbody = http.ResponseBody(
            DummyHttpResponse(200, 'foo-bar-baz'),
            lambda: None
        )
        self.assertEqual(rbody.read(3), 'foo')
        self.assertEqual(rbody.read(1), '-')
        self.assertEqual(rbody.read(3), 'bar')
        self.assertEqual(rbody.read(1), '-')
        self.assertEqual(rbody.read(3), 'baz')

    def test_readlines(self):
        """should read data line by line"""
        resp = DummyHttpResponse(200, '\n'.join(['foo', 'bar', 'baz']))
        rbody = http.ResponseBody(resp, lambda: None)
        self.assertEqual(list(rbody.readlines()), ['foo\n', 'bar\n', 'baz'])
        for i in rbody.readlines():
            print i

    def test_chunked_response(self):
        """should return True if response has chunked transfer encoding"""
        rbody = http.ResponseBody(
            DummyHttpResponse(200, 'foo', {'Transfer-Encoding': 'chunked'}),
            lambda: None
        )
        self.assertTrue(rbody.is_chunked_transfer())

    def test_iterate_over_lines_of_chunks(self):
        """should iterate over lines for each chunk in chunked response"""
        resp = DummyHttpResponse(
            status=200,
            data='\r\n'.join(['\r\n'.join([hex(len(c)), c])
                              for c in ['foo', 'bar\nbar', 'baz', '']]),
            headers={'Transfer-Encoding': 'chunked'}
        )
        rbody = http.ResponseBody(resp, lambda: None)
        self.assertEqual(list(rbody), ['foo', 'bar', 'bar', 'baz'])

    def test_iterate_over_lines(self):
        """should iterate over lines of data for regular response"""
        resp = DummyHttpResponse(200, '\n'.join(['foo', 'bar', 'baz']))
        rbody = http.ResponseBody(resp, lambda: None)
        self.assertEqual(list(rbody), ['foo\n', 'bar\n', 'baz'])

    def test_is_closed(self):
        """should return True if all data has been read"""
        rbody = http.ResponseBody(
            DummyHttpResponse(200, 'foo-bar-baz'),
            lambda: None
        )
        self.assertTrue(not rbody.is_closed())
        rbody.read()
        self.assertTrue(rbody.is_closed())

    def test_close(self):
        """should close data transfer immediately"""
        rbody = http.ResponseBody(
            DummyHttpResponse(200, 'foo-bar-baz'),
            lambda: None
        )
        rbody.close()
        self.assertTrue(rbody.is_closed())
        self.assertEqual(rbody.read(), '')

    def test_callback(self):
        """should call callback function on close, but only once"""
        def callback():
            callback.count += 1
        callback.count = 0
        rbody = http.ResponseBody(
            DummyHttpResponse(200, 'foo-bar-baz'),
            callback
        )
        rbody.close()
        self.assertEqual(callback.count, 1)
        rbody.close()
        self.assertEqual(callback.count, 1)


if __name__ == '__main__':
    unittest.main()
