# -*- coding: utf-8 -*-
"""
Module for deeptracy
"""
from deeptracy.dal.database import db
from deeptracy.api.celery import setup_celery
from deeptracy.api.flask import setup_api

db.init_engine()  # Init database engine
setup_celery()  # setup the celery client

flask_app = setup_api()  # setup flask api
