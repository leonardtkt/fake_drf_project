from rest_framework.test import APITestCase, APIClient

from users.factories import UserFactory


class BaseTestCase(APITestCase):
    """ The base test case to be inherited for all other tests.
    - Use self.user_auth() to create and login as a normal user.
    - Use self.admin_auth() to create and login as a superuser.
    """

    def user_auth(self):
        self.user = UserFactory()
        self._authenticate()

    def admin_auth(self):
        self.user = UserFactory(is_superuser=True, is_staff=True)
        self._authenticate()

    def _authenticate(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access_token}')
        self.client.force_authenticate(user=self.user)
