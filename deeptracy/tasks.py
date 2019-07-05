"""
This module contains the Celery tasks.

"""
# pylint: disable=invalid-name,no-member
import json

import requests

from deeptracy import Config
from deeptracy.model import Analysis


app = Config.CELERY


@app.task
def mark_task_done(analysis_id):
    """Increment the number of finished tasks of the given analysis."""
    with Config.POSTGRES.atomic():
        # This query is not an `UPDATE` because we need `save()` to be executed
        # for the `state` field to be recalculated. The atomic()
        # context-manager should protect us against race conditions.
        analysis = Analysis.get(Analysis.id == analysis_id)
        analysis.tasks_done += 1
        analysis.save()


@app.task
def request_extraction(analysis_id):
    """
    Send a request to buildbot to start the dependency straction phase of
    the analysis.

    """
    analysis = Analysis.get_by_id(analysis_id)
    response = requests.post(
        f"{Config.BUILDBOT_API}/change_hook/base",
        data={"revision": analysis.target.commit,
              "project": analysis.target.repository,
              "repository": analysis.target.repository,
              "properties": json.dumps({"analysis_id": str(analysis_id)}),
              "author": "deeptracy",
              "comments": ""})
    response.raise_for_status()


@app.task
def notify_user(webhook, analysis_id, state):
    """
    Call the user given endpoint to notify their analysis is finished.

    """
    response = requests.post(webhook, json={'id': analysis_id, 'state': state})
    response.raise_for_status()
