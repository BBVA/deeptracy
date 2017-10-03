# -*- coding: utf-8 -*-

import time
from behave import when


@when(u'a task for "{task}" is added to celery for the scan')
def step_impl(context, task):
    context.celery.send_task(task, [context.scan_id])


@when(u'all celery tasks are done')
def step_impl(context):
    i = context.celery.control.inspect()
    max_wait = 120
    waiting = 0
    while True:
        active = i.active()
        # print('active ----- {}'.format(active))
        if waiting > max_wait:
            raise TimeoutError('celery task wait timeout')
        elif active is None:
            waiting = waiting + 5
            time.sleep(5)
            continue

        still_active = False
        for _, tasks in active.items():
            if len(tasks) > 0:
                still_active = True

        if still_active is False:
            return
        elif waiting < max_wait:
            waiting = waiting + 5
            time.sleep(5)
        else:
            raise TimeoutError('celery task wait timeout')
