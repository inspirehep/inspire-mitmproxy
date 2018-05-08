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


class MITMProxyHTTPError(Exception):
    http_status_code = 500


class NoServicesForRequest(MITMProxyHTTPError):
    def __init__(self, request: dict) -> None:
        self.http_status_code = 501
        message = "None of the registered services can handle this request: %s" % request
        super().__init__(message)


class RequestNotHandledInService(MITMProxyHTTPError):
    def __init__(self, service_name: str, request: dict) -> None:
        self.http_status_code = 501
        message = "%s can't handle the request %s" % (service_name, request)
        super().__init__(message)


class InvalidRequest(MITMProxyHTTPError):
    def __init__(self, service_name: str, request: dict) -> None:
        self.http_status_code = 400
        message = "Invalid request %s for service %s" % (request, service_name)
        super().__init__(message)


class DoNotIntercept(Exception):
    def __init__(self, service_name: str, request: dict) -> None:
        message = "Allow request %s in %s to pass through to the outside" % (request, service_name)
        super().__init__(message)


class NoMatchingRecording(MITMProxyHTTPError):
    def __init__(self, service_name: str, request: dict) -> None:
        self.http_status_code = 501
        message = "Service %s cannot handle this request: %s" % (service_name, request)
        super().__init__(message)


class ScenarioNotFound(MITMProxyHTTPError):
    def __init__(self, service_name: str, scenario: str) -> None:
        self.http_status_code = 501
        message = "Scenario %s not found in service %s" % (scenario, service_name)
        super().__init__(message)


class ScenarioUndefined(MITMProxyHTTPError):
    def __init__(self, service_name: str) -> None:
        self.http_status_code = 501
        message = "Scenario not set in service %s" % (service_name)
        super().__init__(message)
