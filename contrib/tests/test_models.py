from contrib.tests.base import BaseTestCase
from contrib import models


class TestPublicGlobalSettings(BaseTestCase):
    def setUp(self):
        self.pgs = models.PublicGlobalSettings()

    def test_repr_and_str(self):
        """ Ensure we can render the __str__ and __repr__ for the model. """
        self.assertIn('PublicGlobalSettings(', repr(self.pgs))
        self.assertEqual('Public Global Settings', str(self.pgs))


class TestPrivateGlobalSettings(BaseTestCase):
    def setUp(self):
        self.pgs = models.PrivateGlobalSettings()

    def test_repr_and_str(self):
        """ Ensure we can render the __str__ and __repr__ for the model. """
        self.assertIn('PrivateGlobalSettings(', repr(self.pgs))
        self.assertEqual('Private Global Settings', str(self.pgs))
