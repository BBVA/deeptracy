import os
import deeptracy.dal.database as database

from deeptracy.dal.models import Base


def before_all(context):
    os.system('docker-compose -f tests/acceptance/docker-compose.yml up -d --build')

    # set environment
    database.DATABASE_URI = "postgresql://postgres:postgres@127.0.0.1:5432/deeptracy_test"
    context.BROKER_URI = "redis://127.0.0.1:6379/1"
    context.SCAN_PATH = "/tmp/deeptracy_test"

    if not os.path.exists(context.SCAN_PATH):
        os.makedirs(context.SCAN_PATH)

    database.db.init_engine()  # Init database engine


def after_all(context):
    Base.metadata.drop_all(bind=database.db.engine)
    os.system('docker-compose -f tests/behave/docker-compose.yml stop')
    os.system('rm -rf {}'.format(context.SCAN_PATH))


def handle_errors(func):
    def wrapper(context, *args, **kwargs):
        try:
            func(context, *args, **kwargs)
        except Exception as e:
            print(e)
            after_all(context)

    return wrapper
