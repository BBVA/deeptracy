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

from deeptracy_core.dal.plugin.manager import get_plugins_for_lang
from deeptracy_core.dal.scan.manager import get_scan, update_scan_state, ScanState
from deeptracy_core.dal.scan_analysis.manager import add_scan_analysis
from deeptracy_core.dal.database import db

from ..config import SHARED_VOLUME_PATH
from ..utils import parse_deeptracy_yml
from .run_analyzer import run_analyzer
from .merge_results import merge_results
from .base_task import TaskException, DeeptracyTask


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@task(name="start_scan", base=DeeptracyTask)
def start_scan(scan_id: str):
    with db.session_scope() as session:
        logger.info('{} START SCAN'.format(scan_id))
        scan = get_scan(scan_id, session)
        project = scan.project

        logger.debug('{} for project({})'.format(scan_id, project.id))

        # clone the repository in a shared volume
        cloned_dir = utils.clone_project(SHARED_VOLUME_PATH, scan_id, project.repo, project.repo_auth_type)
        logger.debug('{} cloned dir {}'.format(scan_id, cloned_dir))

        # if a .deeprtacy.yml is found, parse it to a dictionary
        try:
            deeptracy_yml = parse_deeptracy_yml(cloned_dir)
            logger.debug('{} .deeptracy.yml {}'.format(scan_id, 'TRUE' if deeptracy_yml else 'FALSE'))
        except Exception:
            update_scan_state(scan, ScanState.INVALID_YML_ON_PROJECT, session)
            logger.debug('{} unable to parse .deeptracy.yml'.format(scan_id))
            raise

        # the language for a scan can be specified on the scan of in the deeptracy file in the sources
        if scan.lang is not None:
            lang = scan.lang
        elif deeptracy_yml is None:
            update_scan_state(scan, ScanState.CANT_GET_LANGUAGE, session)
            logger.debug('{} unable to retrieve language for scan'.format(scan_id))
            raise TaskException('unable to retrieve language for scan')
        else:
            lang = deeptracy_yml.get('lang')  # the parse ensures us a valid lang in the dict
            scan.lang = lang  # update the san object to store the language
            session.add(scan)

        # for the lang, get the plugins that can be run
        available_plugins_for_lang = get_plugins_for_lang(lang, session)
        analysis_count = len(available_plugins_for_lang)

        if analysis_count < 1:
            update_scan_state(scan, ScanState.NO_PLUGINS_FOR_LANGUAGE, session)
            logger.debug('{} no plugins found for language {}'.format(scan_id, lang))
            raise TaskException('no plugins found for language {}'.format(lang))

        # when we have the lang, the number of analysis to run and the source code dir, update the scan
        scan.analysis_count = analysis_count
        scan.analysis_done = 0
        scan.source_path = cloned_dir
        scan.state = ScanState.RUNNING.name
        session.add(scan)
        session.commit()  # save at this point as we need the ID for this scan

        # save each analysis to be ran for this scan in the database and collect its ids
        scan_analysis_ids = []
        for plugin in available_plugins_for_lang:
            scan_analysis = add_scan_analysis(scan.id, plugin.id, session)
            session.commit()  # Commit the session to persist the scan_analysis and get and id
            scan_analysis_ids.append(scan_analysis.id)

        # create a task for each analysis to run
        analyzers = [run_analyzer.s(scan_analysis_id)
                     for scan_analysis_id in scan_analysis_ids]

        # launch all jobs
        chord(analyzers)(merge_results.s(scan_id=scan.id))
