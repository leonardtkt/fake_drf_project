from pathlib import Path

from conf.settings.base import *  # noqa
from conf.logging.file import set_file_logging


BACK_URL = 'https://newtktapp.wertkt.com'
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]  # change me to reflect actual staging URL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'newfakedrf',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Basic logging settings
LOGGING_PATH = '/home/logs/newtktapp.wertkt.com/'
MAX_LOG_FILE_SIZE = 1024 * 1024 * 10  # 10 MB
set_file_logging(max_file_size=MAX_LOG_FILE_SIZE, logging_path=LOGGING_PATH)

# Add this to our 1TB storage
FILES_BASE = Path('/home/media/newtktapp.wertkt.com/').resolve(strict=True)
MEDIA_ROOT = FILES_BASE / 'upload'
STATIC_ROOT = FILES_BASE / 'static'
