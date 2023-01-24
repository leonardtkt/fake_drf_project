LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': 'coloredlogs.ColoredFormatter',
            'format': '%(asctime)s [%(levelname)s] %(funcName)s: %(message)s',
        },
        'uncolored': {
            'format': '%(asctime)s [%(levelname)s] %(funcName)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'loggers': {
        'users': {
            'handlers': ['console'],
            'level': 'INFO',
            'propogate': False,
        },
        'emails': {
            'handlers': ['console'],
            'level': 'INFO',
            'propogate': False
        },
        # catchall
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}
