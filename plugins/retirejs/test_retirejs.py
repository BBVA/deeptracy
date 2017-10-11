# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import mock
from deeptracy_core import PluginResult, PluginSeverityEnum

from .retirejs_docker import retirejs


class Identifier:
    summary = None
    CVE = None

    def __init__(self, summary=None, CVE=None):
        self.summary = summary
        self.CVE = CVE


class Vulnerability:
    severity = None
    identifiers = None
    info = None

    def __init__(self, severity=None, identifiers=None, info=None):
        self.severity = severity
        self.identifiers = identifiers
        self.info = info


class Info:
    component = None
    version = None
    vulnerabilities = None

    def __init__(self, component=None, version=None, vulnerabilities=None):
        self.component = component
        self.version = version
        self.vulnerabilities = vulnerabilities


class Result:
    results = None

    def __init__(self, results):
        self.results = results


@mock.patch('plugins.retirejs.retirejs_docker.run_in_docker')
@mock.patch('plugins.retirejs.retirejs_docker.json.loads')
def test_plugin_always_returns_a_list(mock_json_loads, mock_run_in_docker):
    mock_run_in_docker.return_value.__enter__.return_value = ''
    mock_json_loads.return_value = []

    results = retirejs('')
    assert type(results) is list
    assert len(results) == 0


@mock.patch('plugins.retirejs.retirejs_docker.run_in_docker')
@mock.patch('plugins.retirejs.retirejs_docker.json.loads')
def test_plugin_result_with_when_vul_is_none(mock_json_loads, mock_run_in_docker):
    info = Info(component='test', version='1.0', vulnerabilities=None)
    result = Result([info])

    mock_run_in_docker.return_value.__enter__.return_value = ''
    mock_json_loads.return_value = [result]

    results = retirejs('')
    assert type(results) is list
    assert len(results) == 0


@mock.patch('plugins.retirejs.retirejs_docker.run_in_docker')
@mock.patch('plugins.retirejs.retirejs_docker.json.loads')
def test_plugin_result_with_when_vul_is_not_present(mock_json_loads, mock_run_in_docker):
    info = Info(component='test', version='1.0', vulnerabilities=[])
    del info.__dict__['vulnerabilities']
    result = Result([info])

    mock_run_in_docker.return_value.__enter__.return_value = ''
    mock_json_loads.return_value = [result]

    results = retirejs('')
    assert type(results) is list
    assert len(results) == 0


@mock.patch('plugins.retirejs.retirejs_docker.run_in_docker')
@mock.patch('plugins.retirejs.retirejs_docker.json.loads')
def test_plugin_result_complete(mock_json_loads, mock_run_in_docker):
    component = 'test component'
    version = '1.0'
    summary = 'this is the summary'
    CVE = 'CVE-2011-4969'
    info_str = 'and the info'

    iden = Identifier(summary=summary, CVE=[CVE])
    vul = Vulnerability(severity='high', identifiers=iden, info=[info_str])
    info = Info(component=component, version=version, vulnerabilities=[vul])
    result = Result([info])

    mock_run_in_docker.return_value.__enter__.return_value = ''
    mock_json_loads.return_value = [result]

    results = retirejs('')
    assert type(results) is list
    assert len(results) == 1
    assert type(results[0]) is PluginResult

    assert results[0].library == component
    assert results[0].version == version
    assert results[0].severity == PluginSeverityEnum.HIGH.value
    assert results[0].summary == summary + ' ' + info_str
    assert results[0].advisory == CVE


@mock.patch('plugins.retirejs.retirejs_docker.run_in_docker')
@mock.patch('plugins.retirejs.retirejs_docker.json.loads')
def test_plugin_result_complete_multiple_CVE(mock_json_loads, mock_run_in_docker):
    component = 'test component'
    version = '1.0'
    summary = 'this is the summary'
    CVE = 'CVE-2011-4969'
    CVE_2 = 'CVE-2011-1000'
    info_str = 'and the info'

    iden = Identifier(summary=summary, CVE=[CVE, CVE_2])
    vul = Vulnerability(severity='high', identifiers=iden, info=info_str)
    info = Info(component=component, version=version, vulnerabilities=[vul])
    result = Result([info])

    mock_run_in_docker.return_value.__enter__.return_value = ''
    mock_json_loads.return_value = [result]
    results = retirejs('')

    assert type(results) is list
    assert len(results) == 1
    assert type(results[0]) is PluginResult

    assert results[0].library == component
    assert results[0].version == version
    assert results[0].severity == PluginSeverityEnum.HIGH.value
    assert results[0].summary == summary + ' ' + info_str
    assert results[0].advisory == CVE + ' ' + CVE_2
