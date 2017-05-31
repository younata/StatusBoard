import json
import unittest
from unittest import mock
from unittest.mock import MagicMock

from nose.tools import eq_

from main import app
from models import CheckResult
from tests.test_helpers.helpers import contains_


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index_returns_a_single_page_react_app(self):
        result = self.app.get("/")
        eq_(result.status_code, 200)

        received_string = result.data.decode("utf-8")
        contains_(received_string, "welcome")

    @mock.patch('status_controller.data_sources')
    def test_status_when_no_sources_available_returns_empty_dictionary(self, mock_sources):
        mock_sources.return_value = []
        result = self.app.get("/status/")
        eq_(result.status_code, 200)

        received_json = json.loads(result.data.decode("utf-8"))
        eq_(received_json, [])

    @mock.patch('status_controller.data_sources')
    def test_status_when_sources_available_returns_value_from_calling_it(self, mock_sources):
        mock1 = MagicMock()
        mock1.check.return_value = CheckResult("https://example.com/foo", False)

        mock2 = MagicMock()
        mock2.check.return_value = CheckResult("https://example.com/bar", True)
        mock_sources.return_value = [mock1, mock2]

        result = self.app.get("/status/")
        eq_(result.status_code, 200)

        received_json = json.loads(result.data.decode("utf-8"))

        expected_json = [
            {'url': 'https://example.com/foo', 'success': False},
            {'url': 'https://example.com/bar', 'success': True},
        ]

        eq_(received_json, expected_json)
