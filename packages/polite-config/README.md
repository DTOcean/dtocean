[![polite-config actions](https://github.com/DTOcean/dtocean/actions/workflows/test-polite-config.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-polite-config.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=polite-config)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=polite-config)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/polite-config)](https://www.python.org/downloads/)
[![PyPI - Version](https://img.shields.io/pypi/v/polite-config)](https://pypi.org/project/polite-config/)

# polite-config

Easy functions for paths, logging and configuration files.

Part of the [DTOcean](https://github.com/DTOcean/dtocean) suite of tools.

## Installation

```sh
pip install polite-config
```

## Usage

An example of setting up [logging](https://docs.python.org/3/library/logging.html)
using a user-specific [yaml configuration file](https://docs.python.org/3/howto/logging.html#configuring-logging).

Copy the default logging file from the module source code to the user's data
directory (`C:\Users\<USERNAME>\AppData\Roaming\DTOcean\polite`):

```python
>>> from polite_config.paths import (DirectoryMap, ModPath, UserDataPath)

>>> objdir = ModPath("polite", "config")
>>> datadir = UserDataPath("polite", "DTOcean")
>>> dirmap = DirectoryMap(datadir, objdir)
>>> dirmap.copy_file("logging.yaml", overwrite=True)
>>> datadir.isfile("logging.yaml")
True
```

Use the copied configuration file to set up logging:

```python
>>> from polite_config.configuration import Logger

>>> log = Logger(datadir)
>>> log_config_dict = log.read()
>>> log.configure_logger(log_config_dict)
>>> logger = log.get_named_logger("polite")
>>> logger.info("Hello World")
INFO - polite - Hello World
```

Note that classes such as `ModPath` and `UserDataPath` are subclasses of
`pathlib.Path`.

## Development

polite-config is developed using the [Poetry](https://python-poetry.org/)
dependency manager. Poetry must be installed and available on the command line.

To install:

```sh
poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```sh
poetry install --with test
```

Run the tests:

```sh
poetry run pytest
```

Code quality can also be audited using the [ruff](https://docs.astral.sh/ruff/)
and [pyright](https://github.com/microsoft/pyright) tools.

Install the dependencies:

```sh
poetry install --with audit
```

Run the audit:

```sh
poetry run ruff
poetry run pyright src
```

The above tests can be run across all compatible Python versions using
[tox](https://tox.wiki/) and [tox-uv](https://github.com/tox-dev/tox-uv). To
install and run:

```sh
poetry install --with tox
poetry run tox
```

## Contributing

Please see the [dtocean](https://github.com/DTOcean/dtocean) GitHub repository
for contributing guidelines.

## Credits

This package was initially created as part of the [EU DTOcean project](https://cordis.europa.eu/project/id/608597)
by Mathew Topper at [TECNALIA](https://www.tecnalia.com).

It is now maintained by Mathew Topper at [Data Only Greater](https://www.dataonlygreater.com/).

## License

[MIT](https://choosealicense.com/licenses/mit/)
