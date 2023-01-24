from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

import logging
from typing import Optional

logger = logging.getLogger('users')


class User(AbstractUser):
    """ The main user model for further customization. """

    email_verified = models.BooleanField(_('Email vérifié'), default=False)

    @property
    def access_token(self) -> str:
        """ Creates/retrieves a JWT access token for the user that can be used to authenticate. """

        return str(AccessToken.for_user(self))

    @property
    def refresh_token(self) -> str:
        """ Creates/retrieves a JWT access token for the user that can be used to obtain new access token. """

        return str(RefreshToken.for_user(self))

    @property
    def autologin_url(self) -> Optional[str]:
        """ This is where we pass refresh_token and access_token to frontend, so we can login as a user. """

        if settings.FRONTEND_LOGIN_URL:
            return f'{settings.FRONTEND_LOGIN_URL}?accessToken={self.access_token}&refreshToken={self.refresh_token}'
        return None

    class Meta:
        ordering = ['username']
