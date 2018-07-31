import datetime
import functools
import uuid

import bottle
import environconfig
import peewee


###############################################################################
#                     Environment Variables Configuration                     #
###############################################################################
class Config(environconfig.EnvironConfig):
    #
    # Postgres configuration.
    # Do not pass HOST to have a Sqlite in-memory database.
    #
    DATABASE_NAME = environconfig.StringVar(default='deeptracy')
    DATABASE_USER = environconfig.StringVar(default=None)
    DATABASE_HOST = environconfig.StringVar(default=None)
    DATABASE_PASS = environconfig.StringVar(default=None)

    @environconfig.MethodVar
    def DATABASE(env):
        """
        Return a peewee database handler with the given user configuration.
        MethodVar uses memoization, so the objects behaves like a singleton.

        """
        if env.DATABASE_HOST is None:
            return peewee.SqliteDatabase(':memory:')
        else:
            return peewee.PostgresqlDatabase(
                env.DATABASE_NAME,
                user=env.DATABASE_USER,
                password=env.DATABASE_PASS,
                host=env.DATABASE_HOST)

    HOST = environconfig.StringVar(default='localhost')
    PORT = environconfig.IntVar(default=8088)
    DEBUG = environconfig.BooleanVar(default=False)


###############################################################################
#                               Database Models                               #
###############################################################################
class BaseModel(peewee.Model):
    """
    BaseModel is an abstract model with options affecting all its
    children.

    """
    id = peewee.UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        database = Config.DATABASE


class Target(BaseModel):
    repo = peewee.CharField(index=True)
    commit = peewee.CharField()

    class Meta:
        indexes = (
            (('repo', 'commit'), True),  # repo+commit are unique together
        )


class Analysis(BaseModel):
    target = peewee.ForeignKeyField(Target, backref='analyses')
    started = peewee.DateTimeField(default=datetime.datetime.utcnow)
    finished = peewee.DateTimeField(null=True, default=None)
    status = peewee.CharField()
    notify = peewee.CharField()


class RequestedDependency(BaseModel):
    # User provided data
    spec = peewee.CharField()
    installer = peewee.CharField()

    class Meta:
        indexes = (
            # spec+installer are unique
            (('spec', 'installer'), True),
        )


class InstalledDependency(BaseModel):
    package_name = peewee.CharField()
    version = peewee.CharField()
    installer = peewee.CharField()

    # Patton resolved data
    cpe = peewee.CharField(null=True)

    class Meta:
        indexes = (
            # package+version+installer are unique
            (('package_name', 'version', 'installer'), True),
        )


class Vulnerability(BaseModel):
    cve = peewee.CharField(index=True)


class VulnerableDependencies(BaseModel):
    dependency = peewee.ForeignKeyField(InstalledDependency)
    vulnerability = peewee.ForeignKeyField(Vulnerability)


class AnalysisDependencies(BaseModel):
    analysis = peewee.ForeignKeyField(Analysis, backref='dependencies')
    requested_dependency = peewee.ForeignKeyField(RequestedDependency,
                                                  backref='analyses')
    installed_dependency = peewee.ForeignKeyField(InstalledDependency,
                                                  backref='analyses')


###############################################################################
#                               Web Application                               #
###############################################################################
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
    Signal from buildbot that an analysis has started.

    Requires a JSON object with the following parameters:
        * status: Status of the finished analysis.
        * dependencies: A list of JSON objects with the following keys.
            * installer: The system used to install the dependency.
            * spec: The full specification used by the user to request the
                    package.
            * package_name: The real package name.
            * version: The installed version of the package.

    """
    with Config.DATABASE.atomic():
        analysis = Analysis.get_by_id(analysis_id)
        analysis.status = bottle.request.json['status']
        analysis.finished = datetime.datetime.utcnow()
        analysis.save()
        for dependency in bottle.request.json['dependencies']:
            requested, _ = RequestedDependency.get_or_create(
                installer=dependency['installer'],
                spec=dependency['spec'])
            installed, _ = InstalledDependency.get_or_create(
                installer=dependency['installer'],
                package_name=dependency['package_name'],
                version=dependency['version'])
            AnalysisDependencies.get_or_create(
                analysis=analysis,
                requested_dependency=requested,
                installed_dependency=installed)

###############################################################################
#                           Command Line Interface                            #
###############################################################################
def main():
    with Config.DATABASE:
        Config.DATABASE.create_tables(BaseModel.__subclasses__())

    application.run(host=Config.HOST,
                    port=Config.PORT,
                    reloader=Config.DEBUG)


if __name__ == "__main__":
    main()
