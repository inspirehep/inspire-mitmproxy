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

"""Test BaseService"""

from os import environ

from mock import patch
from pytest import fixture, mark, raises

from inspire_mitmproxy.errors import NoMatchingRecording
from inspire_mitmproxy.http import MITMHeaders, MITMRequest, MITMResponse
from inspire_mitmproxy.services import BaseService


@fixture
def service():
    class TestService(BaseService):
        SERVICE_HOSTS = ['host_a.local', 'host_b.local']
        active_scenario = 'test_scenario1'

    return TestService()


@fixture
def scenarios_dir(request):
    with patch.dict(environ, {
        'SCENARIOS_PATH': str(request.fspath.join('../fixtures/scenarios'))
    }):
        yield


@fixture
def sample_request(request) -> MITMRequest:
    return MITMRequest(
        body='body content',
        headers=MITMHeaders({
            'Accept': ['text/plain'],
            'Connection': ['keep-alive'],
            'User-Agent': ['python-requests/2.18.4']
        }),
        method='GET',
        url='https://domain.local/path;param?query=value',
    )


@mark.parametrize(
    'request_, handled',
    [
        ({'uri': 'http://host_a.local/api', 'headers': {'Host': ['host_a.local']}}, True),
        ({'uri': 'http://host_b.local/api', 'headers': {'Host': ['host_b.local']}}, True),
        ({'uri': 'http://wrong.local/api', 'headers': {'Host': ['host_a.local']}}, True),
        ({'uri': 'http://host_a.local/api', 'headers': {'Host': ['wrong.local']}}, False),
        ({'uri': 'http://host_a.local/api', 'headers': {}}, True),
        ({'uri': 'http://wrong.local/api', 'headers': {'Host': ['wrong.local']}}, False),
    ],
    ids=[
        'check first, Host and URI matching: should be handled',
        'check second, Host and URI matching: should be handled',
        'Host matching, URI not: should be handled',
        'URI matching, Host not: should not be handled',
        'URI matching, Host undefined: should be handled',
        'URI and Host both not matching: should not be handled',
    ]
)
def test_base_service_handles_request(service: BaseService, request_: dict, handled: bool):
    request_ = MITMRequest(
        url=request_['uri'],
        headers=MITMHeaders(request_['headers']),
    )
    assert service.handles_request(request_) == handled


def test_base_service_get_responses_for_active_scenario(service: BaseService, scenarios_dir):
    result = service.get_responses_for_active_scenario()
    expected = [
        (
            MITMRequest(
                body='{"value": "response2"}',
                headers=MITMHeaders({
                    'Accept': ['application/json'],
                    'Accept-Encoding': ['gzip, deflate'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['python-requests/2.18.4']
                }),
                method='POST',
                url='https://host_a.local/api',
            ),
            MITMResponse(
                body=None,
                headers=MITMHeaders({
                    'content-type': ['application/json; charset=UTF-8']
                }),
                status_code=201,
            ),
        ), (
            MITMRequest(
                headers=MITMHeaders({
                    'Accept': ['application/json'],
                    'Accept-Encoding': ['gzip, deflate'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['python-requests/2.18.4']
                }),
                method='GET',
                url='https://host_a.local/api',
            ),
            MITMResponse(
                body='{"value": "response1"}',
                headers=MITMHeaders({
                    'content-type': ['application/json; charset=UTF-8']
                }),
                status_code=200,
            )
        ),
    ]

    assert expected == result


@mark.parametrize(
    'request_, matches',
    [
        (
            MITMRequest(
                body='body content',
                headers=MITMHeaders({
                    'Accept': ['text/plain'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['python-requests/2.18.4']
                }),
                method='GET',
                url='https://domain.local/path;param?query=value',
            ),
            True,
        ),
        (
            MITMRequest(
                body='body content',
                headers=MITMHeaders({
                    'Accept': ['text/plain'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['curl/7.5.11']
                }),
                method='GET',
                url='https://domain.local/path;param?query=value',
            ),
            True,
        ),
        (
            MITMRequest(
                body='body content',
                headers=MITMHeaders({
                    'Accept': ['text/plain'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['python-requests/2.18.4']
                }),
                method='GET',
                url='HTTPS://domain.local/path;param?query=value',
            ),
            True,
        ),
        (
            MITMRequest(
                body='body content',
                headers=MITMHeaders({
                    'Accept': ['text/plain'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['python-requests/2.18.4']
                }),
                method='POST',
                url='https://domain.local/path;param?query=value',
            ),
            False,
        ),
        (
            MITMRequest(
                body='body content',
                headers=MITMHeaders({
                    'Accept': ['text/plain'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['python-requests/2.18.4']
                }),
                method='GET',
                url='https://otherdomain.local/path;param?query=value',
            ),
            False,
        ),
        (
            MITMRequest(
                body='different body content',
                headers=MITMHeaders({
                    'Accept': ['text/plain'],
                    'Connection': ['keep-alive'],
                    'User-Agent': ['python-requests/2.18.4']
                }),
                method='GET',
                url='https://domain.local/path;param?query=value',
            ),
            False,
        ),
    ],
    ids=[
        'exact matches',
        'different headers, still matches',
        'uppercase schema, still matches',
        'different method, don\'t match',
        'different domain, don\'t match',
        'different body, don\'t match',
    ]
)
def test_match_request(
    service: BaseService,
    request_: MITMRequest,
    sample_request: MITMRequest,
    matches: bool,
    scenarios_dir
):
    assert service.match_request(request_, sample_request) == matches


@mark.parametrize(
    'request_, response',
    [
        (
            MITMRequest(
                headers=MITMHeaders({
                    'Accept': ['application/json'],
                }),
                method='GET',
                url='https://host_a.local/api',
            ),
            MITMResponse(
                body='{"value": "response1"}',
                headers=MITMHeaders({
                    'content-type': ['application/json; charset=UTF-8'],
                }),
                status_code=200,
            ),
        ),
        (
            MITMRequest(
                body='{"value": "response2"}',
                headers=MITMHeaders({
                    'Accept': ['application/json'],
                }),
                method='POST',
                url='https://host_a.local/api',
            ),
            MITMResponse(
                body=None,
                headers=MITMHeaders({
                    'content-type': ['application/json; charset=UTF-8'],
                }),
                status_code=201,
            ),
        ),
    ],
    ids=[
        'match 0.yaml',
        'match 1.yaml',
    ]
)
def test_process_request(
    service: BaseService,
    request_: MITMRequest,
    response: MITMResponse,
    scenarios_dir
):
    assert service.process_request(request_) == response


def test_process_request_fails_on_unknown_request(service: BaseService, scenarios_dir):
    request = MITMRequest(
        body='{"value": "whatever"}',
        headers=MITMHeaders({
            'Accept': ['application/json'],
        }),
        method='PUT',
        url='https://host_a.local/this/path/is/not/handled',
    )

    with raises(NoMatchingRecording):
        service.process_request(request)
