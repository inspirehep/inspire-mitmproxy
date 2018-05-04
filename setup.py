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

"""INSPIRE MITMProxy for E2E Tests."""

from typing import List

from setuptools import setup

readme = open('README.rst').read()

setup_requires = [
    'autosemver~=0.0,>=0.5.3',
]

install_requires = [
    'autosemver~=0.0,>=0.5.3',
    'mitmproxy~=3.0,>=3.0.4',
    'pathlib~=1.0,>=1.0.1',
]

tests_require = [
    'autosemver~=0.0,>=0.5.3',
    'flake8~=3.0,>=3.5.0',
    'isort~=4.0,>=4.3.4',
    'mitmproxy~=3.0,>=3.0.4',
    'mypy~=0.0,>=0.590',
    'mock~=2.0,>=2.0.0',
    'pathlib~=1.0,>=1.0.1',
    'pytest~=3.0,>=3.5.0',
    'pytest-cov~=2.0,>=2.5.1',
]

docs_require: List[str] = []

extras_require = {
    'docs': docs_require,
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    extras_require['all'].extend(reqs)

URL = 'https://github.com/inspirehep/inspire-mitmproxy'

setup(
    name='inspire-mitmproxy',
    author="CERN",
    author_email='admin@inspirehep.net',
    autosemver={
        'bugtracker_url': URL + '/issues',
    },
    description=__doc__,
    long_description=readme,
    url=URL,
    license='GPLv3',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require=extras_require,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
