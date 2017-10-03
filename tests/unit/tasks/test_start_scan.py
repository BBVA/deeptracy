# # -*- coding: utf-8 -*-
#
# import deeptracy.tasks.start_scan as task
# from unittest import mock
# from unittest.mock import MagicMock, ANY
# from deeptracy.dal.models import Project, Scan, Plugin
# from tests.unit.base_test import BaseDeeptracyTest
# from tests.unit.mock_db import MockDeeptracyDBEngine
#
#
# class TestStartScan(BaseDeeptracyTest):
#
#     @mock.patch('deeptracy.tasks.start_scan.get_plugins_for_lang')
#     @mock.patch('deeptracy.utils.valid_repo')
#     @mock.patch('deeptracy.tasks.start_scan.get_scan')
#     @mock.patch('deeptracy.utils.clone_repo')
#     @mock.patch('deeptracy.tasks.start_scan.db')
#     @mock.patch('deeptracy.tasks.start_scan.add_scan_analysis')
#     @mock.patch('deeptracy.tasks.start_scan.run_analyzer')
#     def test_should_get_project_from_manager(self,
#                                              modk_run_analyzer,
#                                              modk_add_scan_analysis,
#                                              mock_db,
#                                              mock_clone_repo,
#                                              mock_get_scan,
#                                              mock_valid_repo,
#                                              mock_get_plugins_for_lang):
#
#         plugin = Plugin(id='123', name='plugin', lang='lang', active=True)
#         project = Project(id='123', repo='http://repo')
#         scan = Scan(id='123', project_id=project.id, lang='lang', project=project)
#
#         mocked_session = MockDeeptracyDBEngine()
#         mock_db.return_value = mocked_session
#         mock_clone_repo.return_value = MagicMock()
#         mock_get_scan.return_value = scan
#         mock_valid_repo.return_value = True
#         mock_get_plugins_for_lang.return_value = [plugin]
#         modk_add_scan_analysis.return_value = MagicMock()
#         modk_run_analyzer.return_value = MagicMock()
#         task.SCAN_PATH = '/tmp'
#
#         task.start_scan(scan.id)
#
#         mock_get_scan.assert_called_with(scan.id, ANY)
#         mock_valid_repo.assert_called_with(project.repo)
#         mock_get_plugins_for_lang.assert_called_with(scan.lang, ANY)
#         mock_clone_repo.assert_called_with(task.SCAN_PATH, scan.id, project.repo)
#         modk_add_scan_analysis.assert_called_with(scan.id, plugin.id, ANY)
