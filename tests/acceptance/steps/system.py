# -*- coding: utf-8 -*-

from tests.acceptance.utils import clean_db
from behave import given


@given(u'a clean system')
def step_impl(context):
    clean_db(context)
