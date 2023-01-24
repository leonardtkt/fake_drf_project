from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperuserCommand
from django.core.management import CommandError


class Command(CreateSuperuserCommand):
    help = 'This extends built-in superuser creation functionality to set password with no input.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--password', dest='password', default=None,
            help='Specifies the password for the superuser.',
        )

    def handle(self, *args, **options):
        password = options.get('password')
        username = options.get('username')
        database = options.get('database')

        if password and not username:
            raise CommandError("--username is required if specifying --password")

        super().handle(*args, **options)

        if password:
            user = self.UserModel._default_manager.db_manager(database).get(username=username)
            user.set_password(password)
            user.save()
