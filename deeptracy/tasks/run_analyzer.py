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

        # TODO: this should be a function that calls the celery state instead of cherrypicking a counter that can lose
        # integrity if something wrong happen
        scan.analysis_done += 1
        session.add(scan)

        serialized_results = [result.to_dict() for result in results]
        return serialized_results
