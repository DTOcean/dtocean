# mdo-engine

mdo-engine provides data management, coupling between arbitrary sources (such as
files, databases, python packages, etc.) and execution ordering.

It is the framework on which [dtocean-core](https://github.com/DTOcean/dtocean-core) is built.

## Installation

Installation and development of mdo-engine uses the
[Poetry](https://python-poetry.org/) dependency manager. Poetry must be
installed and available on the command line.

To install:

```
$ poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```
$ poetry install --with test
```

Run the tests:

```
$ poetry run pytest
```

## Usage

### Example

An example of using mdo-engine to read data from a DataWell SPT file interface,
store the data using Simulation and DataPool objects, and then retrieve the
data using its specified data structure.

All the setup for this example is in the mdo_engine.test module of the source code.
The example SPT file can be found in the `mdo_engine\\tests\\data` directory.

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

### Command Line Tools

A utility is provided to convert DTOcean data description specifications (DDS)
files saved in MS Excel format to native yaml format. To get help:

```
$ bootstrap-dds -h
```

A seconds utility is provided to merge two DDS files in Excel format. This can
be useful when merging files in a version-control system. To get help:

```
$ xl_merge -h
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

See [this blog post](https://www.dataonlygreater.com/blog/post/dtocean-development-change-management/)
for information regarding development of the DTOcean ecosystem.

Please make sure to update tests as appropriate.

## Credits

This package was initially created as part of the [EU DTOcean project](https://cordis.europa.eu/project/id/608597)
by Mathew Topper at [TECNALIA](https://www.tecnalia.com).

It is now maintained by Mathew Topper at [Data Only Greater](https://www.dataonlygreater.com/).

## License

[MIT](https://choosealicense.com/licenses/mit/)
