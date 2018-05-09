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

"""INSPIRE-MITMProxy internal HTTP request representation."""

from socket import getservbyname
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from mitmproxy.http import HTTPRequest

from .headers import MITMHeaders
from .utils import encoding_by_header


class MITMRequest:
    def __init__(
        self,
        url: str,
        method: str = 'GET',
        body: Optional[str] = None,
        headers: Optional[MITMHeaders] = None,
        original_encoding: Optional[str] = None,
        http_version: Optional[str] = None,
    ) -> None:
        self.url = url
        self.method = method
        self.body = body
        self.headers = headers or MITMHeaders({})
        self.original_encoding = original_encoding or encoding_by_header(self.headers)
        self.http_version = http_version or 'HTTP/1.1'

    @classmethod
    def from_mitmproxy(cls, request: HTTPRequest) -> 'MITMRequest':
        encoding = encoding_by_header(MITMHeaders.from_mitmproxy(request.headers))

        return cls(
            url=request.url,
            method=request.method,
            body=request.content.decode(encoding),
            headers=MITMHeaders.from_mitmproxy(request.headers),
            original_encoding=encoding,
            http_version=request.http_version,
        )

    @classmethod
    def from_dict(cls, request: Dict[str, Any]) -> 'MITMRequest':
        encoding = encoding_by_header(MITMHeaders.from_dict(request['headers']))

        return cls(
            url=request['uri'],
            method=request['method'],
            body=request['body'],
            headers=MITMHeaders.from_dict(request['headers']),
            original_encoding=encoding,
        )

    def to_mitmproxy(self) -> HTTPRequest:
        parsed_url = urlparse(self.url)

        return HTTPRequest(
            first_line_format='absolute',
            method=self.method,
            scheme=parsed_url.scheme,
            host=parsed_url.hostname,
            port=parsed_url.port or getservbyname(parsed_url.scheme),
            path=parsed_url.path,
            http_version=self.http_version,
            headers=self.headers.to_mitmproxy(),
            content=self.body.encode(self.original_encoding),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'method': self.method,
            'uri': self.url,
            'body': self.body,
            'headers': self.headers.to_dict(),
        }

    def __eq__(self, other) -> bool:
        return (
            self.url == other.url
            and self.method == other.method
            and self.body == other.body
            and self.headers == other.headers
        )

    def __repr__(self):
        return f'MITMRequest("{self.url}", "{self.method}", ' \
            f'headers={self.headers}, body="{self.body}")'
