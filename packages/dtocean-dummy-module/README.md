[![dtocean-dummy-module actions](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-dummy-module.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-dummy-module.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-dummy-module)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-dummy-module)

# dtocean-dummy-module

## Overview

A python package to demonstrate some of the many features of Python and
introduce a typical structure for a Python package. This package is used for
testing [mdo-engine](https://pypi.org/project/mdo-engine/).

Part of the [DTOcean](https://github.com/DTOcean/dtocean) suite of tools.

## Installation

Installation and development of the dummy module uses the [Poetry](
https://python-poetry.org/) dependency manager. Poetry must be installed
and available on the command line.

To install:

```sh
poetry install
```

## Example Usage

The following commands are run from the
[command-line interface](http://en.wikipedia.org/wiki/Command-line_interface).

### Execution

```sh
dtocean-dummy 5
```

### Help

```sh
dtocean-dummy -h
```

## Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org).

Install the testing dependencies:

```sh
poetry install --with test
```

Run the tests:

```sh
poetry run pytest
```

Code quality can also be audited using the [ruff](https://docs.astral.sh/ruff/)
and [pyright](https://github.com/microsoft/pyright) tools. Install the
dependencies:

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

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
