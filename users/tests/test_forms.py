from django import forms

from users.admin import UserCreationForm
from users.factories import UserFactory
from contrib.tests.base import BaseTestCase


class TestUserAdminSaveForm(BaseTestCase):
    def test_good_user_change_password(self):
        """ Changing password through back-office with matching password fields should update password. """
        # bit of a hack function... since this is going through back-office.. kind of faked, but it works.
        user = UserFactory()
        form = UserCreationForm(instance=user)
        form.cleaned_data = {
            'password1': 'goldfish123',
            'password2': 'goldfish123',
        }
        self.assertTrue(form.clean_password2())
        form.save(commit=True)
        self.assertFalse(user.check_password('goldfish1234'))
        self.assertTrue(user.check_password('goldfish123'))

    def test_bad_mismatch_user_change_password(self):
        """ Changing password through back-office with mismatching password fields should fail. """
        user = UserFactory()
        form = UserCreationForm(instance=user)
        form.cleaned_data = {
            'password1': 'goldfish123',
            'password2': 'starfish1339',
        }
        with self.assertRaises(forms.ValidationError):
            form.clean_password2()
