import datetime

from deeptracy import Config
from deeptracy.model import Analysis
from deeptracy.model import AnalysisDependencies
from deeptracy.model import InstalledDependency
from deeptracy.model import RequestedDependency
from deeptracy.model import Target
from deeptracy.providers import analyze_dependency

import bottle



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
                repo=bottle.request.json['repo'],
                commit=bottle.request.json['commit'])[0],
            status="IN_PROGRESS",
            notify=bottle.request.json['notify'])
    return {'id': str(analysis.id)}


@application.route('/analysis/<analysis_id>', method='POST')
def analysis_finished(analysis_id):
    """
    Signal from buildbot that an analysis has finished.

    Requires a JSON object with the following parameters:
        * status: Status of the finished analysis.
        * dependencies: A list of JSON objects with the following keys.
            * installer: The system used to install the dependency.
            * spec: The full specification used by the user to request the
                    package.
            * package_name: The real package name.
            * version: The installed version of the package.

    """
    analysis_pending = []

    with Config.DATABASE.atomic():
        analysis = Analysis.get_by_id(analysis_id)
        analysis.status = bottle.request.json['status']
        analysis.finished = datetime.datetime.utcnow()
        analysis.save()
        for dependency in bottle.request.json['dependencies']:
            requested, _ = RequestedDependency.get_or_create(
                installer=dependency['installer'],
                spec=dependency['spec'])

            installed, created = InstalledDependency.get_or_create(
                installer=dependency['installer'],
                package_name=dependency['package_name'],
                version=dependency['version'])
            if created:  # Therefore not analyzed
                analysis_pending.append(installed.id)

            AnalysisDependencies.get_or_create(
                analysis=analysis,
                requested_dependency=requested,
                installed_dependency=installed)

    for dependency_id in analysis_pending:
        Config.QUEUE.enqueue(analyze_dependency, dependency_id)
