[![dtocean-core actions](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-core.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-core.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-core)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-core)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dtocean-core)](https://www.python.org/downloads/)
[![PyPI - Version](https://img.shields.io/pypi/v/dtocean-core)](https://pypi.org/project/dtocean-core/)

# dtocean-core

The dtocean-core module provides the data model and execution environment for
the DTOcean suite of tools. It manages data transfer between the DTOcean
components (modules, database, user), data storage and versioning, and module
execution ordering.

Part of the [DTOcean](https://github.com/DTOcean/dtocean) suite of tools.

## Installation

```sh
pip install dtocean-core
```

## Usage

### Command Line Tool (dtocean)

A command line tool is provided for various functions. All commands are
available from the `dtocean` root. For instance:

```sh
dtocean -h
```

#### dtocean init

The init utility is for calling initialization scripts required before the
first run of any installed DTOcean modules. Note that an internet connection
is required when running this command. To get help:

```sh
dtocean init -h
```

#### dtocean core run

The main `dtocean core run` command can run DTOcean projects saved as `.dtop`
files, either for the next scheduled module or all modules. For help, type:

```sh
dtocean core run -h
```

#### dtocean core config

Another utility is provided to copy user modifiable configuration files to the
users "AppData" directory (on Windows). For instance the logging and database
configuration can be modified once these files have been copied. To get help:

```sh
dtocean core config -h
```

#### dtocean database

This utility is for converting the DTOcean SQL database into a structured
directories of files, or for uploading the same structure into the database is
provided. To get help:

```sh
dtocean database -h
```

#### Module subcommands

Utilities provided by installed modules are also available through the
`dtocean` command. For instance, to get help for the commands provided by the
dtocean-hydrodynamics package:

```sh
dtocean hydrodyamics -h
```

A list of all available subcommands will be shown when calling `dtocean -h`.

### Jupyter Notebooks

Examples of using dtocean-core are given in [Jupyter Notebooks](
http://jupyter.org/) which are found in the "notebooks" folder of the
dtocean-core source code.

## Development

Development of dtocean-core uses the [Poetry](https://python-poetry.org/)
dependency manager. Poetry must be installed and available on the command line.

To install:

```sh
poetry install
```

Download data files with the following command:

```sh
dtocean init
```

### Tests

#### Basic Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org). To install the testing dependencies:

```sh
poetry install --with test
```

Additional tests are available for the plugins to [dtocean-app]. Enable these
tests by installing the `test-extras` group:

```sh
poetry install --with test --with test-extras
```

To run the tests:

```sh
poetry run pytest
```

#### Database Tests

Database integration tests are available upon the installation of the [DTOcean
database](https://github.com/DTOcean/dtocean-database). Once the database
is installed and running, additional options must be provided to the pytest
command, with meanings as follows:

| Option                | Meaning                                |
|-----------------------|----------------------------------------|
| --postgresql-password | The password of the root database user |
| --postgresql-path     | The path to the database setup files   |

The database tests use the
[pytest-postgresql](https://github.com/dbfixtures/pytest-postgresql) plugin to
generate temporary test databases that mirror the DTOcean database schema and
tables. Any additional option provided by pytest-postgresql plugin can also be
applied to the DTOcean tests (for instance, if the default port is not 5432, it
can be set with the `--postgresql-port` option).

To include the database tests (with example values):

```sh
poetry run pytest --postgresql-password="example" --postgresql-path="/path/to/the/database/setup/files"
```

#### Multi-Version Tests

The above tests can be run across all compatible Python versions using
[tox](https://tox.wiki/) and [tox-uv](https://github.com/tox-dev/tox-uv). To
install:

```sh
poetry install --with tox
```

To run without the database tests:

```sh
poetry run tox
```

To include the database tests (with example values):

```sh
poetry run tox -- --postgresql-password="example" --postgresql-path="/path/to/the/database/setup/files"
```

#### Integration Tests

Integration tests are included in the `integration` directory. These
tests are designed to be used in combination with the `scripts/make_test_project.py`
script, which generates a `.dtop` file, labelled with the OS and Python version
used to create it and saved in the `test_data/projects` directory.

The integration tests will try to open all the project files in the `test_data/projects`
directory. This is primarily useful for testing cross-platform loading of
save files and is automated in the GitHub Action workflow for dtocean-core.

To run the tests:

```sh
poetry run pytest integration
```

## Contributing

Please see the [dtocean](https://github.com/DTOcean/dtocean) GitHub repository
for contributing guidelines.

## Credits

This package was initially created as part of the [EU DTOcean project](
https://cordis.europa.eu/project/id/608597) by:

+ Mathew Topper at [TECNALIA](https://www.tecnalia.com)
+ Vincenzo Nava at [TECNALIA](https://www.tecnalia.com)
+ Adam Colin at [the University of Edinburgh](https://www.ed.ac.uk/)
+ David Bould at [the University of Edinburgh](https://www.ed.ac.uk/)
+ Rui Duarte at [France Energies Marines](https://www.france-energies-marines.org/)
+ Francesco Ferri at [Aalborg University](https://www.en.aau.dk/)

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

[dtocean-app]: https://pypi.org/project/dtocean-app/
