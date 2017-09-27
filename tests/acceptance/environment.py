import os
import time

from celery import Celery
import deeptracy.dal.database as database


def before_all(context):
    os.system('docker-compose -f tests/acceptance/docker-compose.yml rm -f')
    os.system('docker-compose -f tests/acceptance/docker-compose.yml -p deeptracy_acceptance up -d --build')
    time.sleep(5)

    # set environment
    database.DATABASE_URI = "postgresql://postgres:postgres@127.0.0.1:5432/deeptracy_test"
    context.BROKER_URI = "redis://127.0.0.1:6379/1"
    context.SCAN_PATH = "/tmp/deeptracy_test"

    if not os.path.exists(context.SCAN_PATH):
        os.makedirs(context.SCAN_PATH)

    database.db.init_engine()  # Init database engine

    context.celery = Celery('deeptracy_test', broker=context.BROKER_URI)


def after_all(context):
    os.system('docker-compose -f tests/acceptance/docker-compose.yml kill')
    os.system('docker-compose -f tests/acceptance/docker-compose.yml rm -f')
    os.system('rm -rf {}'.format(context.SCAN_PATH))
