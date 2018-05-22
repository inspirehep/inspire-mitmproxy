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

"""Tests for the WhitelistService"""

from os import environ

from mock import patch
from pytest import fixture, raises

from inspire_mitmproxy.dispatcher import Dispatcher
from inspire_mitmproxy.errors import ScenarioNotFound
from inspire_mitmproxy.http import MITMHeaders, MITMRequest
from inspire_mitmproxy.services import BaseService


@fixture
def service_a():
    class TestServiceA(BaseService):
        SERVICE_HOSTS = ['host_a.local']
        active_scenario = None

    return TestServiceA


@fixture
def service_b():
    class TestServiceB(BaseService):
        SERVICE_HOSTS = ['host_b.local']
        active_scenario = None

    return TestServiceB


@fixture(scope='function')
def dispatcher(scenarios_dir, service_a, service_b) -> Dispatcher:
    with patch.object(Dispatcher, 'SERVICE_LIST', [service_a, service_b]):
        return Dispatcher()


@fixture
def scenarios_dir(request):
    with patch.dict(environ, {
        'SCENARIOS_PATH': str(request.fspath.join('../fixtures/scenarios'))
    }):
        yield


def test_base_service_process_request_scenario1(dispatcher, request):
    request_set_config = MITMRequest(
        method='POST',
        url='http://mitm-manager.local/config',
        body='{"active_scenario": "test_scenario1"}',
        headers=MITMHeaders({
            'Host': ['mitm-manager.local'],
            'Accept': ['application/json'],
        })
    )

    request_service_1 = MITMRequest(
        method='GET',
        url='https://host_a.local/api',
        headers=MITMHeaders({
            'Host': ['host_a.local'],
            'Accept': ['application/json'],
        })
    )

    request_service_2 = MITMRequest(
        method='GET',
        url='https://host_b.local/api',
        headers=MITMHeaders({
            'Host': ['host_b.local'],
            'Accept': ['application/json'],
        })
    )

    response_set_config = dispatcher.process_request(request_set_config)
    assert response_set_config.status_code == 201

    response_service_1 = dispatcher.process_request(request_service_1)
    assert response_service_1.body == b'test_scenario1/TestServiceA/0'

    response_service_2 = dispatcher.process_request(request_service_2)
    assert response_service_2.body == b'test_scenario1/TestServiceB/0'


def test_base_service_process_request_scenario2_and_raise(dispatcher, request):
    request_set_config = MITMRequest(
        method='POST',
        url='http://mitm-manager.local/config',
        body='{"active_scenario": "test_scenario2"}',
        headers=MITMHeaders({
            'Host': ['mitm-manager.local'],
            'Accept': ['application/json'],
        })
    )

    request_service_1 = MITMRequest(
        method='GET',
        body='correct body content',
        url='https://host_a.local/api',
        headers=MITMHeaders({
            'Host': ['host_a.local'],
            'Accept': ['application/json'],
        })
    )

    request_service_2 = MITMRequest(
        method='GET',
        url='http://host_b.local/api',
        headers=MITMHeaders({
            'Host': ['host_b.local'],
            'Accept': ['application/json'],
        })
    )

    response_set_config = dispatcher.process_request(request_set_config)
    assert response_set_config.status_code == 201

    response_service_1 = dispatcher.process_request(request_service_1)
    assert response_service_1.body == b'test_scenario2/TestServiceA/0'

    with raises(ScenarioNotFound):
        dispatcher.process_request(request_service_2)
