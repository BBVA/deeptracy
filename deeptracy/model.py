"""
This module contains the database model of DeepTracy.

The database model is managed with peewee.

"""
# pylint: disable=missing-docstring,too-few-public-methods,unused-argument
# pylint: disable=no-else-return,no-member,not-context-manager
import datetime
import time
import uuid

from playhouse import postgres_ext
from playhouse import signals
import peewee

from deeptracy import Config


class BaseModel(signals.Model):
    """
    BaseModel is an abstract model with options affecting all its
    children.
    """
    id = peewee.UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        database = Config.POSTGRES


class Target(BaseModel):
    repository = peewee.CharField(
        index=True,
        help_text='Git repository subject to analysis.')
    commit = peewee.CharField(
        help_text='Code version.')

    class Meta:
        indexes = (
            (('repository', 'commit'), True),  # Unique Index
        )


class Analysis(BaseModel):
    target = peewee.ForeignKeyField(
        Target,
        backref='analyses',
        help_text='Subject of this analysis.')
    started = peewee.DateTimeField(
        default=datetime.datetime.utcnow,
        help_text='Timestamp of analysis start.')
    webhook = peewee.CharField(
        null=True,
        default=True,
        help_text='URL to notify when analysis is DONE')
    state = peewee.CharField(
        choices=(
            ('CREATED', 'CREATED'),
            ('EXTRACTING', 'EXTRACTING'),
            ('ANALYZYING', 'ANALYZYING'),
            ('SUCCESS', 'SUCCESS'),
            ('FAILURE', 'FAILURE')),
        default='CREATED',
        help_text='Current analysis state.')
    task_count = peewee.IntegerField(
        null=True,
        default=None,
        help_text='Total number of spawned tasks for this analysis.')
    tasks_done = peewee.IntegerField(
        default=0,
        help_text='Number of finished tasks.')

    def save(self, *args, **kwargs):
        if (self.state == 'ANALYZYING'
                and self.task_count == self.tasks_done):
            self.state = 'SUCCESS'
        super().save(*args, **kwargs)


@signals.post_save(sender=Analysis)
def notify_analysis_done(model_class, instance, created):
    if (instance.state in ['FAILURE', 'SUCCESS']
            and instance.webhook is not None):
        from deeptracy import tasks
        tasks.notify_user.delay(
            webhook=instance.webhook,
            analysis_id=instance.id,
            state=instance.state)


class Artifact(BaseModel):
    source = peewee.CharField(
        help_text='Name of the entity providing the artifact.')
    name = peewee.CharField(
        help_text='Unique identification key of the artifact on source.')
    version = peewee.CharField(
        help_text='Version of the artifact.')
    last_checked = peewee.DateTimeField(
        null=True,
        default=None,
        help_text=('Timestamp of the latest analysis performed for '
                   'this artifact.'))

    def analysis_needed(self):
        if self.last_checked is None:
            return True
        else:
            return self.last_checked < (datetime.datetime.utcnow()
                                        + Config.MAX_ANALYSIS_INTERVAL)

    class Meta:
        indexes = (
            (('source', 'version', 'name'), True),  # Unique Index
        )


class Vulnerability(BaseModel):
    artifact = peewee.ForeignKeyField(
        Artifact,
        help_text='Affected artifact.')
    provider = peewee.CharField(
        help_text='Tool providing the information.')
    reference = peewee.CharField(
        help_text='Vulnerability identifier used by the provider.')
    details = postgres_ext.BinaryJSONField(
        help_text='Extra information provided about the vulnerability.')
    last_seen = peewee.DateTimeField(
        default=datetime.datetime.utcnow,
        help_text=('Timestamp of the latest analysis detecting '
                   'this vulnerability.'))

    class Meta:
        indexes = (
            (('artifact', 'provider', 'reference'), True),  # Unique Index
        )


class Installation(BaseModel):
    analysis = peewee.ForeignKeyField(
        Analysis,
        backref='dependencies',
        help_text='Cause of the installation.')
    execution = peewee.UUIDField(
        help_text='Identifier of the installer execution.')
    installer = peewee.CharField(
        help_text='Name of the system used to perform the installation.')
    spec = peewee.CharField(
        help_text='The user specification to the installer.')
    artifact = peewee.ForeignKeyField(
        Artifact,
        backref='installations',
        help_text='The installed artifact.')

    class Meta:
        indexes = (
            (('analysis', 'execution', 'artifact', 'spec'), True),  # Unique Index
        )


def register_installations(analysis_id, execution_id, installations):
    """
    Register Installations for an Analysis under one execution context,
    creating Artifacts when necessary.

    Return a list of the artifacts needing analysis.

    """
    artifacts = list()
    with Config.POSTGRES.atomic():
        analysis = Analysis.get_by_id(analysis_id)
        for installation in installations:
            artifact, created = Artifact.get_or_create(
                source=installation['source'],
                name=installation['name'],
                version=installation['version'])
            artifacts.append(artifact)
            Installation.get_or_create(
                analysis=analysis,
                execution=execution_id,
                installer=installation['installer'],
                spec=installation['spec'],
                artifact=artifact)
    return artifacts


def init():
    def is_ready():
        try:
            with Config.POSTGRES:
                # Create database when empty
                print('Creating tables')
                Config.POSTGRES.create_tables(BaseModel.__subclasses__())
        except Exception:  # TODO: Capture specific exception
            return False
        else:
            return True

    # Wait for database connection
    print('Initializing database')
    while not is_ready():
        print('Waiting for database...')
        time.sleep(1)


if Config.POSTGRES_HOST is not None:
    Config.POSTGRES.init(
        Config.POSTGRES_DB,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        host=Config.POSTGRES_HOST)
else:
    Config.POSTGRES.init('deeptracy.db')
