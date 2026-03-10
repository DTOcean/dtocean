# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

<!-- version list -->

## v4.0.0 (2026-03-10)

### Features

- Release version 4
  ([`71138d3`](https://github.com/DTOcean/dtocean/commit/71138d35971d931370d91b3898763a5b954e7935))


## v4.0.0.dev0 (2026-03-06)

### Added

- Support Python versions 3.12 to 3.14
- Added size hints to delegates to allow space for editor buttons

## Changed

- Moved pandas table editor code to pandas submodule
- Supports pandas>=3.0.1 and numpy>=2.3.5

### Removed

- Remove support for Python version 2.7
- Remove support for PyQT
- Removed backup error dialogue provided by easygui package

## v0.10.1 - 2022-04-12

### Changed

- Use the appveyor configuration file as the single source for the version
  number.

### Removed

- Removed `__build__` and `__version__` dunders.

### Fixed

- Fixed minimum pandas dependency version.
- Fixed codacy configuration.

## v0.10.0 - 2019-03-12

### Added

- Added change log.
- Added CI files
- Added python-magic as a dependency.
- Added pagination to DataFrameModel to accelerate loading times.

### Removed

- Removed unused ui module (which contained a copy of easygui) and german
  translations.
- Removed packaged libmagic library due to version conflicts.

### Fixed

- Fixed incorrect use of Pandas ix method which read wrong table rows.
- Fixed reference to pandasqt in MANIFEST.in which caused crash.
- Fixed various bugs with use of QVariant v2 API, which is not default for
  Python 2.
- Fixed bugs with comparison of QStrings to Python strings.
- Fixed incorrect format (python 3) for validator return value in remove
  column dialog of a DataTable widget.
- Fixed various depreciated pandas API issues.

## v0.9.0 - 2017-02-23

### Added

- Initial import of pandas-qt from SETIS.

### Changed

- Changed package name to dtocean-qt.
