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

"""Service used to orchestrate fake services."""

from autosemver import get_current_version
from json import dumps as json_dumps
from mitmproxy.net.http.status_codes import RESPONSES
from os import getcwd
from typing import List, Union
from urllib.parse import urlparse

from .base_service import BaseService
from .errors import RequestNotHandledInService


class ManagementService(BaseService):
    def __init__(self, services: List[BaseService]) -> None:
        self.services = services

    def process_request(self, request: dict) -> dict:
        parsed_url = urlparse(request['uri'])
        path = parsed_url.path
        method = request['method']

        if path == '/services' and method == 'GET':
            return self.build_response(200, self.get_services())
        elif path == '/scenarios' and method == 'GET':
            return self.build_response(201, self.get_scenarios())

        raise RequestNotHandledInService(self, request)

    def get_services(self) -> dict:
        return {
            idx: {
                'class': type(service).__name__,
                'service_hosts': service.SERVICE_HOSTS,
            }
            for idx, service in enumerate([self] + self.services)
        }

    def get_scenarios(self) -> dict:
        return NotImplemented


    def build_response(self, code: int, json_message: Union[dict, list]) -> dict:
        return {
            'status': {
                'message': RESPONSES[code],
                'code': code,
            },
            'body': json_dumps(json_message, indent=2),
            'headers': {
                'Content-Type': ['application/json'],
                'Server': ['inspire-mitmproxy/' + get_current_version(getcwd())]
            }
        }
