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
import deeptracy.utils as utils

from celery import task, chord
from deeptracy.config import SHARED_VOLUME_PATH
from deeptracy_core.dal.plugin.manager import get_plugins_for_lang
from deeptracy_core.dal.scan.manager import get_scan, update_scan_state, ScanState
from deeptracy_core.dal.scan_analysis.manager import add_scan_analysis
from deeptracy_core.dal.database import db
from deeptracy.tasks.run_analyzer import run_analyzer
from deeptracy.tasks.merge_results import merge_results

log = logging.getLogger("deeptracy")


@task(name="start_scan")
def start_scan(scan_id: str):
    with db.session_scope() as session:
        scan = get_scan(scan_id, session)

        project = scan.project

        available_plugins_for_lang = get_plugins_for_lang(scan.lang, session)
        analysis_count = len(available_plugins_for_lang)

        if analysis_count < 1:
            update_scan_state(scan, ScanState.NO_PLUGINS_FOR_LANGUAGE, session)
            return

        # clone the repository in a shared volume
        cloned_dir = utils.clone_project(SHARED_VOLUME_PATH, scan_id, project)

        # update the scan object
        scan.analysis_count = analysis_count
        scan.analysis_done = 0
        scan.source_path = cloned_dir
        scan.state = ScanState.RUNNING.name
        session.add(scan)
        session.commit()

        # save each analysis for this scan in the database and collect its ids
        scan_analysis_ids = []
        for plugin in available_plugins_for_lang:
            scan_analysis = add_scan_analysis(scan.id, plugin.id, session)
            session.commit()  # Commit the session to persist the scan_analysis and get and id
            scan_analysis_ids.append(scan_analysis.id)

        # create a task for each analyzer to run
        analyzers = [run_analyzer.s(scan_analysis_id)
                     for scan_analysis_id in scan_analysis_ids]

        # launch all jobs
        chord(analyzers)(merge_results.s(scan_id=scan.id))
