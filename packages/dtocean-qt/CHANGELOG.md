# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.10.1] - 2022-04-12

### Changed

-   Use the appveyor configuration file as the single source for the version
    number.

### Removed

-   Removed `__build__` and `__version__` dunders.

### Fixed

-   Fixed minimum pandas dependency version.
-   Fixed codacy configuration.

## [0.10.0] - 2019-03-12

### Added

-   Added change log.
-   Added CI files
-   Added python-magic as a dependency.
-   Added pagination to DataFrameModel to accelerate loading times.
  
### Removed

-   Removed unused ui module (which contained a copy of easygui) and german
    translations.
-   Removed packaged libmagic library due to version conflicts.

### Fixed

-   Fixed incorrect use of Pandas ix method which read wrong table rows.
-   Fixed reference to pandasqt in MANIFEST.in which caused crash.
-   Fixed various bugs with use of QVariant v2 API, which is not default for
    Python 2.
-   Fixed bugs with comparison of QStrings to Python strings.
-   Fixed incorrect format (python 3) for validator return value in remove 
    column dialog of a DataTable widget.
-   Fixed various depreciated pandas API issues.

## [0.9.0] - 2017-02-23

### Added

-   Initial import of pandas-qt from SETIS.

### Changed

-   Changed package name to dtocean-qt.
