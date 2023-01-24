from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

import logging

from users.models import User
from .utils import get_client_ip

logger = logging.getLogger('users')


@receiver(user_login_failed)
def user_login_failed_callback(sender: User, credentials: dict, **kwargs):
    """ Any failed login attempts to the back-office/etc. are logged
    with the username and IP address. """

    username = credentials['username']
    ip = get_client_ip(kwargs['request'])
    logger.warn(f'BAD LOGIN ATTEMPT | {username} | {ip}')
