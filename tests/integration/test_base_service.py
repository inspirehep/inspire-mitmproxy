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
from inspire_mitmproxy.services import BaseService


@fixture
def service_a():
    class TestServiceA(BaseService):
        SERVICE_HOSTS = ['host_a.local']
        active_scenario = None

    return TestServiceA()


@fixture
def service_b():
    class TestServiceB(BaseService):
        SERVICE_HOSTS = ['host_b.local']
        active_scenario = None

    return TestServiceB()


@fixture(scope='function')
def dispatcher(scenarios_dir, service_a, service_b) -> Dispatcher:
    return Dispatcher([service_a, service_b])


@fixture
def scenarios_dir(request):
    with patch.dict(environ, {
        'SCENARIOS_PATH': str(request.fspath.join('../fixtures/scenarios'))
    }):
        yield


def test_base_service_process_request_scenario1(dispatcher, request):
    response_set_config = dispatcher.process_request({
        'method': 'POST',
        'uri': 'http://mitm-manager.local/config',
        'body': '{"active_scenario": "test_scenario1"}',
        'headers': {
            'Host': ['mitm-manager.local'],
            'Accept': ['application/json'],
        }
    })

    assert response_set_config['status']['code'] == 201

    response_service_1 = dispatcher.process_request({
        'method': 'GET',
        'uri': 'https://host_a.local/api',
        'body': None,
        'headers': {
            'Host': ['host_a.local'],
            'Accept': ['application/json'],
        }
    })

    assert response_service_1['body'] == 'test_scenario1/TestServiceA/0'

    response_service_2 = dispatcher.process_request({
        'method': 'GET',
        'uri': 'https://host_b.local/api',
        'body': None,
        'headers': {
            'Host': ['host_b.local'],
            'Accept': ['application/json'],
        }
    })

    assert response_service_2['body'] == 'test_scenario1/TestServiceB/0'


def test_base_service_process_request_scenario2_and_raise(dispatcher, request):
    response_set_config = dispatcher.process_request({
        'method': 'POST',
        'uri': 'http://mitm-manager.local/config',
        'body': '{"active_scenario": "test_scenario2"}',
        'headers': {
            'Host': ['mitm-manager.local'],
            'Accept': ['application/json'],
        }
    })

    assert response_set_config['status']['code'] == 201

    response_service_1 = dispatcher.process_request({
        'method': 'GET',
        'uri': 'https://host_a.local/api',
        'body': None,
        'headers': {
            'Host': ['host_a.local'],
            'Accept': ['application/json'],
        }
    })

    assert response_service_1['body'] == 'test_scenario2/TestServiceA/0'

    with raises(ScenarioNotFound):
        dispatcher.process_request({
            'method': 'GET',
            'uri': 'https://host_b.local/api',
            'body': None,
            'headers': {
                'Host': ['host_b.local'],
                'Accept': ['application/json'],
            }
        })
