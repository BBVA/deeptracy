# -*- coding: utf-8 -*-

from celery import task


@task(name="merge_results")
def merge_results(results):
    for result in results:
        print('----- {} ------'.format(result))
