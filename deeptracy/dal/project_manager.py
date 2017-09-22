# -*- coding: utf-8 -*-

from deeptracy.dal.models import Project
from deeptracy.dal.database import db


def get_project(project_id: str) -> Project:
    """Get a project from its id"""
    session = db.Session()

    if project_id is None:
        raise ValueError('Invalid project id {}'.format(project_id))

    project = session.query(Project).get(project_id)
    if project is None:
        raise ValueError('Project {} not found in database'.format(project_id))

    session.close()

    return project
