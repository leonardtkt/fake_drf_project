# Logging

## Overview

This project uses the built-in [logging](https://docs.python.org/3/library/logging.html) module. The logging in streamed into several loggers, organized around functionality. For example, Django-specific information is logged (GET requests, etc.) are logged separately from user-related data (authentication, etc.)

## Specifications

There are three forms of logging setup on this project.

* Colored console-based logging: ideal for dev environments;
* File-based text logging: ideal for standard preproduction or production environments;
* CloudWatch logging: ideal for AWS deployments.

This can be changed by modifying the appropriate settings file (i.e. `dev.py` or `experimental.py` or `prod.py` - import all from the appropriate logging settings.)

These logging types are intended to be used separately, but with a bit of work they could be combined, so that you would have both file and console output.

If you have file logging activated, please be aware that the default output path will be `/var/www/logs/` - as always, you will have to check permissions and make sure it's writable by the service that is running your application.

For [CloudWatch](https://aws.amazon.com/cloudwatch/) logging, be sure you add and complete the following lines in your preproduction or production server (in addition to importing all from `conf/logging/aws.py` in your `prod.py` settings file):

```python
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
```

Depending on where the AWS_REGION setting, you will then be able to access the logs at a location like [this one](https://eu-west-1.console.aws.amazon.com/cloudwatch/home?region=eu-west-1#logs:) - it should be listed there under the log group name `newtktapp.wertkt.com`. By clicking on it, you should then see each of the individual log streams from your project - django, users, etc.

Note that IP addresses for failed logins to the back-office are automatically logged in `signals.py`. If desired, [Fail2ban](https://www.fail2ban.org/wiki/index.php/Main_Page) or similar can be used to block bots or persons who are fraudulently attempting to intrude into the system.
