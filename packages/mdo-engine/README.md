[![mdo-engine actions](https://github.com/DTOcean/dtocean/actions/workflows/test-mdo-engine.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-mdo-engine.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=mdo-engine)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=mdo-engine)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mdo-engine)

# mdo-engine

mdo-engine provides data management, coupling between arbitrary sources (such
as files, databases, python packages, etc.) and execution ordering. It is the
framework on which [dtocean-core](https://pypi.org/project/dtocean-core/) is
built.

Part of the [DTOcean](https://github.com/DTOcean/dtocean) suite of tools.

## Installation

```sh
pip install mdo-engine
```

## Usage

### Example

An example of using mdo-engine to read data from a DataWell SPT file interface,
store the data using Simulation and DataPool objects, and then retrieve the
data using its specified data structure.

All the setup for this example is in the mdo_engine.test module of the source code.
The example SPT file can be found in the `mdo_engine/tests/data` directory.

First, look for interfaces that are subclasses of FileInterface in the
mdo_engine.test.interfaces module:

```python
>>> from mdo_engine.control.sockets import NamedSocket
>>> import mdo_engine.test.interfaces as interfaces

>>> interfacer = NamedSocket("FileInterface")
>>> interfacer.discover_interfaces(interfaces)
>>> interfacer.get_interface_names()
{'Datawell SPT File': 'SPTInterface'}
```

Load the SPTInterface interface and see what file types it can load:

```python
>>> file_interface = interfacer.get_interface_object('SPTInterface')
>>> file_interface.get_valid_extensions()
['.spt']
```

See which variables the interface can provide:

```python
>>> output_variables = file_interface.get_outputs()
>>> output_variables
['site:wave:dir',
 'site:wave:spread',
 'site:wave:skewness',
 'site:wave:kurtosis',
 'site:wave:freqs',
 'site:wave:PSD1D',
 'site:wave:Hm0',
 'site:wave:Tz']
```

Get the data from the test SPT file:

```python
>>> file_interface.set_file_path(test_spectrum_30min.spt)
>>> file_interface.connect()
```

Create a data catalogue and read the defined structures and meta data for each
variable:

```python
>>> from mdo_engine.control.data import DataValidation
>>> from mdo_engine.entity.data import DataCatalog

>>> catalog = DataCatalog()
>>> validation = DataValidation(meta_cls=data.MyMetaData)
>>> validation.update_data_catalog_from_definitions(catalog,
                                                    data)
```

Check which variables in the interface are defined in the data catalogue:

```python
>>> valid_variables = validation.get_valid_variables(catalog, output_variables)
>>> valid_variables
['site:wave:dir', 'site:wave:PSD1D', 'site:wave:freqs']
```

Collect the raw data for the valid variables:

```python
>>> raw_data = []

>>> for variable in valid_variables:
>>>     raw_data.append(file_interface.get_data(variable))
```

Create DataPool, Simulation and Loader objects and store the collected data:

```python
>>> from mdo_engine.control.data import DataStorage
>>> from mdo_engine.control.simulation import Loader
>>> from mdo_engine.entity import Simulation
>>> from mdo_engine.entity.data import DataPool

>>> pool = DataPool()
>>> simulation = Simulation("Hello World!")
>>> data_store = DataStorage(data)
>>> loader = Loader(data_store)

>>> loader.add_datastate(pool,
...                      simulation,
...                      None,
...                      catalog,
...                      valid_variables,
...                      raw_data)
```

Retrieved variables are now pandas Series objects, as defined in the data
catalogue:

```python
>>> freqs = loader.get_data_value(pool,
...                               simulation,
...                               'site:wave:freqs')
>>> type(freqs)
pandas.core.series.Series
```

## Development

Development of mdo-engine uses the [Poetry](https://python-poetry.org/)
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

Database integration tests are available upon the installation of the [DTOcean
database](https://github.com/DTOcean/dtocean-database-next). Once the database
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

Run the tests:

```sh
poetry run pytest
```

To include the database tests (with example values):

```sh
poetry run pytest --postgresql-password="example" --postgresql-path="/path/to/the/database/setup/files"
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

## Contributing

Please see the [dtocean](https://github.com/DTOcean/dtocean) GitHub repository
for contributing guidelines.

## Credits

This package was initially created as part of the [EU DTOcean project](https://cordis.europa.eu/project/id/608597)
by Mathew Topper at [TECNALIA](https://www.tecnalia.com).

It is now maintained by Mathew Topper at [Data Only Greater](https://www.dataonlygreater.com/).

## License

[MIT](https://choosealicense.com/licenses/mit/)
