# -*- coding: utf-8 -*-

import os
from behave import then


@then(u'a scan folder with the cloned repo exists')
def step_impl(context):
    scan_dir = os.path.join(context.SCAN_PATH, context.scan_id)
    git_scan_dir = os.path.join(scan_dir, '.git')

    assert os.path.exists(scan_dir)
    assert len(os.listdir(scan_dir)) > 0
    assert os.path.exists(git_scan_dir)
    context.scan_dir = scan_dir
