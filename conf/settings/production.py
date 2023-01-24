from conf.settings.base import *  # noqa
from conf.logging.file import set_file_logging  # noqa


DEBUG = False
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]  # change me to reflect actual production URL

ALLOWED_HOSTS = ['*']  # change to something more secure

# Basic logging settings
LOGGING_PATH = '/var/www/logs/new_fake_drf_project/'
MAX_LOG_FILE_SIZE = 1024 * 1024 * 10  # 10 MB
set_file_logging(max_file_size=MAX_LOG_FILE_SIZE, logging_path=LOGGING_PATH)

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
