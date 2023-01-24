from invoke import task
from colorama import Fore, Back, Style
import os


# helpers

def clear_screen():
    """ Clears screen. Deals with special case for Windows. """

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def blanks(n):
    """ Print n line breaks.

    Args:
      n (int)       number of lines breaks to print
    """
    for i in range(n):
        print()


# menus

def display_welcome_menu():
    """ Just prints quick overview of project name, description, requirements. """

    clear_screen()
    blanks(5)

    print(f'\t\t - You are installing {Fore.BLUE}{Back.YELLOW}new_fake_drf_project{Style.RESET_ALL} -')
    blanks(3)

    print('Make sure this is done before proceeding:')
    blanks(1)
    print(f'\t1. Installed non-Python dependencies with {Fore.GREEN}brew/apt{Style.RESET_ALL} (see {Fore.RED}README.md{Style.RESET_ALL})')
    print(f'\t2. Created PostgreSQL database called {Fore.GREEN}newfakedrf{Style.RESET_ALL}')
    blanks(5)


# task choices

@task
def install(ctx):
    """ Install project (run once only.) """

    display_welcome_menu()

    response = input(f'{Fore.YELLOW}{Back.BLACK}Would you like to continue? [Y/n]{Style.RESET_ALL} ')
    blanks(2)
    if response not in ['', 'y', 'Y']:
        print(f'{Fore.RED}Process aborted by user.{Style.RESET_ALL}')
        blanks(3)
        return

    # create local .env file that we will use
    print('.. Creating .env file.')
    with open('.env', 'w') as f:
        f.write('DJANGO_SETTINGS_MODULE=conf.settings.dev')

    # venv + pip install
    print('.. Creating virtual environment and installing Python dependencies.')
    ctx.run('pipenv install --dev')

    #pre-commit
    try:
        print("... Updating pre-commit hooks.")
        ctx.run("pipenv run pre-commit autoupdate")
        print("Installing pre-commit hooks.")
        ctx.run("pipenv run pre-commit install")
    except Exception:
        print(f"{Fore.RED}Error: No git directory found.\n"
              f"{Fore.YELLOW}Running `git init`{Style.RESET_ALL}")
        ctx.run('git init', replace_env=False)
        ctx.run("pipenv run pre-commit autoupdate")
        ctx.run("pipenv run pre-commit install")
        ctx.run('git add .', replace_env=False)
        ctx.run('git commit -m "🎉 first commit" --no-verify', replace_env=False)
        ctx.run('git branch -M main', replace_env=False)


    print('.. Creating cache table...')
    ctx.run('pipenv run python manage.py createcachetable')

    # migrations
    print('.. Migrating database.')
    ctx.run('pipenv run python manage.py migrate')

    # superuser
    print('.. Creating superuser.')
    su = 'pipenv run python manage.py customsuperuser --username admin --email admin@wertkt.com --password adminadmin --noinput'
    ctx.run(su)

    # confirmation
    blanks(3)
    print(f'{Fore.GREEN}✓ Your application is now installed.{Style.RESET_ALL}')
    blanks(2)
    print('+ Your superuser account (for back-office) ->')
    print(f'\t{Fore.MAGENTA}username: admin')
    print(f'\tpassword: adminadmin{Style.RESET_ALL}')
    blanks(2)


@task
def coverage(ctx):
    """ Run tests then display coverage results in browser. """

    clear_screen()
    ctx.run('pipenv run coverage run manage.py test')
    ctx.run('pipenv run coverage html')
    ctx.run('open htmlcov/index.html')


@task
def run(ctx):
    """ Launch local development server. """

    ctx.run('pipenv run python manage.py runserver')


@task
def docs(ctx):
    """ Launch the docs server and open in browser. """

    ctx.run('(sleep 4;open http://127.0.0.1:8000) & pipenv run mkdocs serve')


@task
def test(ctx):
    """ Run all tests for the project. """

    ctx.run('pipenv run python manage.py test')


@task
def sync(ctx):
    """ Apply new migrations, install new dependencies. """

    ctx.run('pipenv sync')
    ctx.run('pipenv run python manage.py migrate')


@task
def activate(ctx):
    """ Activate the virtual environment for manual commands. """

    ctx.run('pipenv shell')


@task
def template(ctx, app_name):
    """ Generate views.py, admin.py, serializers.py, etc for an app based on corresponding models.py """

    blanks(2)
    print('This will auto-generate views.py, admin.py, serializers.py, and urls.py for an app.')
    print('The new app directory must already have been created and the app name must already be in INSTALLED_APPS')

    blanks(2)
    response = input(f'{Fore.RED}{Back.BLACK}This will overwrite existing data. Continue? [y/N]{Style.RESET_ALL} ')

    if response not in ['y', 'Y']:
        print(f'{Fore.RED}Process aborted by user.{Style.RESET_ALL}')
        blanks(3)
        return

    ctx.run(f'pipenv run python manage.py generator api {app_name}')

    # success message
    blanks(1)
    print(f'{Fore.GREEN}✓ Basic templating completed for {app_name}.{Style.RESET_ALL}')
    blanks(1)

    # warning message - manual updates needed from user
    print(f'{Fore.YELLOW}Please manually add the following to conf/urls.py:')
    print(f'\t{Fore.MAGENTA}from {app_name}.urls import router as {app_name}_router')
    print(f'\trouter.extend({app_name}_router)')
    blanks(1)
    print(f'{Fore.YELLOW}Also, please update {Fore.MAGENTA}ADMIN_REORDER{Fore.YELLOW} in conf/base.py{Style.RESET_ALL}')
    blanks(2)
