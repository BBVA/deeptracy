import os
import time

from behave import given, when, then
from deeptracy.dal.database import db
from deeptracy.dal.project import Project
from deeptracy.dal.models import Scan, ScanAnalysis, ScanAnalysisVulnerability
from deeptracy.plugins.retirejs import OUTPUT_FILE


@given(u'a project with "{repo}" repo exists in the database')
def step_impl(context, repo):
    session = db.Session()
    project = Project(repo=repo)
    session.add(project)
    session.commit()
    context.project_id = project.id


@when(u'a scan with "{lang}" is added to celery for the project')
def step_impl(context, lang):
    session = db.Session()
    scan = Scan(project_id=context.project_id, lang=lang)
    session.add(scan)
    session.commit()
    context.scan_id = scan.id

    context.celery.send_task("start_scan", [scan.id])


@when(u'all celery tasks are done')
def step_impl(context):
    i = context.celery.control.inspect()
    while True:
        active = i.active()
        print('active ----- {}'.format(active))
        if active is None:
            time.sleep(5)
            continue

        still_active = False
        for _, tasks in active.items():
            if len(tasks) > 0:
                still_active = True

        if still_active is False:
            return
        else:
            time.sleep(5)


@then(u'a scan folder with the cloned repo exists')
def step_impl(context):
    scan_dir = os.path.join(context.SCAN_PATH, context.scan_id)
    git_scan_dir = os.path.join(scan_dir, '.git')

    assert os.path.exists(scan_dir)
    assert len(os.listdir(scan_dir)) > 0
    assert os.path.exists(git_scan_dir)
    context.scan_dir = scan_dir


@then(u'the results for retirejs exists in a file in the scanned folder')
def step_impl(context):
    result_file = os.path.join(context.scan_dir, OUTPUT_FILE)
    assert os.path.isfile(result_file)


@then(u'the results for the scan in the database includes the results in the file')
def step_impl(context):
    session = db.Session()
    scan = session.query(Scan).get(context.scan_id)
    scan_analysis = scan.scan_analysis

    assert len(scan_analysis) == 1  # this scan generates 1 analysis

    scan_analysis_vulnerabilities = scan_analysis[0].scan_analysis_vulnerability

    assert len(scan_analysis_vulnerabilities) > 0  # this analysis generates at least 1 vuln
