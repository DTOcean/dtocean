[![appveyor](https://ci.appveyor.com/api/projects/status/github/DTOcean/aneris?branch=master&svg=true)](https://ci.appveyor.com/project/DTOcean/aneris)
[![codecov](https://codecov.io/gh/DTOcean/aneris/branch/master/graph/badge.svg)](https://codecov.io/gh/DTOcean/aneris)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/31fbdbe9502b4985a6b8d4222fd13923)](https://www.codacy.com/gh/DTOcean/aneris/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DTOcean/aneris&amp;utm_campaign=Badge_Grade)
[![release](https://img.shields.io/github/release/DTOcean/aneris.svg)](https://github.com/DTOcean/aneris/releases/latest)

# aneris

Aneris provides data management, coupling between arbitrary sources (such as
files, databases, python packages, etc.) and execution ordering.

It is the framework on which [dtocean-core](
https://github.com/DTOcean/dtocean-core) is built.

\* For python 2.7 only.

## Installation

Installation and development of aneris uses the [Anaconda Distribution](
https://www.anaconda.com/distribution/) (Python 2.7)

### Conda Package

To install:

```
$ conda install -c defaults -c conda-forge -c dataonlygreater aneris
```

### Source Code

Conda can be used to install dependencies into a dedicated environment from
the source code root directory:

```
conda create -n _aneris python=2.7 pip
```

Activate the environment, then copy the `.condrc` file to store installation  
channels:

```
$ conda activate _aneris
$ copy .condarc %CONDA_PREFIX%
```

OR, if you're using Powershell:

```
$ conda activate _aneris
$ copy .condarc $env:CONDA_PREFIX
```

Install [polite](https://github.com/DTOcean/polite) into the environment. For 
example, if installing it from source:

```
$ cd \\path\\to\\polite
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

Finally, install aneris and its dependencies using conda and pip:

```
$ cd \\path\\to\\aneris
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

To deactivate the conda environment:

```
$ conda deactivate
```

### Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org).

If not already active, activate the conda environment set up in the [Source 
Code](#source-code) section:

```
$ conda activate _aneris
```

Install pytest to the environment (one time only):

```
$ conda install -y mock pytest pytest-mock
```

Optionally, you can also install [dtocean-dummy-module](https://github.com/DTOcean/dtocean-dummy-module)
for additional tests:

```
$ conda install -y dtocean-dummy-module mock pytest pytest-mock
```

Run the tests:

``` 
$ pytest tests
```

### Uninstall

To uninstall the conda package:

```
$ conda remove aneris
```

To uninstall the source code and its conda environment:

```
$ conda remove --name _aneris --all
```

## Usage

### Example

An example of using aneris to read data from a DataWell SPT file interface,
store the data using Simulation and DataPool objects, and then retrieve the
data using its specified data structure.

All the setup for this example is in the aneris.test module of the source code.
The example SPT file can be found in the `aneris\\tests\\data` directory.

First, look for interfaces that are subclasses of FileInterface in the
aneris.test.interfaces module:

```python
>>> from aneris.control.sockets import NamedSocket
>>> import aneris.test.interfaces as interfaces

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
>>> from aneris.control.data import DataValidation
>>> from aneris.entity.data import DataCatalog

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
>>> from aneris.control.data import DataStorage
>>> from aneris.control.simulation import Loader
>>> from aneris.entity import Simulation
>>> from aneris.entity.data import DataPool

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

See [this blog post](
https://www.dataonlygreater.com/latest/professional/2017/03/09/dtocean-development-change-management/)
for information regarding development of the DTOcean ecosystem.

Please make sure to update tests as appropriate.

## Credits

This package was initially created as part of the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by Mathew Topper at
[TECNALIA](https://www.tecnalia.com).

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## License

[MIT](https://choosealicense.com/licenses/mit/)
