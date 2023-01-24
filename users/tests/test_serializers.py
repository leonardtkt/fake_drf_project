from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from rest_framework.validators import ValidationError
from unittest import mock
from hashids import Hashids

from contrib.tests.base import BaseTestCase
from users.serializers import PasswordResetConfirmSerializer, PasswordResetSerializer, AccountVerifySerializer
from users.factories import UserFactory


class TestPasswordResetConfirmSerializer(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = PasswordResetConfirmSerializer

    @mock.patch('users.serializers.PasswordResetConfirmSerializer.validate')
    @mock.patch('users.serializers.PasswordResetConfirmSerializer.validate_new_password2')
    @mock.patch('users.serializers.PasswordResetConfirmSerializer.validate_uid')
    def test_basic(self, validate_uid, validate_pass, validate_all):
        """ No params = bad result. Basic necessary params = good result. """

        # basic dicts which we will supply to serializer
        empty_data = {}
        complete_data = {
            'new_password1': 'password123',
            'new_password2': 'password123',
            'uid': '54',
            'token': 'faketoken123'
        }

        # mock so we can have a clean unit test
        validate_uid.return_value = '54'
        validate_pass.return_value = 'password123'
        validate_all.return_value = complete_data

        # should be false
        bad = self.serializer(data=empty_data)
        self.assertFalse(bad.is_valid())

        # should be true
        good = self.serializer(data=complete_data)
        self.assertTrue(good.is_valid(raise_exception=True))

    def test_validate_password_must_be_more_than_six(self):
        """ Gotta be MORE than 6 chars. """

        s = self.serializer()

        # should raise validation error
        with self.assertRaises(ValidationError):
            s.validate_new_password2('CRiPS')

        # should still fail!
        with self.assertRaises(ValidationError):
            s.validate_new_password2('BLooDS')

        # ah, just perfect
        result = s.validate_new_password2('2 Live Crew')
        self.assertTrue(result)

    def test_validate_uids(self):
        """ Some examples of uids that should fail. + 1 that should succeed. """

        s = self.serializer()

        # blank uid
        with self.assertRaises(ValidationError):
            s.validate_uid('')

        # null uid
        with self.assertRaises(ValidationError):
            s.validate_uid(None)

        # gibberish uid
        with self.assertRaises(ValidationError):
            s.validate_uid('2345678')

        # proper uid but not in database
        uid = 'MQ=='  # 1
        with self.assertRaises(ValidationError):
            s.validate_uid(uid)

        # ah, just perfect
        user = UserFactory()
        uid = urlsafe_base64_encode(force_bytes(user.id))
        result = s.validate_uid(uid)
        self.assertTrue(result)

    def test_validate_generally(self):
        """ Check password match, check for good token. """

        s = self.serializer()
        s.user = UserFactory()

        # mismatched password
        with self.assertRaises(ValidationError):
            bad_pass = {
                'new_password1': 'ab345678987654',
                'new_password2': 'hgfhkggkgkj',
                'uid': '555',
                'token': 'faketoken123'
            }
            s.validate(bad_pass)

        # bad token
        with self.assertRaises(ValidationError):
            bad_token = {
                'new_password1': 'ab345678987654',
                'new_password2': 'ab345678987654',
                'uid': '555',
                'token': 'faketoken123'
            }
            s.validate(bad_token)

        # ah, just perfect
        good_stuff = {
            'new_password1': 'ab345678987654',
            'new_password2': 'ab345678987654',
            'uid': '555',
            'token': default_token_generator.make_token(s.user)
        }
        result = s.validate(good_stuff)
        self.assertEqual(good_stuff, result)

    def test_save(self):
        """ Integration test, because it's here than a unit test. Ensure we can
        save our serializer and update a User instance with new password. """

        user = UserFactory()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        new_password = '231hhd123871823jadhs'

        self.assertFalse(user.check_password(new_password))

        good_stuff = {
            'new_password1': new_password,
            'new_password2': new_password,
            'uid': uid,
            'token': token
        }
        serializer = self.serializer(data=good_stuff)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))


class TesPasswordResetSerializer(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = PasswordResetSerializer

    @mock.patch('contrib.services.Mail.reset_password')
    @mock.patch('users.serializers.PasswordResetSerializer.validate_email')
    def test_just_the_basic_save(self, validate_email, reset_password):
        """ Skips the validation for this unit test. """

        reset_password.return_value = True
        validate_email.return_value = 'dylan@wertkt.com'
        self.serializer.user = UserFactory()

        serializer = self.serializer(data={'email': 'dylan@wertkt.com'})
        self.assertTrue(serializer.is_valid())
        serializer.save()

    def test_invalid_email(self):
        """ Emails that dont exist in database should fail. """

        unregistered_email = 'gao123@wertkt.com'
        serializer = self.serializer(data={'email': unregistered_email})
        self.assertFalse(serializer.is_valid())

    def test_valid_email(self):
        """ Emails that do exist in database should pass. """

        registered_email = 'gao@wertkt.com'
        UserFactory(email='gao@wertkt.com')
        serializer = self.serializer(data={'email': registered_email})
        self.assertTrue(serializer.is_valid())


class TestAccountVerifySerializer(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.serializer = AccountVerifySerializer

    @mock.patch('users.serializers.AccountVerifySerializer.validate_email')
    @mock.patch('users.serializers.AccountVerifySerializer.validate')
    def test_just_the_basic_save(self, validate_email, validate):
        """ Skips the validation for this unit test. """

        user = UserFactory()
        self.assertFalse(user.email_verified)
        serializer = self.serializer(data={'email': 'dylan@wertkt.com', 'key': '555'})
        serializer.user = user
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user.refresh_from_db()
        self.assertTrue(user.email_verified)

    @mock.patch('users.serializers.AccountVerifySerializer.validate')
    def test_invalid_email(self, validate):
        """ Emails that dont exist in database should fail. """

        unregistered_email = 'gao123@wertkt.com'
        serializer = self.serializer(data={'email': unregistered_email, 'key': '123'})
        self.assertFalse(serializer.is_valid())

    @mock.patch('users.serializers.AccountVerifySerializer.validate')
    def test_valid_email(self, validate):
        """ Emails that do exist in database should pass. """

        validate.return_value = True

        registered_email = 'gao@wertkt.com'
        UserFactory(email='gao@wertkt.com')
        serializer = self.serializer(data={'email': registered_email, 'key': '123'})
        self.assertTrue(serializer.is_valid())

    def test_valid_email_but_invalid_key(self):
        """ Emails that do exist in database that don't match the key should fail. """

        email = 'gao@wertkt.com'
        UserFactory(email='gao@wertkt.com')

        serializer = self.serializer(data={'email': email, 'key': '123'})
        self.assertFalse(serializer.is_valid())

    def test_valid_email_with_matching_key(self):
        """ Good key? Pass. """

        email = 'gao@wertkt.com'
        user = UserFactory(email=email)

        hashers = Hashids(salt=settings.SECRET_KEY, min_length=24)
        key = hashers.encode(user.id)

        serializer = self.serializer(data={'email': email, 'key': key})
        self.assertTrue(serializer.is_valid())

    def test_already_confirmed(self):
        """ If already confirmed, should produce error. """

        email = 'gao@wertkt.com'
        user = UserFactory(email='gao@wertkt.com', email_verified=True)

        hashers = Hashids(salt=settings.SECRET_KEY, min_length=24)
        key = hashers.encode(user.id)

        serializer = self.serializer(data={'email': email, 'key': key})
        self.assertFalse(serializer.is_valid())
