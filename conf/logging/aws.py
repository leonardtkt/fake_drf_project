from boto3.session import Session
import os

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region_name = os.environ.get('AWS_REGION')

if not all([aws_access_key_id, aws_secret_access_key, region_name]):
    print('Critical error! AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION must be set as env variables!')

boto3_session = Session(aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=region_name)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(funcName)s: %(message)s'
        },
    },
    'handlers': {
        'watchtower-django': {
            'class': 'watchtower.CloudWatchLogHandler',
                     'boto3_session': boto3_session,
                     'log_group': 'newtktapp.wertkt.com',
                     'stream_name': 'django',
            'formatter': 'standard',
        },
        'watchtower-users': {
            'class': 'watchtower.CloudWatchLogHandler',
                     'boto3_session': boto3_session,
                     'log_group': 'newtktapp.wertkt.com',
                     'stream_name': 'users',
            'formatter': 'standard',
        },
        'watchtower-emails': {
            'class': 'watchtower.CloudWatchLogHandler',
                     'boto3_session': boto3_session,
                     'log_group': 'newtktapp.wertkt.com',
                     'stream_name': 'emails',
            'formatter': 'standard',
        }
    },
    'loggers': {
        'users': {
            'handlers': ['watchtower-users'],
            'level': 'INFO',
            'propogate': False,
        },
        'emails': {
            'handlers': ['watchtower-emails'],
            'level': 'INFO',
            'propogate': False
        },
        # catchall
        '': {
            'handlers': ['watchtower-django'],
            'level': 'WARN',
            'propogate': False
        }
    }
}
