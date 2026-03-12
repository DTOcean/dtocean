# Contributing to DTOcean

This page describes the structure of the DTOcean monorepo, the tools used to
manage it and how you can contribute to the project.

## Repository Structure

This repository is structured as a monorepo, in that all of the individual
packages that make up the DTOcean suite of tools are all stored in a single
git repo. Details of the files and folders within the repository are given
in the tables below.

### Top-Level Files

The table below describes the purposes of the files found at the root level of
the repository.

| File            | Purpose                                                       |
| --------------- | ------------------------------------------------------------- |
| .codecov.yml    | Configuration for the [Codecov] test coverage service         |
| .gitattributes  | git attributes for files, used mainly for [LFS] configuration |
| .gitignore      | Lists files to be ignored (globally) by git                   |
| CHANGELOG.md    | A record of changes at root level or for docs[^1]             |
| CONTRIBUTING.md | This document                                                 |
| poetry.lock     | Global (and only tracked) [Poetry] lock file                  |
| pyproject.toml  | Global configuration file                                     |
| README.md       | Top level README[^2]                                          |

### Top-Level Folders

The table below describes the contents of the folders found at the root level
of the repository.

| Folder   | Purpose                                                     |
| -------- | ----------------------------------------------------------- |
| .github  | GitHub configuration files including Actions workflows      |
| .vscode  | Visual Studio Code workspace settings                       |
| docs     | Global documentation source in [Sphinx] format              |
| images   | Assets (e.g. images) for use in the top level README        |
| packages | Folders containing the Python packages that make up DTOcean |
| scripts  | Top level Python scripts, e.g., version calculation         |

### Package Folders

The table below describes the contents of the sub-folders found in the
`packages` folder.

| Folder                | Purpose                                                          |
| --------------------- | ---------------------------------------------------------------- |
| dtocean               | Meta package for installing the whole DTOcean suite              |
| dtocean-app           | Graphical representation of the dtocean-core functionality       |
| dtocean-core          | Main orchestration and data management module                    |
| dtocean-docs          | Provides an offline copy of the global documentation             |
| dtocean-dummy-module  | Basic engineering assessment module for testing mdo-engine       |
| dtocean-hydrodynamics | Device positioning and mechanical power calculation module       |
| dtocean-qt            | Support module providing specialised QT6 widgets for dtocean-app |
| mdo-engine            | General data management, execution ordering and plugin framework |
| polite-config         | Helper utilities for setting up logging, config files, etc.      |
| dtocean-economics     | Economic assessment module[^3]                                   |
| dtocean-electrical    | Electrical network design module[^3]                             |
| dtocean-environment   | Environmental impact assessment module[^3]                       |
| dtocean-installation  | Farm installation logistics design module[^3]                    |
| dtocean-logistics     | Support module used by other logistics modules[^3]               |
| dtocean-maintenance   | Operations and maintenance logistics design module[^3]           |
| dtocean-moorings      | Station keeping / foundation design module[^3]                   |
| dtocean-reliability   | Farm system reliability assessment module[^3]                    |

### Files and Folders in a Package

The table below describes the files and folder consistently found in a package
folder.

| File / Folder          | Purpose                                                    |
| ---------------------- | ---------------------------------------------------------- |
| .vsode                 | Visual Studio Code workspace settings for the package      |
| src                    | Python source code                                         |
| tests                  | [pytest] test code                                         |
| .gitignore             | Lists files to be ignored by git within the package folder |
| CHANGELOG.md           | A record of changes for the package                        |
| LICENSES / LICENSE.txt | License(s) governing the use of the package code           |
| pyproject.toml         | Configuration file for the package                         |
| README.md              | Package specific README                                    |

Other folders containing examples (with names such as `examples`, `notebooks`,
etc.) or additional data for test or examples may or may not be included within
the package folders.

[^1]: Changes to packages are recorded in their own change logs

[^2]: Also used as the README for the `dtocean` meta package

[^3]: Not yet implemented in this version but planned (stub package)

## Tools

### Build

The [Poetry](https://python-poetry.org/) package manager is used to manage
package dependencies and builds. The [poetry-monoranger-plugin] Poetry plugin
ensures dependency compatibility between the all the packages and to replace
path dependencies (where one DTOcean package depends on another) with concrete
version specifiers at build time. With poetry-monoranger-plugin installed and
enabled (for each package), the `poetry install` command will always install
all of the packages at once, as defined by the root level `pyproject.toml`
file. To ensure dependency compatibility between all of the packages, the
poetry-monoranger-plugin enforces a single global lock file (`poetry.lock`).

The `dtocean` package (`packages/dtocean`) also uses the root version
specification (as defined in the root `pyproject.toml` file) to set its own
version number. To do this automatically, the [poetry-dynamic-versioning]
Poetry plugin is used to dynamically set the version using the root
`pyproject.toml` file.

Note that for certain packages (dtocean-hydodynamics for instance), a custom
build script is required for certain bootstrapping steps (such as compiling a
Fortran module in the case of dtocean-hydodynamics). In these circumstances,
Poetry does an "isolates" build, pinned to the operating system and Python
version used to call the build. For this type of build, the
poetry-monoranger-plugin does not rewrite path dependencies, so this is
achieved instead by calling the `scripts/pre-build.py` script, created for this
task. This script will manually rewrite the path dependencies in the packages
`pyproject.toml` file. Importantly, do not commit (to git) any rewritten
dependencies if using the `pre-build.py` script locally.

### Release

Release numbering uses a mix of [semantic](https://semver.org/) and
[calendar](https://calver.org/) versioning schemes, with most of the DTOcean
packages using semantic versioning while the top-level project uses calendar
versioning, with the docs and `dtocean` meta package sharing the same. The
supporting repositories, such as [dtocean-examples], also tend to use calendar
versioning schemes.

Calculating the level of a new release and updating files accordingly, is done
using the [Python Semantic Release] (PSR) package. Python Semantic Release uses
git tags to determine when the last release of a package occurred, then
examines the commit history after that point to determine whether a version
bump is required and to what level. For dtocean, the [Conventional Commits]
convention is used to determine the version bump level required by each commit
since the last release. When the bump level is determined Python Semantic
Release will update the version in the `pyproject.toml`, update the
CHANGELOG.md files with changes since the last release, and create a tagged
commit for the new version.

#### Monorepo Support

Python Semantic Release has recently added [monorepo support], where each
package in the monorepo can define its own tag and scope format and path
specifications, in order to isolate commits to an individual package. The
`DTOceanCommitParser` class, defined in the `scripts/dtocean_commit_parser.py`
file, extends this functionality to provide more customisation for path
specifications than in the default parser. Two new configuration options are
added to the path filters:

1. **max_bump_level**: The maximum bump level that can be created from commits
   to files on the given path
2. **trigger_bump_level**: The bump level that must be achieved in order for
   commits to the files on the given path to be included

Using these options, packages with path dependencies can watch for changes to
the files in those dependencies and then bump their own version should a
significant version change (i.e. a breaking change) in the dependency occur.
The resulting update to the dependant package is limited to patch level, unless
significant changes to the dependant package have been made as well.

#### Calendar Versioning

In order for Python Semantic Release to be used with calendar versioning, a
patched interface is provided by the `scripts/calver.py` script. The can be
called with the same arguments as the main PSR CLI, for instance:

```sh
poetry run python scripts/calver.py version --no-commit --no-tag
```

The modification makes the version specification have year.month.PATCH format
and all (releasing) bump levels are considered equal. The PATCH number is
incremented for every release made within the same calendar month.

### Testing

Both unit and code quality tests are available for all packages. The unit tests
are written using the [pytest] framework, utilising various plugins. The
mdo-engine and dtocean-core packages also include tests that use the [DTOcean
database]. Once the database is running, the [pytest-postgresql] plugin can
create temporary copies of the database for running tests. Some additional
command line parameters are required to direct the tests at the database setup
files, as documented in the package README files.

Two types of code quality tests are available: firstly the [ruff] linter is
used to check for syntax and style issues and then [pyright] is used for static
type checking (typically with its "basic" mode).Both the unit and quality
tests can be run across multiple Python versions using [tox] and [tox-uv] ([uv]
is used to automatically install the Python interpreter). Again, see the
package README files for usage instructions.

During automated testing (see the [Automation](#automation) section), the
[pytest-cov] plugin is used in combination with the [Codecov] service to
measured and record the [code coverage] of the source code and how any changes
have affected it. The code coverage for each package (also a link to the
Codecov page) is published at the top of its README file.

### File Storage

This repository uses Git [LFS] for storing non-source rarely-changing files.
These are typically filtered by file extension, as defined in the root
`.gitattributes` file. It is important to remember to explicitly pull the
stored files (i.e. `git lfs pull`) should they be needed for a build, for
example.

GitHub has limited free LFS storage, so for very large file collections, the
[DVC] framework is used. This acts like Git LFS, expect that the external
storage location is customisable. This repository does not currently use DVC
but it is used in the [DTOcean database] and [dtocean-examples] repositories,
with AWS providing the storage backend.

### Documentation

The top level documentation (found in the `docs` directory) uses the [Sphinx]
documentation framework. Sphinx can be used to convert files written in
reStructuredText format into various hypermedia representations such as web
pages and PDFs. Plugins are used to extend the functionality of Sphinx. For
example, the [sphinx-multiversion] plugin is used to publish multiple versions
of the docs (e.g. branches / tags) at once. See the README in the `docs`
directory for further details.

### Automation

[GitHub Actions] is used to automate continuous integration/delivery (CI/CD)
workflows for DTOcean. In layman's terms, this means that on each commit to the
`main` branch the tests are run automatically on GitHub and, if they succeed,
any pending released (as defined by [Conventional Commits]) will be
automatically published. Additionally, if changes have been made to the
documentation, this will be published also. Tests are also be run automatically
on pull requests.

The tools described in the sections above are all used in the automation
process, along with some prepackaged actions such as the [PyPI publish GitHub
Action]. The GitHub Actions workflows for this repository are defined in the
`.github/workflows` folder. Some "composite" workflows (defining a series of
step reused by other workflows) are found in the `.github/actions` folder.

## Setting up

This section describes setting up the entire DTOcean suite for development.
See the README files of the individual packages (in the `packages` folder) for
instructions regarding their usage and testing.

### Source Code

1. [One time] Install [Poetry]
1. [One time] Install Poetry plugins:

   ```sh
   poetry self add poetry-monoranger-plugin
   poetry self add poetry_dynamic_versioning
   ```

1. Create a Python compatible environment (see the [README](/README.md) for
   supported versions). This can be achieved using [pyenv] on Linux or
   [Miniforge] on Windows.

1. Move to the repo root directory:

   ```sh
   cd /path/to/dtocean
   ```

1. Install all packages and dependencies (this can be customised as required):

   ```sh
   poetry install --with test --with audit --with docs --with release --with tox
   ```

   At this stage dtocean should available as an editable install. This can be
   tested by calling the CLI, e.g.

   ```sh
   poetry run dtocean -h
   ```

   (Note that for conda environments (created using [Miniforge], for instance),
   the `poetry run` part is not necessary.)

1. Finally, make sure that all necessary data files have been downloaded
   (requires an internet connection):

   ```sh
   poetry run dtocean init
   ```

### Database

To develop or test integration with the DTOcean database see the installation
instructions in the [DTOcean database] repository.

### Visual Studio Code

Some [Visual Studio Code] (VSCode) configuration is set at the root and package
level (allowing for package folders to be opened independently). This allows
VSCode to show issues that might arise during [code quality tests](#testing)
and to help with automatic formatting. To use these features the following
plugins should be installed:

- [prettier-vscode](https://github.com/prettier/prettier-vscode)
- [pylance](https://github.com/microsoft/pylance-release)
- [vscode-python](https://github.com/Microsoft/vscode-python)
- [ruff-vscode](https://github.com/astral-sh/ruff-vscode)

## Contributing

Contributions are gratefully received and should be offered using a [pull
request].

For your convenience, consider adding your work to a new feature [branch]
created from a [fork] of this repository (rather than developing on the fork's
`main` branch). Once the new code has been accepted into the upstream (this)
repository, you can then delete the feature branch and pull the updated `main`
branch without having to delete your fork.

To ensure that contributions meet the standards required for inclusion, please:

- Write tests for all new code (coverage should not fall)
- Ensure all tests pass
- Do not commit any extraneous files (such as environment config or lock files
  below the root level)
- Update/create any relevant documentation
- Write a sensible description of the changes in the pull request (or reference
  an existing [issue])

**A NOTE ON AI: please do not offer contributions that have been predominantly
created using AI (i.e. using vibe/agentic coding). This is because such code
[may not be copyrightable](https://eurekasoft.com/blog/aigenerated-code-and-copyright-who-owns-aiwritten-software).**

[Codecov]: https://about.codecov.io/
[LFS]: https://git-lfs.com/
[Poetry]: https://python-poetry.org/
[Sphinx]: https://www.sphinx-doc.org/
[pytest]: https://docs.pytest.org/
[poetry-monoranger-plugin]: https://github.com/ag14774/poetry-monoranger-plugin
[poetry-dynamic-versioning]: https://github.com/mtkennerly/poetry-dynamic-versioning
[dtocean-examples]: https://github.com/DTOcean/dtocean-examples
[DTOcean database]: https://github.com/DTOcean/dtocean-database
[Python Semantic Release]: https://python-semantic-release.readthedocs.io
[monorepo support]: https://python-semantic-release.readthedocs.io/en/latest/configuration/configuration-guides/monorepos.html
[Conventional Commits]: https://www.conventionalcommits.org/
[pytest-postgresql]: https://github.com/dbfixtures/pytest-postgresql
[tox]: https://tox.wiki/
[tox-uv]: https://github.com/tox-dev/tox-uv
[uv]: https://docs.astral.sh/uv/
[pytest-cov]: https://pytest-cov.readthedocs.io/
[code coverage]: https://en.wikipedia.org/wiki/Code_coverage
[ruff]: https://docs.astral.sh/ruff/
[pyright]: https://github.com/microsoft/pyright
[DVC]: https://dvc.org/
[sphinx-multiversion]: https://github.com/sphinx-contrib/multiversion
[GitHub Actions]: https://docs.github.com/en/actions
[PyPI publish GitHub Action]: https://github.com/pypa/gh-action-pypi-publish
[pyenv]: https://github.com/pyenv/pyenv
[Miniforge]: https://github.com/conda-forge/miniforge
[Visual Studio Code]: https://code.visualstudio.com/
[pull request]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
[branch]: https://www.w3schools.com/git/git_branch.asp
[fork]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks
[issue]: https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
