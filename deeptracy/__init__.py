import functools
import datetime

import environconfig
import peewee
import celery


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
    @functools.lru_cache()
    def DATABASE(env):
        """
        Return a peewee database handler with the given user configuration.

        """
        if env.DATABASE_HOST is None:
            return peewee.SqliteDatabase(None)
        else:
            return peewee.PostgresqlDatabase(None)

    REDIS_HOST = environconfig.StringVar(default=None)
    REDIS_PORT = environconfig.IntVar(default=6379)
    REDIS_DB = environconfig.IntVar(default=0)

    @environconfig.MethodVar
    @functools.lru_cache()
    def REDIS(env):
        return f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}/{env.REDIS_DB}"

    @environconfig.MethodVar
    @functools.lru_cache()
    def CELERY(env):
        return celery.Celery(broker=env.REDIS, backend=env.REDIS)

    PATTON_HOST = environconfig.StringVar(
        default='patton.owaspmadrid.org:8000')
    SAFETY_API_KEY = environconfig.StringVar(default=None)
    BOTTLE_MEMFILE_MAX = environconfig.IntVar(default=1024*1024)
    MAX_ANALYSIS_INTERVAL = environconfig.CustomVar(
        lambda secs: datetime.timedelta(seconds=int(seconds)),
        default=datetime.timedelta(seconds=24*60*60))

    #
    # Service configuration
    #
    HOST = environconfig.StringVar(default='localhost')
    PORT = environconfig.IntVar(default=8088)
    DEBUG = environconfig.BooleanVar(default=False)
