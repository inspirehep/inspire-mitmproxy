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

import json

from pytest import fixture, mark, raises

from inspire_mitmproxy import services
from inspire_mitmproxy.dispatcher import Dispatcher
from inspire_mitmproxy.errors import NoServicesForRequest
from inspire_mitmproxy.http import MITMHeaders, MITMRequest, MITMResponse


class TestService(services.BaseService):
    def process_request(self, request: dict):
        return MITMResponse(
            body=self.name,
            headers=MITMHeaders({
                'Content-Type': ['text/plain'],
            })
        )


@fixture(scope='module')
def dispatcher():
    return Dispatcher(
        service_list=[
            TestService(
                name='TestServiceA',
                hosts_list=['test-service-a.local'],

            ),
            TestService(
                name='TestServiceB',
                hosts_list=['test-service-b.local'],

            ),
            TestService(
                name='TestServiceC',
                hosts_list=['test-service-a.local'],

            ),
        ],
    )


@mark.parametrize(
    'url, message',
    [
        ('http://test-service-a.local', b'TestServiceA'),
        ('http://test-service-b.local/some_path', b'TestServiceB'),
        ('http://test-service-a.local/other_path', b'TestServiceA'),
    ],
    ids=[
        'first',
        'second, with path',
        'match first, even though also matches third (ordered)'
    ]
)
def test_dispatcher_process_request(dispatcher, url, message):
    result = dispatcher.process_request(
        MITMRequest(
            url=url,
            headers=MITMHeaders({
                'Accept': ['text/plain'],
            })
        )
    )

    assert result.body == message


def test_dispatcher_process_request_fail_if_none_match(dispatcher):
    with raises(NoServicesForRequest):
        dispatcher.process_request(
            MITMRequest(
                url='http://test-service-z.local/does_not_exist',
                headers=MITMHeaders({
                    'Accept': ['text/plain'],
                })
            )
        )


def test_dispatcher_default_services():
    dispatcher = Dispatcher()
    result = dispatcher.process_request(
        MITMRequest(url='http://mitm-manager.local/services')
    )

    expected = {
        "0": {
            "class": "ManagementService",
            "hosts_list": [
                "mitm-manager.local"
            ]
        },
        "1": {
            "class": "ArxivService",
            "hosts_list": [
                "arxiv.org",
                "export.arxiv.org"
            ]
        },
        "2": {
            "class": "LegacyService",
            "hosts_list": [
                "inspirehep.net"
            ]
        },
        "3": {
            "class": "RTService",
            "hosts_list": [
                "inspirevm13.cern.ch",
                "rt.inspirehep.net"
            ]
        },
        "4": {
            "class": "WhitelistService",
            "hosts_list": [
                "test-indexer", "test-scrapyd", "test-web-e2e.local",
            ]
        }
    }
    json_response = json.loads(result.body)

    assert json_response == expected
