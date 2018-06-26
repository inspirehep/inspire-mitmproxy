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

"""Priority-ordered list of services for the proxy."""

from typing import Any, Dict, List

from .errors import InvalidServiceParams, InvalidServiceType
from .services.base_service import BaseService
from .services.whitelist_service import WhitelistService


SERVICE_TYPENAME_TO_CLASS_MAP = {
    'BaseService': BaseService,
    'WhitelistService': WhitelistService,
}


class ServiceList:
    def __init__(self, service_list: List[BaseService]) -> None:
        self._service_list = service_list

    def replace_from_descrition(self, service_list: List[Dict[str, Any]]):
        self._service_list = [
            self._instantiate_service_from_dict(description)
            for description in service_list
        ]

    def prepend(self, *args: BaseService):
        self._service_list = list(args) + self._service_list

    def _instantiate_service_from_dict(self, description: Dict[str, Any]) -> BaseService:
        service_typename = description.pop('type', 'BaseService')

        try:
            service_class = SERVICE_TYPENAME_TO_CLASS_MAP[service_typename]
        except KeyError:
            raise InvalidServiceType(service_typename)

        try:
            return service_class(**description)
        except TypeError:
            raise InvalidServiceParams(service_typename, description)

    def to_list(self) -> List[Dict[str, Any]]:
        return [service.to_dict() for service in self._service_list]

    def __iter__(self):
        return iter(self._service_list)

    def __repr__(self):
        return f'ServiceList({self._service_list!r})'
