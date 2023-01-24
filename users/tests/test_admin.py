from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import override_settings

from copy import deepcopy

from contrib.tests.base import BaseTestCase
from users import factories

User = get_user_model()


class TestUserCreation(BaseTestCase):
    # add your required fields here
    payload = {
        'username': 'dylan',
        'email': 'dylan@wertkt.com',
        'first_name': 'Dylan',
        'last_name': 'Hayward',
    }
    USER_CREATE_URL = reverse('admin:users_user_add')

    def setUp(self):
        self.admin_auth()
        self.client.force_login(self.user)

    def test_create_user_through_back_office(self):
        """ Admin user can create new user through the backoffice. """

        # add a password
        self.payload['password1'] = 'GaoIsGod1312'
        self.payload['password2'] = 'GaoIsGod1312'

        # blank slate check (remember we are starting with 1 staff user)
        self.assertEqual(User.objects.count(), 1)

        # if you get management form errors here, it's prob bc u have an inline
        # in your user adminform now. needs different payload structure.
        self.client.post(self.USER_CREATE_URL, data=self.payload)

        # and the magic of life: our new user is created
        self.assertEqual(User.objects.count(), 2)
        new_user = User.objects.get(email='dylan@wertkt.com')
        self.assertFalse(new_user.check_password('badpassword'))
        self.assertTrue(new_user.check_password('GaoIsGod1312'))


class TestUserChange(BaseTestCase):
    payload = {
        'username': 'dylan',
        'email': 'dylan@wertkt.com',
        'first_name': 'Dylan',
        'last_name': 'Hayward',
        '_autologin': 'Login as user'
    }

    def setUp(self):
        self.admin_auth()
        self.client.force_login(self.user)
        new_user = factories.UserFactory()
        self.USER_CHANGE_URL = reverse('admin:users_user_change', kwargs={'object_id': new_user.id})

    @override_settings(FRONTEND_LOGIN_URL='http://127.0.0.1:8000')
    def test_autologin_good(self):
        """ With the correct settings field set. """

        response = self.client.post(self.USER_CHANGE_URL, data=self.payload, follow=True)
        redirect_url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 302)
        self.assertRegexpMatches(redirect_url, r'http://127.0.0.1:8000\?accessToken=.+&refreshToken=.+')

    @override_settings(FRONTEND_LOGIN_URL='')
    def test_autologin_bad(self):
        """ With NO settings field set. """

        response = self.client.post(self.USER_CHANGE_URL, data=self.payload, follow=True)
        redirect_url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 301)
        self.assertEqual(redirect_url, r'/admin/')

    @override_settings(FRONTEND_LOGIN_URL='')
    def test_normal_save(self):
        """ Ensure we can save User instance normally, without autologin data. """

        payload = deepcopy(self.payload)
        payload.pop('_autologin')
        response = self.client.post(self.USER_CHANGE_URL, data=payload, follow=True)
        redirect_url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 302)
        self.assertEqual(redirect_url, reverse('admin:users_user_changelist'))
