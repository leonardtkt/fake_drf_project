from django.core.management.base import BaseCommand
from django.conf import settings

from contrib.services import Backup


class Command(BaseCommand):
    help = 'Backup the database to a json file.'

    def handle(self, *args, **options):
        backup = Backup(
            path=settings.BACKUP_PATH,
            max_backup_count=settings.MAXIMUM_BACKUP_COUNT)
        backup.run()
