# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.11.1] - 2021-10-15

### Changed

-   Set minimum pandas version to 0.21 to ensure than read_excel without
    sheet_name=None works consistently.
-   Remove conda version pin

## [0.11.0] - 2021-10-12

### Added

-   Added the ability to import simulations from one DataPool into another,
    with the Controller.import_simulation method. If a DataPool entry with
    matching value already exists in the destination pool, the new simulation
    uses that entry rather than create new one.
-   Added the ability to remove simulations from a DataPool with the
    Controller.remove_simulation method.
-   Structure subclasses can now implement an equals method to determine if
    data values are equal.

### Changed

-   When creating new simulations with the Controller class, contiguous data
    states with no label are compacted into a single state.

## [0.10.2] - 2019-07-08

### Added

-   Added test of xl_to_data_yaml

### Fixed

-   Fixed incorrect use of Dumper class in yaml.safe_dump in xl_to_data_yaml.

## [0.10.1] -   2019-07-08

### Changed

-   Added Loader and Dumper arguments to pyyaml calls as required by pyyaml 
    version 5.1 to improve safety.

## [0.10.0] -   2019-03-04

### Added

-   Add gitignore.
-   Add change log.
-   Add Database.execute_transaction method which will commit a query immediately
    without returning results.
-   Add Sequencer.refresh_interfaces and Hub.refresh_interface to replace
    interfaces in Hubs. Useful if interfaces have gone stale after saving.
-   Add create_pool_subset method to DataStorage class. Given a pool and 
    datastate, this creates a new pool and datastate containing just the variables
    in the datastate.
-   Added create_merged_state method to the Loader class. By default, this
    generates a merged pseudo state from a given simulation unless the simulation
    already has one stored.
-   Added compatibility for loading pandas data from version prior to 0.20 when
    using version 0.20 or greater.
-   Interfaces which do not import properly can now be allowed to skip if
    the warn_import flag is set in Socket.discover_interfaces or Sequencer.
-   Added conda requirements file for developers that doesn't include any DTOcean
    packages (requirements-conda-dev.txt).
-   Added test module, which contains SPT interface example, which as been added
    to the README.
    
### Changed

-   For pipelines, changed labelling of inputs for one interface that appear in a
    previous interface to say "overwritten" rather than "unavailable".
-   In DataStorage._convert_box_to_data will catch errors and pass with a warning
    when unpickling, if the warn_unpickle flag is True.
-   In DataStorage._convert_data_to_box will catch errors and pass with a warning
    when saving, if the warn_save flag is True.
-   In DataStorage._make_data allow data not in the data catalogue to pass with a
    warning if the warn_missing flag is True.
-   Modify add_datastate in the Controller class so that it can take Data objects
    as the variable values, if the use_objects flag is set to True.
-   Updated API for pandas.read_excel
-   Moved the add_datastate method from the Controller to the Loader class.
    
### Fixed
    
-   Removed unnecessary psycopg2 import
-   Fixed bug in FileInterface.check_path
-   Ensure SerialBox is replaced if encountering unknown data identifier when
    deserializing a data pool.
-   Fixed bug for Hub.get_next_scheduled when no interfaces are scheduled. Now
    returns None in this case.

## [0.9.1] - 2017-01-04

### Added

-   Initial import of aneris from SETIS.
