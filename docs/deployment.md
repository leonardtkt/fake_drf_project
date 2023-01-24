# Deployment

This project is configured to use CI/CD via [Github Actions](https://github.com/features/actions). Once this option has been enabled by the owner of the project, all pushes to the staging branch should be automatically deploy to the preproduction server (after the tests have passed.)

If it hasn't been done already, the GITHUB_TOKEN and SLACK_WEBHOOK secrets should be set in the repository. And you will need to set HOST, USERNAME, and KEY for deployment to staging.

On push to a Github repository, the tests will be run by Github Actions and the result of the test will be displayed in the commit history on the repo. If the SLACK_WEBHOOK and GITHUB_TOKEN keys are configured on the Github repository, it will automatically display the results of the test on the company Slack channel (if the relevant sections of `build_dev.yml` are uncommented)
