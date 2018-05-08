# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE-MITMPROXY.
# Copyright (C) 2018 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from mitmproxy.http import HTTPRequest, HTTPResponse
from mitmproxy.net.http.headers import Headers

from inspire_mitmproxy.translator import (
    dict_to_headers,
    dict_to_response,
    encoding_by_header,
    headers_to_dict,
    request_to_dict
)

TEST_DICT_RESPONSE = {
    'status': {
        'code': 200,
        'message': 'OK',
    },
    'body': 'Witaj, świecie!',
    'headers': {
        'content-type': ['text/plain; charset=ISO-8859-2'],
        'date': ['Wed, 21 Mar 2018 12:47:18 GMT'],
        'server': ['nginx/1.12.2'],
    }
}

TEST_DICT_RESPONSE_WITH_BYTES_BODY = {
    'status': {
        'code': 200,
        'message': 'OK',
    },
    'body': b'Witaj, \xb6wiecie!',
    'headers': {
        'content-type': ['text/plain; charset=ISO-8859-2'],
        'date': ['Wed, 21 Mar 2018 12:47:18 GMT'],
        'server': ['nginx/1.12.2'],
    }
}


TEST_MITM_RESPONSE = HTTPResponse(
    http_version='HTTP/1.1',
    status_code=200,
    reason='OK',
    headers=Headers(
        fields=[
            (b'content-type', b'text/plain; charset=ISO-8859-2'),
            (b'date', b'Wed, 21 Mar 2018 12:47:18 GMT'),
            (b'server', b'nginx/1.12.2'),
        ]
    ),
    content=b'Witaj, \xb6wiecie!',
)


TEST_DICT_REQUEST = {
    'body': '{"message": "Witaj, świecie!"}',
    'headers': {
        'Accept': ['application/json; charset=UTF-8'],
        'Accept-Encoding': ['gzip, deflate'],
        'Connection': ['keep-alive'],
        'User-Agent': ['python-requests/2.18.4'],
    },
    'method': 'GET',
    'uri': 'http://127.0.0.1/test',
}


TEST_MITM_REQUEST = HTTPRequest(
    first_line_format='absolute',
    method='GET',
    scheme='http',
    host='127.0.0.1',
    port=80,
    path='/test',
    http_version='HTTP/1.1',
    headers=[
        (b'Accept', b'application/json; charset=UTF-8'),
        (b'Accept-Encoding', b'gzip, deflate'),
        (b'Connection', b'keep-alive'),
        (b'User-Agent', b'python-requests/2.18.4'),
    ],
    content=b'{"message": "Witaj, \xc5\x9bwiecie!"}'
)


TEST_DICT_HEADERS = {
    'content-type': ['text/plain; charset=ASCII'],
    'access-control-expose-headers': [
        'Content-Type, ETag, Link, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, '
        'X-Multiple-Values',
    ],
    'x-multiple-values': [
        'Value1',
        'Value2',
    ]
}


TEST_MITM_HEADERS = Headers(
    fields=[
        (b'content-type', b'text/plain; charset=ASCII'),
        (b'access-control-expose-headers', b'Content-Type, ETag, Link, X-RateLimit-Limit, '
            b'X-RateLimit-Remaining, X-RateLimit-Reset, X-Multiple-Values'),
        (b'x-multiple-values', b'Value1'),
        (b'x-multiple-values', b'Value2'),
    ]
)


def test_dict_to_headers():
    expected = TEST_MITM_HEADERS
    result = dict_to_headers(TEST_DICT_HEADERS)

    assert expected == result


def test_headers_to_dict():
    expected = TEST_DICT_HEADERS
    result = headers_to_dict(TEST_MITM_HEADERS)

    assert expected == result


def test_dict_to_response():
    result = dict_to_response(TEST_DICT_RESPONSE)
    expected = TEST_MITM_RESPONSE

    assert result == expected


def test_dict_to_response_with_bytes_body():
    result = dict_to_response(TEST_DICT_RESPONSE_WITH_BYTES_BODY)
    expected = TEST_MITM_RESPONSE

    assert result == expected


def test_response_to_dict():
    result = request_to_dict(TEST_MITM_REQUEST)
    expected = TEST_DICT_REQUEST

    assert result == expected


def test_encoding_by_header():
    result = encoding_by_header('content-type', TEST_MITM_HEADERS)
    expected = 'ASCII'

    assert result == expected
