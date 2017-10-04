# -*- coding: utf-8 -*-

from celery import task
from typing import List
from deeptracy.plugin_store import plugin_store
from deeptracy_core.dal.database import db
from deeptracy_core.dal.scan_analysis.manager import get_scan_analysis, add_scan_vulnerabilities_results


@task(name="run_analyzer")
def run_analyzer(scan_analysis_id: str) -> List[str]:
    with db.session_scope() as session:
        scan_analysis = get_scan_analysis(scan_analysis_id, session)

        scan = scan_analysis.scan

        # a plugin is a function
        plugin = plugin_store.get_plugin(scan_analysis.plugin_id)
        results = plugin(scan.source_path)
        add_scan_vulnerabilities_results(scan_analysis_id, results, session)

        serialized_results = [result.to_dict() for result in results]
        return serialized_results
