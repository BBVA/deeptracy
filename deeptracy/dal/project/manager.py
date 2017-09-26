# -*- coding: utf-8 -*-

from sqlalchemy.orm import Session
from deeptracy.dal.project import Project


def get_project(project_id: str, session: Session) -> Project:
    """Get a project from its id"""
    if project_id is None:
        raise ValueError('Invalid project id {}'.format(project_id))

    project = session.query(Project).get(project_id)
    if project is None:
        raise ValueError('Project {} not found in database'.format(project_id))

    return project


def get_project_list(session: Session):
    return session.query(Project).all()


def add_project(session: Session, **kwargs):
    project = Project(**kwargs)
    session.add(project)
    return project


__all__ = ['get_project', 'get_project_list', 'add_project', ]
