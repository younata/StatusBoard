from unittest import mock
from unittest.mock import MagicMock

import flask_testing
from nose.tools import eq_

import models
from main import app


class URLDataSourceTests(flask_testing.TestCase):
    def create_app(self):
        return app

    def setUp(self):
        self.db = models.db
        self.app = app.test_client()
        self.db.init_app(app)

        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    @mock.patch('requests.get')
    def test_check_perform_request_makes_get_request_to_the_url(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        subject = models.URLDataSource('https://example.com/endpoint')
        eq_(subject.check(), models.CheckResult('https://example.com/endpoint', True))

        eq_(mock_get.called, True)
        mock_get.assert_called_with('https://example.com/endpoint')
        eq_(len(mock_get.mock_calls), 1)

    @mock.patch('requests.get')
    def test_check_returns_unsuccessful_if_not_200_status_returned(self, mock_get):
        mock_get.return_value = MagicMock(status_code=400)
        subject = models.URLDataSource('https://example.com/endpoint')
        eq_(subject.check(), models.CheckResult('https://example.com/endpoint', False))

        eq_(mock_get.called, True)
        mock_get.assert_called_with('https://example.com/endpoint')
        eq_(len(mock_get.mock_calls), 1)
