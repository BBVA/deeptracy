# -*- coding: utf-8 -*-

"""Provides the sqlalchemy engine."""
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from deeptracy.config import DATABASE_URI


class DeeptracyDBEngine:

    engine = None
    Session = None

    def init_engine(self):
        self.engine = sqlalchemy.create_engine(DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        if not database_exists(db.engine.url):
            create_database(db.engine.url)

        # reflect the engine into metadata object from models
        Base.metadata.reflect(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


db = DeeptracyDBEngine()
Base = declarative_base()
