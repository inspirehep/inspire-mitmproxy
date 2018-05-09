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

"""INSPIRE-MITMProxy headers wrapper."""

from copy import copy, deepcopy
from typing import Dict, List

from mitmproxy.net.http.headers import Headers


class MITMHeaders:
    def __init__(self, headers: Dict[str, List[str]]) -> None:
        self.headers: Dict[str, List[str]] = {}
        for header_name, header_value in headers.items():
            header_name = header_name.title()
            self.headers[header_name] = copy(header_value)

    @classmethod
    def from_dict(cls, headers_dict: Dict[str, List[str]]) -> 'MITMHeaders':
        return cls(headers=headers_dict)

    @classmethod
    def from_mitmproxy(cls, headers: Headers) -> 'MITMHeaders':
        header_dict: Dict[str, List[str]] = {}

        for key, value in headers.fields:
            key, value = key.decode('ascii'), value.decode('ascii')

            if key in header_dict:
                header_dict[key].append(value)
            else:
                header_dict[key] = [value]

        return cls(headers=header_dict)

    def to_dict(self) -> Dict[str, List[str]]:
        return deepcopy(self.headers)

    def to_mitmproxy(self) -> Headers:
        fields = []

        for key, values in self.headers.items():
            for value in values:
                fields.append(
                    (key.encode('ascii'), value.encode('ascii'))
                )

        return Headers(fields=fields)

    def __getitem__(self, item: str) -> str:
        try:
            return self.headers[item.title()][0]
        except IndexError:
            raise KeyError(item.title())

    def __eq__(self, other) -> bool:
        return self.headers == other.headers

    def __repr__(self):
        return f'MITMHeaders(headers={repr(self.headers)})'
