# DTOcean Documentation

## Compile Instructions

The docs are written using the [Sphinx](https://www.sphinx-doc.org/en/master/)
documentation generator. The [Poetry](https://python-poetry.org/)
dependency manager is used to install Sphinx and additional plugins. Poetry
must be installed and available on the command line.

To install Sphinx run the following from the root directory:

```console
poetry install --only docs
```

### Testing the Current Branch

The documentation for the current branch can be built locally for inspection
prior to publishing. They are built in the `docs/_build` directory. Note,
unlike the final documentation, version tags and other branches will not be
available.

To test the current branch from the root directory:

```console
poetry run sphinx-build -a -W --keep-going -b html docs _build/html
```

The front page of the docs can be accessed at `_build/html/index.html`.

### Building Final Version Locally

The final documentation can be built locally for inspection prior to
publishing. They are built in the `docs/_build` directory. Note, docs are built
from the remote so only pushed changes on branches will be shown. To build the
docs use the following command from the root directory:

```console
poetry run sphinx-multiversion -a -W --keep-going docs _build/html
```

The front page of the docs can be accessed at `_build/html/next/index.html`.

## License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
