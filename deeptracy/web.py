import datetime

from deeptracy import Config
from deeptracy import providers
from deeptracy import tasks
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
def analysis_create():
    """
    Create and start a new analysis for the given repository & commit.

    Requires a JSON object with the following parameters:
        * repository: The repository.
        * commit: The commit.
        * webhook (optional): Webhook to notify to when the analysis finish.

    Example:

    .. code-block:: json

       {"repository": "https://github.com/nilp0inter/gitsectest",
        "commit": "fdd09edd73f3fe87ea4265eeddb95935c7d25a51",
        "webhook": "http://myapp.com/analysis-finished"}

    Returns a JSON object containing the id of the created analysis.

    .. code-block:: json

       {"id": "b6e98743-7830-4aef-adf6-6a0b022f778a"}

    """
    with Config.DATABASE.atomic():
        analysis = Analysis.create(
            target=Target.get_or_create(
                repository=bottle.request.json['repository'],
                commit=bottle.request.json['commit'])[0],
            webhook=bottle.request.json.get('webhook', None))

    tasks.request_extraction.delay(analysis.id)

    return {'id': str(analysis.id)}


@application.route('/analysis/<analysis_id>/extraction/started', method='PUT')
def extraction_started(analysis_id):
    """
    Signal from buildbot that the extraction phase for an analysis has started.

    .. note:: Internal API

    """
    with Config.DATABASE.atomic():
        analysis = Analysis.get(Analysis.id == analysis_id)
        # TODO: Check analysis state or implement a state machine inside the
        # model
        analysis.state = 'EXTRACTING'
        analysis.save()


@application.route('/analysis/<analysis_id>/extraction/succeeded',
                   method='PUT')
def extraction_succeeded(analysis_id):
    """
    Dependency extraction phase succeeded.

    Must contain a JSON object with the number of tasks spawned in the server
    (requests made to `/dependencies` and `/vulnerabilities` endpoints.

    Example result:

    .. code-block:: json

       {'task_count': <int>}

    .. note:: Internal API

    """
    with Config.DATABASE.atomic():
        analysis = Analysis.get(Analysis.id == analysis_id)
        analysis.state = 'ANALYZYING'
        analysis.task_count = int(bottle.request.json['task_count'])
        analysis.save()


@application.route('/analysis/<analysis_id>/extraction/failed', method='PUT')
def extraction_failed(analysis_id):
    """
    Dependency extraction phase failed.

    .. note:: Internal API

    """
    with Config.DATABASE.atomic():
        analysis = Analysis.get(Analysis.id == analysis_id)
        analysis.state = 'FAILURE'
        analysis.save()


@application.route('/analysis/<analysis_id>/dependencies', method='POST')
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

    .. note:: Internal API

    """

    # Create database objects returning a list of scanneable artifacts.
    artifacts = create_dependencies(analysis_id, bottle.request.json)

    # Launch dependency scan and mark done when finished.
    analysis_task = (
        providers.analyze_artifacts(artifacts)  # Returns a group of tasks.
        | tasks.mark_task_done.si(analysis_id)).delay()

    return {'task_id': analysis_task.id, 'scanning': len(artifacts)}


@application.route('/analysis/<analysis_id>/vulnerabilities', method='POST')
def vulnerabilities_found(analysis_id):
    """
    Vulnerability data from buildbot.

    .. note:: Internal API

    """
    pass
