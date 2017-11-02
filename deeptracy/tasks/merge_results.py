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
import logging
from celery import task

from deeptracy_core.dal.database import db
from deeptracy_core.dal.scan.manager import get_scan
from deeptracy_core.dal.project.project_hooks import ProjectHookType
from deeptracy_core.dal.scan.manager import ScanState, update_scan_state

from ..config import SHARED_VOLUME_PATH
from .notify_results import notify_results

logger = logging.getLogger('deeptracy')


@task(name="merge_results")
def merge_results(results, scan_id=None):
    for result in results:
        logger.info('{} merge results'.format(result))

    # with db.session_scope() as session:
    #     scan = get_scan(scan_id, session)

    # After the merge we remove the folder with the scan source
    scan_dir = os.path.join(SHARED_VOLUME_PATH, scan_id)
    try:
        shutil.rmtree(scan_dir)
    except IOError as e:
        logger.error("Error while removing tmp dir: {} - {}".format(
            scan_dir,
            e
        ))

    with db.session_scope() as session:
        scan = get_scan(scan_id, session)
        project = scan.project

        scan = update_scan_state(scan, ScanState.DONE, session)
        session.commit()

        if project.hook_type != ProjectHookType.NONE.name:
            # launch notify task
            logger.debug('{} launch notify task for project.hook_type'.format(scan.id))
            notify_results.delay(scan.id)
