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

from typing import Any, Dict, Optional

from mitmproxy.http import HTTPResponse
from mitmproxy.net.http.status_codes import RESPONSES

from .headers import MITMHeaders
from .utils import encoding_by_header


class MITMResponse:
    def __init__(
        self,
        status_code: int = 200,
        status_message: Optional[str] = None,
        body: Optional[str] = None,
        headers: Optional[MITMHeaders] = None,
        original_encoding: Optional[str] = None,
        http_version: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.status_message = status_message or RESPONSES[status_code]
        self.body = body
        self.headers = headers or MITMHeaders({})
        self.http_version = http_version or 'HTTP/1.1'
        self.original_encoding = original_encoding or encoding_by_header(self.headers)

    @classmethod
    def from_mitmproxy(cls, response: HTTPResponse) -> 'MITMResponse':
        encoding = encoding_by_header(MITMHeaders.from_mitmproxy(response.headers))

        return cls(
            status_code=response.status_code,
            status_message=response.reason,
            body=response.content.decode(encoding),
            headers=MITMHeaders.from_mitmproxy(response.headers),
            original_encoding=encoding,
            http_version=response.http_version,
        )

    @classmethod
    def from_dict(cls, response: Dict[str, Any]) -> 'MITMResponse':
        encoding = encoding_by_header(MITMHeaders.from_dict(response['headers']))

        body = response['body']
        if isinstance(body, bytes):
            body = body.decode(encoding)

        return cls(
            status_code=response['status']['code'],
            status_message=response['status']['message'],
            body=body,
            headers=MITMHeaders.from_dict(response['headers']),
            original_encoding=encoding
        )

    def to_mitmproxy(self) -> HTTPResponse:
        return HTTPResponse(
            http_version='HTTP/1.1',
            status_code=self.status_code,
            reason=self.status_message,
            headers=self.headers.to_mitmproxy(),
            content=self.body.encode(self.original_encoding),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': {
                'code': self.status_code,
                'message': self.status_message,
            },
            'body': self.body,
            'headers': self.headers.to_dict(),
        }

    def __eq__(self, other) -> bool:
        return (
            self.status_code == other.status_code
            and self.body == other.body
            and self.headers == other.headers
        )

    def __repr__(self):
        return f'MITMResponse({self.status_code}, "{self.status_message}", ' \
            f'headers={self.headers}, body="{self.body}")'
