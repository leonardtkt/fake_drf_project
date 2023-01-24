from django.core import mail
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.core.exceptions import ImproperlyConfigured

from unittest import mock
import tempfile
import glob

from contrib.models import PrivateGlobalSettings
from contrib.services import Mail, Backup
from users.factories import UserFactory


class EmailTest(TestCase):
    @mock.patch('contrib.services.Mail._get_from_address')
    def test_send_functionality(self, from_addr):
        """ Check that send method behaves as expected. """

        from_addr.return_value = 'gao@wertkt.com'

        result = Mail.send(to=['gao@wertkt.com'], subject='hi gao', body='123')

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'hi gao')
        self.assertTrue(result)

    @mock.patch('contrib.services.Mail._get_from_address')
    def test_send_attachments(self, from_addr):
        """ Can we attach a file? Let's find out! """

        from_addr.return_value = 'gao@wertkt.com'

        temp_file = NamedTemporaryFile(delete=True)
        attachments = [temp_file.name]

        result = Mail.send(to=['gao@wertkt.com'], subject='hi gao', body='123', attachments=attachments)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'hi gao')
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertTrue(result)

    @override_settings(DEFAULT_FROM_EMAIL='gao@wertkt.com')
    def test_get_from_email_with_default_settings(self):
        """ We won't create a PrivateGlobalSettings singleton, so it should instead take
        the default value from our settings. """

        email = Mail._get_from_address()
        self.assertEqual(email, 'gao@wertkt.com')

    @override_settings(DEFAULT_FROM_EMAIL='gao@wertkt.com')
    def test_get_from_email_with_custom_settings(self):
        """ We will create a PrivateGlobalSettings singleton, so it should take value from
        the singleton rather than from django settings. """

        PrivateGlobalSettings.objects.create(sender_email_address='tim@wertkt.com')
        email = Mail._get_from_address()
        self.assertEqual(email, 'tim@wertkt.com')

    @mock.patch('contrib.services.Mail.send')
    def test_reset_password(self, send):
        """ Basically we are just checking for pass here. Can find template, etc. """

        send.return_value = True
        user = UserFactory()
        self.assertTrue(Mail.reset_password(user))

    @mock.patch('contrib.services.Mail.send')
    def test_new_user(self, send):
        """ Basically we are just checking for pass here. Can find template, etc. """

        send.return_value = True
        user = UserFactory()
        self.assertTrue(Mail.new_user(user))

    def test_build_minimal_context(self):
        """ Let's pretend our urls are bad that we are passing it but don't realize it. """

        ctx = Mail._build_context(title='Hello 123')
        self.assertEqual(ctx['TITLE'], 'Hello 123')

    def test_build_bad_url(self):
        """ Let's pretend our urls are bad that we are passing it but don't realize it. """

        images = {'image1': '/static/images123.jpg', 'image2': None, 'image3': 'http://google.com/img.jpg'}
        with self.assertLogs('emails', level='ERROR') as cm:
            self.assertTrue(Mail._build_context(title='Hello :)', images=images))
        self.assertEqual(len(cm.output), 2)

        bad_url = '/static/images/'
        with self.assertLogs('emails', level='ERROR') as cm:
            self.assertTrue(Mail._build_context(title='Hello :)', button_url=bad_url))
        self.assertEqual(len(cm.output), 1)

    def test_full(self):
        """ Add all normal values to ctx. """

        title = 'Title!'
        subtitle = 'Subtitle!'
        text = 'Text!'
        button_url = 'http://wertkt.com/img.jpg'
        button_text = 'Click me!'

        ctx = Mail._build_context(title, subtitle, text, button_url, button_text, EXTRA_TEXT='123', SIG='456')
        self.assertEqual(ctx['TITLE'], title)
        self.assertEqual(ctx['SUBTITLE'], subtitle)
        self.assertEqual(ctx['TEXT'], text)
        self.assertEqual(ctx['BUTTON_URL'], button_url)
        self.assertEqual(ctx['BUTTON_TEXT'], button_text)
        self.assertEqual(ctx['BACK_URL'], settings.BACK_URL)
        self.assertEqual(ctx['FRONT_URL'], settings.FRONT_URL)
        self.assertEqual(ctx['EXTRA_TEXT'], '123')
        self.assertEqual(ctx['SIG'], '456')


class BackupTest(TestCase):
    def test_get_filepath(self):
        """ Abs filename is good stuff. """

        backup = Backup(path='/tmp', max_backup_count=5)
        filename = backup._get_filepath()
        self.assertRegexpMatches(filename, r'\/tmp\/\d{4}-\d{2}-\d{2}Z\d{2}:\d{2}.json')

    def test_validate_path_no_path(self):
        """ Path must be set in base.py, etc. """

        backup = Backup(path=None, max_backup_count=5)
        with self.assertRaises(ImproperlyConfigured):
            backup._validate_path()

    def test_validate_path_path_not_exist(self):
        """ Path not found. """

        backup = Backup(path='/asjkdjakjsdkasdjkas', max_backup_count=5)
        with self.assertRaises(OSError):
            backup._validate_path()

    def test_clean_path_deletes_proper(self):
        """ Should delete 2 of the 3 files here. """

        with tempfile.TemporaryDirectory() as tempdir:
            open(f'{tempdir}/9891283812387.json', 'w').write('hi')
            open(f'{tempdir}/2213123123123.json', 'w').write('hi')
            open(f'{tempdir}/2481238412343.json', 'w').write('hi')

            files = glob.glob(f'{tempdir}/*.json')

            self.assertEqual(len(files), 3)
            backup = Backup(path=tempdir, max_backup_count=1)
            backup._clean_path()

            files = glob.glob(f'{tempdir}/*.json')
            self.assertEqual(len(files), 1)

    @mock.patch('contrib.services.Backup._clean_path')
    @mock.patch('contrib.services.Backup._validate_path')
    @mock.patch('contrib.services.Backup._get_filepath')
    @mock.patch('django.core.management.call_command')
    def test_run(self, m1, m2, m3, m4):
        """ We just make sure this doesn't crash. """

        backup = Backup(path='/asjkdjakjsdkasdjkas', max_backup_count=5)
        backup.run()
