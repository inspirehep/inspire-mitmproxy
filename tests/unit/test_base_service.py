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

from pytest import fixture, mark

from inspire_mitmproxy.base_service import BaseService


@fixture
def base_service():
    class Service(BaseService):
        SERVICE_HOSTS = ['host_a.local', 'host_b.local']

    return Service()


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
        'check first, Host and URI matching',
        'check second, Host and URI matching',
        'Host matching, URI not',
        'URI matching, Host not',
        'URI matching, Host undefined',
        'URI and Host both not matching',
    ]
)
def test_base_service_handles_request(base_service, request_, handled):
    assert base_service.handles_request(request_) == handled
