import re

from contrib.tests.base import BaseTestCase
from users.factories import UserFactory


class TestUserModel(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_model_access_token_property(self):
        """ Ensure that the access_token property in User model produces valid JTI token. """
        self.assertTrue(re.match(r'[a-f0-9]+', self.user.access_token))

    def test_model_refresh_token_property(self):
        """ Ensure that the refresh_token property in User model produces valid JTI token. """
        self.assertTrue(re.match(r'[a-f0-9]+', self.user.refresh_token))

    def test_repr_and_str(self):
        """ Ensure we can render the __str__ and __repr__ for the model. """
        self.assertIn('<User:', repr(self.user))
        self.assertIn(self.user.username, str(self.user))
