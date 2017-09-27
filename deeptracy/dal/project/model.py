# -*- coding: utf-8 -*-

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from deeptracy.utils import make_uuid
from deeptracy.dal.database import Base


class Project(Base):
    """SQLAlchemy Project model"""
    __tablename__ = 'project'

    id = Column(String, primary_key=True, default=make_uuid)
    repo = Column(String)

    scans = relationship('Scan')

    def to_dict(self):
        return {
            'id': self.id,
            'repo': self.repo,
            'scans': len(self.scans)
        }
