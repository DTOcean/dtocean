
[![docs actions](https://github.com/DTOcean/dtocean/actions/workflows/test-docs.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-docs.yml)

# DTOcean Documentation

## Installation

The docs are written using the [Sphinx](https://www.sphinx-doc.org/en/master/)
documentation generator. The [Poetry](https://python-poetry.org/)
dependency manager is used to install Sphinx and additional plugins. Poetry
must be installed and available on the command line.

To install Sphinx run the following from the root directory:

```sh
poetry install --only docs
```

If the docs are built from the git repository, the image files must first be
retrieved using git-lfs (ensure that [git-lfs](https://git-lfs.com/) is installed
first):

```sh
git lfs fetch --all
git lfs pull
```

## Live Preview

A live preview of the documentation for the current branch can be created
using the `sphinx-autobuild` command. From the root directory:

```sh
sphinx-autobuild docs _build/html
```

Using the default settings, the docs should be available to view at
<http://127.0.0.1:8000>.

## Testing

### Current Branch

The documentation for the current branch can be built locally for inspection
prior to publishing. They are built in the `docs/_build` directory. Note,
unlike the final documentation, version tags and other branches will not be
available.

To test the current branch from the root directory:

```sh
poetry run sphinx-build -a -W --keep-going -b html docs _build/html
```

The front page of the docs can be accessed at `_build/html/index.html`.

### Final Version

The final documentation can be built locally for inspection prior to
publishing. They are built in the `docs/_build` directory. Note, docs are built
from the remote so only pushed changes on branches will be shown. To build the
docs use the following command from the root directory:

```sh
poetry run sphinx-multiversion -a -W --keep-going docs _build/html
```

The front page of the docs can be accessed at `_build/html/main/index.html`.

## License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
