# dtocean-dummy-module

## Overview

A python package to demonstrate some of the many features of Python and
introduce a typical structure for a Python package.

## Installation

Installation and development of the dummy module uses the [Poetry](
https://python-poetry.org/) dependency manager. Poetry must be installed
and available on the command line.

To install:

```
$ poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org).

Install the testing dependencies:

```
$ poetry install --with test
```

Run the tests:

``` 
$ poetry run pytest
```

## Example Usage

The following commands are run from the
[command-line interface](http://en.wikipedia.org/wiki/Command-line_interface).

### Execution

```shell
dtocean-dummy 5
```

### Help

```shell
dtocean-dummy -h
```

## Update

### Anaconda

```shell
conda update dtocean-dummy-module
```

## Uninstallation

### Pip

```shell
pip uninstall dtocean-dummy-module
```

### Anaconda

```shell
conda remove dtocean-dummy-module
```
