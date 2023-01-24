# Only used for setting up a new server! fabfile.py
from pathlib import Path

LOGGING_PATH = '/home/logs/newtktapp-exp.wertkt.com/'

# Add this to our 1TB storage
FILES_BASE = Path('/home/media/newtktapp-exp.wertkt.com/').resolve(strict=False)
MEDIA_ROOT = FILES_BASE / 'upload'
STATIC_ROOT = FILES_BASE / 'static'

DEPLOY_CONFIG = {
    'connection': {
        'host': 'ns3029811.ip-91-121-65.eu',
        'ip': '91.121.65.6',
        'username': 'root'
    },
    'server': {
        'project_name': 'new_fake_drf_project',
        'project_url': 'newtktapp-exp.wertkt.com',
        'python_version': '3.7.6',
        'branch': 'experimental',
        'db_name': 'newfakedrfexperimental',
        'apache_conf_path': 'conf/deploy/experimental/apache/new_fake_drf_project.conf',
        'nginx_conf_path': 'conf/deploy/experimental/nginx/new_fake_drf_project.conf',
        'uvicorn_conf_path': 'conf/deploy/experimental/uvicorn/new_fake_drf_project.service',
        'project_path': '/home/projects/newtktapp-exp.wertkt.com',
        'logging_path': LOGGING_PATH,
        'static_path': STATIC_ROOT,
        'media_path': MEDIA_ROOT,
    }
}
