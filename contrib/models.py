from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class PrivateGlobalSettings(SingletonModel):
    """ Dynamic config parameters for internal use -- should NEVER be exposed via API.
    Add a field here when you want the client to dynamically set value in back office.

    Examples include:
    * Administrator email addresses for site reports
    * Private keys that occasionally change
    * Etc.
    """

    sender_email_address = models.EmailField(
        verbose_name=_('e-mail de l\'expéditeur'),
        help_text=_('l\'adresse à utiliser pour tous les courriers électroniques sortants'),
        null=True, blank=True)

    def __str__(self) -> str:
        return 'Private Global Settings'

    def __repr__(self) -> str:
        return 'PrivateGlobalSettings()'

    class Meta:
        verbose_name = 'Private Global Settings'
        verbose_name_plural = 'Private Global Settings'


class PublicGlobalSettings(SingletonModel):
    """ Dynamic config parameters for external use -- WILL be sent to frontend via API.
    Add a field here when you want the client to dynamically set value in back office.

    Examples include:
    * Mailing address of the company
    * Default product from a list of products
    * Etc.
    """

    def __str__(self) -> str:
        return 'Public Global Settings'

    def __repr__(self) -> str:
        return 'PublicGlobalSettings()'

    class Meta:
        verbose_name = 'Public Global Settings'
        verbose_name_plural = 'Private Global Settings'
