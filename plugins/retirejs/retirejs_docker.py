# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging

from types import SimpleNamespace as Namespace
from typing import List, Dict

from deeptracy_core import PluginResult, PluginSeverityEnum
from deeptracy_core.decorator import deeptracy_plugin
from deeptracy_core.docker_helpers import run_in_docker, get_plugin_image

log = logging.getLogger('deeptracy')


@deeptracy_plugin('nodejs')
def retirejs(source_code_location: str) -> List[Dict]:
    log.debug('start plugin retirejs')

    current_plugin_path = get_plugin_image()

    with run_in_docker(current_plugin_path, source_code_location) as f:
        # raw_results = f.splitlines()
        json_raw_results = json.loads(f, object_hook=lambda d: Namespace(**d))

    log.debug('plugin retirejd end running, parse results')
    results = []

    for result in json_raw_results:

        # Load partial result
        for v_info in result.results:
            log.debug('parse raw result {}'.format(v_info))
            v_info_library = v_info.component
            v_info_version = v_info.version

            vulnerabilities = []
            if getattr(v_info, 'vulnerabilities', []) and v_info.vulnerabilities is not None:
                vulnerabilities = v_info.vulnerabilities

            # TODO: there are libraries that are reported without vulnerabilities
            for vuln in vulnerabilities:

                # -------------------------------------------------------------
                # Severity
                # -------------------------------------------------------------
                if vuln.severity == 'high':
                    v_info_severity = PluginSeverityEnum.HIGH
                elif vuln.severity == 'medium':
                    v_info_severity = PluginSeverityEnum.MEDIUM
                elif vuln.severity == 'low':
                    v_info_severity = PluginSeverityEnum.LOW
                else:
                    v_info_severity = PluginSeverityEnum.NONE

                # -------------------------------------------------------------
                # Identifier + Summary
                # -------------------------------------------------------------
                v_info_summary = ''
                v_info_advisory = ''
                if hasattr(vuln, 'identifiers'):
                    if hasattr(vuln.identifiers, 'summary'):
                        v_info_summary = vuln.identifiers.summary
                    if hasattr(vuln.identifiers, 'CVE'):
                        # CVE is always list
                        v_info_advisory += ' '.join(vuln.identifiers.CVE)

                if hasattr(vuln, 'info'):
                    # info is always a list, append it to summary
                    v_info_summary += ' ' + ''.join(vuln.info)

                results.append(PluginResult(
                    library=v_info_library,
                    version=v_info_version,
                    severity=v_info_severity,
                    summary=v_info_summary,
                    advisory=v_info_advisory
                ))

    return results


if __name__ == '__main__':
    import os.path as op
    log.info(retirejs(op.abspath(op.join(op.dirname(__file__), '..', '..', 'vulnerable-node'))))
