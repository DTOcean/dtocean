# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

<!-- version list -->

## v4.0.1 (2026-04-21)

### Bug Fixes

- Allow partially defined records ([#73](https://github.com/DTOcean/dtocean/pull/73),
  [`0b9363d`](https://github.com/DTOcean/dtocean/commit/0b9363d93acf87d1ae7b0ba7580cbfc1abe9e110))


## v4.0.0 (2026-04-21)

### Features

- Reimplement dtocean-economics ([#68](https://github.com/DTOcean/dtocean/pull/68),
  [`8df626c`](https://github.com/DTOcean/dtocean/commit/8df626cfa2a4b922d6163de1eff475bb8eb5f239))


## [2.0.0] - 2019-03-07

### Added

- Added main function which takes three dataframes, one for CAPEX, OPEX, and
  energy plus the discount rate and returns a dictionary of results.
- Added a preprocessing module which provides functions for preparing the
  required dataframes and for calculating estimates to the inputs.

### Changed

- Reorganised the functions module to undertake all dataframe manipulation
  work. The main function just collects any valid results.
- Now considers multiple series for energy and OPEX, as per changes in
  the dtocean-maintenance module. Returns summed, discounted values and LCOE
  calculations for each series.

## [1.0.0] - 2017-01-05

### Added

- Initial import of dtocean-economics from SETIS.
