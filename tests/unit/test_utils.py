import requests

from unittest import mock

from tests.unit.base_test import BaseDeeptracyTest
from deeptracy.utils import valid_repo


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://not-accessible.com':
        return MockResponse({}, 403)
    elif args[0] == 'http://accessible.com':
        return MockResponse({"ok": "ok"}, 200)
    elif args[0] == 'http://not-found.com':
        return MockResponse({"ok": "ok"}, 404)

    raise requests.exceptions.RequestException


class TestUtilsValidRepo(BaseDeeptracyTest):

    @mock.patch('deeptracy.utils.requests.get', side_effect=mocked_requests_get)
    def test_valid_repo_not_found(self, mock_get):
        repo = 'http://not-found.com'
        valid = valid_repo(repo)
        assert valid is False

    @mock.patch('deeptracy.utils.requests.get', side_effect=mocked_requests_get)
    def test_valid_repo_not_accessible(self, mock_get):
        repo = 'http://not-accessible.com'
        valid = valid_repo(repo)
        assert valid is False

    @mock.patch('deeptracy.utils.requests.get', side_effect=mocked_requests_get)
    def test_valid_repo_accessible(self, mock_get):
        repo = 'http://accessible.com'
        valid = valid_repo(repo)
        assert valid is True

    @mock.patch('deeptracy.utils.requests.get', side_effect=mocked_requests_get)
    def test_valid_repo_error(self, mock_get):
        repo = 'test'
        with self.assertRaises(requests.exceptions.RequestException):
            valid_repo(repo)

    def test_invalid_repo_error(self):
        repo = None
        with self.assertRaises(ValueError):
            valid_repo(repo)
