# -*- coding: utf-8 -*-

import shutil
import logging
from celery import task


log = logging.getLogger("deeptracy")


@task(name="merge_results")
def merge_results(results, cloned_dir=None):
    for result in results:
        print('----- {} ------'.format(result))

    # After the merge we remove the shared volume with source code
    try:
        shutil.rmtree(cloned_dir)
    except IOError as e:
        log.error("Error while removing tmp dir: {} - {}".format(
            cloned_dir,
            e
        ))
