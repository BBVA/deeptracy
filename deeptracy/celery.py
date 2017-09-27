# -*- coding: utf-8 -*-
"""
Module for deeptracy
"""
from celery import Celery
from deeptracy.config import BROKER_URI
from deeptracy.dal.database import db
from deeptracy.plugins.store import plugin_store
from deeptracy.dal.project import Project

db.init_engine()  # Init database engine
plugin_store.load_plugins()    # Load analyzer plugins


# SETUP AND CREATE CELERY APP
celery = Celery('deeptracy',
                broker=BROKER_URI,
                backend=BROKER_URI,
                include=[
                    'deeptracy.tasks.start_scan',
                    'deeptracy.tasks.run_analyzer',
                    'deeptracy.tasks.merge_results'
                ])
