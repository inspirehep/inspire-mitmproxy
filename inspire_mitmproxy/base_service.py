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

from typing import List
from urllib.parse import urlparse


class BaseService:
    """Mocked service base."""
    SERVICE_HOSTS: List[str] = []

    def handles_request(self, request: dict) -> bool:
        """Can this service handle the request?"""
        try:
            host = request['headers']['Host'][0]
        except KeyError:
            host = urlparse(request['uri']).netloc

        return host in self.SERVICE_HOSTS

    def process_request(self, request: dict) -> dict:
        """Perform operations and give response."""
        return {}
