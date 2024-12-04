[![appveyor](https://ci.appveyor.com/api/projects/status/github/DTOcean/polite?branch=master&svg=true)](https://ci.appveyor.com/project/DTOcean/polite)
[![codecov](https://codecov.io/gh/DTOcean/polite/branch/master/graph/badge.svg)](https://codecov.io/gh/DTOcean/polite)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1a2d478b95544457b22fdf444b4a8b6f)](https://www.codacy.com/gh/DTOcean/polite/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DTOcean/polite&amp;utm_campaign=Badge_Grade)
[![release](https://img.shields.io/github/release/DTOcean/polite.svg)](https://github.com/DTOcean/polite/releases/latest)

# polite

Easy functions for paths, logging and configuration files.

\* For python 2.7 only.

## Installation

Installation and development of polite uses the [Anaconda Distribution](
https://www.anaconda.com/distribution/) (Python 2.7)

### Conda Package

To install:

```
$ conda install -c dataonlygreater polite
```

### Source Code

Conda can be used to install dependencies into a dedicated environment from
the source code root directory:

```
$ conda create -n _polite python=2.7 pip
```

Now activate the environment and use conda and pip to install the source code:

```
$ conda activate _polite
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
$ conda activate _polite
```

Install pytest to the environment (one time only):

```
$ conda install -y mock pytest pytest-mock
```

Run the tests:

``` 
$ pytest tests
```

### Uninstall

To uninstall the conda package:

```
$ conda remove polite
```

To uninstall the source code and its conda environment:

```
$ conda remove --name _polite --all
```

## Usage

An example of setting up [logging](
https://docs.python.org/2/library/logging.html) using a user-specific [yaml 
configuration file](https://docs.python.org/2/howto/logging.html#configuring-logging).

Copy the default logging file from the module source code to the user's data
directory (`C:\Users\<USERNAME>\AppData\Roaming\DTOcean\polite`):

```python
>>> from polite.paths import (DirectoryMap,
                              ObjDirectory,
                              UserDataDirectory)

>>> objdir = ObjDirectory("polite", "config")
>>> datadir = UserDataDirectory("polite", "DTOcean")
>>> dirmap = DirectoryMap(datadir, objdir)
>>> dirmap.copy_file("logging.yaml", overwrite=True)
>>> datadir.isfile("logging.yaml")
True
```

Use the copied configuration file to set up logging:

```python
>>> from polite.configuration import Logger

>>> log = Logger(datadir)
>>> log_config_dict = log.read()
>>> log.configure_logger(log_config_dict)
>>> logger = log.add_named_logger("polite")
>>> logger.info("Hello World")
INFO - polite - Hello World
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

See [this blog post](https://www.dataonlygreater.com/latest/professional/2017/03/09/dtocean-development-change-management/)
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
