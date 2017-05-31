import unittest
from unittest import mock
from unittest.mock import MagicMock

from nose.tools import eq_

from main import app
from tests.test_helpers.helpers import contains_


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    @mock.patch('status_controller.data_sources')
    def test_index_when_no_sources_available_returns_not_yet_configured(self, mock_sources):
        mock_sources.return_value = []
        result = self.app.get("/")
        eq_(result.status_code, 200)

        string = result.data.decode("utf-8")
        contains_(string, "Not yet configured")

    @mock.patch('status_controller.data_sources')
    def test_index_when_sources_available_returns_value_from_calling_it(self, mock_sources):
        mock1 = MagicMock()
        mock1.return_value = 'woot'

        mock2 = MagicMock()
        mock2.return_value = 'bloop'
        mock_sources.return_value = [mock1, mock2]

        result = self.app.get("/")
        eq_(result.status_code, 200)

        string = result.data.decode("utf-8")
        contains_(string, "['woot', 'bloop']")
