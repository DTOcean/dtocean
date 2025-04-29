# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.1] - 2021-07-12

### Changed

-   The version number in the about dialog is now set using the version number 
    of the `dtocean` package, if installed. If the `dtocean` package is not 
    installed the `dtocean-app` package version will be displayed instead.

### Removed

-   Removed 32 bit `.condarc-32` conda configuration file, as it is currently
    identical to the 64bit version. 64 and 32 bit installation instructions are
    now identical, also.

## [2.1.0] - 2021-07-07

### Added

-   Add advanced position strategy to available optimisation strategies. This
    strategy can be used to optimise the layout of an array for a given cost
    function, such as the LCOE.
-   Allowed text selection of the value in PointSelect input widgets.
-   Values added to DataTable structures must now conform to the given data 
    type.
-   Activated modules and themes are now checked against the active simulation 
    to ensure they match (when loading a project, for instance).
-   Added command line option to quit before the interface starts (for testing).
-   Allowed maximum and minimum values to be set on SimpleData widgets.
-   Added option to delete a simulation to the simulation dock context menu.

### Changed

-   Added Loader and Dumper arguments to pyyaml calls as required by pyyaml 
    version 5.1 to improve safety.
-   Prevented project closing when the database dialogue is open.
-   All file dialogues now start in the user's home directory.
-   The strategy manager window can now be maximised.
-   Debug logging of figure numbers was improved.
-   Moved responsibility for creating a pure Project object when saving to
    dtocean_core.
-   Added note in GUI that only a single simulation can exist when starting the 
    sensitivity strategies.

## Fixed

-   Fixed bug where the file extensions for variable file import were being 
    used when exporting a variable.
-   Widgets are now removed if a simulation is set active which doesn't contain 
    the last selected variable.
-   Fix a regression where the "Use Strategy" tick boxes in the comparison view
    were not being enabled.
-   Allow backwards compatibility for some older project files.
-   Ensured tools with widgets are modal and destroy any plots they have when
    closing.
-   Prevented crash when project loading fails.

## [2.0.0] - 2019-03-12

### Added

-   Added high DPI scaling widgets which activate when Windows virtual DPI 
    exceeds 100. Improves look and feel on high DPI displays.
-   Split high low and shared QtDesigner files into separate directories.
-   Added dynamic generation of tools menu from plugins created in the tools
    module.
-   Added constraints plot tool.
-   Allow filtering of database when only sites or only devices are defined.
-   Added DateTimeDict structure and output widget.
-   Added input and output widgets for SimpleDictColumn.
-   Added ScientificDoubleSpinBox widget to allow scientific notation for 
    floats.
-   Created static version of Ui_FloatSelect (called Ui_ScientificSelect) which
    uses ScientificDoubleSpinBox.
-   Added configuration file generator called dtocean-app-config which copies
    the default configuration files (as required) to the
    User\AppData\Roaming\DTOcean\dtocean_app\config folder.
-   Added configuration file for setting the location of logs using the 
    files.ini configuration file (found in 
    User\AppData\Roaming\DTOcean\dtocean_app\config folder).
-   Added save file robustness compatibility with dtocean-core.
-   Added widgets for CartesianListColumn structure.
-   Added Alt key shortcuts to menus.
-   Added Export and Import actions to the Data menu to create and load 
    datastate files. These save the data in the active datastate and can be 
    reused in any project.
-   Added "Export (mask outputs)" and "Import (skip satisfied)" actions to allow
    greater control of exporting and importing datastates.
-   Allow text to be selected in variable details widget.
-   Added output widget for SimpleList structure.
-   Added LineTableExpand structure and input and output widgets.
-   Added custom disabled states to some widgets to allow greater use once a 
    module has completed. For instance, table widgets can now be scrolled even 
    when disabled.
-   Added option to save plots with a given size in the PlotManagerWidget 
    widget.
-   Implemented add and delete for database credentials in DBSelector widget.
-   Added actionView_Logs action to the help menu to open the location of the 
    log files.
-   Allowed module imports to be skipped on failure. This allows partial
    installations of DTOcean, such as for testing a single module.
-   Added buttons to DBSelector widget for database dump and load to and from
    structured files.
-   Added tooltips to help explain the buttons of DBSelector widget.
-   Added the option to save to project files (.prj) which can be opened by
    dtocean-core (note, some information about the state of the GUI is lost, so
    .dto files are preferable for GUI use).
-   The file path in FileManagerWidget is now cleared following load and save
    to indicate that the action was successful. 
-   None can now be given as a variable value to strategies to allow for 
    optional variables to be run in their unset mode.

### Changed

-   Removed "schema" from database configuration dialog.
-   Hid input variables labelled as overwritten and output variables labelled
    as unavailable or overwritten.
-   Moved ListWidget ui file to shared directory and add specific unit label.
-   FloatSelect widget now subclasses Ui_ScientificSelect.
-   Using default configuration files in source code unless a user configuration
    is found.
-   Changed timed rotating file logger for a standard rotating file logger that
    is rolled over at the beginning of each session.
-   Exposed add and remove column buttons for InputDataTable widget for use by
    LineTableExpand structure.
-   Changed read signal on string based widgets to emit on return press rather
    than on every text input.
-   Released variables which were hidden by the use of strategy if the strategy
    has completed and cannot be rerun.
-   The current simulation is now highlighted in bold in the simulation dock.
-   Allowed themes to be run after modules have completed.
-   The main window can now be minimised while running modules (although a small
    title bar is still visible).
-   Allowed direct setting of database credentials in DBSelector for passwords 
    to be provided without storing them an ASCII file.
-   Updated the splash screen to DTOcean2 logo.
-   Updated About dialog, active developers and host institutions.
-   Improved backwards compatibility for loaded tables which do not have the 
    same columns as found in the current data catalogue.
-   Switched to the dtocean-core DataMenu export_data and import_data methods
    for export and import of datastates.
-   Strategy selection now comes after the dataflow is initialised to allow
    data viewing manipulation prior to choosing a strategy.
-   Updated the open and close file logic and added option to discard changes 
    and close DTOcean.
-   The Reset and Inspect context menu actions and now only active when valid.
-   Changed buttons in FileManagerWidget and PlotManagerWidget file dialogs to
    say "Select" rather than "Save" or "Load" to help user understand another 
    step must be taken (pressing "OK") for the action to complete.
-   The configure module was moved to utils.config.
-   Removed fixup method from ScientificDoubleSpinBox to aviod bad return value.
-   Thread safety improved to fix occasional UI bugs. The interface will no 
    longer update until execution has completed.
-   The Strategy Manager is no longer modal to allow easier setting of variables
    values.

### Removed

-   Removed floatselect.ui as the widget is now built inside the package.
-   Removed file extension selection from FileManagerWidget which is now handled
    in the file dialog or when OK is pressed.
-   Removed forcing of theme completion.

### Fixed

-   Fixed bug in InputTriStateTable widget that stopped input of Observed 
    Receptors variable in environmental assessment theme.
-   Fixed issue with displaying PointList data (such as the user defined array
    layout) when z-coordinates are not set.
-   Fixed issue with missing data in IndexTable and SimpleDict widgets.
-   Fixed incorrect order of columns in DatetimeDict output widget.
-   Fixed bug with log file rollover when opening two or more sessions.
-   Fixed bug caused by QVariant APIv2 when removing columns from a
    DataTableWidget.
-   Fixed issue with CoordSelect widget not setting value for z-coordinate.
-   Fixed race condition on reading the project status when being updated by
    a strategy in progress.
-   Fixed bug where no negative numbers could be used in 
    ScientificDoubleSpinBox.
-   Fixed bug related to getting database credentials when none are set.
-   The logging window now has a maximum number of lines (99999) to avoid 
    crashes from too many log messages.
-   Fixed issue with unreadable context menus when mouseover is triggered.
-   Added taskfinished signals to all Thread classed after an error has been
    detected to ensure proper cleanup and GUI response.
-   Fixed bug with displaying table cells with None as their value.
-   Fixed reloading of strategy configuration in the Strategy Manager when
    opening a dto file.
-   Fixed bug where an error was being logged when renaming a simulation to its
    current value.
-   Added names to the toolbars, so they can be distinguished in the 
    right-click menu.
-   Fixed issue where the view action for docks would still be active if the 
    dock was opened from the right-click toolbar menu.
-   Fixed issue with DataFrameModel initialisation where bugs occur if the
    dataframe is not passed in the constructor.

## [1.0.0] - 2017-02-23

### Added

-   Initial import of dtocean-gui from SETIS.

### Changed

-   Changed package name to dtocean-app.
-   Changed pandas-qt dependency to dtocean-qt.
