[![dtocean-app actions](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-app.yml/badge.svg?branch=next)](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-app.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-app)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-app)

# dtocean-app

This repository contains the main graphical application of the DTOcean software
tools. The code contained in this package is a
[Qt](https://en.wikipedia.org/wiki/Qt_(software)) GUI view of the underlying
model, provided by the [dtocean-core][1] package. Related dtocean-\* modules
and themes are installed separately.

Developers of DTOcean modules may wish to install this module, following the
installation instructions below, and the source code of any other DTOcean
module they wish to develop. In this way, the impact of changes can be observed
in a graphical environment.

## Installation

Installation and development of dtocean-app uses the
[Poetry](https://python-poetry.org/) dependency manager. Poetry must be
installed and available on the command line.

If installing from the git repository, the image files must first be
retrieved using git-lfs (ensure that [git-lfs](https://git-lfs.com/) is installed
first):

```sh
git lfs fetch --all
git lfs pull
```

To install:

```sh
poetry install
```

Design and assessment modules must be installed separately.

### Tests

A test suite is provided with the source code that uses
[pytest](https://docs.pytest.org). To install the testing dependencies:

```sh
poetry install --with test
```

Alternatively to include additional modules which enable the full suite of tests,
use the command:

```sh
poetry install --with test --with test-extras
```

Run the tests:

```sh
poetry run pytest
```

## Documentation

See [dtocean.github.io](https://dtocean.github.io/dtocean) for the latest
documentation.

## Usage

### Graphical Interface

The graphical interface is started from a command line terminal, from the
root directory using poetry:

```sh
poetry run dtocean app
```

To send all output to the cmd window (useful when crashes occur before logging
is started) use "debug mode":

```sh
poetry run dtocean app --debug
```

See the "Getting Started 1: Example Project" chapter of the [DTOcean
documentation](https://dtocean.github.io/dtocean) for an example project.

### Command Line Tools

A utility is provided to copy user modifiable configuration files to the users
"AppData" directory (on Windows). For instance the logging configuration can be
modified once these files have been copied. To get help:

```sh
poetry run dtocean app config -h
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change. Please make sure to update tests as appropriate.

## Credits

This package was initially created as part of the [EU DTOcean
project](https://www.dtoceanplus.eu/About-DTOceanPlus/History) by:

- Mathew Topper at [TECNALIA](https://www.tecnalia.com)
- Vincenzo Nava at [TECNALIA](https://www.tecnalia.com)
- Rui Duarte at [France Energies Marines](https://www.france-energies-marines.org/)

It is now maintained by Mathew Topper at [Data Only
Greater](https://www.dataonlygreater.com/).

## Licenses

### Software

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

### Icons

The icons used with the graphical interface are source directly or derived from
the following open source icon sets:

- Crystal Clear ([LPGL-2.1](https://choosealicense.com/licenses/lgpl-2.1/))
- GNOME ([GPL-2.0](https://choosealicense.com/licenses/gpl-2.0/))
- ScreenRuler Tango ([GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/))

[1]: https://github.com/DTOcean/dtocean/tree/next/packages/dtocean-core
