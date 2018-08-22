import datetime

from deeptracy import Config
from deeptracy.providers import analyze_artifacts, mark_task_done
from deeptracy.model import Analysis
from deeptracy.model import Installation
from deeptracy.model import Artifact
from deeptracy.model import Target
from deeptracy.model import create_dependencies

import bottle


bottle.BaseRequest.MEMFILE_MAX = Config.BOTTLE_MEMFILE_MAX
application = bottle.Bottle(autojson=True)


@application.hook('before_request')
def _connect_db():
    Config.DATABASE.connect()


@application.hook('after_request')
def _close_db():
    if not Config.DATABASE.is_closed():
        Config.DATABASE.close()


@application.route('/analysis/', method='POST')
def analysis_started():
    """
    Signal from buildbot that an analysis has started.

    Requires a JSON object with the following parameters:
        * repo: The repository.
        * commit: The commit.
        * notify: Webhook to notify to when vulnerabilities are detected.

    Returns a JSON object containing the id of the created analysis.

    """
    with Config.DATABASE.atomic():
        analysis = Analysis.create(
            target=Target.get_or_create(
                repository=bottle.request.json['repo'],
                commit=bottle.request.json['commit'])[0],
            notify=bottle.request.json['notify'])
    return {'id': str(analysis.id)}


@application.route('/analysis/<analysis_id>/dependencies', method='PUT')
def dependencies_found(analysis_id):
    """
    Installation data from buildbot.

    Requires a JSON list of objects with the following keys:
        * installer: The system used to install the dependency.
        * spec: The full specification used by the user to request the
                package.
        * source: Entity providing the artifact.
        * name: The real package name.
        * version: The installed version of the package.

    """

    # Create database objects returning a list of scanneable artifacts.
    artifacts = create_dependencies(analysis_id, bottle.request.json)

    # Launch dependency scan and mark done when finished.
    task = (analyze_artifacts(artifacts) | mark_task_done.si(analysis_id)).delay()

    return {'task_id': task.id, 'scanning': len(artifacts)}

@application.route('/analysis/<analysis_id>/vulnerabilities', method='PUT')
def vulnerabilities_found(analysis_id):
    pass


@application.route('/analysis/<analysis_id>/state/build-finished',
                   method='PUT')
def analysis_build_finished(analysis_id):
    """
    Dependency extraction phase finished.

    Must contain a JSON object with the number of tasks spawned in the server
    (requests made to `/dependencies` and `/vulnerabilities` endpoints.

    Ex::
       {'task_count': <int>}
    """
    with Config.DATABASE.atomic():
        analysis = Analysis.get(Analysis.id == analysis_id)
        analysis.task_count = int(bottle.request.json['task_count'])
        analysis.save()
