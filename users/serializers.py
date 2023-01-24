from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import ValidationError

import logging
from urllib.parse import unquote_plus
from hashids import Hashids

from contrib.services import Mail
from users.models import User

logger = logging.getLogger('users')


class UserSerializer(serializers.ModelSerializer):
    """ Serializer interface for base User model. Write only access to update password. """

    class Meta:
        model = User
        fields = ['id', 'password', 'first_name', 'last_name', 'username', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data: dict) -> User:
        """ In addition to creation of new user, logs creation information. """

        user = super().create(validated_data)
        msg = 'Registered new user: {}'
        logger.info(msg.format(user.username))
        return user

    def validate_password(self, value: str) -> str:
        """ Transform the plain text supplied for password field of POST/PUT/PATCH into a proper Django hash. """

        return make_password(value)

    def validate_email(self, value: str) -> str:
        """ Blocks the creation/update if the email address is not unique. """

        if not self.instance:
            if User.objects.filter(username=value).exists() or User.objects.filter(email=value).exists():
                raise ValidationError("This email is already registered.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """ Serializer for requesting a password reset e-mail. """

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        # Create PasswordResetForm with the serializer
        try:
            self.user = User.objects.get(email=value)
        except (TypeError, AttributeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'email': ['Valeur invalide']})
        return value

    def save(self) -> None:
        Mail.reset_password(self.user)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """ Serializer for validating a password reset and setting new password. """

    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate_new_password2(self, value: str) -> str:
        """ Transform the plain text supplied for password field of POST/PUT/PATCH into a proper Django hash. """

        if not len(value) > 6:
            # Password should be 6 chars long at least
            raise ValidationError(_("Mot de passe trop court"))
        return value

    def validate_uid(self, value: str) -> str:
        """ Decode the uidb64 to uid to get User object. """

        try:
            uid = force_text(urlsafe_base64_decode(value))
            self.user = User.objects.get(pk=uid)
        except (TypeError, AttributeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'uid': ['Valeur invalide']})
        return value

    def validate(self, attrs: dict) -> dict:
        """ Construct SetPasswordForm instance. """

        self.set_password_form = SetPasswordForm(user=self.user, data=attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': [_('Invalid value')]})
        return attrs

    def save(self) -> AbstractBaseUser:
        return self.set_password_form.save()


class AccountVerifySerializer(serializers.Serializer):
    """ Verifies that a user's account hasn't already been validated. Checks that
    key is valid (i.e. they clicked a genuine link from their email that came from us).
    Marks user account as as verified. """

    email = serializers.CharField(required=True)
    key = serializers.CharField(required=True)

    def validate_email(self, value: str) -> str:
        """ Look User instance by email address and ensure not already registered. """

        try:
            self.user = User.objects.get(email=unquote_plus(value))
            if self.user.email_verified:
                raise serializers.ValidationError(_('Ce compte est déjà validé'))
        except (TypeError, AttributeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'email': ['Valeur invalide']})
        return value

    def validate(self, values: dict) -> dict:
        """ Check the provided key against the true key. """

        hashers = Hashids(salt=settings.SECRET_KEY, min_length=24)
        key = hashers.encode(self.user.id)
        if key != values['key']:
            raise serializers.ValidationError(_('Mauvaise clé de validation'))
        return super().validate(values)

    def save(self) -> None:
        """ Indicate that the user is not registered. """

        self.user.email_verified = True
        self.user.save()


class SocialAuthInputSerializer(serializers.Serializer):
    """ Serializer which accepts an OAuth2 access token and provider. """

    provider = serializers.CharField(help_text='chosen from limited list on backend (i.e. "facebook")', max_length=255)
    access_token = serializers.CharField(help_text='the oauth token you received from that service', max_length=4096, trim_whitespace=True)


class SocialAuthOutputSerializer(serializers.Serializer):
    """ After a social OAuth2 process from user, return this information to them. """

    email = serializers.EmailField(help_text='the email address of the user in our database')
    username = serializers.CharField(help_text='the username of the user in our database', max_length=256)
    token = serializers.CharField(help_text='use this on our API as your Bearer Token', max_length=4096, trim_whitespace=True)
