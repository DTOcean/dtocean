[![dtocean-dummy-module actions](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-dummy-module.yml/badge.svg?branch=next)](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-dummy-module.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-dummy-module)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-dummy-module)

# dtocean-dummy-module

## Overview

A python package to demonstrate some of the many features of Python and
introduce a typical structure for a Python package.

## Installation

Installation and development of the dummy module uses the [Poetry](
https://python-poetry.org/) dependency manager. Poetry must be installed
and available on the command line.

To install:

```console
poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org).

Install the testing dependencies:

```console
poetry install --with test
```

Run the tests:

```console
poetry run pytest
```

## Example Usage

The following commands are run from the
[command-line interface](http://en.wikipedia.org/wiki/Command-line_interface).

### Execution

```console
dtocean-dummy 5
```

### Help

```console
dtocean-dummy -h
```
