from django.urls import reverse
from django.db import DatabaseError
from django.conf import settings
from django.core.cache import cache

from unittest import mock
import shutil

from contrib.tests.base import BaseTestCase
from contrib.models import PublicGlobalSettings


class TestGlobalSettingsView(BaseTestCase):
    GLOBALS_URL = reverse('globals')

    def setUp(self):
        self.user_auth()

    def test_global_settings_created(self):
        """ If settings created in back office, ensure we get a response. """

        PublicGlobalSettings.objects.create()
        response = self.client.get(self.GLOBALS_URL)
        self.assertEqual(response.status_code, 200)

    def test_global_settings_not_created(self):
        """ If settings NOT created in back office, ensure we still get a response. """

        response = self.client.get(self.GLOBALS_URL)
        self.assertEqual(response.status_code, 200)


class TestHealthViewSet(BaseTestCase):
    HEALTH_URL = reverse('health-list')

    def setUp(self):
        self.status_fields = ['db', 'status']
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        """ No file pollution. """
        try:
            cls.addCleanup(shutil.rmtree('health_check_storage_test'))
        except FileNotFoundError:
            pass
        finally:
            super().tearDownClass()

    def test_health_endpoint_ok(self):
        """ Should get this result normally. """
        response = self.client.get(self.HEALTH_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'version': settings.HEALTH_ENDPOINT_VERSION, 'postgres': True, 'storage': True})
        self.assertEqual(response.status_code, 200)

    def test_determine_db_status(self):
        """ Health should not be ok if it cannot connect to the db. """
        with mock.patch('django.db.backends.utils.CursorWrapper') as mock_cursor:
            mock_cursor.side_effect = DatabaseError
            response = self.client.get(self.HEALTH_URL)
        self.assertEqual(response.data, {'version': settings.HEALTH_ENDPOINT_VERSION, 'postgres': False, 'storage': True})
        self.assertEqual(response.status_code, 400)

    @mock.patch('django.core.files.storage.FileSystemStorage.exists')
    def test_file_doesnt_exist(self, m1):
        """ Health should not be ok if the file created cannot be found. """
        # @TODO handle other storage backends
        m1.return_value = False
        response = self.client.get(self.HEALTH_URL)
        self.assertEqual(response.data, {'version': settings.HEALTH_ENDPOINT_VERSION, 'postgres': True, 'storage': False})
        self.assertEqual(response.status_code, 400)

    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='bad_value')
    def test_read_file_mismatch_fail(self, m1):
        """ Health should not be ok if the contents of file dont match. """
        # @TODO handle other storage backends
        response = self.client.get(self.HEALTH_URL)
        self.assertEqual(response.data, {'version': settings.HEALTH_ENDPOINT_VERSION, 'postgres': True, 'storage': False})
        self.assertEqual(response.status_code, 400)

    @mock.patch('django.core.files.storage.FileSystemStorage.delete')
    def test_file_exists_after_deletion(self, m1):
        """ Health should not be ok if file exists after deletion. """
        # @TODO handle other storage backends
        m1.return_value = True
        response = self.client.get(self.HEALTH_URL)
        self.assertEqual(response.data, {'version': settings.HEALTH_ENDPOINT_VERSION, 'postgres': True, 'storage': False})
        self.assertEqual(response.status_code, 400)


class SwaggerTest(BaseTestCase):
    SWAGGER_URL = reverse('schema-swagger-ui')

    def test_basepath_only(self):
        """ Should produce a 200 if we are currently generating a valid schema. """
        params = {
            'format': 'openapi',
        }
        response = self.client.get(self.SWAGGER_URL, params)
        self.assertEqual(response.status_code, 200)
