# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

<!-- version list -->

## v3.0.1 (2026-03-12)

### Bug Fixes

- Repair broken links
  ([`0ee2bc3`](https://github.com/DTOcean/dtocean/commit/0ee2bc357cf3be9455fc1043dc3a02eb12952db4))


## v3.0.0 (2026-03-10)

### Features

- Release version 3
  ([`2fe6ac1`](https://github.com/DTOcean/dtocean/commit/2fe6ac1c493dabca093f0cd738422dd17081e304))


## v3.0.0.dev0 (2026-03-06)

### Added

- Support Python versions 3.12 to 3.14
- Handle import errors in utilities.plugins.get_subclass_names_from_module
- Allow list of immutable classes in Structure to be extended
- Added PostGIS Database subclass to interface with geoalchemy2
- Added Sequencer.dump_hub and load_hub for conversion of Hub classes to and
  from JSON compatible dictionaries
- Added equality operator for DataPool class
- Added Controller.serialise_simulation and deserialise_simulation for
  converting between JSON compatible dictionaries
- Added abstract property "version" to Structure class for backwards compatible
  serialization

### Bug Fixes

- Don't include the superclass itself when discovering subclasses in
  utilities.plugins.get_subclass_names_from_module

### Changed

- Renamed package from aneris to mdo-engine
- Initiate Sequencer class with a sequence of interface modules rather than
  a single one
- Don't raise an error if a Database.close is called repeatedly
- DataStorage.serialise_pool now returns a JSON compatible dictionary
- DataStorage.deserialise_pool now accepts DataPool or a dictionary for its
  serial_pool argument
- Renamed utilities.database.call_stored_proceedure to call_function
- Paths are now always serialized in Posix format for cross platform
  compatibility

### Removed

- Remove support for Python version 2.7
- Removed DDS Excel sheet conversion utilities

## v0.11.1 - 2021-10-15

### Changed

- Set minimum pandas version to 0.21 to ensure than read_excel without
  sheet_name=None works consistently.
- Remove conda version pin

## v0.11.0 - 2021-10-12

### Added

- Added the ability to import simulations from one DataPool into another,
  with the Controller.import_simulation method. If a DataPool entry with
  matching value already exists in the destination pool, the new simulation
  uses that entry rather than create new one.
- Added the ability to remove simulations from a DataPool with the
  Controller.remove_simulation method.
- Structure subclasses can now implement an equals method to determine if
  data values are equal.

### Changed

- When creating new simulations with the Controller class, contiguous data
  states with no label are compacted into a single state.

## v0.10.2 - 2019-07-08

### Added

- Added test of xl_to_data_yaml

### Fixed

- Fixed incorrect use of Dumper class in yaml.safe_dump in xl_to_data_yaml.

## v0.10.1 - 2019-07-08

### Changed

- Added Loader and Dumper arguments to pyyaml calls as required by pyyaml
  version 5.1 to improve safety.

## v0.10.0 - 2019-03-04

### Added

- Add gitignore.
- Add change log.
- Add Database.execute_transaction method which will commit a query immediately
  without returning results.
- Add Sequencer.refresh_interfaces and Hub.refresh_interface to replace
  interfaces in Hubs. Useful if interfaces have gone stale after saving.
- Add create_pool_subset method to DataStorage class. Given a pool and
  datastate, this creates a new pool and datastate containing just the variables
  in the datastate.
- Added create_merged_state method to the Loader class. By default, this
  generates a merged pseudo state from a given simulation unless the simulation
  already has one stored.
- Added compatibility for loading pandas data from version prior to 0.20 when
  using version 0.20 or greater.
- Interfaces which do not import properly can now be allowed to skip if
  the warn_import flag is set in Socket.discover_interfaces or Sequencer.
- Added conda requirements file for developers that doesn't include any DTOcean
  packages (requirements-conda-dev.txt).
- Added test module, which contains SPT interface example, which as been added
  to the README.

### Changed

- For pipelines, changed labelling of inputs for one interface that appear in a
  previous interface to say "overwritten" rather than "unavailable".
- In DataStorage.\_convert_box_to_data will catch errors and pass with a warning
  when unpickling, if the warn_unpickle flag is True.
- In DataStorage.\_convert_data_to_box will catch errors and pass with a warning
  when saving, if the warn_save flag is True.
- In DataStorage.\_make_data allow data not in the data catalogue to pass with a
  warning if the warn_missing flag is True.
- Modify add_datastate in the Controller class so that it can take Data objects
  as the variable values, if the use_objects flag is set to True.
- Updated API for pandas.read_excel
- Moved the add_datastate method from the Controller to the Loader class.

### Fixed

- Removed unnecessary psycopg2 import
- Fixed bug in FileInterface.check_path
- Ensure SerialBox is replaced if encountering unknown data identifier when
  deserializing a data pool.
- Fixed bug for Hub.get_next_scheduled when no interfaces are scheduled. Now
  returns None in this case.

## v0.9.1 - 2017-01-04

### Added

- Initial import of aneris from SETIS.
