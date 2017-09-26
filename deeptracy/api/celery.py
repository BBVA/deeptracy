from celery import Celery
from deeptracy.config import BROKER_URI


celery = None


def setup_celery():
    global celery
    celery = Celery('deeptracy',
                    broker=BROKER_URI,
                    backend=BROKER_URI)
    return celery
