from pathlib import Path
import logging.config


def set_file_logging(max_file_size: int, logging_path: str) -> None:
    """ Allows us to pass in a couple arguments to setup file logging for the whole project. """

    # make sure our path is correct
    try:
        dir = Path(logging_path).resolve(strict=True)
    except (FileNotFoundError, TypeError):
        print(f'Critical error -> checking LOGGING_PATH. Currently set to {logging_path}')
        exit()

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'uncolored': {
                'format': '%(asctime)s [%(levelname)s] %(funcName)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'file-django': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'uncolored',
                'filename': dir / 'django.log',
                'maxBytes': max_file_size,
                'backupCount': 5,
            },
            'file-users': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'uncolored',
                'filename': dir / 'users.log',
                'maxBytes': max_file_size,
                'backupCount': 5,
            },
            'file-emails': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'uncolored',
                'filename': dir / 'emails.log',
                'maxBytes': max_file_size,
                'backupCount': 5,
            },
        },
        'loggers': {
            'users': {
                'handlers': ['file-users'],
                'level': 'INFO',
                'propogate': False,
            },
            'emails': {
                'handlers': ['file-emails'],
                'level': 'INFO',
                'propogate': False
            },
            # catchall
            '': {
                'handlers': ['file-django'],
                'level': 'WARN',
            },
        }
    })
