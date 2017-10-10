import os
import time
import sqlalchemy
import redis
from celery import Celery
from urllib.parse import urlparse


def before_all(context):
    """For LOCAL_BEHAVE you need to setup the environment manually"""

    if os.environ.get('LOCAL_BEHAVE', None) is None:
        # set environment
        os.environ['DATABASE_URI'] = 'postgresql://postgres:postgres@127.0.0.1:5433/deeptracy_test'
        os.environ['BROKER_URI'] = 'redis://127.0.0.1:6379'
        os.environ['SHARED_VOLUME_PATH'] = '/tmp/deeptracy'

        os.system('docker-compose -f tests/acceptance/docker-compose.yml rm -f')
        os.system('docker-compose -f tests/acceptance/docker-compose.yml up -d --build')
        time.sleep(10)

    context.BROKER_URI = os.environ['BROKER_URI']
    context.SHARED_VOLUME_PATH = os.environ['SHARED_VOLUME_PATH']

    if not os.path.exists(context.SHARED_VOLUME_PATH):
        os.makedirs(context.SHARED_VOLUME_PATH)

    context.engine = sqlalchemy.create_engine(os.environ['DATABASE_URI'])
    context.redis_db = _setup_redis(context.BROKER_URI)
    context.celery = Celery('deeptracy', broker=context.BROKER_URI)


def after_all(context):
    if os.environ.get('LOCAL_BEHAVE', None) is None:
        os.system('docker-compose -f tests/acceptance/docker-compose.yml logs ')
        os.system('docker-compose -f tests/acceptance/docker-compose.yml kill')
        os.system('docker-compose -f tests/acceptance/docker-compose.yml rm -f')
        os.system('rm -rf {}'.format(context.SHARED_VOLUME_PATH))


def _setup_redis(uri: dict) -> redis.StrictRedis:
    _, netloc, path, _, _, _ = urlparse(uri)

    host, port = netloc.split(":", maxsplit=1)

    if not path:
        path = 0

    redis_db = redis.StrictRedis(host=host,
                                 port=port,
                                 db=path)

    return redis_db
