[![dtocean-docs actions](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-docs.yml/badge.svg?branch=next)](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-docs.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-docs)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-docs)

# dtocean-docs

Provides an offline copy of the DTOcean documentation for the
[dtocean-app](https://github.com/DTOcean/dtocean/tree/next/packages/dtocean-app)
GUI.

## Installation

Installation and development of polite-config uses the [Poetry](https://python-poetry.org/)
dependency manager. Poetry must be installed and available on the command line.

To install:

```console
poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```console
poetry install --with test
```

Run the tests:

```console
poetry run pytest
```
