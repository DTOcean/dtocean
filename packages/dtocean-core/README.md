[![dtocean-core actions](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-core.yml/badge.svg?branch=next)](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-core.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-core)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-core)

# dtocean-core

The dtocean-core module provides the data model and execution environment for
the DTOcean suite of tools. It manages data transfer between the DTOcean
components (modules, database, user), data storage and versioning, and module
execution ordering.

## Installation

Installation and development of dtocean-core uses the
[Poetry](https://python-poetry.org/) dependency manager. Poetry must be
installed and available on the command line.

To install:

```sh
poetry install
```

Design and assessment modules must be installed separately. For the graphical
interface, install [dtocean-app](https://github.com/DTOcean/dtocean/tree/next/packages/dtocean-app).

### Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org). To install the testing dependencies:

```sh
poetry install --with test
```

Run the tests:

```sh
poetry run pytest
```

Additional tests are available upon the installation of the
[dtocean-hydrodynamics](https://github.com/DTOcean/dtocean/tree/next/packages/dtocean-hydrodynamics)
module and the [DTOcean
database](https://github.com/DTOcean/dtocean-database-next).

Once the database is installed and running, additional options must be provided
to the pytest command, with meanings as follows:

| Option                | Meaning                                |
|-----------------------|----------------------------------------|
| --postgresql-password | The password of the root database user |
| --postgresql-path     | The path to the database setup files   |

Thus, the minimum necessary test command to include the database tests is (with example values):

```sh
poetry run pytest --postgresql-password="example" --postgresql-path="/path/to/the/database/setup/files"
```

The database tests use the
[pytest-postgresql](https://github.com/dbfixtures/pytest-postgresql) plugin to
generate temporary test databases that mirror the DTOcean database schema and
tables. Any additional option provided by pytest-postgresql plugin can also be
applied to the DTOcean tests (for instance, if the default port is not 5432, it
can be set with the `--postgresql-port` option).

## Usage

### Jupyter Notebooks

Examples of using dtocean-core are given in [Jupyter Notebooks](
http://jupyter.org/) which are found in the "notebooks" folder of the
dtocean-core source code.

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

The main `dtocean core run` command can run DTOcean projects saved as `.prj` files,
either for the next scheduled module or all modules. For help, type:

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

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

See [this blog post](
https://www.dataonlygreater.com/latest/professional/2017/03/09/dtocean-development-change-management/)
for information regarding development of the DTOcean ecosystem.

Please make sure to update tests as appropriate.

## Credits

This package was initially created as part of the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by:

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
