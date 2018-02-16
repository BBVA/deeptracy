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

import logging
from celery import task

from deeptracy.tasks.base_task import DeeptracyTask
from deeptracy_core.dal.database import db
from deeptracy_core.dal.vulnerability.manager import get_vulns_for_cpe, add_vulns_in_scan_dep
from deeptracy.notifications.manager import notify_deltas

logger = logging.getLogger('deeptracy')


@task(name="notify_patton_deltas", base=DeeptracyTask)
def notify_patton_deltas(vulnerabilities):
    scan_dep_by_project_id = {}
    with db.session_scope() as session:
        for cpe in vulnerabilities:
            scan_deps_ids = []
            cves = vulnerabilities[cpe]
            for vuln_db in get_vulns_for_cpe(cpe, session):
                for scan_vuln in vuln_db.scan_vulns:
                    scan_dep = scan_vuln.scan_dep
                    scan_deps_ids.append(scan_dep.id)
                    raw_dep = scan_dep.raw_dep
                    scan = scan_dep.scan
                    project = scan.project
                    if project.id in scan_dep_by_project_id:
                        scan_dep_by_project_id[project.id]['dependencies'].append(raw_dep)
                    else:
                        scan_dep_by_project_id[project.id] = {'project': project, 'dependencies': [raw_dep]}
            for scan_dep_id in set(scan_deps_ids):
                add_vulns_in_scan_dep(cpe=cpe, cves=cves, scan_dep_id=scan_dep_id, session=session)

        for project_id in scan_dep_by_project_id:
            elem = scan_dep_by_project_id[project_id]
            dependencies = set(elem['dependencies'])
            notify_deltas(elem['project'], dependencies)
    logger.debug('notify vulnerabilities')


def format_notify_text(dependencies):
    return " , ".join(dependencies)
