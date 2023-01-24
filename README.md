# New Fake DRF project Backend

Django 3.1 with Django-Rest-Framework 3.12

## Getting Started

These are basic quickstart instructions. There are two options here for you to choose from:

- Standard virtualenv
- Docker container-based

The Docker option is recommended for frontend since it doesn't require setup of Postgres, Redis, etc and no need to be concerned about specific versions of Python.

For further documentation regarding deployment, testing, logging, and advanced functionality, please run the command `inv docs` after a normal install.

## Option A: Standard Virtualenv Setup

### Prerequisites

On Mac, with Homebrew installed:

```sh
brew install postgresql python3 pipenv redis
```

Make sure that Postgresql and Redis are running. Depending how you installed, it could be as simple as:

```bash
brew services start redis
brew services start postgresql
```

Additionally you need [Python Invoke](http://www.pyinvoke.org/) installed globally. Usually this is as simple as running the following:

```sh
python3 -m pip install invoke fabric colorama
```

You should now be able to run the command `inv` in your shell.

### Installation (local)

Ensure PostgreSQL is installed and running (looking at you here, frontend). If you are stuck, read here:
https://chartio.com/resources/tutorials/how-to-start-postgresql-server-on-mac-os-x/

Create a new database. When prompted to enter a password, type `admin`:

```sh
createuser admin --superuser -W
createdb newfakedrf -O admin
```

To setup a virtual environment in the project directory and install Python dependencies and run migrations:

```sh
inv install
```

### Running project

After the project has been installed. You can now run the project anytime with this command:

```sh
inv run
```

### After fresh pull from repository

If there are new Python dependencies or migrations, pull from the repo and then enter this command to sync the project:

```sh
inv sync
```

### Accessing virtualenv

No need to use Invoke shortcuts or pipenv commands if you prefer regular virtual interaction. To activate the virtualenv shell: 

```sh
pipenv shell
```

This is the rough equivalent of `source <venv_dir>/bin/activate` and now you can run commands as you wish (i.e. `./manage.py test`)

## Option B: Docker Setup

### Prerequisites

This specific option will require Docker. Please follow these [Docker install instructions for Mac](https://docs.docker.com/docker-for-mac/install/).

### Running container

This command in the project directory should build/pull the necessary images and launch:

```bash
docker-compose up
```

Find the name of the web container by running `docker ps`. To run migrations and create a superuser:

```bash
docker exec -it <instance_name> python manage.py migrate
docker exec -it <instance_name> python manage.py createsuperuser
```

You can now login here: http://127.0.0.1:8000/admin/

If there are changes in the dependencies (i.e. Pipfile has changed since previous pull), then start with:

``bash
docker-compose up --build
```
