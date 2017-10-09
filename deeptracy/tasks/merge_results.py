# -*- coding: utf-8 -*-
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
