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

"""Tests for the ManagementService"""

from os import environ

from mock import patch
from pytest import fixture, mark, raises

from inspire_mitmproxy.base_service import BaseService
from inspire_mitmproxy.errors import InvalidRequest
from inspire_mitmproxy.management_service import ManagementService


@fixture(scope='function')
def management_service() -> ManagementService:
    class TestService(BaseService):
        SERVICE_HOSTS = ['test-service.local']

    mgmt_service = ManagementService([TestService()])

    mgmt_service.config = {
        'active_scenario': None,
        'a_setting': 'value',
    }

    return mgmt_service


@fixture
def fake_scenarios_dir(tmpdir) -> str:
    scenarios = tmpdir.mkdir('scenarios')

    scenario1 = scenarios.mkdir('scenario1')
    scenario2 = scenarios.mkdir('scenario2')

    scenario1_serviceA = scenario1.mkdir('A')
    scenario2_serviceA = scenario2.mkdir('A')
    scenario2_serviceB = scenario2.mkdir('B')

    scenario1_serviceA.join('1.yaml').ensure()
    scenario1_serviceA.join('2.yaml').ensure()

    scenario2_serviceA.join('1.yaml').ensure()
    scenario2_serviceB.join('1.yaml').ensure()
    scenario2_serviceB.join('2.yaml').ensure()
    scenario2_serviceB.join('3.yaml').ensure()

    environ['SCENARIOS_PATH'] = scenarios.strpath
    return scenarios.strpath


def test_management_service_get_services(management_service):
    result = management_service.get_services()
    expected = {
        0: {
            'class': 'ManagementService',
            'service_hosts': ['mitm-manager.local']
        },
        1: {
            'class': 'TestService',
            'service_hosts': ['test-service.local']
        }
    }

    assert expected == result


def test_management_service_get_scenarios(fake_scenarios_dir, management_service):
    result = management_service.get_scenarios()
    expected = {
        'scenario1': {
            'responses': {
                'A': ['1.yaml', '2.yaml'],
            }
        },
        'scenario2': {
            'responses': {
                'A': ['1.yaml'],
                'B': ['1.yaml', '2.yaml', '3.yaml'],
            }
        },
    }

    assert expected == result


def test_management_service_get_config(management_service):
    result = management_service.get_config()
    expected = {
        'active_scenario': None,
        'a_setting': 'value',
    }

    assert expected == result


def test_management_service_put_config(management_service):
    management_service.put_config({
        'body': '{"active_scenario": "a scenario"}'
    })
    result = management_service.config

    expected = {
        'active_scenario': 'a scenario',
        'a_setting': 'value',
    }

    assert expected == result


@mark.parametrize(
    '_request',
    [
        {'body': 'definitely not valid JSON'},
        {'body': '["parses as valid json, but is not a dict update"]'},
    ],
)
def test_management_service_put_config_malformed_raises(management_service, _request):
    with raises(InvalidRequest):
        management_service.put_config(_request)


def test_management_service_post_config(management_service):
    management_service.post_config({
        'body': '{"active_scenario": "a scenario"}'
    })
    result = management_service.config

    expected = {
        'active_scenario': 'a scenario',
    }

    assert expected == result


def test_management_service_post_config_malformed_raises(management_service):
    with raises(InvalidRequest):
        management_service.post_config({
            'body': 'definitely not valid JSON'
        })


@mark.xfail
def test_management_service_post_config_array_raises(management_service):
    with raises(InvalidRequest):
        management_service.post_config({
            'body': '["parses as valid json, but is not a dict update"]'
        })


def test_management_service_build_response(management_service):
    with patch('inspire_mitmproxy.management_service.get_current_version', return_value='0.0.1'):
        result = management_service.build_response(201, json_message={'test': 'message'})

    expected = {
        'body': '{\n  "test": "message"\n}',
        'headers': {
            'Content-Type': ['application/json'],
            'Server': ['inspire-mitmproxy/0.0.1'],
        },
        'status': {
            'code': 201,
            'message': 'Created',
        }
    }

    assert expected == result
