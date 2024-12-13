# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [3.0.2] - 2022-04-25

### Changed

-   The `AdvancedPosition.get_optimiser_status` method now returns a code in
    the range `[0, 2]`, with `0` meaning the status can not be determined, `1` 
    meaning the optimisation is complete and `2` meaning the optimisation is 
    incomplete.

## [3.0.1] - 2022-04-14

### Changed

-   The minimum version of the aneris dependency was set to 0.11.1 or greater.

## [3.0.0] - 2022-04-04

### Added

-   Added functions `rmtree_retry` and `remove_retry` which can keep retrying
    to remove directories or files if blocked by the OS and fail silently if
    necessary.
-   Types can now be defined for the columns of `DataTable` structures and 
    entries in `NumpyLineDict`, `CartesianDict`, `CartesianListDict` structures.
-   Added shapefile import and export for `Point`, `PointList` and `Polygon`
    structures.
-   Added UH-CMA-ES based parallel optimiser to `utils.optimiser` module.
-   Added global position optimising strategy (called "Advanced Positioning")
    that can position devices based on minimising or maximising any floating
    point variable. Experimental support for optimising the number of devices
    per cable string was also added.
-   Added ability to import a simulation from one project to another using the
    `Core.import_simulation` method. This intelligently updates the DataPool of
    the destination project, so that matching data in both projects is not
    duplicated. This is achieved by adding `equals` methods to a number of the
    data structures to test for equality.
-   Added ability to remove a simulation from a project using the
    `Core.remove_simulation` method. A `Project.remove_simulation` method was
    also added but this will not remove any orphaned data from the DataPool.
    Other `Project` methods were updated for the case of all sims being removed.
-   Add `auto_file` methods to `PointList` as `PointData`'s methods no longer
    covers it.
-   Added `raise_if_missing flag` to `Project.get_simulation_indexes` to allow
    missing titles to be ignored.
-   Provided legacy support for loading old strategies by adding a "version" key
    to the saved strategy dict and then converting from sim indexes to titles
    if the old strategy type is detected.
-   Added units of degrees to maximum cable lay gradient
    ("project.equipment_gradient_constraint").
-   Added CLI to allow execution of `.prj` files using the `dtocean-core` 
    command. Can run just the next scheduled module or all modules and then
    save results.
-   Added "options.use_max_thrust" variable to indicate if tidal turbines
    maximum thrust coefficient should be used for all calculations in the
    mooring module.
-   Added `to_project` method to the `Project` class for producing copies of the
    object.
-   Added `SpacingConstraintsTool` tool for checking hydrodynamics module
    distance constraints.
-   Added "options.tidal_use_all_steps" variable to allow calculation of the
    tidal hydrodynamics using all available time steps (i.e. this skips the
    tidal statistics calculation).
-   Added `file.utils.init_dir` function for creating a new directory or
    cleaning an existing directory, as required.
-   Added calculation of some LCOE variables, in the economics interface, if
    less than 3 data points are available.
-   Added `median` methods to `utils.stats.UniVariate` and
    `utils.stats.BiVariate` classes.
-   Added annotations to all polygons in array layout plots.
-   Added per sub-system outputs for the reliability module.
-   Added static cable per km reliability variables.
-   Added "project.apply_kfactors" variable to use k-factors in reliability
    calculation. Currently this means using per km reliability values for the
    static cables only.
-   Added "project.reliability_confidence" variable for setting the confidence
    level to be used in the reliability module calculations.
-   Added maximum and minimum limits on `SimpleData` structures. Fixes 
    https://github.com/DTOcean/dtocean/issues/10.
-   Added lifetime total cost variables as output from the economics interface.
-   Added `dump_config_hook` method to the `Strategy` class as a hook for
    modifying the stored config before dumping.
-   Added `utils.stats.get_standard_error` function to provide a standard
    error calculation. Used mostly for testing other stats calculations.

### Changed

-   The BoundariesInterface now includes the "site.projection" variable as a
    required input.
-   Stopped exporting data from module runs by default to avoid conflict when
    running in parallel.
-   Improved error message for TimeTable structure if input dict's DateTime key
    does not contain all `datetime.datetime` objects.
-   Increased strictness of type assignment in `SimpleData`, `SimpleList` and
    `SimpleDict` structures.
-   An error is now raised in the `XGridND` structure if it is used without
    subclassing.
-   `FileInputInterface` and `FileOutputInterface` interfaces now have access to
    variable meta data.
-   Modified `Project.get_simulation_titles` to take an `indexes` argument to
    only fetch titles of specific sim indices.
-   Now using simulation titles rather than indexes for Strategy simulation
    records. This avoids issues if simulation indexes change when sims are
    removed from a project (or potentially reordered).
-   Updated hydrodynamics interface for changes in dtocean-hydrodynamics. This
    included changing the bed roughness calculation for tidal simulation.
-   Removed y-label from `LineTable` structure plots.
-   Ensured structures with dictionary keys are sorted using natural sort.
-   Updated moorings interface for changes in dtocean-moorings. This included
    allowing maximum turbine thrust to be used for all calculations.
-   Renamed `tools.constaints` module as `tools.cable_constraints` and also
    renamed `ConstraintsTool` class to `CableConstraintsTool`.
-   Updated reliability and maintenance interfaces for major changes in
    dtocean-reliability version 3.
-   Allow the "farm.tidal_occurrence" variable to be used as an input to the
    hydrodynamics module or spacing constraints tool. This is useful to shortcut
    the tidal statistics calculations.

### Removed

-   Removed Manning's number ("bathymetry.mannings") variable and all
    database processing associated to it.
-   Removed mode calculation for variables with only one data point in the
    economics interface.
-   Removed modification of the provided lease area polygon in the hydrodynamics
    interface.
-   Removed `utils.reliability.read_RAM` function as no longer required with
    dtocean-reliability version 3.

### Fixed

-   Fixed compatibility issues with database keys in installation and
    maintenance data preparation by assigning types to DataTable based
    variables. Component ids are now always coerced to strings.
-   Fixed issue with incorrect sorting of time indexes in operations time
    series. A primary key was added to the Database filter tables to avoid this
    issue when fetching from the DB.
-   Fixed `SimpleList.get_value` not returning None when data was None.
-   Fixed `SimpleListColumn.auto_db` not returning None when retrieving an empty
    list.
-   Fixed conversion of floats to ints for "float" typed inputs when reading
    data for `SimpleList` or `SimpleDict` structures from excel input.
-   Fixed type conversion issues in maintenance module CAPEX and best and worse
    downtime outputs.
-   Fixed syntax error in environmental module interface when calculating
    surface coverage of vessels.
-   Fixed `SimplePie.autoplot` plots including zero valued entries.
-   Fixed bug where the O&M CAPEX contribution was being overwritten in the
    economics interface.
-   Fixed issues with `utils.hydrodynamics.make_tide_statistics`. See
    https://www.mdpi.com/2077-1312/8/9/646 for details.
-   Fixed incorrect device id numbering in the hydrodynamics module results by
    sorting naturally before assigning values.
-   Fixed bug in `SimpleList auto_load` if no type was set.
-   Fixed bug in `Strata` structure's file import when the string 'None' was
    used to indicate missing sedimentary data.
-   Fixed bug in label repositioning in `XGrid2D` structure's `autoplot` method.
-   Fixed bug where the lease area polygon was not plotted in the array layout
    plots if no padding was specified.
-   Fixed case in economics interface where energy record is faked but there
    were no OPEX costs provided.
-   Fixed https://github.com/DTOcean/dtocean/issues/30.
-   Fixed issue with `utils.stats.pdf_confidence_densities` function failing
    for a given pdf passed by the economics interface.

## [2.0.1] - 2019-07-08

### Changed

-   Added Loader and Dumper arguments to pyyaml calls as required by pyyaml
    version 5.1 to improve safety.

## [2.0.0] - 2019-03-10

### Added

-   Added change log.
-   Added tools plugin framework to add generic data manipulation or external
    tools.
-   Increased the number of spectrum types available to the hydrodynamics wave
    submodule.
-   Allowed filtering of the database when only sites or only devices are
    defined.
-   Added tests for "System Type Selection" and "Site and System Options"
    interfaces.
-   Added new parameter for recording JONSWAP spectrum gamma value in extreme
    calculations used by the moorings module.
-   Added more complete device subsystem descriptions for maintenance module.
    These split the requirements for each subsystem for access and the different
    maintenance strategies.
-   Added DateTimeDict data structure for dictionaries of datetime.datetime
    objects.
-   Completed database integration for installation and maintenance modules.
-   Added better error if predefined array layout option is chosen but no layout
    is given.
-   Added more comprehensive tests of various Structure subclasses.
-   Allow suppression of tagging datastates with an output level when executing
    interfaces using Connector.execute_interface. All DB output interfaces are
    no longer tagged with an output level and therefore are not hidden when
    using the module-only output scope.
-   Added plots for tidal stream velocities over the domain, using a single,
    random, time step.
-   Added configuration file for setting the location of logs and debug files
    using the files.ini configuration file (found in
    User\AppData\Roaming\DTOcean\dtocean_core\config folder).
-   Added configuration file generator called dtocean-core-config which copies
    the default configuration files (as requested) to the
    User\AppData\Roaming\DTOcean\dtocean_core\config folder.
-   Added labels and units to various variables which use the PointDict
    structure.
-   Added key annotation to PointDict plots.
-   Added "Lease Area Array Layout" plot to show devices in relation to the
    lease area definition.
-   Added "Te & Hm0 Time Series" plot to show the Te and Hm0 time series 
    separately from the wave directions.
-   Added "Wave Resource Occurrence Matrix" plot to show the wave module
    occurrence matrix summed over all wave directions.
-   Added logging of module execution time.
-   Added more robustness to opening dto files from older versions. Note,
    datastate corruption may still occur and new data may need to be added.
-   Added capacity factor as an output of the hydrodynamics interface.
-   Added plots for electrical cable layout.
-   Added plot for foundations layout.
-   Added optional boundary padding input to the electrical module so that the
    substation can be moved away from the lease area edge.
-   Added operational limit conditions to data catalogue to allow modification
    in the installation interface.
-   Added "passive hub" as a valid collection point type in the installation
    interface.
-   Added dump_datastate and load_datastate methods to Core class to allow
    the active datastate to be serialised and reloaded without storing the
    project information.
-   Added exclude option to load_datastate which will exclude loading any
    variables which contain the passed string.
-   Added lease area entry point to design boundaries plot.
-   Added variable 'project.estimate_energy_record' as a flag for indicating
    that the energy record should be estimated from the annual energy.
-   Added spares cost multiplier for maintenance interface to allow portion of
    full part cost to be used.
-   Added automated moorings subsystem cost estimation to maintenance interface
    utilities.
-   Added univariate and bivariate kernel density estimation classes to
    utils.stats module. 
-   Added univariate statistical analysis to outputs of maintenance module.
-   Added relax_cols option to TableData and LineTable structures to allow 
    arbitrary columns to be given in the input.
-   Added LineTableExpand structure for tables with an arbitrary number of
    columns (relax_cols is set to True by default).
-   Added univariate and bivariate analysis to economics interface for
    statistical analysis of LCOE and its components.
-   Added utils.reliability module to provide functions for reading the output
    of the dtocean-reliability module. The code was borrowed from
    dtocean-maintenance.
-   Enhanced outputs from reliability interface to show the reliability values
    for all sub-systems.
-   Added project.mttf_test variable to add test for exceeded design reliability
    for the array.
-   Added no-go areas to design boundary plots.
-   Added mask option to Core.dump_datastate to allow a mask to be applied
    before serialisation.
-   Added overwrite option to Core.load_datastate which, when false, will not
    allow variables with satisfied status to be loaded.
-   Added device.turbine_hub_height variable for setting tidal turbine hub
    height.
-   Added options.ignore_fex variable to tell dtocean-moorings module to ignore
    NEMOH values passed by dtocean-hydrodynamics, as they are currently not
    compatible.
-   Replaced device.system_draft as input to electrical module for umbilical
    calculation.
-   Added device.wave_power_matrix variable to collect the single machine power
    matrix output from the hydrodynamics module wave energy calculation.
-   Added options.repeat_foundations variable which when set to True will use
    a single foundation design for each device.
-   Added alternative repair actions in maintenance interface based on whether a
    device is being towed or transported on deck.
-   Allowed operation types to be associated with no sub-systems in maintenance
    interface.
-   Added device sub-system failure rates to array level reliability
    calculation.
-   Added plot of single wave device power matrix.
-   Added variables project.externalities_capex and project.externalities_opex
    for inclusion of one-off CAPEX and annual OPEX costs from external sources.
-   Added variables project.capex_lcoe_breakdown and project.opex_lcoe_breakdown
    to record the breakdown of CAPEX and OPEX LCOE values calculated in the
    economics interface.
-   Added variable project.lcoe_breakdown variable to compare OPEX and CAPEX
    contributions to the most-likely LCOE.
-   Added project.export_voltage variable to record export cable voltage chosen
    by the electrical module.
-   Added file I/O for DateTimeDict structure.
-   Added "Failure Date" column to corrective maintenance events tables to
    record date of sub-system failure.
-   Added options.corrective_prep_time variable to allow the amount of
    preparation time for corrective maintenance operations to be changed.
-   Added sort=False to all pandas concat and append calls.
-   Added array layout plot without device numbers.
-   Added plots for bathymetry and first sediment layer of the combined
    deployment area and cable corridor.
-   Interfaces which do not import on discovery are now skipped allowing
    customisable installations (such as for testing a single DTOcean module).
-   Added database export and import command line tool called dtocean-database.
    This program can dump the database into a folder structure of excel and csv
    files and then overwrite the database using the same file structure.
-   Add "CAPEX (Excluding Externalities)" variable to show CAPEX resulting from
    modules only.
-   Added experimental variables or variable values. The label "(Experimental)" 
    is automatically added to the titles.

### Changed

-   Renamed tools submodule to utils.
-   Changed database stored procedure calls to match changes to database
    structure.
-   Added "category" and "group" fields to DDS and removed "symbol,
    sample_value, maximum_value, minimum_value, default_value, input_widget,
    output_widget" which were unused.
-   Changed database table definitions to explicitly require the schema to be
    included, for instance project.farm rather than just farm.
-   Changed table definitions in DDS files and configuration to work with
    new database structure.
-   Changed table references to filter.farm to filter.lease_area.
-   Changed location of cable landing points to project.site table.
-   Changed categories (i.e category.name) of multiple variables to make a 
    clear distinction between site, device, reference and project specific data.
-   Device construction strategy is now simplified to offer just a "two stage
    assembly" option.
-   Split vessels table into separate tables per vehicle type.
-   Improved plot labelling and included Latex symbols.
-   SQLAlchemy calls moved out of structure definitions and into utils.database.
    This allows for easier testing of database reading.
-   Using default configuration files in source code unless a user configuration
    is found, or if the database definitions are written using
    DataMenu.update_database.
-   SimpleDict bar plots are now sorted by label.
-   Changed title metadata of project.array_efficiency variable to 'Array
    Capacity Factor'.
-   Switched timed rotating file logger for a standard rotating file logger
    which is rolled over at each invocation of start_logging.
-   Changed inputs to installation gantt plot in order to remove repeated
    variables.
-   Changed economics interface to work with updated dtocean-economics API.
-   Replaced corrective maintenance activation flag with alternative optional
    flag to suppress it. It is therefore active by default.
-   Maintenance module test data now shares more inputs with installation
    module test data.
-   Compilation of the moorings component database is now a separate method in
    the moorings interface to allow reuse by the maintenance interface.
-   Made compilation of electrical and moorings component databases dependent on
    which networks have been provided.
-   Modified variables and interface to dtocean-maintenance in response to API
    changes in the module.
-   Modified interface to dtocean-environment in response to new variables due
    to changes in the dtocean-maintenance module.
-   Changed meaning of device.foundation_type variable to defining a preferred
    foundation type for the device, rather than a fixed type.
-   Variables that are not within the active simulation will not be added when
    loading a datastate.
-   Variables which have status "unavailable" or "overwritten" will not be
    added when loading a datastate.
-   Estimated costs to the economics module are now given as absolute values
    (rather than per power), to avoid issues if no devices are simulated.
-   Themes are now allowed to be executed at any point, including after the
    module pipeline has completed.
-   If safety factors are not supplied to the installation module, these are now
    automatically set to unity.
-   Changed cable rated voltage symbol from U to U0 to ensure nominal voltage to
    earth is provided.
-   Clarified difference between piles with anchors and without in results of
    installation module.
-   Modified electrical interface for requirement of separate entries for static
    and dynamic cables from electrical module.
-   Changed calls to depreciated pandas from_csv to read_csv.
-   Changed calls to depreciated pandas sort_level to sort_index.
-   Changed calls to depreciated pandas convert_objects to to_numeric.
-   Changed calls to depreciated pandas Series.to_datetime to pandas.to_datetime
    function.
-   Change depreciated "sheetname" argument in pandas read_excel to
    "sheet_name".
-   Allow database credentials to be set directly, as an alternative to reading
    them from the config file. This is useful if the user does not wish to store
    their password in a plain text file.
-   Plot interfaces are now sorted by name.
-   Import and export of datastates is now accessed through the DataMenu class
    using the export_data and import_data methods.
-   The versions of packages in interfaces are now (manually) checked in the
    interfaces themselves and are no longer listed in setup.py.
-   Ensure the Branch.reset method cannot be called if a module has not yet been
    executed.
-   Allow None values when collecting data for comparisons.
-   Improved simulation name repetition logic in unit sensitivity strategy.
-   Switch to saving project files as tar.gz archives to improve performance.
    The zip versions are still supported for opening.
-   Module interfaces changed from MapInterfaces to MetaInterfaces to allow
    access to meta data.
-   Improved error messages for missing optional variables in installation
    interface.
-   Changed to using a bar chart in simulation comparison plot if x-axis ticks
    are non-numeric.
-   Renamed tests to better reflect source code file structure.
-   Changed name of "Environmental Impact Assessment" module to "Environmental
    Impact Assessment (Experimental)".
-   Changed project.ignore_fex variable to project.apply_fex. If set to True
    hydrodynamic force calculations are used for wave devices in the moorings
    module. Set to experimental.
-   Set "Star" network layout option to electrical sub-systems module as 
    experimental.

### Removed

-   Schema is no longer set in database configuration.
-   Removed farm.point_sea_surface_height.
-   Removed lead times as unused.
-   Remove unused power quality variables.
-   Removed unused switchgear variables.
-   Removed numerous unused fields from component tables.
-   Removed numerous unused fields from equipment tables.
-   Removed numerous unused fields from ports table.
-   Removed numerous unused fields from vessels table.
-   Removed some header lines from inputs to moorings module and hard coded them
    into the interface.
-   Removed power law exponent variable as this is not used when Manning's
    number is used to describe channel roughness.
-   Removed variables that are inputs to the electrical module but are not used 
    in any way.
-   Remove adjust_outliers options from make_power_histograms as was always set
    to True.
-   Removed repeated output variables from installation interface and DDS.
-   Removed network failure rate inputs to maintenance interface.
-   Removed moorings subsystem cost inputs to maintenance interface.
-   Removed unused maintenance optimisation options.
-   Removed depreciated control options for maintenance module.
-   Removed device.coordinate_system variable as only partially used.
-   Removed depreciated variables in the maintenance module interface.
-   Removed the word "device" from array layout plots.

### Fixed

-   Fix missing type declarations in DDS for installation module outputs.
-   Fixed PointData incorrectly storing coordinates passed as lists.
-   Fix boolean inputs to installation module that require conversion to
    "yes/no".
-   Fix incorrect device type in installation module test data. 
-   Fixed units of directions to electrical module which required conversion to
    radians.
-   Fixed spectrum definitions to hydrodynamics module.
-   Fixed use of fibre optic channels variable in electrical module interface.
-   Fixed use of device bollard pull in installation module interface.
-   Merged umbilical table and dynamic cable tables.
-   Fixed installation module date based outputs.
-   General improvements to variable and table column names.
-   Fixed trenching type variable definition.
-   Fixed bugs with database reading empty tables -   now returns None.
-   Fixed TimeSeries structure plots.
-   Fixed soil type name conversions with the electrical module interface.
-   Fixed bug in PointList structure file I/O.
-   Fixed power histogram calculation which was not ordering the powers
    correctly.
-   Fixed file I/O and plots for NumpyLineDict and HistogramDict structures.
-   Fix issue with None values in the sediments layers being incorrectly passed
    to the moorings module.
-   Fix issues with formatting of some tabulated outputs of the moorings module.
-   Fixed missing variable mapping in constraints plot tool interface. It uses
    the input declaration of the electrical module interface, but its own id_map
    and so they went out of sync following changes to the electrical interface.
-   Fixed installation module gantt chart plot and changed "Waiting time" label
    to "Start delay".
-   Fixed bug in lease area entry point definition which was breaking the auto
    plot.
-   Ensure that installation operation end dates are costed in the correct
    project year.
-   Fixed typo "devide" in hydrodynamics interface error regarding power
    histogram bin width.
-   Fixed bug where the phase name was missing from the OPEX data input to the
    economics module.
-   Fixed bugs with conversion of maintenance module events tables.
-   Fixed bugs with missing components in electrical subsystem cost estimation.
-   Fixed bugs with energy and OPEX post-processing from the maintenance module
    including using project years rather than the date years in outputs to the
    economics module.
-   Fix bug loading datastates that contain variables no longer in the data
    catalogue.
-   Fixed bug where an interface would be marked as complete even if there was
    an error when reading the outputs from an interface.
-   Fixed bug in maintenance interface when device sub-system costs were
    incorrectly divided by the number of devices.
-   Fixed bug in UnitSensitivity strategy where it was attempting to use
    duplicate simulation titles.
-   Fixed issue with nogo areas not being set in electrical interface.
-   Fixed foundation type naming in installation interface.
-   Fixed removing null points and merging of lease area and cable corridor in
    installation interface.
-   Fixed units of sub-system failure rates in maintenance interface.
-   Fixed issue where drag anchors were not included in the sub-system cost
    estimates in the maintenance interface.
-   Fixed duplicated symbols in plot legends.
-   Fixed confusing units for wave period inputs to the hydrodynamics module.
-   Fixed bug when 3rd coordinate in given in the user-defined array layout.
-   Attempted to fix issue with maintenance module not responding to dual
    turbine tidal energy case by doubling the failure rates of the associated
    sub-systems. Requires a more robust fix in the maintenance module itself.
-   Fixed bug in utils.hydrodynamics.make_wave_statistics when save_flag is set
    to True.
-   Fixed connection between device cost and the database.
-   Fixed unit attributes being set to string "None" for non-dimensional data
    stored in the XGridND structure.
-   Fixed description of device.umbilical_type in DDS.
-   Fixed bug in utils.hydrodynamics.radians_to_bearing.
-   Fixed substation foundation type being treated as floating in installation
    interface.
-   Patched double counting of umbilical costs and reliability if both the 
    electrical and moorings modules are run. Requires a more robust fix (such as
    using a dedicated network for the umbilical) in the future.
-   Fixed conversion to scientific notation in XGrid2D plots if variables on 
    axis contain strings.
-   Fixed calling methods on numpy arrays with NaNs in the environmental
    interface.
-   Fixed multiple instances of pandas SettingWithCopyWarning.
-   Fixed floats being used as numpy array indexes in
    utils.hydrodynamics.make_tide_statistics.
-   Fixed units in economics metrics table.
-   Fixed bug when multiple interfaces are discovered for a variable in the
    pipeline.
-   Fixed upstream bug where timestamps could not be saved to excel files.
-   Fixed bug in set_output_state where only the output state of the active 
    simulation would be changed. Correct behaviour is for all simulations to be 
    modified.
-   Fixed bug when setting a simulation title to its existing value.
-   Fix issue with network configuration being undefined in reliability
    interface.
-   Fix misspelling of "interruptible".
-   Fixed dtocean-wec tool extension leaving an open a cmd window when called.
-   Fixed reference frame conversion for floating devices in moorings 
    calculations.

## [1.0.0] - 2017-02-23

### Added

-   Initial import of dtocean-core from SETIS.
