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

"""Dispatcher forwards requests to Services."""

from logging import getLogger
from typing import List, Type, cast

from mitmproxy.http import HTTPFlow, HTTPResponse

from .errors import DoNotIntercept, NoServicesForRequest
from .http import MITMRequest, MITMResponse
from .services import ArxivService, BaseService, LegacyService, ManagementService, WhitelistService


logger = getLogger(__name__)


class Dispatcher:
    SERVICE_LIST: List[Type[BaseService]] = [
        ArxivService,
        LegacyService,
        WhitelistService,
    ]

    def __init__(self) -> None:
        self.services = [service_class() for service_class in self.SERVICE_LIST]
        mgmt_service = ManagementService(self.services)
        self.services = [cast(BaseService, mgmt_service)] + self.services

    def process_request(self, request: MITMRequest) -> MITMResponse:
        """Perform operations and give response."""
        for service in self.services:
            if service.handles_request(request):
                return service.process_request(request)
        raise NoServicesForRequest(request)

    def request(self, flow: HTTPFlow):
        """MITMProxy addon event interface for outgoing request."""
        try:
            request = MITMRequest.from_mitmproxy(flow.request)
            response = self.process_request(request).to_mitmproxy()
            flow.response = response
        except DoNotIntercept as e:
            # Let the request pass through, by not interrupting the flow, but log it
            logger.warning(str(e))
        except Exception as e:
            flow.response = HTTPResponse.make(
                status_code=getattr(e, 'http_status_code', 500),
                content=str(e),
                headers={'Content-Type': 'text/plain'}
            )
