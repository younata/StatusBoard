import json
from base64 import b64encode
from unittest import mock
from unittest.mock import MagicMock

import flask_testing
from nose.tools import eq_

import models
from main import app
from models import CheckResult
from tests.test_helpers.helpers import contains_


class AppTests(flask_testing.TestCase):
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
        eq_(result.content_type, "application/json")

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
        eq_(result.content_type, "application/json")

        received_json = json.loads(result.data.decode("utf-8"))

        expected_json = [
            {'url': 'https://example.com/foo', 'success': False},
            {'url': 'https://example.com/bar', 'success': True},
        ]

        eq_(received_json, expected_json)

    @mock.patch('status_controller.authenticator')
    def test_status_create_with_proper_authentication_creates_new_URLDataSource(self, mock_authenticator):
        mock_authenticator.return_value = True
        result = self.app.post("/status/create",
                               data=json.dumps({"url": "https://example.com/foo"}),
                               content_type='application/json',
                               headers={'Authorization': 'Basic %s' % b64encode(b"username:password").decode("ascii")}
                               )

        eq_(result.status_code, 201)
        eq_(result.content_type, "application/json")

        mock_authenticator.assert_called_with("username", "password")

        eq_(len(models.URLDataSource.query.all()), 1)
        eq_(models.URLDataSource.query.all()[0].url, "https://example.com/foo")

    @mock.patch('status_controller.authenticator')
    def test_status_create_with_proper_authentication_and_existing_URLDataSource_doesnt_make_new_one(self, mock_authenticator):
        mock_authenticator.return_value = True
        existing = models.URLDataSource('https://example.com/foo')
        self.db.session.add(existing)
        self.db.session.commit()

        result = self.app.post("/status/create",
                               data=json.dumps({"url": "https://example.com/foo"}),
                               content_type='application/json',
                               headers={'Authorization': 'Basic %s' % b64encode(b"username:password").decode("ascii")}
                               )

        eq_(result.status_code, 400)
        eq_(result.content_type, "application/json")

        mock_authenticator.assert_called_with("username", "password")

        received_json = json.loads(result.data.decode("utf-8"))

        expected_json = {
            "error": "Exists"
        }

        eq_(received_json, expected_json)

        eq_(len(models.URLDataSource.query.all()), 1)
        eq_(models.URLDataSource.query.all()[0].url, "https://example.com/foo")

    @mock.patch('status_controller.authenticator')
    def test_status_create_with_proper_authentication_and_wrong_content_type_returns_400(self, mock_authenticator):
        mock_authenticator.return_value = True
        result = self.app.post("/status/create",
                               data=json.dumps({"url": "https://example.com/foo"}),
                               headers={'Authorization': 'Basic %s' % b64encode(b"username:password").decode("ascii")}
                               )

        eq_(result.status_code, 400)
        eq_(result.content_type, "application/json")

        mock_authenticator.assert_called_with("username", "password")

        received_json = json.loads(result.data.decode("utf-8"))

        expected_json = {
            "error": "JSON Required"
        }

        eq_(received_json, expected_json)

        eq_(len(models.URLDataSource.query.all()), 0)

    @mock.patch('status_controller.authenticator')
    def test_status_create_with_proper_authentication_and_no_url_returns_400(self, mock_authenticator):
        mock_authenticator.return_value = True
        result = self.app.post("/status/create",
                               data=json.dumps({}),
                               content_type='application/json',
                               headers={'Authorization': 'Basic %s' % b64encode(b"username:password").decode("ascii")}
                               )

        eq_(result.status_code, 400)
        eq_(result.content_type, "application/json")

        received_json = json.loads(result.data.decode("utf-8"))

        expected_json = {
            "error": "URL Required"
        }

        eq_(received_json, expected_json)

        eq_(len(models.URLDataSource.query.all()), 0)

    @mock.patch('status_controller.authenticator')
    def test_status_create_with_improper_authentication_challenges_user_and_does_not_proceed(self, mock_authenticator):
        mock_authenticator.return_value = False
        result = self.app.post("/status/create",
                               data=json.dumps({"url": "https://example.com/foo"}),
                               content_type='application/json')

        eq_(result.status_code, 401)

        eq_(len(models.URLDataSource.query.all()), 0)
