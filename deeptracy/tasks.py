import collections
import functools
import json

import celery
import requests

from deeptracy import Config
from deeptracy.model import Analysis


app = Config.CELERY


@app.task
def mark_task_done(analysis_id):
    with Config.DATABASE.atomic():
        # This query is not an `UPDATE` because we need `save()` to be executed
        # for the `state` field to be recalculated. The atomic()
        # context-manager should protect us against race conditions.
        analysis = Analysis.get(Analysis.id == analysis_id)
        analysis.tasks_done += 1
        analysis.save()


@app.task
def request_extraction(analysis_id):
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
    response = requests.post(webhook, json={'id': analysis_id, 'state': state})
    response.raise_for_status()
