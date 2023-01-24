from conf.settings.base import *  # noqa
from conf.logging.console import *  # noqa


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
