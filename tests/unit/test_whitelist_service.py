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

"""Test Whitelist Service"""

import os

from mock import patch

from inspire_mitmproxy.services import WhitelistService


def test_load_services_from_os():
    expected_whitelist = ['my-indexer', 'my-worker']
    custom_environ = {'MITM_PROXY_WHITELIST': 'my-indexer my-worker'}

    with patch.dict(os.environ, custom_environ):
        service = WhitelistService(name='WhitelistService')
        whitelist = service.hosts_list

    assert whitelist == expected_whitelist


def test_env_services_have_priority():
    expected_whitelist = ['test-indexer', 'test-scrapyd', 'test-web-e2e.local']

    custom_environ = {'MITM_PROXY_WHITELIST': ' '.join(expected_whitelist)}

    with patch.dict(os.environ, custom_environ):
        service = WhitelistService(name='WhitelistService', hosts_list=[])

    whitelist = service.hosts_list

    assert whitelist == expected_whitelist
