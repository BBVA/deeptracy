# -*- coding: utf-8 -*-

from celery import task, chord

import deeptracy.utils as utils
from deeptracy.config import SCAN_PATH
from deeptracy.dal.plugin_manager import get_plugins_for_lang
from deeptracy.dal.scan_manager import get_scan, update_scan_state, ScanState
from deeptracy.dal.scan_analysis_manager import add_scan_analysis
from deeptracy.tasks.run_analyzer import run_analyzer
from deeptracy.tasks.merge_results import merge_results
from deeptracy.dal.database import db


@task(name="start_scan")
def start_scan(scan_id: str):
    with db.session_scope() as session:
        scan = get_scan(scan_id, session)

        project = scan.project

        if utils.valid_repo(project.repo) is False:
            update_scan_state(scan, ScanState.INVALID_REPO, session)
            return

        available_plugins_for_lang = get_plugins_for_lang(scan.lang, session)
        analysis_count = len(available_plugins_for_lang)

        if analysis_count < 1:
            update_scan_state(scan, ScanState.NO_PLUGINS_FOR_LANGUAJE, session)
            return

        # clone the repo to share sources for all analysis
        source_path = utils.clone_repo(SCAN_PATH, scan_id, project.repo)

        # update the scan object
        scan.analysis_count = analysis_count
        scan.analysis_done = 0
        scan.source_path = source_path
        scan.state = ScanState.RUNNING.name
        session.add(scan)
        session.commit()

        # save each analysis for this scan in the database and collect its ids
        scan_analysis_ids = []
        for plugin in available_plugins_for_lang:
            scan_analysis = add_scan_analysis(scan.id, plugin.id, session)
            session.commit()  # Commit the session to persist the scan_analysis and get and id
            scan_analysis_ids.append(scan_analysis.id)

        # make a celey chord to execute all analyzers in parallel and then run the callback
        # result merger task
        callback = merge_results.s()
        header = [run_analyzer.s(scan_analysis_id) for scan_analysis_id in scan_analysis_ids]
        # launch the chord (they are async)
        chord(header)(callback)
