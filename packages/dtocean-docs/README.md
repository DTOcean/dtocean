[![dtocean-docs actions](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-docs.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-docs.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-docs)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-docs)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dtocean-docs)

# dtocean-docs

Provides an offline copy of the DTOcean documentation.

Part of the [DTOcean](https://github.com/DTOcean/dtocean) suite of tools.

## Installation

```sh
pip install dtocean-docs
```

## Usage

To access the documentation from the DTOcean GUI (see [dtocean-app]), open
the `Help` menu and choose the `Index...` option.

The documentation can also be opened in a separate browser (without the need to
install dtocean-app) by using following command:

```sh
dtocean-docs
```

Alternatively, if [dtocean-core] is installed, the docs can be opened using:

```sh
dtocean docs
```

## Development

Development of polite-config uses the [Poetry](https://python-poetry.org/)
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

Additional tests are available for the plugins to [dtocean-core]. Enable these
tests by installing the `test-extras` group:

```sh
poetry install --with test --with test-extras
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

[dtocean-app]: https://pypi.org/project/dtocean-app/
[dtocean-core]: https://pypi.org/project/dtocean-core/
