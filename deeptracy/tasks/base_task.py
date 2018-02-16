"""This module contains base class for all celery task in deeptracy and other common classes used in all tasks"""
import logging
from celery import Task

logger = logging.getLogger('deeptracy')


class DeeptracyTask(Task):
    """Default class for all task in deeptracy. It has error handling for logging all celery failures in tasks"""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception('celery task failure', exc_info=exc)
        super().on_failure(exc, task_id, args, kwargs, einfo)


class TaskException(BaseException):
    """Exception for use in controlled errors inside tasks"""
    pass
