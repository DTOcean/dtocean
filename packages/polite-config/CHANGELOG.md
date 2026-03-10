# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

<!-- version list -->

## v3.0.0 (2026-03-10)

### Features

- Release version 3
  ([`fef02d9`](https://github.com/DTOcean/dtocean/commit/fef02d95eb1c4cb8f170e6416a5dde60afd4ef1a))


## v3.0.0.dev0 (2026-03-06)

### Added

- Support Python versions 3.12 to 3.14
- Added archive extraction tools (extract_tar, extract_zip)
- Added download retry for online archives and ability to redirect retry
  messages (defaults to stdout)
- Allow prefix path to be set for logging file handlers (e.g.
  Logger.configure_logger method)

### Changed

- Renamed package from polite to polite-config
- Changed path handling to Pathlib - xxxDirectory classes now named xxxPath
- Renamed Logger.add_named_logger to get_named_logger

### Removed

- Remove support for Python version 2.7
- Remove abstractclassmethod definition as its now in standard library

## v0.10.3 - 2022-07-14

### Changed

- Made EtcDirectory guess the path based on the system architecture only.
  It won't raise an error now if it's not found.

## v0.10.2 - 2022-07-13

### Added

- Added EtcDirectory class to the paths module for locating the Python
  distribution's etc directory.

## v0.10.1 - 2019-07-08

### Changed

- Added Loader and Dumper arguments to pyyaml calls as required by pyyaml
  version 5.1 to improve safety.

## v0.10.0 - 2019-03-01

### Added

- Added dummy logging configuration file to config/logging.yaml and added
  usage example to README.
- Added Directory.list_files method to list the files in a directory if it
  exists.
- Added DirectoryMap.copy_all and DirectoryMap.safe_copy_all to copy all files
  in the source directory to the target directory.
- Directory objects now returns their path when printed.

### Changed

- Made Logger.configure_logger require the configuration dictionary as an
  input.

### Fixed

- Ensured that the target directory exists when calling ReadYAML.write().

## v0.9.0 - 2017-01-04

### Added

- Initial import of dtocean-gui from SETIS.
