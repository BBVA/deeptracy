# -*- coding: utf-8 -*-
from enum import Enum
from typing import List
from sqlalchemy.orm import Session
from deeptracy.dal.models import ScanAnalysis, ScanAnalysisVulnerability


class ScanAnalysisState(Enum):
    PENDING = 'PENDING'


def get_scan_analysis(scan_analysis_id: str, session: Session) -> ScanAnalysis:
    scan_analysis = session.query(ScanAnalysis).get(scan_analysis_id)
    return scan_analysis


def add_scan_vulnerabilities_results(scan_analysis_id: str, vulnerabilities: List[dict], session: Session):

    if scan_analysis_id is None:
        raise ValueError('Invalid scan analysis id {}'.format(scan_analysis_id))

    for vul in vulnerabilities:
        scan_analysis_vul = ScanAnalysisVulnerability(
                                scan_analysis_id=scan_analysis_id,
                                library=vul.get('library'),
                                version=vul.get('version'),
                                severity=vul.get('severity'),
                                summary=vul.get('summary'),
                                advisory=vul.get('advisory'))
        session.add(scan_analysis_vul)


def add_scan_analysis(scan_id: str, plugin_id: str, session: Session) -> ScanAnalysis:

    if scan_id is None:
        raise ValueError('Invalid scan id {}'.format(scan_id))

    if plugin_id is None:
        raise ValueError('Invalid plugin_id id {}'.format(plugin_id))

    scan_analysis = ScanAnalysis(scan_id=scan_id, plugin_id=plugin_id, state=ScanAnalysisState.PENDING.name)
    session.add(scan_analysis)
    return scan_analysis
