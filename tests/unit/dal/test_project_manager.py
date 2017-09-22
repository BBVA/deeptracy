# -*- coding: utf-8 -*-

import deeptracy.dal.project_manager as project_manager

from deeptracy.dal.models import Project
from tests.unit.base_test import BaseDeeptracyTest
from tests.unit.mock_db import MockDeeptracyDBEngine


class TestProjectManager(BaseDeeptracyTest):

    @classmethod
    def setUpClass(cls):
        project_manager.db = MockDeeptracyDBEngine()
        cls.db = project_manager.db

    def setUp(self):
        self.db.Session.query._ret_val = None

    def test_get_project_invalid_id(self):
        with self.assertRaises(ValueError):
            project_manager.get_project(None)

    def test_get_project_not_found(self):
        with self.assertRaises(ValueError):
            project_manager.get_project('123')

    def test_get_project_found(self):
        # mock the return value
        self.db.Session.query._ret_val = Project(id='123', repo='repo')

        project = project_manager.get_project('123')
        assert project is not None
        assert project.repo == 'repo'
