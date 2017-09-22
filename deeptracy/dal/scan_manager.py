# -*- coding: utf-8 -*-
from enum import Enum
from sqlalchemy.orm import Session
from deeptracy.dal.models import Scan


class ScanState(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    INVALID_REPO = 'INVALID_REPO'
    NO_PLUGINS_FOR_LANGUAJE = 'NO_PLUGINS_FOR_LANGUAJE'


def get_scan(scan_id: str, session: Session) -> Scan:
    """Get a project from its id"""
    if scan_id is None:
        raise ValueError('Invalid scan id {}'.format(scan_id))

    scan = session.query(Scan).get(scan_id)
    if scan is None:
        raise ValueError('Scan {} not found in database'.format(scan_id))

    return scan


def update_scan_state(scan: Scan, state: ScanState, session: Session) -> Scan:
    if scan.id is None:
        raise ValueError('Cant create scans')

    scan.state = state.name
    session.add(scan)
    return scan
