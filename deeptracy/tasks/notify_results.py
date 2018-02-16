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

from deeptracy_core.dal.database import db
from deeptracy_core.dal.scan.manager import get_scan, get_scan_vulnerabilities
from deeptracy.notifications.manager import notify_scan_results

logger = logging.getLogger('deeptracy')


@task(name="notify_results")
def notify_results(scan_id):
    with db.session_scope() as session:
        scan = get_scan(scan_id, session)
        scan_vulns = set([scan_vuln.scan_dep.raw_dep for scan_vuln in get_scan_vulnerabilities(scan_id, session)])
        project = scan.project

        logger.debug('notify project data {}'.format(project.hook_data))
        notify_scan_results(project, scan_vulns)
