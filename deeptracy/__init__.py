import functools

import environconfig
import peewee
import redis
import rq


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
        if env.REDIS_HOST is None:
            import fakeredis
            return fakeredis.FakeStrictRedis()
        else:
            return redis.StrictRedis(host=env.REDIS_HOST,
                                     port=env.REDIS_PORT,
                                     db=env.REDIS_DB)

    @environconfig.MethodVar
    @functools.lru_cache()
    def QUEUE(env):
        return rq.Queue(is_async=env.REDIS_HOST is not None,
                        connection=env.REDIS)

    PATTON_HOST = environconfig.StringVar(
        default='patton.owaspmadrid.org:8000')
    #
    # Service configuration
    #
    HOST = environconfig.StringVar(default='localhost')
    PORT = environconfig.IntVar(default=8088)
    DEBUG = environconfig.BooleanVar(default=False)
