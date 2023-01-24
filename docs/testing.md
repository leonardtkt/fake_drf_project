# Testing

Tests are constructed using the built-in [unittest](https://docs.python.org/3/library/unittest.html) module and rely heavily on [factory_boy](https://factoryboy.readthedocs.io/en/latest/) and where necessary use [mock](https://mock.readthedocs.io/en/latest/).

Tests can be run manually by running `inv test` (or by activating the virtual environment first with `pipenv shell` followed by `./manage.py test`).

A shortcut for generating the coverage reports: `inv coverage`. This uses [Coverage.py](https://coverage.readthedocs.io/en/coverage-5.0/) and will generate a HTML report which is interactive - click on a filename in the report to get a detailed line-by-line report of that file.
