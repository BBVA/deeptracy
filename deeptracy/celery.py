"""
Celery worker module.
~~~~~~~~~~~~~~~~~~~~~

This module can be launched with celery to create workers to handle tasks.

Run deeptracy celery workers with `INFO` log levels::

    $ celery -A deeptracy.celery:celery worker -l INFO

"""
from celery import Celery

from deeptracy_core.dal.database import db
from .config import BROKER_URI

db.init_engine()  # Init database engine


# SETUP AND CREATE CELERY APP
celery = Celery('deeptracy',
                broker=BROKER_URI,
                backend="",
                include=[
                    'deeptracy.tasks.prepare_scan',
                    'deeptracy.tasks.scan_deps',
                    'deeptracy.tasks.get_vulnerabilities',
                    'deeptracy.tasks.notify_results',
                    'deeptracy.tasks.notify_patton_deltas'
                ])
