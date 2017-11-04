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
from .plugin_store import plugin_store

db.init_engine()  # Init database engine
plugin_store.load_plugins()  # Load analyzer plugins


# SETUP AND CREATE CELERY APP
celery = Celery('deeptracy',
                broker=BROKER_URI,
                backend=BROKER_URI,
                include=[
                    'deeptracy.tasks.prepare_scan',
                    'deeptracy.tasks.scan_deps',
                    'deeptracy.tasks.start_scan',
                    'deeptracy.tasks.run_analyzer',
                    'deeptracy.tasks.merge_results',
                    'deeptracy.tasks.notify_results'
                ])
