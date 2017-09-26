# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
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
    scan_vulnerability = relationship('ScanVulnerability', lazy='subquery')
    project = relationship("Project", lazy='subquery')


class Plugin(Base):
    """SQLAlchemy Plugin model"""
    __tablename__ = 'plugin'

    id = Column(String, primary_key=True, default=make_uuid)
    name = Column(String)
    lang = Column(String)
    active = Column(Boolean)


class ScanAnalysis(Base):
    """SQLAlchemy ScanAnalysis model"""
    __tablename__ = 'scan_analysis'

    id = Column(String, primary_key=True, default=make_uuid)
    scan_id = Column(String, ForeignKey('scan.id'))
    plugin_id = Column(String, ForeignKey('plugin.id'))
    state = Column(String)

    scan_analysis_vulnerability = relationship('ScanAnalysisVulnerability')
    plugin = relationship('Plugin')
    scan = relationship('Scan', lazy='subquery')


class ScanAnalysisVulnerability(Base):
    """SQLAlchemy ScanAnalysisVulnerability model"""
    __tablename__ = 'scan_analysis_vulnerability'

    id = Column(String, primary_key=True, default=make_uuid)
    scan_analysis_id = Column(String, ForeignKey('scan_analysis.id'))
    library = Column(String)
    version = Column(String)
    severity = Column(String)
    summary = Column(String)
    advisory = Column(String)


class ScanVulnerability(Base):
    """SQLAlchemy ScanVulnerability model"""
    __tablename__ = 'scan_vulnerability'

    id = Column(String, primary_key=True, default=make_uuid)
    scan_id = Column(String, ForeignKey('scan.id'))
    library = Column(String)
    version = Column(String)
    severity = Column(String)
    summary = Column(String)
    advisory = Column(String)
