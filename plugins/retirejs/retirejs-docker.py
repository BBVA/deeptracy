# -*- coding: utf-8 -*-

import json

from types import SimpleNamespace as Namespace
from typing import List, Dict

from deeptracy_core import PluginResult, PluginSeverityEnum
from deeptracy_core.decorator import deeptracy_plugin
from deeptracy_core.docker_helpers import run_in_docker, get_plugin_image


@deeptracy_plugin("nodejs")
def retirejs(source_code_location: str) -> List[Dict]:

    current_plugin_path = get_plugin_image()

    with run_in_docker(current_plugin_path,
                       source_code_location) as f:
        # raw_results = f.splitlines()
        json_raw_results = json.loads(f, object_hook=lambda d: Namespace(**d))

    results = []
    for result in json_raw_results:

        # Load partial result
        for v_info in result.results:

            v_info_library = v_info.component
            v_info_version = v_info.version
            v_info_summary = ""
            v_info_advisory = ""
            v_info_severity = "xxxx"

            for vuln in v_info.vulnerabilities:

                # -------------------------------------------------------------
                # Severity
                # -------------------------------------------------------------
                if vuln.severity == "high":
                    v_info_severity = PluginSeverityEnum.HIGH
                elif vuln.severity == "medium":
                    v_info_severity = PluginSeverityEnum.MEDIUM
                elif vuln.severity == "low":
                    v_info_severity = PluginSeverityEnum.MEDIUM
                else:
                    raise ValueError("Invalid Plugin Severity: {}".format(
                        vuln.severity
                    ))

                # -------------------------------------------------------------
                # Identifier + Summary
                # -------------------------------------------------------------
                if hasattr(vuln.identifiers, "summary"):
                    v_info_summary = vuln.identifiers.summary
                    v_info_advisory = ""
                elif hasattr(vuln.identifiers, "CVE"):
                    v_info_summary = vuln.identifiers.advisory
                    v_info_advisory = vuln.identifiers.CVE
                else:
                    v_info_summary = ""
                    v_info_advisory = ""

                v_info_summary = vuln.identifiers.summary

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
    print(retirejs(op.abspath(op.join(op.dirname(__file__), "..", "..", "vulnerable-node"))))
