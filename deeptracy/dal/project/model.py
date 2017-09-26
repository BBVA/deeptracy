# -*- coding: utf-8 -*-
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

import deeptracy.utils as utils
from deeptracy.dal.database import Base
from deeptracy.dal.models import Scan


class Project(Base):
    """SQLAlchemy Project model"""
    __tablename__ = 'project'

    id = Column(String, primary_key=True, default=utils.make_uuid)
    lang = Column(String)
    repo = Column(String)

    scans = relationship(Scan)

    def to_dict(self):
        return {
            'id': self.id,
            'lang': self.lang,
            'scans': len(self.scans)
        }
