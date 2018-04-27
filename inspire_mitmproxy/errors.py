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

"""INSPIRE-MITMProxy Errors"""

from .base_service import BaseService


class NoServicesForRequest(Exception):
    def __init__(self, request: dict) -> None:
        message = "None of the registered services can handle this request: %s" % request
        super().__init__(message)


class RequestNotHandledInService(Exception):
    def __init__(self, service: BaseService, request: dict):
        message = "%s can't handle the request %s" % (service, request)
        super().__init__(message)
