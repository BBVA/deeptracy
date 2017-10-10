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

from deeptracy.config import SHARED_VOLUME_PATH

log = logging.getLogger("deeptracy")


@task(name="merge_results")
def merge_results(results, scan_id=None):
    for result in results:
        print('----- {} ------'.format(result))

    # with db.session_scope() as session:
    #     scan = get_scan(scan_id, session)

    # After the merge we remove the folder with the scan source
    scan_dir = os.path.join(SHARED_VOLUME_PATH, scan_id)
    try:
        shutil.rmtree(scan_dir)
    except IOError as e:
        log.error("Error while removing tmp dir: {} - {}".format(
            scan_dir,
            e
        ))
