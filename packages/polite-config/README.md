# polite-config

Easy functions for paths, logging and configuration files.

## Installation

Installation and development of polite-config uses the [Poetry](https://python-poetry.org/)
dependency manager. Poetry must be installed and available on the command line.

To install:

```console
poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```console
poetry install --with test
```

Run the tests:

```console
poetry run pytest
```

## Usage

An example of setting up [logging](https://docs.python.org/3/library/logging.html)
using a user-specific [yaml configuration file](https://docs.python.org/3/howto/logging.html#configuring-logging).

Copy the default logging file from the module source code to the user's data
directory (`C:\Users\<USERNAME>\AppData\Roaming\DTOcean\polite`):

```python
>>> from polite_config.paths import (DirectoryMap, ModPath, UserDataPath)

>>> objdir = ModPath("polite", "config")
>>> datadir = UserDataPath("polite", "DTOcean")
>>> dirmap = DirectoryMap(datadir, objdir)
>>> dirmap.copy_file("logging.yaml", overwrite=True)
>>> datadir.isfile("logging.yaml")
True
```

Use the copied configuration file to set up logging:

```python
>>> from polite_config.configuration import Logger

>>> log = Logger(datadir)
>>> log_config_dict = log.read()
>>> log.configure_logger(log_config_dict)
>>> logger = log.add_named_logger("polite")
>>> logger.info("Hello World")
INFO - polite - Hello World
```

Note that classes such as `ModPath` and `UserDataPath` are subclasses of
`pathlib.Path`.

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
