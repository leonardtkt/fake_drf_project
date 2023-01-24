from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.validators import URLValidator
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core import management
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.template.loader import render_to_string

from typing import Optional, Dict, List
from hashids import Hashids
import urllib.parse
import logging
import glob
import os

from users.models import User
from contrib.models import PrivateGlobalSettings

mail_logger = logging.getLogger('emails')
django_logger = logging.getLogger('django')


class Mail:
    """ Piping all outgoing email through this process == logging, validation, centralizaton.  """

    @staticmethod
    def _get_from_address() -> str:
        """ From address for outgoing email should normally be set via back office.
        If it hasn't been set, we can fallback to the one specified in our base settings. """

        try:
            pub_settings = PrivateGlobalSettings.objects.get()
            return pub_settings.sender_email_address
        except PrivateGlobalSettings.DoesNotExist:
            return settings.DEFAULT_FROM_EMAIL

    @staticmethod
    def _build_context(
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        text: Optional[str] = None,
        button_url: Optional[str] = None,
        button_text: Optional[str] = None,
        images: Dict[str, str] = {},
        **kwargs
    ) -> Dict[str, Optional[str]]:
        """ Create the context to be used in the mail.

        * images field (optional) should be a dict - key: template name / value: abs URL
        * button_url (optional) must be a valid url
        """

        validate = URLValidator()

        if button_url:
            try:
                validate(button_url)
            except (ValidationError, AttributeError):
                mail_logger.error(f'Invalid URL attached to email: "{button_url}"')

        # add the default things that should be okay to include on every email,
        # even if they aren't used in the template, plus the stuff the stuff provided
        # from parent method.
        ctx = {
            'TITLE': title,
            'SUBTITLE': subtitle,
            'TEXT': text,
            'BUTTON_URL': button_url,
            'BUTTON_TEXT': button_text,
            'FRONT_URL': f'{settings.FRONT_URL}',
            'BACK_URL': f'{settings.BACK_URL}'
        }

        # add images
        for key, value in images.items():
            try:
                validate(value)
            except (ValidationError, AttributeError):
                mail_logger.error(f'Invalid URL attached to email: "{value}"')
            # allow url always - hope we are checking logs...
            ctx[key] = value

        # add any extra params
        for key, value in kwargs.items():
            ctx[key] = value

        return ctx

    @classmethod
    def send(
        cls,
        to: List[str],
        subject: str,
        body: str,
        cc: List[str] = [],
        bcc: List[str] = [],
        attachments: List[str] = [],
    ) -> bool:
        """ Combines the normal Django send_mail function with a bit of validation and logging.
        Attachments should be a list of absolute file paths as strings. """

        from_address = cls._get_from_address()

        email = EmailMultiAlternatives(
            to=to,
            body=body,
            subject=subject,
            from_email=from_address,
            cc=cc,
            bcc=bcc,
        )
        for file_path in attachments:
            email.attach_file(file_path)
        email.content_subtype = 'html'
        send_status = email.send(fail_silently=True)

        if send_status != 1:
            mail_logger.error(f'Failed to send email to {to}')
            return False

        recipients = to + cc + bcc
        recipient_str = ','.join(recipients)
        mail_logger.info(f'Sent email! To: {recipient_str}; From: {from_address}; Subject: {subject}')
        return True

    @classmethod
    def reset_password(cls, user: User) -> bool:
        """ Send password reset form to user. """

        # build special variables
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # generate html from template and send
        html_template = 'mails/index.html'
        ctx = cls._build_context(
            title=_('Vous avez oublié votre mot de passe ?'),
            button_url=f'{settings.FRONT_URL}/reset/uid={uid}&token={token}',
            button_text=_('RÉINITIALISER MON MOT DE PASSE')
        )
        body = render_to_string(html_template, ctx)

        return cls.send(
            to=[user.email],
            subject=_('Réinitialisation du mot de passe'),
            body=body
        )

    @classmethod
    def new_user(cls, user: User) -> bool:
        """ Send welcome email to new user. """

        # build special variables
        hashers = Hashids(salt=settings.SECRET_KEY, min_length=24)
        key = hashers.encode(user.id)
        base_url = urllib.parse.urljoin(settings.FRONT_URL, reverse('users-list'))
        params = f'validate-email/?email={user.email}&key={key}&firstname={user.first_name}'
        verification_url = urllib.parse.urljoin(base_url, params)

        # build email content and send
        html_template = 'mails/index.html'
        sub_text = _(f'Bonjour {user.first_name}, vous êtes désormais inscrit sur le site de New Fake DRF project')
        ctx = cls._build_context(
            title=_('Confirmation de votre compte'),
            subtitle=sub_text,
            text=_('Vous pouvez désormais composer et commander votre formule rapidement.'),
            button_url=verification_url,
            button_text=_('Confirmer mon compte'),
        )
        body = render_to_string(html_template, ctx)

        return cls.send(
            to=[user.email],
            subject=_('Confirmation de votre compte'),
            body=body
        )


class Backup:
    """ Tool the exports the DB to JSON in a specified directory (and keeps it clean.)

    Basically just a wrapper for the django `dumpdata` management command, with
    good default params + auto-filename + path validation + cleanup of export directory.
    """

    def __init__(self, path: str, max_backup_count: int = 5) -> None:
        """ path = directory for exports """

        self.max_backup_count = max_backup_count
        self.path = path

    def _get_filepath(self) -> str:
        """ Returns absolute filename of destination json export. """

        now = timezone.now()
        now_str = now.strftime('%Y-%m-%dZ%H:%M')
        filename = f'{now_str}.json'
        return os.path.join(self.path, filename)

    def _validate_path(self) -> None:
        """ Ensures the path supplied exists and is writable. """

        if not self.path:
            raise ImproperlyConfigured(f'Invalid path given to Backup tool - you may need to check your settings.py: {self.path}')
        if not os.access(self.path, os.W_OK):
            raise OSError(2, 'Path supplied to Backup service does not exist or is not writeable!', self.path)

    def _clean_path(self) -> None:
        """ Deletes all old json backup files that are over the prescribed limited number of backups. """

        unsorted_files = glob.glob(f'{self.path}/*.json')
        sorted_files = sorted(unsorted_files, key=os.path.getmtime)
        while len(sorted_files) > self.max_backup_count:
            file_to_delete = sorted_files.pop(0)
            os.remove(file_to_delete)
            django_logger.info(f'Deleted old backup file: {file_to_delete}')

    def run(self):
        """ Start backing up the database. For big dbs might take a while, so schedule when server
        is less active. """

        self._validate_path()
        abs_file_path = self._get_filepath()

        management.call_command(
            'dumpdata',
            natural_foreign=True,
            indent=2,
            exclude=['contenttypes', 'auth.permission', 'admin'],
            output=abs_file_path)

        django_logger.info(f'Backed up database: {abs_file_path}')
        self._clean_path()
