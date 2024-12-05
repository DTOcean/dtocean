# polite

Easy functions for paths, logging and configuration files.

\* For python 2.7 only.

## Installation

Installation and development of polite uses the [Poetry](
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
