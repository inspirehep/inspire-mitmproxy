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

"""Base for fake services."""

from os import environ
from pathlib import Path
from typing import Dict, List, Optional, Union, cast
from urllib.parse import splitport  # type: ignore
from urllib.parse import urlparse

from yaml import load as yaml_load

from ..errors import NoMatchingRecording, ScenarioNotFound, ScenarioUndefined
from ..http import MITMRequest, MITMResponse


Interaction = Dict[str, Union[MITMRequest, MITMResponse]]


class BaseService:
    """Mocked service base."""
    SERVICE_HOSTS: List[str] = []
    active_scenario: Optional[str] = None

    @property
    def name(self):
        return type(self).__name__

    def handles_request(self, request: MITMRequest) -> bool:
        """Can this service handle the request?"""
        try:
            host = splitport(request.headers['Host'])[0]
        except (TypeError, KeyError):
            host = urlparse(request.url).hostname

        return host in self.SERVICE_HOSTS

    def process_request(self, request: MITMRequest) -> MITMResponse:
        """Perform operations and give response."""
        for recorded_response in self.get_interactions_for_active_scenario():
            if self.match_request(request, cast(MITMRequest, recorded_response['request'])):
                return cast(MITMResponse, recorded_response['response'])

        raise NoMatchingRecording(self.name, request)

    def match_request(self, incoming_request: MITMRequest, recorded_request: MITMRequest) -> bool:
        parsed_incoming_uri = urlparse(incoming_request.url)
        parsed_recorded_uri = urlparse(recorded_request.url)

        return (
            incoming_request.method == recorded_request.method
            and parsed_incoming_uri == parsed_recorded_uri
            and incoming_request.body == recorded_request.body
        )

    def get_interactions_for_active_scenario(self) -> List[Interaction]:
        """Get a list of scenarios"""
        if not self.active_scenario:
            raise ScenarioUndefined(self.name)

        scenarios_path = Path(environ.get('SCENARIOS_PATH', './scenarios/'))
        responses_dir = scenarios_path / self.active_scenario / self.name

        if not responses_dir.exists():
            raise ScenarioNotFound(self.name, self.active_scenario)

        responses = [
            self._get_interaction_from_file(response)
            for response in responses_dir.iterdir()
            if response.is_file() and response.suffix == '.yaml'
        ]

        return responses

    @staticmethod
    def _get_interaction_from_file(response_file: Path) -> Interaction:
        text = response_file.read_text()  # type: ignore
        pair = yaml_load(text)
        return {
            'request': MITMRequest.from_dict(pair['request']),
            'response': MITMResponse.from_dict(pair['response']),
        }
