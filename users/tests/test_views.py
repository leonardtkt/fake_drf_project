from django.urls import reverse
from django.test import override_settings

from unittest import mock
from requests.exceptions import HTTPError
from social_core.exceptions import AuthTokenError

from contrib.tests.base import BaseTestCase
from users.factories import UserFactory


class TestMeView(BaseTestCase):
    ME_URL = reverse('me')

    def test_not_logged_in_means_401(self):
        """ Ensure that we fail gracefully if the user isn't logged in. """

        response = self.client.get(self.ME_URL)
        self.assertEqual(response.status_code, 401)

    def test_can_see_current_user_data(self):
        """ Ensure we see our user info if we are logged in. """

        self.user_auth()
        response = self.client.get(self.ME_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)


class TestPasswordResetView(BaseTestCase):
    RESET_URL = reverse('password-reset')

    @mock.patch('users.serializers.PasswordResetSerializer.is_valid', return_value=True)
    @mock.patch('users.serializers.PasswordResetSerializer.save', return_value=True)
    def test_password_reset_endpoint(self, m1, m2):
        """ Just a good response, nothing special. """

        payload = {'email': 'gao@wertkt.com'}
        response = self.client.post(self.RESET_URL, payload=payload)
        self.assertEqual(response.status_code, 200)


class TestPasswordResetConfirmView(BaseTestCase):
    RESET_CONFIRM_URL = reverse('password-reset-confirm')

    @mock.patch('users.serializers.PasswordResetConfirmSerializer.is_valid', return_value=True)
    @mock.patch('users.serializers.PasswordResetConfirmSerializer.save', return_value=True)
    def test_password_reset_endpoint(self, m1, m2):
        """ Just a good response, nothing special. """

        payload = {
            'token': '123',
            'uid': '321',
            'new_password1': 'gaogao',
            'new_password2': 'gaogao'
        }
        response = self.client.post(self.RESET_CONFIRM_URL, payload=payload)
        self.assertEqual(response.status_code, 200)


class TestAPIAuthViewSet(BaseTestCase):
    PASSWORD_LOGIN_URL = reverse('token-obtain-pair')

    def setUp(self):
        self.user = UserFactory(password='Trump2020')

    def test_password_login_no_password(self):
        """ A password login POST with no password should fail. """

        data = {'username': self.user.username}
        response = self.client.post(self.PASSWORD_LOGIN_URL, data=data)
        self.assertEqual(response.status_code, 400)

    def test_password_login_bad_password(self):
        """ A password login POST with incorrect password should fail. """

        data = {'username': self.user.username, 'password': 'Biden2020'}
        response = self.client.post(self.PASSWORD_LOGIN_URL, data=data)
        self.assertEqual(response.status_code, 401)

    def test_password_login_good(self):
        """ A password login POST with good username and matching password should pass. """

        data = {'username': self.user.username, 'password': 'Trump2020'}
        response = self.client.post(self.PASSWORD_LOGIN_URL, data=data)
        self.assertEqual(response.status_code, 200)
        # TODO: Better checks.
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])


class TestUserViewSet(BaseTestCase):
    USERS_URL = reverse('users-list')
    USERS_VAL_EMAIL = reverse('users-validate-email')

    def test_good_registration(self):
        """ User registration POST with required fields should pass. """

        data = {'username': 'cheeto', 'password': '505asde50',
                'first_name': 'Dylan', 'last_name': 'Hayward',
                'email': 'email@email.com'}
        response = self.client.post(self.USERS_URL, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'cheeto')

    def test_bad_registration_preexisting_email(self):
        """ User registration POST with email address of preexisting user should fail. """

        user = UserFactory()
        data = {'username': 'cheeto', 'password': '505asde50',
                'first_name': 'Dylan', 'last_name': 'Hayward',
                'email': user.email}
        response = self.client.post(self.USERS_URL, data=data)
        self.assertEqual(response.status_code, 400)

    def test_bad_registration_preexisting_username(self):
        """ User registration POST with username of preexisting user should fail. """

        user = UserFactory()
        data = {'username': user.username, 'password': '505asde50',
                'first_name': 'Dylan', 'last_name': 'Hayward',
                'email': user.email}
        response = self.client.post(self.USERS_URL, data=data)
        self.assertEqual(response.status_code, 400)

    def test_update_email_address_should_pass(self):
        """ PATCHing our user endpoint should update our email. """

        self.user_auth()
        data = {'email': 'trump2020@hotmail.com'}
        patch_url = reverse('users-detail', args=[self.user.id])
        response = self.client.patch(patch_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'trump2020@hotmail.com')

    def test_user_cannot_see_other_users(self):
        """ List view should only show the currently logged in user (if using default permissions.) """

        self.user_auth()
        UserFactory.create_batch(10)
        response = self.client.get(self.USERS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_normal_user_can_see_own_user_data_but_not_password(self):
        """ Ensure that the serializer isn't returning the hashed password. """

        self.user_auth()
        response = self.client.get(self.USERS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['email'], self.user.email)
        self.assertFalse('password' in response.data['results'][0].keys())

    @mock.patch('users.serializers.AccountVerifySerializer.is_valid', return_value=True)
    @mock.patch('users.serializers.AccountVerifySerializer.save', return_value=True)
    def test_validate_email(self, m1, m2):
        """ Ensure we get a good response from account verify endpoint. """

        self.user_auth()
        response = self.client.get(self.USERS_VAL_EMAIL)
        self.assertEqual(response.status_code, 200)


class TestSocialViewSet(BaseTestCase):
    OAUTH_URL = reverse('oauth-login-list')

    def setUp(self):
        self.payload = {
            'provider': 'facebook',
            'access_token': 'all-cats-are-beautiful',
        }

    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='321')
    @override_settings(SOCIAL_AUTH_FACEBOOK_SECRET='123')
    @mock.patch('social_core.backends.facebook.FacebookOAuth2.do_auth')
    def test_good_oauth_to_fake_facebook(self, m1):
        """ We should get a beautiful response back. """

        user = UserFactory()
        m1.return_value = user
        response = self.client.post(self.OAUTH_URL, self.payload)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['username'], user.username)
        self.assertTrue(response.data['token'])  # token won't match since diff timestamp

    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='321')
    @override_settings(SOCIAL_AUTH_FACEBOOK_SECRET='123')
    def test_bad_oauth_with_invalid_provider_name(self):
        """ Bad provider name returns 400. """

        custom_payload = {
            'provider': 'fakebook',
            'access_token': 'all-cats-are-beautiful',
        }
        response = self.client.post(self.OAUTH_URL, custom_payload)
        self.assertEqual(response.status_code, 400)

    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY=None)
    @override_settings(SOCIAL_AUTH_FACEBOOK_SECRET=None)
    def test_bad_oauth_with_provider_key_not_set(self):
        """ Must set provider key. """

        response = self.client.post(self.OAUTH_URL, self.payload)
        self.assertEqual(response.status_code, 400)

    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='321')
    @override_settings(SOCIAL_AUTH_FACEBOOK_SECRET='123')
    @mock.patch('social_core.backends.facebook.FacebookOAuth2.do_auth')
    def test_some_general_error_idk(self, m1):
        """ This will generate a 400-series response from the OAuth provider. """

        m1.side_effect = HTTPError()
        response = self.client.post(self.OAUTH_URL, self.payload)
        self.assertEqual(response.status_code, 400)

    @override_settings(SOCIAL_AUTH_FACEBOOK_KEY='321')
    @override_settings(SOCIAL_AUTH_FACEBOOK_SECRET='123')
    @mock.patch('social_core.backends.facebook.FacebookOAuth2.do_auth')
    def test_bad_oauth_token(self, m1):
        """ This will generate a Token login error response from the OAuth provider. """

        m1.side_effect = AuthTokenError(backend='facebook')
        response = self.client.post(self.OAUTH_URL, self.payload)
        self.assertEqual(response.status_code, 400)
