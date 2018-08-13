import datetime
import time
import uuid

from deeptracy import Config

import peewee


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
    last_checked = peewee.DateTimeField(null=True, default=None)
    vulnerable = peewee.BooleanField(default=False)

    class Meta:
        indexes = (
            # package+version+installer are unique
            (('package_name', 'version', 'installer'), True),
        )


class VulnerableDependencies(BaseModel):
    dependency = peewee.ForeignKeyField(InstalledDependency)
    provider = peewee.CharField()
    ref = peewee.CharField()  # Maybe CVE, maybe not.
    details = peewee.TextField()

    class Meta:
        indexes = (
            (('dependency', 'provider', 'ref'), True),
        )


class AnalysisDependencies(BaseModel):
    analysis = peewee.ForeignKeyField(Analysis, backref='dependencies')
    requested_dependency = peewee.ForeignKeyField(RequestedDependency,
                                                  backref='analyses')
    installed_dependency = peewee.ForeignKeyField(InstalledDependency,
                                                  backref='analyses')


def init():
    def is_ready():
        try:
            with Config.DATABASE:
                # Create database when empty
                print("Creating tables")
                Config.DATABASE.create_tables(BaseModel.__subclasses__())
        except Exception as exc:
            return False
        else:
            return True

    # Wait for database connection
    print("Initializing database")
    while not is_ready():
        print("Waiting for database...")
        time.sleep(1)


if Config.DATABASE_HOST is not None:
    Config.DATABASE.init(
        Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASS,
        host=Config.DATABASE_HOST)
else:
    Config.DATABASE.init('deeptracy.db')
