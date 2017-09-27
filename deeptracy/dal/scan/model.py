# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from deeptracy.utils import make_uuid
from deeptracy.dal.database import Base


class Scan(Base):
    """SQLAlchemy Scan model"""
    __tablename__ = 'scan'

    id = Column(String, primary_key=True, default=make_uuid)
    project_id = Column(String, ForeignKey('project.id'))
    lang = Column(String)
    analysis_count = Column(Integer)
    analysis_done = Column(Integer)
    state = Column(String)
    source_path = Column(String)

    scan_analysis = relationship('ScanAnalysis', lazy='subquery')
    scan_vulnerabilities = relationship('ScanVulnerability', lazy='subquery')

    project = relationship('Project', lazy='subquery')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'lang': self.lang,
            'analysis_count': self.analysis_count,
            'analysis_done': self.analysis_done,
            'state': self.state,
            'scan_analysis': self.scan_analysis,
            'project': self.project
        }
