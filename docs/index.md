# New Fake DRF project

Detailed instructions for Django project: new_fake_drf_project.

## Commands

* `inv install` - Setup a virtual environment, install Python dependencies, run migrations.
* `inv sync` - After pulling new version of project, will install new dependencies and run any new migrations.
* `inv docs` - Serve these documents on localhost and open in web browser.
* `inv test` - Run all tests for the project.
* `inv coverage` - Test project and generate coverage HTML reports and open in web browser.
* `inv run` - Serve Django project on localhost and open in web browser.
* `inv activate` - Equivalent to `source /path/to/virtualenv/bin/activate` using old virtualenv system.
* `inv template <app_name>` - Using models.py create and OVERWRITE views.py, serializers.py using these models.

Generally if you are frontend dev trying to get a local version up and running, you will only need to run `inv install` to initialize the project then `inv run` to launch a local server. Anytime you pull new commits from the repository, you should run `inv sync` (only necessary when new migrations or changes to the dependencies - when in doubt, run `inv sync`.)

## Installation

### Dev

* Clone repository;
* Setup Postgres db with correct name and appropriate user permissions;
* Run `inv install`;

### Staging

You will need to have a `staging` branch created for this project and a repo on Github.

You will need the following variables set correctly in your environment:

* `MAILGUN_API_KEY`
* `CLOUDFLARE_API_KEY`

Also you will need to have rights to ssh into the staging server (i.e. pubkey already added, etc.)

Running `fab create` will do the following:

* Clone the repo to staging server
* Switch to staging branch
* Create a database for project
* Setup a virtual environment
* Install dependencies
* Run migrations
* Collect static files
* Set appropriate file/folder permissions
* Setup and proxy Uvicorn through Nginx/Apache2
* Configure DNS on Cloudflare
* Setup Certbot
* Setup a Mailgun account
* Send a message to our Slack with notification

If the process fails at any point, you should have a detailed logs on your screen - so it's easy to start again and continue
from there. See fabfile.py `setup_staging` function for details.

Example -> sometimes the DNS hasn't propogated yet so we can't veryify with Mailgun. If that's the case, just drop into shell
with `pipenv run ./manage.py shell` and run the following:

```
import os
from fabfile import Mailgun, CONFIGS
project_url = CONFIGS['staging']['server']['project_url']
mailgun = Mailgun(mailgun_api_key)
mailgun.verify()
```
