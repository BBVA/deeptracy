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
import os
import shutil
import requests

from celery import task
from celery.utils.log import get_task_logger

from deeptracy_core.dal.project.project_hooks import ProjectHookType
from deeptracy_core.dal.database import db
from deeptracy_core.dal.scan.manager import get_scan, update_scan_state, ScanState
from deeptracy_core.dal.scan_dep.manager import get_scan_deps, get_scan_dep_by_scan_id_and_raw_dep
from deeptracy_core.dal.scan_vul.manager import add_scan_vuln

from ..config import SHARED_VOLUME_PATH, PATTON_URI
from .notify_results import notify_results

logger = get_task_logger('deeptracy')


@task(name="get_vulnerabilities")
def get_vulnerabilities(scan_id: str):
    with db.session_scope() as session:
        logger.debug('{} extract dependencies'.format(scan_id))

        scan_deps = get_scan_deps(scan_id, session)
        scan = get_scan(scan_id, session)
        project = scan.project
        total_vulnerabilities = 0
        if scan_deps:
            url = '{}/api/v1/check-dependencies?cpeDetailed=1'.format(PATTON_URI)
            req_body = {
                'method': 'auto',
                'source': 'auto',
                'libraries': [{'library': scan_dep.library, 'version': scan_dep.version} for scan_dep in scan_deps]
            }
            response = requests.post(url, json=req_body).json()


            if response:
                for key in response:
                    if response[key]:
                        [library, version] = key.split(':')
                        scan_dep = get_scan_dep_by_scan_id_and_raw_dep(scan_id, '{}:{}'.format(library, version), session)
                        cpes = response[key]
                        for cpe_dict in cpes['cpes']:
                            cpe = cpe_dict['cpe']
                            cves = cpe_dict['cves']
                            total_vulnerabilities += len(cves)
                            # save all dependencies in the database
                            add_scan_vuln(scan_dep.id, scan.id, scan.lang, cpe, cves, session)
                            logger.info('saved {cves} cves for cpe {cpe}'.format(
                                cves=len(cves), cpe=cpe))

        scan.total_vulnerabilities = total_vulnerabilities
        update_scan_state(scan, ScanState.DONE, session)
        session.commit()

        # After the merge we remove the folder with the scan source
        scan_dir = os.path.join(SHARED_VOLUME_PATH, scan_id)
        try:
            shutil.rmtree(scan_dir)
        except IOError as e:
            logger.error("Error while removing tmp dir: {} - {}".format(
                scan_dir,
                e
            ))
        if project.hook_type != ProjectHookType.NONE.name:
            # launch notify task
            logger.debug('{} launch notify task for project.hook_type'.format(scan.id))

            notify_results.delay(scan.id)
