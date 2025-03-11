[![dtocean-hydrodynamics actions](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-hydrodynamics.yml/badge.svg?branch=next)](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-hydrodynamics.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-hydrodynamics)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-hydrodynamics)

# dtocean-hydrodynamics

This package provides the Hydrodynamics design module for the DTOcean tools.
It can calculate the energy output of arrays of fixed or floating wave or tidal
ocean energy converters, including the effect of interactions. It can optimise
the position of the devices for maximum energy yield, constrained by the given
environment.

## Installation

Installation and development ofdtocean-hydrodynamics uses the
[Poetry](https://python-poetry.org/) dependency manager. Poetry must be
installed and available on the command line.

To install:

```
$ poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```sh
$ poetry install --with test
```

Run the tests:

```sh
$ poetry run pytest
```

### Data Files

When installing from source, the DTOcean data files must also be installed.
They can be downloaded and installed using the `dtocean-hydro` command from the
command line (note that an internet connection is required):

```sh
$ dtocean-hydro init
```

## Usage

### Examples

Example scripts are available in the "examples" folder of the source code.

For tidal energy converters:

```sh
$ cd examples
$ python tidal_fixed_layout.py
```

For wave energy converters:

```sh
$ cd examples
$ python wave_fixed_layout.py
```

### Command Line Tools

A graphical user interface to the WEC analysis tool is provided. This tool is a
required pre-processing step for analysing the interactions of wave energy
converters. To get help:

```sh
$ dtocean-wec -h
```

## Credits

This package was initially created as part of the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by:

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
