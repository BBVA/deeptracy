"""
Contains the environconfig classes to parse environment variable.

"""
# pylint: disable=no-self-argument,invalid-name,no-else-return

import functools
import datetime

import environconfig
import peewee
import celery


class Config(environconfig.EnvironConfig):
    """Main environment variable parser."""
    #
    # Postgres configuration.
    # Do not pass HOST to have a Sqlite in-memory database.
    #
    POSTGRES_DB = environconfig.StringVar(default='deeptracy')
    POSTGRES_USER = environconfig.StringVar(default=None)
    POSTGRES_HOST = environconfig.StringVar(default=None)
    POSTGRES_PASSWORD = environconfig.StringVar(default=None)

    @environconfig.MethodVar
    @functools.lru_cache()
    def POSTGRES(env):
        """
        Return a peewee database handler with the given user configuration.

        """
        if env.POSTGRES_HOST is None:
            return peewee.SqliteDatabase(None)
        else:
            return peewee.PostgresqlDatabase(None)

    REDIS_HOST = environconfig.StringVar(default=None)
    REDIS_PORT = environconfig.IntVar(default=6379)
    REDIS_DB = environconfig.IntVar(default=0)

    @environconfig.MethodVar
    @functools.lru_cache()
    def REDIS(env):
        """Build the redis connection URI."""
        return f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}/{env.REDIS_DB}"

    @environconfig.MethodVar
    @functools.lru_cache()
    def CELERY(env):
        """Build the configured Celery object."""
        return celery.Celery(broker=env.REDIS, backend=env.REDIS)

    BUILDBOT_API = environconfig.StringVar(
        default='http://deeptracy-buildbot:8010')
    PATTON_HOST = environconfig.StringVar(
        default='patton.owaspmadrid.org:8000')
    SAFETY_API_KEY = environconfig.StringVar(default=None)
    BOTTLE_MEMFILE_MAX = environconfig.IntVar(default=1024*1024)
    MAX_ANALYSIS_INTERVAL = environconfig.CustomVar(
        lambda s: datetime.timedelta(seconds=int(s)),
        default=datetime.timedelta(seconds=24*60*60))

    #
    # Service configuration
    #
    HOST = environconfig.StringVar(default='localhost')
    PORT = environconfig.IntVar(default=8088)
    DEBUG = environconfig.BooleanVar(default=False)
