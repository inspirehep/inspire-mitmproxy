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

"""Tools to convert between responses and request formats."""

from cgi import parse_header
from typing import Dict, List

from mitmproxy.http import HTTPRequest, HTTPResponse
from mitmproxy.net.http.headers import Headers


def request_to_dict(request: HTTPRequest) -> dict:
    encoding = encoding_by_header('Accept', request.headers)

    return {
        'method': request.method,
        'uri': request.url,
        'body': request.content.decode(encoding),
        'headers': {
            k: request.headers.get_all(k)
            for k in request.headers.keys()
        },
    }


def dict_to_response(response: dict) -> HTTPResponse:
    headers = dict_to_headers(response['headers'])
    encoding = encoding_by_header('content-type', headers)

    content = response['body']
    if isinstance(content, str):
        content = content.encode(encoding)

    return HTTPResponse(
        http_version='HTTP/1.1',
        status_code=response['status']['code'],
        reason=response['status']['message'].encode('ascii'),
        headers=headers,
        content=content,
    )


def headers_to_dict(headers: Headers) -> dict:
    header_dict: Dict[str, List[str]] = {}

    for key, value in headers.fields:
        key, value = key.decode('ascii'), value.decode('ascii')

        if key in header_dict:
            header_dict[key].append(value)
        else:
            header_dict[key] = [value]

    return header_dict


def dict_to_headers(headers: dict) -> Headers:
    fields = []

    for key, values in headers.items():
        for value in values:
            fields.append(
                (key.encode('ascii'), value.encode('ascii'))
            )

    return Headers(fields=fields)


def encoding_by_header(header_name: str, headers: Headers) -> str:
    """Extract charset param from Content-Type or Accept headers"""
    try:
        content_type = headers[header_name]
        _, params = parse_header(content_type)
        return params['charset']
    except KeyError:
        return 'utf-8'
