# -*- coding: utf-8 -*-

import os
from behave import then


@then(u'the scan folder is deleted')
def step_impl(context):
    scan_dir = os.path.join(context.SHARED_VOLUME_PATH, context.scan_id)

    assert not os.path.exists(scan_dir)
