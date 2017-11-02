# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import logging
from behave import when

log = logging.getLogger(__name__)


@when(u'a task for "{task}" is added to celery for the scan')
def step_impl(context, task):
    context.celery.send_task(task, [context.scan_id])


@when(u'all celery tasks are done')
def step_impl(context):
    i = context.celery.control.inspect()
    max_wait = 240
    waiting = 0
    while True:
        active = i.active()
        log.info('active ----- {}'.format(active))
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
