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
from typing import List, Optional

from mitmproxy.http import HTTPFlow, HTTPResponse

from .errors import DoNotIntercept, NoServicesForRequest
from .http import MITMRequest, MITMResponse
from .service_list import ServiceList
from .services.base_service import BaseService
from .services.management_service import ManagementService
from .services.whitelist_service import WhitelistService


logger = getLogger(__name__)


class Dispatcher:
    DEFAULT_SERVICE_LIST: List[BaseService] = [
        BaseService(
            name='ArxivService',
            hosts_list=['arxiv.org', 'export.arxiv.org'],
        ),
        BaseService(
            name='LegacyService',
            hosts_list=['inspirehep.net'],
        ),
        BaseService(
            name='RTService',
            hosts_list=['inspirevm13.cern.ch', 'rt.inspirehep.net'],
        ),
        WhitelistService(
            name='WhitelistService',
            hosts_list=['test-indexer', 'test-scrapyd', 'test-web-e2e.local'],
        ),
    ]

    def __init__(self, service_list: Optional[List[BaseService]]=None) -> None:
        self.services = ServiceList(service_list or self.DEFAULT_SERVICE_LIST)
        mgmt_service = ManagementService(self.services)
        self.services.prepend(mgmt_service)

    def find_service_for_request(self, request: MITMRequest) -> BaseService:
        for service in self.services:
            if service.handles_request(request):
                return service
        raise NoServicesForRequest(request)

    def process_request(self, request: MITMRequest) -> MITMResponse:
        """Perform operations and give response."""
        service = self.find_service_for_request(request)
        return service.process_request(request)

    def process_response(self, request: MITMRequest, response: MITMResponse):
        """Hook for live responses."""
        service = self.find_service_for_request(request)
        service.process_response(request=request, response=response)

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

    def response(self, flow: HTTPFlow):
        if self.is_flow_passed_through(flow):
            request = MITMRequest.from_mitmproxy(flow.request)
            response = MITMResponse.from_mitmproxy(flow.response)
            self.process_response(request, response)

    @staticmethod
    def is_flow_passed_through(flow: HTTPFlow) -> bool:
        return flow.server_conn.connected()
