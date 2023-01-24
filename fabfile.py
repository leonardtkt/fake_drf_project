from fabric import task, Connection
from paramiko.ssh_exception import PasswordRequiredException, AuthenticationException, SSHException
from colorama import Fore, Style
from urllib.parse import urljoin
from typing import List, Dict, Union
import secrets
import importlib
import requests
import os


# HELPERS

def green(s: str) -> str:
    """ Makes stdout green. """

    return f'{Fore.GREEN}{s}{Style.RESET_ALL}'


def yellow(s: str) -> str:
    """ Makes stdout yellow. """

    return f'{Fore.YELLOW}{s}{Style.RESET_ALL}'


def red(s: str) -> str:
    """ Makes stdout red. """

    return f'{Fore.RED}{s}{Style.RESET_ALL}'


def blanks(n: int) -> None:
    """ Print n line breaks.

    Args:
      n (int)       number of lines breaks to print
    """

    for i in range(n):
        print()


def error(error_msg: str) -> None:
    """ Print error with coloring. """

    blanks(2)
    print(red(f'✖️  {error_msg}'))
    blanks(1)


def success(good_msg: str) -> None:
    """ Things are great. Let's report that. """

    print(green(f'✓ {good_msg}'))


def clear_screen() -> None:
    """ Clears screen. Deals with special case for Windows. """

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# Services

class Cloudflare:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        zone_id = '7b2aaee467442b881508c96ec4be138d'  # the special id for wertkt.com and subdomains
        self.dns_url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'

    def add_dns(self, name: str, record_type: str, content: str, ttl: int = 1) -> None:
        """ Using provided args, create a new DNS entry on Cloudflare. """

        payload = {
            'name': name,
            'type': record_type,
            'content': content,
            'ttl': ttl
        }
        print(f'+ Posting Cloudflare payload... {payload}')
        headers = {
            'authorization': f'Bearer {self.api_key}'
        }

        response = requests.post(self.dns_url, json=payload, headers=headers)
        if response.status_code == 200:
            success(f'Created "{record_type}" record type DNS entry')
            return
        error(f'Bad response from cloudflare: {response.text}')


class Mailgun:
    """ Interface for Mailgun. """

    def __init__(self, api_key: str) -> None:
        """
        Args:
            api_key (str)       Key to interact with the Mailgun API
        """
        self.api_key = api_key
        self.mailgun_base_url = 'https://api.eu.mailgun.net/v3/'

    def setup(self, domain: str, new_password: str) -> Union[List[Dict], None]:
        """
        Add a new european domain to an existing mailgun account.

        Args:
            domain (str)        URL to send email from (no https://)
            new_password (str)  SMTP password to set
        """

        new_domain_url = urljoin(self.mailgun_base_url, 'domains')
        new_password = secrets.token_hex(nbytes=15)
        payload = {
            'smtp_password': new_password,
            'name': domain,
            'web_scheme': 'https'
        }
        response = requests.post(new_domain_url, data=payload, auth=('api', self.api_key))
        if response.status_code != 200:
            error('Mailgun setup failed!')
            print(response.json())
            return None

        email = response.json()['domain']['smtp_login']
        success('Mailgun setup. Please copy-paste this into appropriate settings file (i.e. staging.py)')
        blanks(2)
        print("EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'")
        print("EMAIL_HOST = 'smtp.eu.mailgun.org'")
        print(f"EMAIL_HOST_USER = '{email}'")
        print(f"EMAIL_HOST_PASSWORD = '{new_password}'")
        print("EMAIL_PORT = 587")
        print("EMAIL_USE_TLS = True")
        blanks(2)

        # in order to verify the account, we need we need to add some dns entries in order to verify this account
        dns_entries_to_create = []
        for record in response.json()['sending_dns_records']:
            new_rec = {
                'name': record['name'],
                'record_type': record['record_type'],
                'content': record['value']
            }
            dns_entries_to_create.append(new_rec)

        return dns_entries_to_create

    def verify(self, project_url: str) -> None:
        """ Mail wants to see that the SPF and DKIM records have been set in DNS.

            project_url (str)     i.e. 'viva-bolino.wertkt.com'
        """

        verify_domain_url = urljoin(self.mailgun_base_url, f'domains/{project_url}/verify')
        response = requests.put(verify_domain_url, auth=('api', self.api_key))
        if response.status_code != 200:
            error(f'Received bad response from Mailgun: {response.text}')
            return
        if response.json()["domain"]["state"] == "unverified":
            error('Could not yet verify DNS records for Mailgun. Wait a bit, try again.')
        else:
            success('Verified the domain with Mailgun.')


class Slack:
    """ Interact with Slack webhook - see: https://api.slack.com/messaging/webhooks. """

    def __init__(self):
        """ Out of convience, we specify the webhook url here. Note that
        the webhook url contains the secret and should not be shared.
        Anyone with access to their url can post to our channel. """

        self.webhook_url = 'https://hooks.slack.com/services/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'
        self.channel_name = '#server-updates'

    def announce(
        self,
        project_name: str,
        project_url: str,
        branch: str,
        github_url: str,
        admin_password: str,
        admin_username: str = 'admin'
    ) -> None:
        """ Post an announcement that a server has been setup.
        Test here: https://api.slack.com/block-kit

        Args:
           project_name (str)       the project we will be announcing about.
           project_url (str)        used to link to the documentation
           branch (str)             i.e. 'staging'
           github_url (str)         the URL where people can see the full repository
           admin_password (str)     superuser password for back office
           admin_username (str)     superuser login for back office
        """

        announce_image = 'http://91.121.65.6/asjdkjas7/star.jpg'
        msg = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":rocket: New Instance Launched",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "block_id": "announce",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Project* \n {project_name} \n {project_url} \n {github_url}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Branch* \n {branch}"
                        }
                    ],
                    "accessory": {
                        "type": "image",
                        "image_url": announce_image,
                        "alt_text": "Good job star"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "block_id": "general",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Back Office URL* \n {project_url}/admin/"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Superuser login/password* \n {admin_username} \n {admin_password} \n"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "block_id": "documentation",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Documentation* \n {project_url}/redoc/ \n {project_url}/swagger/"
                        }
                    ]
                }
            ]
        }

        response = requests.post(self.webhook_url, json=msg)
        if response.status_code == 200:
            success(f'Announced on {self.channel_name}.')
        else:
            error(f'Could not announce on {self.channel_name}!')
            print(response.status_code)


class Github:
    """ Communicates with Github. That's it. That's all it does really. """

    def __init__(self, access_token: str) -> None:
        """ access_token -> https://github.com/settings/tokens """

        self.access_token = access_token
        self.base_url = 'https://api.github.com'

    def make_private_repo(self, org_name: str, repo_name: str) -> bool:
        """ Sets up a new empty private repo on github with standard config. """

        url = f'{self.base_url}/orgs/{org_name}/repos'
        success(f'Creating new repo via {url}')
        headers = {
            'Authorization': f'token {self.access_token}'
        }
        payload = {
            'name': repo_name,
            'private': True,
            'has_projects': False,
            'has_wiki': False,
            'is_template': False
        }

        response = requests.post(url, json=payload, headers=headers)
        if not response.status_code == 201:
            print(response.json())
            return False
        return True


class ProjectServer:
    """ The main class that manages the connection to the server that we are configuring. """
    def __init__(self,
                 python_version: str,
                 project_name: str,
                 project_url: str,
                 branch: str,
                 db_name: str,
                 apache_conf_path: str,
                 nginx_conf_path: str,
                 uvicorn_conf_path: str,
                 project_path: str,
                 logging_path: str,
                 static_path: str,
                 media_path: str,
                 admin_password: str,
                 admin_username: str = 'admin',
                 admin_email: str = 'admin@wertkt.com') -> None:
        """
        Args:
            python_version (str)    for use in pyenv - i.e '3.7.1'
            project_name (str)      i.e. 'cinesociety-back'
            project_url (str)       i.e. 'viva-bolino.wertkt.com'
            branch (str)            i.e. 'staging' vs. 'prod'
            db_name (str)           database name we will create
            apache_conf_path (str)  rel path to apache file to use when configuring remote server
            nginx_conf_path (str)   rel path to nginx file to use when configuring remote server
            uvicorn_conf_path (str) rel path to uvicorn server conf to use when configuring remote server
            project_path (str)      abs path on remote server where will install project
            logging_path (str)      abs path on remote server where logs will live
            static_path (str)       abs_path on remote server where static files will be served
            media_path (str)        abs_path on remote server where users can upload files
            admin_password (str)    superuser password for back office
            admin_username (str)    superuser username for back office
            admin_email (str)       superuser email for back office
        """

        self.python_version = python_version
        self.project_name = project_name
        self.project_url = project_url
        self.branch = branch
        self.db_name = db_name
        self.apache_conf_path = apache_conf_path
        self.nginx_conf_path = nginx_conf_path
        self.uvicorn_conf_path = uvicorn_conf_path
        self.project_path = project_path
        self.logging_path = logging_path
        self.static_path = static_path
        self.media_path = media_path
        self.github_clone_path = f'git@github.com:wertkt/{project_name}.git'
        self.admin_username = admin_username
        self.admin_email = admin_email
        self.admin_password = admin_password

    def connect(self, host: str, username: str) -> None:
        """ Sets Connection object for executing commands on staging server. """

        try:
            self.conn = Connection(host=host, user=username, connect_timeout=5, port=22)
            self.conn.open()
            user = self.conn.run('whoami', hide='stdout')
            success(f'Logged in as {user.stdout.strip()}.')
            return
        except PasswordRequiredException:
            error('Password was required. Check your username first. Second try this: ssh-add ~/.ssh/id_rsa')
        except AuthenticationException:
            error('Server rejected your auth credentials. Ensure ~/.ssh/id_rsa.pub was added to server.')
        except SSHException:
            error('SSH connection problem. Network down? Server not responding?')
        except TimeoutError:
            error('Connection timed out.')
        except Exception as e:
            error(str(e))
        exit()

    def close(self) -> None:
        """ Closes connection to server. """

        self.conn.close()
        print('Connection closed.')

    def create_db(self) -> None:
        """ Creates PSQL DB. """

        if self.conn.run(f'sudo -u postgres createdb {self.db_name}', hide='stderr', warn=True):
            success(f'Created database named {self.db_name}.')
        else:
            error(f'Could not create database named {self.db_name} - already exists?')

    def clone_repository(self) -> None:
        """ Get repo URL, install destination, clone to path. """

        is_ok = input(f'This will clone the project to {yellow(self.project_path)}. Ok? [Y/n] ')
        if is_ok in ['', 'Y', 'y']:
            if self._exists(self.project_path):
                error(f'Can\'t create {self.project_path} -- already exists.')
            self.conn.run(f'git clone {self.github_clone_path} {self.project_path}')
            success(f'Successfully cloned into {self.project_path}')
        else:
            self._abort()

    def set_or_create_branch(self) -> None:
        """ Let's switch branches so we aren't running on wrong branch. """

        with self.conn.cd(self.project_path):
            if not self.conn.run(f'git checkout {self.branch}', hide='stderr', warn=True):
                print(f'{self.branch} branch does not exist. Creating {self.branch}.')
                self.conn.run(f'git branch {self.branch}')
                self.conn.run(f'git checkout {self.branch}')
            else:
                self.conn.run('git pull')
            success(f'Switched to {self.branch} branch.')

    def install_project(self) -> None:
        """ Setup venv, install python depencies, migrate, create super user. """

        self.set_or_create_branch()

        with self.conn.cd(self.project_path):

            if self.conn.run(f'pyenv global {self.python_version}'):
                success(f'Switched to Python {self.python_version}')
            else:
                error(f'Something went wrong switching to {self.python_version}!')

            if self.conn.run(f'pipenv install --python {self.python_version}'):
                success('Created virtual environment and installed dependencies.')
            else:
                error('Could not install with pipenv. Aborting.')
                self._abort()

            if self.conn.run(f'echo DJANGO_SETTINGS_MODULE=conf.settings.{self.branch} >> .env'):
                success('Created .env file.')
            else:
                error('Something went wrong - check your .env file.')

            # need to this here first or we can't run ./manage.py
            self.make_log_dirs()
            self.make_static_dirs()

            if self.conn.run('pipenv run python manage.py migrate'):
                success('Created virtual environment and installed dependencies.')
            else:
                error('Migrations could NOT be installed - you need to check this out.')

            superuser_cmd = 'pipenv run python manage.py customsuperuser '
            superuser_args = f'--username {self.admin_username} --email {self.admin_email} --password {self.admin_password} --noinput'
            if self.conn.run(superuser_cmd + superuser_args):
                success(f'Created superuser with following username/password:\n{self.admin_username}\n{self.admin_password}')
            else:
                error('Could not create superuser. Login to back-office impossible.')

            if self.conn.run('pipenv run python manage.py collectstatic'):
                success('Collected static files.')
            else:
                error('Could not collect static files!')

        self.chown(self.project_path, 'www-data')
        self.chown(self.logging_path, 'www-data')
        self.chown(self.static_path, 'www-data')

        self.symlink(self.project_path, '/var/www/')

    def chown(self, path: str, owner: str, is_recursive: bool = True) -> None:
        """ Just a wrapper that basically does 'chown -R www-data /home/whatever'

        Args:
            path (str)          absolute path to file/folder to chown
            owner (str)         the new owner of the file/folder
            is_recursive (bool)    default: true, whether to apply new ownership recursively
        """

        cmd = 'chown '
        if is_recursive:
            cmd += '-R '
        cmd += f'{owner} {path}'
        result = self.conn.run(cmd)
        if result:
            success(f'Set owner of {path} to {owner}.')
        else:
            error(f'Could not set owner of {path} to {owner}.')

    def symlink(self, origin: str, destination: str) -> None:
        """ Create symbolic link of directory or file.

        Args:
            origin (str)        absolute path of file/folder to link
            destination (str)   the place where we will create the link
        """

        cmd = f'ln -s {origin} {destination}'
        result = self.conn.run(cmd, warn=True)
        if result:
            success(f'Created symlink in this directory: {destination}.')
        else:
            error(f'Could NOT create symlink from {origin}.')

    def make_log_dirs(self) -> None:
        """ Make logging directories, symlink, and set permissions. """

        if self.conn.run(f'mkdir {self.logging_path}', warn=True):
            success(f'Created logging directory: {self.logging_path}.')
        else:
            error(f'Could not creating logging directory! {self.logging_path}')
        self.chown(self.logging_path, 'www-data')
        self.symlink(self.logging_path, '/var/www/logs/')

    def make_static_dirs(self) -> None:
        """ Make static/media directories, and set permissions. """

        if self.conn.run(f'mkdir --parents {self.media_path}', warn=True):
            success(f'Created media directory: {self.media_path}.')
        else:
            error(f'Could not creating media directory! {self.media_path}')
        if self.conn.run(f'mkdir  --parents {self.static_path}', warn=True):
            success(f'Created static directory: {self.static_path}.')
        else:
            error(f'Could not creating static directory! {self.static_path}')
        self.chown(self.static_path, 'www-data')
        self.chown(self.media_path, 'www-data')

    def setup_systemd(self) -> None:
        """ Copies uvicorn config to services directory so it launches automatically + creates
        socket file of this app for nginx to use. """

        uvicorn_service_file = os.path.join(self.project_path, self.uvicorn_conf_path)
        self.conn.run(f'cp {uvicorn_service_file} /etc/systemd/system/{self.project_url}.service', warn=True)
        success('Copied uvicorn service file.')

        # Note: ! the .service file references the remote virtualenv location that is unknown until
        # we've setup a virtualenv via pipenv on server.
        # so we symlink the virtual path so we can use a more predictable path :D it's bad but...
        with self.conn.cd(self.project_path):
            venv_path = self.conn.run('pipenv --venv').stdout.strip()
        self.symlink(venv_path, f'/home/virtualenvs/{self.project_url}')
        success('Created symlink of virtualenv.')

        self.conn.run(f'service {self.project_url} start')
        success(f'Started {self.project_url} service.')

    def setup_apache(self) -> None:
        """ Copy and enable Apache conf. """

        from_path = os.path.join(self.project_path, self.apache_conf_path)
        to_path = f'/etc/apache2/sites-available/{self.project_url}.conf'
        self.conn.run(f'cp {from_path} {to_path}', warn=True)
        success('Copied configuration to Apache.')
        self.symlink(to_path, f'/etc/apache2/sites-enabled/{self.project_url}.conf')
        success('Enabled site in Apache.')
        self.conn.run('service apache2 restart')
        success('Restarted Apache.')

    def setup_nginx(self) -> None:
        """ Copy and enable Nginx conf. """

        from_path = os.path.join(self.project_path, self.nginx_conf_path)
        to_path = f'/etc/nginx/sites-available/{self.project_url}.conf'
        self.conn.run(f'cp {from_path} {to_path}', warn=True)
        success('Copied configuration to Nginx.')
        self.symlink(to_path, f'/etc/nginx/sites-enabled/{self.project_url}.conf')
        success('Enabled site in Nginx.')
        self.conn.run('service nginx restart')
        success('Restarted Nginx.')

    def run_certbot(self, webserver: str = 'apache') -> None:
        """ Setup SSL for site with forced SSL redirect.

        Args:
            webserver (str)     'apache' or 'nginx'
        """

        cmd = f'certbot --non-interactive --agree-tos -d {self.project_url} --redirect --apache'
        cmd += f' --{webserver}'
        if self.conn.run(cmd, warn=True):
            success('SSL setup via Certbot.')
        else:
            error('Could not setup Certbot!')

    def _exists(self, path: str) -> bool:
        """
        Return True if given path exists on the current remote host.

        Args:
        path (str)            the file/dir to check existance of

        Returns:
        is_existing (bool)
        """

        cmd = f'test -e "$(echo {path})"'
        return self.conn.run(cmd, hide=True, warn=True).ok

    def _abort(self) -> None:
        """ Display general failure message and exit. """

        error('+++ Process aborted. Exiting program.')
        self.conn.close()
        exit()


# TASKS

@task
def setup(ctx, branch):
    """ This will fully set up a branch your project on TKT-staging server.

    *** MAKE SURE `branch` exactly matches your conf file and the branch name you want to deploy! ***
    """

    branch = branch.lower()
    admin_password = secrets.token_hex(nbytes=15)  # make a random superuser password

    # workaround for logging issue on staging import
    os.environ['DJANGO_SETTINGS_MODULE'] = f'conf.settings.{branch}'
    try:
        conf = importlib.import_module(f'conf.deploy.{branch}.config')
    except ModuleNotFoundError:
        error(f'Could not find conf.deploy.{branch}.config - are you sure you typed the correct branch name?')
        exit()

    server_settings = conf.DEPLOY_CONFIG['server']
    server_settings['admin_password'] = admin_password

    project_name = server_settings['project_name']
    project_url = server_settings['project_url']
    github_url = f'www.github.com/wertkt/{project_name}'

    connection_settings = conf.DEPLOY_CONFIG['connection']

    clear_screen()
    blanks(5)
    print('+++ Installation starting.')

    server = ProjectServer(**server_settings)

    server.connect(host=connection_settings['host'], username=connection_settings['username'])
    server.clone_repository()
    server.create_db()
    server.install_project()

    server.setup_systemd()
    server.setup_apache()
    server.setup_nginx()

    # our base ANAME record
    dns_records_to_create = [
        {
            'name': project_url,
            'record_type': 'A',
            'content': conf.DEPLOY_CONFIG['connection']['ip']
        }
    ]

    mailgun_api_key = os.getenv('MAILGUN_API_KEY')
    if not mailgun_api_key:
        error('Cannot setup Mailgun for this domain without API key.')
        print('Please add MAILGUN_API_KEY to your .bashrc or .zshrc and try again.')
        print('https://app.mailgun.com/app/account/security/api_keys')
    else:
        new_smtp_password = secrets.token_hex(nbytes=15)
        mailgun = Mailgun(mailgun_api_key)
        dns_records_to_create += mailgun.setup(project_url, new_smtp_password)

    cloudflare_api_key = os.getenv('CLOUDFLARE_API_KEY')
    if not cloudflare_api_key:
        error('Cannot set Cloudflare DNS for this domain without API key.')
        print('Please add CLOUDFLARE_API_KEY to your .bashrc or .zshrc and try again.')
        print('https://support.cloudflare.com/hc/en-us/articles/200167836-Managing-API-Tokens-and-Keys')
    else:
        cloudflare = Cloudflare(cloudflare_api_key)
        for record in dns_records_to_create:
            cloudflare.add_dns(**record)

    server.run_certbot()
    server.close()

    if mailgun_api_key:  # meaning, we've already got mailgun object
        mailgun.verify(project_url)

    slack = Slack()
    slack.announce(project_name, project_url, branch, github_url, admin_password)

    success(f'{branch} installed - hopefully successfully!')
    blanks(5)


@task
def gitinit(ctx):
    """ Run once, at start of project.
    Sets up the project for the first time, commits all, and pushes to github. """

    ctx.run('git init', replace_env=False)
    ctx.run('git add .', replace_env=False)
    ctx.run('git commit -m "🎉 first commit"', replace_env=False)
    ctx.run('git branch -M main', replace_env=False)

    access_token = os.getenv('GITHUB_ACCESS_TOKEN')
    if not access_token:
        error('You need to add GITHUB_ACCESS_TOKEN to your environment before running this command.')
    github = Github(access_token)
    if github.make_private_repo(org_name='wertkt', repo_name='new_fake_drf_project'):
        ctx.run('git remote add origin git@github.com:wertkt/new_fake_drf_project.git', replace_env=False)
        ctx.run('git push -u origin main', replace_env=False)
        success('Project is ready.')
    else:
        error('Something went wrong. You will need to set this up manually.')
