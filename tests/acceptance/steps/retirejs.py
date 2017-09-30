import os

from behave import then
from deeptracy.plugins.retirejs import OUTPUT_FILE


@then(u'the results for retirejs exists in a file in the scanned folder')
def step_impl(context):
    result_file = os.path.join(context.scan_dir, OUTPUT_FILE)
    assert os.path.isfile(result_file)
