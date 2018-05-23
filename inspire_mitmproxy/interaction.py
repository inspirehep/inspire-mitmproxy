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

"""Load/dump interaction files."""

from os.path import expandvars
from pathlib import Path
from re import compile
from threading import Timer
from typing import Dict, List, Optional, Pattern, Union

import requests
from yaml import load as yaml_load

from .http import MITMRequest, MITMResponse


class Interaction:
    DEFAULT_EXACT_MATCH_FIELDS: List[str] = ['url', 'method', 'body']
    DEFAULT_REGEX_MATCH_FIELDS: Dict[str, Pattern[str]] = {}
    DEFAULT_CALLBACK_DELAY = 0.5

    def __init__(
        self,
        request: MITMRequest,
        response: MITMResponse,
        match: Optional[dict],
        callbacks: Optional[List[dict]],
    ) -> None:
        self.request = request
        self.response = response
        self.match = match or {}
        self.callbacks = callbacks or []

    @classmethod
    def from_file(cls, interaction_file: Optional[Path]) -> 'Interaction':
        interaction_string = interaction_file.read_text()  # type: ignore
        interaction_dict = yaml_load(interaction_string)

        return cls(
            request=MITMRequest.from_dict(interaction_dict['request']),
            response=MITMResponse.from_dict(interaction_dict['response']),
            match=interaction_dict.get('match'),
            callbacks=interaction_dict.get('callbacks'),
        )

    @property
    def exact_match_fields(self) -> List[str]:
        if not self.match:
            return self.DEFAULT_EXACT_MATCH_FIELDS

        try:
            return self.match['exact']
        except KeyError:
            return []

    @property
    def regex_match_fields(self) -> Dict[str, Pattern[str]]:
        if not self.match:
            return self.DEFAULT_REGEX_MATCH_FIELDS

        try:
            regexes = self.match['regex']
            return {field: compile(regex) for field, regex in regexes.items()}
        except KeyError:
            return {}

    def _matches_by_exact_rules(self, request: MITMRequest) -> bool:
        for match_on in self.exact_match_fields:
            if self.request[match_on] != request[match_on]:
                return False

        return True

    def _matches_by_regex_rules(self, request: MITMRequest) -> bool:
        for match_on, regex in self.regex_match_fields.items():
            if not regex.match(request[match_on]):
                return False

        return True

    def matches_request(self, request: MITMRequest) -> bool:
        return self._matches_by_exact_rules(request) and self._matches_by_regex_rules(request)

    @staticmethod
    def execute_callback(request: MITMRequest, delay: Union[int, float]):
        def execute_request(_request: MITMRequest):
            requests.request(
                method=request.method,
                url=expandvars(request.url),
                data=request.body,
                headers={
                    key: expandvars(request.headers[key])
                    for key in request.headers.keys()
                },
                timeout=10,
            )

        timer = Timer(delay, execute_request, args=[request])
        timer.start()

    def execute_callbacks(self):
        for callback in self.callbacks:
            request = MITMRequest.from_dict(callback['request'])
            self.execute_callback(
                request=request,
                delay=callback.get('delay', self.DEFAULT_CALLBACK_DELAY)
            )
