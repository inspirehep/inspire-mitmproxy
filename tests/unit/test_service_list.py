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

"""Tests for the ServiceList."""

from typing import Any, Dict

from pytest import mark

from inspire_mitmproxy.service_list import ServiceList
from inspire_mitmproxy.services.base_service import BaseService
from inspire_mitmproxy.services.whitelist_service import WhitelistService


def test_service_list_replace_from_decription():
    expected = [
        BaseService(name='ReplacedService', hosts_list=['replaced_host.local']),
        WhitelistService(name='WhitelistService', hosts_list=['whitelist_me.local']),
    ]

    service_list = ServiceList([
        BaseService(name='OriginalService', hosts_list=['original_host.local']),
    ])

    service_list.replace_from_descrition([
        {
            'type': 'BaseService',
            'name': 'ReplacedService',
            'hosts_list': ['replaced_host.local'],
        },
        {
            'type': 'WhitelistService',
            'name': 'WhitelistService',
            'hosts_list': ['whitelist_me.local'],
        }
    ])

    assert list(service_list) == expected


def test_service_list_prepend():
    expected = [
        BaseService(name='Service', hosts_list=['host.local']),
        WhitelistService(name='WhitelistService', hosts_list=['whitelist_me.local']),
    ]

    service_list = ServiceList([
        WhitelistService(name='WhitelistService', hosts_list=['whitelist_me.local']),
    ])

    service_list.prepend(BaseService(name='Service', hosts_list=['host.local']))

    assert list(service_list) == expected


@mark.parametrize(
    'service_description, expected_service',
    [
        (
            {
                'type': 'BaseService',
                'name': 'TestName',
                'hosts_list': ['test_host.local', 'test_host2.local'],
            },
            BaseService(name='TestName', hosts_list=['test_host.local', 'test_host2.local']),
        ),
        (
            {
                'name': 'TestName',
                'hosts_list': ['test_host.local'],
            },
            BaseService(name='TestName', hosts_list=['test_host.local']),
        ),
        (
            {
                'type': 'WhitelistService',
                'name': 'TestWhitelist',
                'hosts_list': ['test_host.local'],
            },
            WhitelistService(name='TestWhitelist', hosts_list=['test_host.local']),
        ),
    ],
    ids=(
        'base service with two hosts',
        'base service with implicit BaseService type',
        'whitelist service',
    )
)
def test_service_list_instantiate_service_from_dict(
    service_description: Dict[str, Any],
    expected_service: BaseService,
):
    service_list = ServiceList([])

    result_service = service_list._instantiate_service_from_dict(service_description)

    assert expected_service == result_service


def test_service_list_to_dict():
    service_list = ServiceList([
        BaseService(name='TestName', hosts_list=['test_host.local', 'test_host2.local']),
        WhitelistService(name='TestWhitelist', hosts_list=['test_host.local']),
    ])

    expected_description = [
        {
            'type': 'BaseService',
            'name': 'TestName',
            'hosts_list': ['test_host.local', 'test_host2.local'],
        },
        {
            'type': 'WhitelistService',
            'name': 'TestWhitelist',
            'hosts_list': ['test_host.local'],
        },
    ]

    result_service = service_list.to_list()

    assert expected_description == result_service
