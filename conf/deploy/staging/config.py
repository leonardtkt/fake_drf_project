from pathlib import Path


FILES_BASE = Path('/home/media/newtktapp.wertkt.com/').resolve(strict=False)
MEDIA_ROOT = FILES_BASE / 'upload'
STATIC_ROOT = FILES_BASE / 'static'
LOGGING_PATH = '/home/logs/newtktapp.wertkt.com/'

DEPLOY_CONFIG = {
    'connection': {
        'host': 'ns3029811.ip-91-121-65.eu',
        'ip': '91.121.65.6',
        'username': 'root'
    },
    'server': {
        'project_name': 'new_fake_drf_project',
        'project_url': 'newtktapp.wertkt.com',
        'python_version': '3.7.6',
        'branch': 'staging',
        'db_name': 'newfakedrf',
        'apache_conf_path': 'conf/deploy/staging/apache/new_fake_drf_project.conf',
        'nginx_conf_path': 'conf/deploy/staging/nginx/new_fake_drf_project.conf',
        'uvicorn_conf_path': 'conf/deploy/staging/uvicorn/new_fake_drf_project.service',
        'project_path': '/home/projects/newtktapp.wertkt.com',
        'logging_path': LOGGING_PATH,
        'static_path': STATIC_ROOT,
        'media_path': MEDIA_ROOT,
    }
}
