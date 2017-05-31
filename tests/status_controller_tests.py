from unittest import mock

import flask_testing
from nose.tools import eq_

import models
from main import app
from status_controller import authenticator, data_sources


class StatusControllerTests(flask_testing.TestCase):
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

    @mock.patch('os.getenv')
    def test_authenticator_returns_true_if_matches_environmental_stuff(self, env_mock):
        def env_side_effect(env_name):
            if env_name == "ADMIN_USERNAME":
                return "admin_username"
            elif env_name == "ADMIN_PASSWORD":
                return "admin_password"
            return "dunno"
        env_mock.side_effect = env_side_effect

        eq_(authenticator("admin_username", "admin_password"), True)
        eq_(authenticator("admin_username", "wrong password"), False)
        eq_(authenticator("admin_username", None), False)
        eq_(authenticator("wrong username", "admin_password"), False)
        eq_(authenticator(None, "admin_password"), False)
        eq_(authenticator("wrong username", "wrong password"), False)
        eq_(authenticator(None, None), False)

    @mock.patch('os.getenv')
    def test_authenticator_returns_false_if_not_configured(self, env_mock):
        env_mock.return_value = None

        eq_(authenticator("admin_username", "admin_password"), False)
        eq_(authenticator(None, None), False)

    def test_data_sources_returns_all_known_url_data_sources(self):
        source1 = models.URLDataSource('https://example.com/endpoint')
        source2 = models.URLDataSource('https://example.com/endpoint_2')
        source3 = models.URLDataSource('https://example.com/endpoint_3')

        for source in [source1, source2, source3]:
            self.db.session.add(source)
        self.db.session.commit()

        sorted_data_sources = sorted(
            data_sources(),
            key=lambda s: s.url
        )
        eq_(sorted_data_sources, [source1, source2, source3])
