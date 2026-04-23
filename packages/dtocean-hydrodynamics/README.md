[![dtocean-hydrodynamics actions](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-hydrodynamics.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-hydrodynamics.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-hydrodynamics)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-hydrodynamics)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dtocean-hydrodynamics)](https://www.python.org/downloads/)
[![PyPI - Version](https://img.shields.io/pypi/v/dtocean-hydrodynamics)](https://pypi.org/project/dtocean-hydrodynamics/)

# dtocean-hydrodynamics

This package provides the Hydrodynamics design module for the DTOcean tools.
It can calculate the energy output of arrays of fixed or floating wave or tidal
ocean energy converters, including the effect of interactions. It can optimise
the position of the devices for maximum energy yield, constrained by the given
environment.

Part of the [DTOcean](https://github.com/DTOcean/dtocean) suite of tools.

## Installation

```sh
pip install dtocean-hydrodynamics
```

After installation, ensure that all the necessary data files are downloaded
using the following command:

```sh
dtocean-hydro init
```

Alternatively, if [dtocean-core] is installed, use:

```sh
dtocean init
```

## Usage

### Examples

Example scripts are available in the `examples` folder of the source code.

For tidal energy converters:

```sh
cd examples
python tidal_fixed_layout.py
```

For wave energy converters:

```sh
cd examples
python wave_fixed_layout.py
```

### Command Line Tools

A graphical user interface to the WEC analysis tool is provided. This tool is a
required pre-processing step for analysing the interactions of wave energy
converters. To get help:

```sh
dtocean-wec -h
```

Alternatively, if [dtocean-core] is installed, the GUI can be accessed using:

```sh
dtocean hydrodynamics wec
```

## Documentation

Video tutorials describing how to use the WEC simulator tool can be found on
the Data Only Greater [YouTube
Channel](https://www.youtube.com/@dataonlygreater).

## Development

Development of dtocean-hydrodynamics uses the
[Poetry](https://python-poetry.org/) dependency manager. Poetry must be
installed and available on the command line.

To install:

```sh
poetry install
```

After installation, ensure that all the necessary data files are downloaded
using the following command:

```sh
dtocean-hydro init
```

Alternatively, if [dtocean-core] is installed, use:

```sh
dtocean init
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```sh
poetry install --with test
```

Additional tests are available for the plugins to [dtocean-core] and
[dtocean-app]. Enable these tests by installing the `test-extras` group:

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
install:

```sh
poetry install --with test --with test-extras --with audit --with tox
```

To run the tests:

```sh
poetry run tox
```

## Contributing

Please see the [dtocean](https://github.com/DTOcean/dtocean) GitHub repository
for contributing guidelines.

## Credits

This package was initially created as part of the [EU DTOcean project](
https://cordis.europa.eu/project/id/608597) by:

* Francesco Ferri at [Aalborg University](https://www.en.aau.dk/)
* Pau Mercade Ruiz at [Aalborg University](https://www.en.aau.dk/)
* Thomas Roc at IT Power (now [ITPEnergised](http://www.itpenergised.com/))
* Chris Chartrand at [Sandia National Labs](https://www.sandia.gov/)
* Jean-Francois Filipot at [France Energies Marines](https://www.france-energies-marines.org/)
* Rui Duarte at [France Energies Marines](https://www.france-energies-marines.org/)
* Mathew Topper at [TECNALIA](https://www.tecnalia.com)

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

[dtocean-app]: https://pypi.org/project/dtocean-app/
[dtocean-core]: https://pypi.org/project/dtocean-core/
