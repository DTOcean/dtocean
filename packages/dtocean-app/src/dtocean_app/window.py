# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2025 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Created on Thu Apr 23 12:51:14 2015

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import logging
import os
import sys
import threading
import traceback
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from shiboken6 import Shiboken
from win32event import CreateMutex

from . import get_log_dir
from .extensions import GUIStrategyManager, GUIToolManager
from .help import HelpWidget
from .menu import DBSelector
from .pipeline import (
    HubControl,
    InputBranchControl,
    InputVarControl,
    OutputBranchControl,
    OutputVarControl,
    PipeLine,
    SectionControl,
)
from .shell import Shell
from .simulation import SimulationDock
from .widgets.central import (
    ContextArea,
    DetailsWidget,
    FileManagerWidget,
    LevelComparison,
    PlotManagerWidget,
    SimulationComparison,
)
from .widgets.dialogs import (
    About,
    DataCheck,
    MainWindow,
    ProgressBar,
    ProjProperties,
    Shuttle,
)
from .widgets.display import (
    MPLWidget,
    get_current_filetypes,
    save_current_figure,
)
from .widgets.docks import LogDock

# Set up logging
module_logger = logging.getLogger(__name__)

# User home directory
HOME = os.path.expanduser("~")

# Check if running coverage
RUNNING_COVERAGE = "coverage" in sys.modules


class ThreadTool(QtCore.QThread):
    """QThread for executing dtocean-wec"""

    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, core, project, tool):
        super().__init__()
        self._tool = tool
        self._core = core
        self._project = project

        self._tool_manager = GUIToolManager()

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            self._tool_manager.execute_tool(
                self._core, self._project, self._tool
            )

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)


class DTOceanWindow(MainWindow):
    def __init__(self, shell: Shell, debug=False):
        super().__init__()

        self._mutexname = None
        self._mutex = None

        # Create a windows mutex (TODO: does this still prevent multiple instances?)
        if sys.platform == "win32":
            self._mutexname = "mutex_{AEF365BF-44B8-41E8-9906-4D1BADEE42E0}"
            self._mutex = CreateMutex(None, False, self._mutexname)  # type: ignore

        # Context Area
        self._data_context: ContextArea
        self._plot_context: ContextArea
        self._comp_context: ContextArea

        # Dialogs
        self._project_properties: ProjProperties
        self._data_check: DataCheck
        self._module_shuttle: Shuttle
        self._assessment_shuttle: Shuttle
        self._db_selector: DBSelector
        self._strategy_manager: GUIStrategyManager
        self._help: HelpWidget
        self._progress: ProgressBar
        self._about: About

        # Temporary widgets
        self._data_details: Optional[DetailsWidget] = None
        self._plot_details: Optional[DetailsWidget] = None
        self._data_file_manager: Optional[FileManagerWidget] = None
        self._plot_manager: Optional[PlotManagerWidget] = None
        self._level_comparison: Optional[LevelComparison] = None
        self._sim_comparison: Optional[SimulationComparison] = None

        # Docks
        self._pipeline_dock: PipeLine
        self._simulation_dock: SimulationDock
        self._system_dock: LogDock

        # Widget re-use
        self._last_tree_controller = None
        self._last_data_controller = None
        self._last_data_controller_status = None
        self._last_plot_id = None
        self._last_plot_name = "auto"
        self._force_plot = False

        # Last used stack index
        self._last_stack_index = None

        # Threads
        self._thread_tool = None

        # Tools
        self._tool_manager: GUIToolManager
        self._tool_widget = None

        # Redirect excepthook
        if not debug:
            sys.excepthook = self._display_error

        # Init Shell
        self._shell = self._init_shell(shell)

        # Init context areas
        self._init_context()

        # Init dialogs
        self._init_shuttles()
        self._init_dialogs()

        # Initiate docks
        self._init_pipeline_dock()
        self._init_simulation_dock()
        self._init_system_dock(debug)

        # Initiate menus
        self._init_file_menu()
        self._init_sim_menu()
        self._init_data_menu()
        self._init_view_menu(debug)
        self._init_tools_menu()
        self._init_help_menu()

    def _init_shell(self, shell):
        shell.project_activated.connect(self._active_project_ui_switch)
        shell.project_closed.connect(self._closed_project_ui_switch)
        shell.reset_widgets.connect(
            lambda: self._set_context_widget(self._last_tree_controller, True)
        )
        shell.pipeline_active.connect(self._active_pipeline_ui_switch)
        shell.bathymetry_active.connect(self._active_bathymetry_ui_switch)
        shell.filter_active.connect(self._active_filter_ui_switch)
        shell.dataflow_active.connect(self._active_dataflow_ui_switch)
        shell.strategy_selected.connect(self._strategy_box_ui_switch)
        shell.update_run_action.connect(self._run_action_ui_switch)
        shell.module_executed.connect(self._run_action_ui_switch)
        shell.themes_executed.connect(self._run_action_ui_switch)
        shell.strategy_executed.connect(self._run_action_ui_switch)
        shell.update_scope.connect(self._current_scope_ui_switch)

        def _set_stack_index():
            if self._last_stack_index is None:
                return
            self.stackedWidget.setCurrentIndex(self._last_stack_index)

        shell.strategy_executed.connect(_set_stack_index)

        # Collect all saved and unsaved signals
        shell.project_title_change.connect(self._set_project_unsaved)
        shell.project_activated.connect(self._set_project_unsaved)
        shell.reset_widgets.connect(self._set_project_unsaved)
        shell.update_run_action.connect(self._set_project_unsaved)
        shell.project_saved.connect(self._set_project_saved)

        return shell

    def _init_context(self):
        # Blank context
        blank_widget = QtWidgets.QWidget(self)
        self.stackedWidget.addWidget(blank_widget)

        # Data context
        self._data_context = ContextArea(self)
        self.stackedWidget.addWidget(self._data_context)

        # Plot context
        self._plot_context = ContextArea(self)
        self.stackedWidget.addWidget(self._plot_context)

        # Comparison context
        self._comp_context = ContextArea(self)
        self._comp_context._top_left.setMaximumWidth(16777215)
        self._comp_context._top_right.setMinimumWidth(320)
        self.stackedWidget.addWidget(self._comp_context)

        # Collect the input widget parent
        self._shell.core.set_input_parent(self._data_context._bottom)

    def _init_shuttles(self):
        # Set up the module shuttle widget
        self._module_shuttle = Shuttle(self, "Add Modules...")
        self._module_shuttle.list_updated.connect(self._shell.queue_module_list)

        # Set up the assessment shuttle widget
        self._assessment_shuttle = Shuttle(self, "Add Assessment...")
        self._assessment_shuttle.list_updated.connect(
            self._shell.queue_theme_list
        )

    def _init_dialogs(self):
        # Set up project properties dialog
        self._project_properties = ProjProperties(self)
        self._project_properties.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._set_project_title)

        # Set up the database selection dialog
        self._db_selector = DBSelector(self, self._shell.data_menu)
        self._db_selector.database_selected.connect(self._shell.select_database)
        self._db_selector.database_deselected.connect(
            self._shell.deselect_database
        )
        self._db_selector.database_dump.connect(self._dump_database)
        self._db_selector.database_load.connect(self._load_database)
        self._db_selector.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Close
        ).clicked.connect(self._unset_database_properties)

        self._shell.database_updated.connect(self._db_selector._update_current)
        self._shell.database_convert_active.connect(
            self._db_selector._convert_disabled
        )
        self._shell.database_convert_complete.connect(
            self._db_selector._convert_enabled
        )
        self._shell.database_convert_active.connect(
            lambda: self.actionInitiate_Pipeline.setDisabled(True)
        )
        self._shell.database_convert_complete.connect(
            lambda: self.actionInitiate_Pipeline.setEnabled(True)
        )

        # Set up the strategy manager
        self._strategy_manager = GUIStrategyManager(self._shell, self)
        self._strategy_manager.setWindowFlags(
            self._strategy_manager.windowFlags()
            | Qt.WindowType.WindowMaximizeButtonHint
        )

        self._strategy_manager.strategy_selected.connect(
            self._shell.select_strategy
        )
        self._shell.strategy_loaded.connect(
            self._strategy_manager._load_strategy
        )

        # Set up the data check diaglog
        self._data_check = DataCheck(self)
        self._data_check.setModal(True)

        # Set up progress bar
        self._progress = ProgressBar(self)
        self._progress.setModal(True)
        self._progress.force_quit.connect(self.close)

        # Set up the help dialog
        self._help = HelpWidget(self)

        # Set up the about dialog (actionAbout)
        self._about = About(self)
        self._about.setModal(True)

    def _init_pipeline_dock(self):
        # Give the bottom left corner to left dock
        self.setCorner(Qt.Corner(0x00002), Qt.DockWidgetArea(1))

        # Pipeline dock
        self._pipeline_dock = PipeLine(self)
        self._pipeline_dock._showclose_filter._show.connect(
            lambda: self.actionShow_Pipeline.setEnabled(False)
        )
        self._pipeline_dock._showclose_filter._close.connect(
            lambda: self.actionShow_Pipeline.setEnabled(True)
        )
        self.addDockWidget(Qt.DockWidgetArea(1), self._pipeline_dock)

        # Set widgets on tree click
        self._pipeline_dock.treeView.clicked.connect(self._set_details_widget)
        self._pipeline_dock.treeView.clicked.connect(self._set_context_widget)

        # Change the output scope on button click
        self._pipeline_dock.globalRadioButton.clicked.connect(
            lambda: self._waitcursor_scope("global")
        )
        self._pipeline_dock.localRadioButton.clicked.connect(
            lambda: self._waitcursor_scope("local")
        )
        self._pipeline_dock.scopeFrame.setDisabled(True)

        # Variable filtering
        self._pipeline_dock.filterFrame.setDisabled(True)

        def _refresh_pipeline():
            self._pipeline_dock._refresh(self._shell)

        # Refresh on module and theme activation or execution
        self._shell.modules_queued.connect(_refresh_pipeline)
        self._shell.themes_queued.connect(_refresh_pipeline)
        self._shell.module_executed.connect(_refresh_pipeline)
        self._shell.themes_executed.connect(_refresh_pipeline)
        self._shell.strategy_executed.connect(_refresh_pipeline)

        # Repeat any filtering on widget update
        self._shell.reset_widgets.connect(self._pipeline_dock._repeat_filter)

        def _make_pipeline_menus(x):
            self._pipeline_dock._make_menus(self._shell, x)

        # Add context menu(s)
        self._pipeline_dock.treeView.customContextMenuRequested.connect(
            _make_pipeline_menus
        )

        # Handle errors
        self._pipeline_dock.error_detected.connect(self._display_error)

    def _init_simulation_dock(self):
        # Simulation dock
        self._simulation_dock = SimulationDock(self)
        self._simulation_dock._showclose_filter._show.connect(
            lambda: self.actionShow_Simulations.setEnabled(False)
        )
        self._simulation_dock._showclose_filter._close.connect(
            lambda: self.actionShow_Simulations.setEnabled(True)
        )
        self.addDockWidget(Qt.DockWidgetArea(1), self._simulation_dock)
        self._simulation_dock.name_changed.connect(
            self._shell.set_simulation_title
        )
        self._simulation_dock.active_changed.connect(
            self._shell.set_active_simulation
        )

        def _make_simulation_menus(x):
            self._simulation_dock._make_menus(self._shell, x)

        # Add context menu(s)
        self._simulation_dock.listWidget.customContextMenuRequested.connect(
            _make_simulation_menus
        )

        # Set disabled until dataflow activated.
        self._simulation_dock.setDisabled(True)

        # Tab docks
        self.setTabPosition(
            Qt.DockWidgetArea(1), QtWidgets.QTabWidget.TabPosition(0)
        )
        self.tabifyDockWidget(self._simulation_dock, self._pipeline_dock)

        # Collect unsaved signals
        self._simulation_dock.name_changed.connect(self._set_project_unsaved)
        self._simulation_dock.active_changed.connect(self._set_project_unsaved)

    def _init_system_dock(self, disable_log=False):
        if disable_log:
            return

        # System dock
        self._system_dock = LogDock(self)
        self._system_dock._showclose_filter._show.connect(
            lambda: self.actionSystem_Log.setEnabled(False)
        )
        self._system_dock._showclose_filter._close.connect(
            lambda: self.actionSystem_Log.setEnabled(True)
        )
        self.addDockWidget(Qt.DockWidgetArea(8), self._system_dock)

    def _init_file_menu(self):
        self.actionNew.triggered.connect(self._new_project)
        self.actionOpen.triggered.connect(self._open_project)
        self.actionSave.triggered.connect(self._save_project)
        self.actionSave_As.triggered.connect(self._saveas_project)
        self.actionProperties.triggered.connect(self._set_project_properties)
        self.actionClose.triggered.connect(self._close_project)
        self.actionExit.triggered.connect(self.close)

    def _init_sim_menu(self):
        # Set up the simulation menu
        self.actionAdd_Modules.triggered.connect(self._set_module_shuttle)
        self.actionAdd_Assessment.triggered.connect(
            self._set_assessment_shuttle
        )
        self.actionAdd_Strategy.triggered.connect(self._set_strategy)
        self.actionRun_Current.triggered.connect(self._execute_current)
        self.actionRun_Themes.triggered.connect(self._execute_themes)
        self.actionRun_Strategy.triggered.connect(self._execute_strategy)

    def _init_data_menu(self):
        # Database selection dialog
        self.actionSelect_Database.triggered.connect(
            self._set_database_properties
        )

        # Set up data preparation stages
        self.actionInitiate_Pipeline.triggered.connect(self._initiate_pipeline)
        self.actionInitiate_Bathymetry.triggered.connect(
            self._initiate_bathymetry
        )
        self.actionInitiate_Dataflow.triggered.connect(self._initiate_dataflow)

        # Data export / import functions
        self.actionExport.triggered.connect(self._export_data)
        self.actionExport_mask.triggered.connect(self._export_data_mask)
        self.actionImport.triggered.connect(self._import_data)
        self.actionImport_skip.triggered.connect(self._import_data_skip)

    def _init_view_menu(self, disable_log=False):
        # Dock show buttons
        self.actionShow_Pipeline.triggered.connect(self._pipeline_dock.show)
        self.actionShow_Pipeline.triggered.connect(
            lambda: self.actionShow_Pipeline.setDisabled(True)
        )

        self.actionShow_Simulations.triggered.connect(
            self._simulation_dock.show
        )
        self.actionShow_Simulations.triggered.connect(
            lambda: self.actionShow_Simulations.setDisabled(True)
        )

        if not disable_log:
            self.actionSystem_Log.triggered.connect(self._system_dock.show)
            self.actionSystem_Log.triggered.connect(
                lambda: self.actionSystem_Log.setDisabled(True)
            )

        # Context Actions
        self.actionData.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(1)
        )
        self.actionPlots.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(2)
        )
        self.actionComparison.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(3)
        )
        self.actionData.triggered.connect(
            lambda: self._set_context_widget(self._last_tree_controller)
        )
        self.actionPlots.triggered.connect(
            lambda: self._set_context_widget(self._last_tree_controller)
        )

        self.contextGroup = QtGui.QActionGroup(self)
        self.contextGroup.addAction(self.actionData)
        self.contextGroup.addAction(self.actionPlots)
        self.contextGroup.addAction(self.actionComparison)

    def _init_tools_menu(self):
        """Dynamically generate tool menu entries and signal/slots"""

        self._tool_manager = GUIToolManager()

        all_tools = self._tool_manager.get_available()

        for tool_name in all_tools:
            new_action = self._add_dynamic_action(tool_name, "menuTools")
            new_action.triggered.connect(
                lambda x, name=tool_name: self._open_tool(name)
            )

            self._dynamic_actions[tool_name] = new_action

    def _init_help_menu(self):
        self.actionHelp_Index.triggered.connect(self._help.show)
        self.actionAbout.triggered.connect(self._about.show)

        # Open the logs folder
        log_dir = get_log_dir()
        self.actionView_Logs.triggered.connect(lambda: os.startfile(log_dir))

    @QtCore.Slot(str)
    def _set_window_title(self, title):
        if not title:
            title_str = "DTOcean"
        else:
            title_str = "DTOcean: {}".format(title)

        self.setWindowTitle(title_str)

    @QtCore.Slot()
    def _set_project_properties(self):
        assert self._shell.project is not None
        self._project_properties.lineEdit.setText(self._shell.project.title)
        self._project_properties.show()

    @QtCore.Slot()
    def _set_project_title(self):
        new_title = self._project_properties.lineEdit.text()
        self._shell.set_project_title(new_title)

    @QtCore.Slot()
    def _set_project_saved(self):
        if self._shell.project is None:
            return

        if self._shell.project_path is None:
            window_title = self._shell.project.title
        else:
            window_title = "{} ({})".format(
                self._shell.project.title, self._shell.project_path
            )

        self._set_window_title(window_title)
        self._shell.project_unsaved = False

    @QtCore.Slot()
    def _set_project_unsaved(self):
        if self._shell.project is None:
            return

        if self._shell.project_path is None:
            window_title = "{}*".format(self._shell.project.title)
        else:
            window_title = "{} ({})*".format(
                self._shell.project.title, self._shell.project_path
            )

        self._set_window_title(window_title)
        self._shell.project_unsaved = True

    @QtCore.Slot()
    def _set_database_properties(self):
        self.actionClose.setDisabled(True)
        self._db_selector.show()

    @QtCore.Slot()
    def _unset_database_properties(self):
        self.actionClose.setEnabled(True)

    @QtCore.Slot()
    def _active_project_ui_switch(self):
        assert self._shell.project is not None

        # Disable Actions
        self.actionNew.setDisabled(True)
        self.actionOpen.setDisabled(True)
        self.actionSave.setDisabled(True)
        self.actionSave_As.setDisabled(True)
        self.actionComparison.setDisabled(True)

        # Enable Actions
        self.actionProperties.setEnabled(True)
        self.actionClose.setEnabled(True)
        self.actionData.setEnabled(True)
        self.actionPlots.setEnabled(True)
        self.actionInitiate_Pipeline.setEnabled(True)
        self.actionSelect_Database.setEnabled(True)
        self.actionExport.setEnabled(True)
        self.actionExport_mask.setEnabled(True)
        self.actionImport.setEnabled(True)
        self.actionImport_skip.setEnabled(True)

        # Activate the pipeline
        start_branch_map = [
            {"hub": SectionControl, "name": "Configuration"},
            {
                "hub": HubControl,
                "name": "Scenario",
                "args": [
                    "project",
                    InputBranchControl,
                    True,
                    [
                        "System Type Selection",
                        "Database Filtering Interface",
                        "Project Boundaries Interface",
                    ],
                ],
            },
        ]

        self._pipeline_dock._set_branch_map(start_branch_map)
        self._pipeline_dock._refresh(self._shell)
        self._pipeline_dock._set_title("Define scenario selections...")
        self._pipeline_dock.scopeFrame.setEnabled(True)
        self._pipeline_dock.filterFrame.setEnabled(True)

        # Link the project to the simulation dock and initialise the list
        self._simulation_dock.setDisabled(True)
        self._shell.project.sims_updated.connect(
            lambda: self._simulation_dock._update_simulations(
                self._shell.project
            )
        )
        self._simulation_dock._update_simulations(self._shell.project)

        # Set up details widget on the data context area
        self._data_details = DetailsWidget(self)
        self._data_context._top_left_box.addWidget(self._data_details)

        # Set up file manager widget on the data context area
        self._data_file_manager = FileManagerWidget(self)
        self._data_context._top_right_box.addWidget(self._data_file_manager)
        self._data_file_manager.setDisabled(True)

        # Set up details widget on the plot context area
        self._plot_details = DetailsWidget(self)
        self._plot_context._top_left_box.addWidget(self._plot_details)

        # Set up plot manager widget on the plot context area
        self._plot_manager = PlotManagerWidget(self)
        self._plot_context._top_right_box.addWidget(self._plot_manager)
        self._plot_manager.setDisabled(True)

        # Set up the level comparison in the comparison context area
        self._level_comparison = LevelComparison(self)  # type: ignore
        self._comp_context._top_left_box.addWidget(self._level_comparison)

        # Set up the simulation comparison in the comparison context area
        self._sim_comparison = SimulationComparison(self)  # type: ignore
        self._comp_context._top_right_box.addWidget(self._sim_comparison)

        # Set up level comparison signals
        self._level_comparison.varBox.currentIndexChanged.connect(
            self._sim_comparison_ui_switch
        )
        self._level_comparison.plot_levels.connect(self._set_level_plot)
        self._level_comparison.tab_levels.connect(self._set_level_table)
        self._level_comparison.save_plot.connect(self._save_comparison_plot)
        self._level_comparison.save_data.connect(self._save_comparison_data)

        # Set up simulation comparison signals
        self._sim_comparison.plot_levels.connect(self._set_sim_plot)
        self._sim_comparison.tab_levels.connect(self._set_sim_table)
        self._sim_comparison.save_plot.connect(self._save_comparison_plot)
        self._sim_comparison.save_data.connect(self._save_comparison_data)

        # Update the central widget
        self.stackedWidget.setCurrentIndex(1)
        self.actionData.setChecked(True)

        # Connect actions
        self._shell.update_pipeline.connect(self._tool_menu_ui_switch)
        self._shell.update_pipeline.connect(self._set_project_unsaved)

        # Trigger the pipeline
        self._pipeline_dock._set_top_item()

        # Trigger tools menu (not likely concurrent)
        self._tool_menu_ui_switch(self._shell)

        # Update the active sim title
        active_sim_title = self._shell.project.get_simulation_title()
        self._shell.project.active_title_changed.emit(active_sim_title)

    @QtCore.Slot()
    def _closed_project_ui_switch(self):
        # Disable Actions
        self.actionSave.setDisabled(True)
        self.actionSave_As.setDisabled(True)
        self.actionProperties.setDisabled(True)
        self.actionClose.setDisabled(True)
        self.actionData.setDisabled(True)
        self.actionPlots.setDisabled(True)
        self.actionComparison.setDisabled(True)
        self.actionInitiate_Pipeline.setDisabled(True)
        self.actionSelect_Database.setDisabled(True)
        self.actionInitiate_Dataflow.setDisabled(True)
        self.actionInitiate_Bathymetry.setDisabled(True)
        self.actionAdd_Modules.setDisabled(True)
        self.actionAdd_Assessment.setDisabled(True)
        self.actionAdd_Strategy.setDisabled(True)
        self.actionRun_Current.setDisabled(True)
        self.actionRun_Themes.setDisabled(True)
        self.actionRun_Strategy.setDisabled(True)
        self.actionExport.setDisabled(True)
        self.actionExport_mask.setDisabled(True)
        self.actionImport.setDisabled(True)
        self.actionImport_skip.setDisabled(True)

        # Enable actions
        self.actionNew.setEnabled(True)
        self.actionOpen.setEnabled(True)

        # Close the strategy manager
        self._strategy_manager.close()

        # Clear the pipeline
        self._pipeline_dock._clear()
        self._pipeline_dock._clear_filter()
        self._pipeline_dock._set_title("Waiting...")
        self._pipeline_dock.scopeFrame.setDisabled(True)
        self._pipeline_dock.filterFrame.setDisabled(True)

        # Disable the simulation widget
        self._simulation_dock.setDisabled(True)
        self._simulation_dock._update_simulations(None)

        # Remove details widget from data context
        assert self._data_details is not None
        self._data_context._top_left_box.removeWidget(self._data_details)
        self._data_details.setParent(None)
        self._data_details.deleteLater()
        self._data_details = None

        # Remove file manager widget from data context
        assert self._data_file_manager is not None
        self._data_context._top_right_box.removeWidget(self._data_file_manager)
        self._data_file_manager.setParent(None)
        self._data_file_manager.deleteLater()
        self._data_file_manager = None

        # Remove details widget from plot context
        assert self._plot_details is not None
        self._plot_context._top_left_box.removeWidget(self._plot_details)
        self._plot_details.setParent(None)
        self._plot_details.deleteLater()
        self._plot_details = None

        # Remove plot manager widget from plot context
        assert self._plot_manager is not None
        self._plot_context._top_right_box.removeWidget(self._plot_manager)
        self._plot_manager.setParent(None)
        self._plot_manager.deleteLater()
        self._plot_manager = None

        # Remove level comparison widget from comparison context
        assert self._level_comparison is not None
        self._comp_context._top_left_box.removeWidget(self._level_comparison)
        self._level_comparison.setParent(None)
        self._level_comparison.deleteLater()
        self._level_comparison = None

        # Remove simulation comparison widget from comparison context
        assert self._sim_comparison is not None
        self._plot_context._top_right_box.removeWidget(self._sim_comparison)
        self._sim_comparison.setParent(None)
        self._sim_comparison.deleteLater()
        self._sim_comparison = None

        # Remove main widget from comparison context
        if self._comp_context._bottom_contents is not None:
            self._clear_bottom_contents(self._comp_context)

        # Update the central widget
        self.stackedWidget.setCurrentIndex(0)
        self._last_tree_controller = None
        self._last_data_controller = None
        self._last_data_controller_status = None
        self._last_plot_id = None
        self._last_plot_name = "auto"

        # Trigger the tool menu switcher (not likely concurrent)
        self._tool_menu_ui_switch(self._shell)

        # Reset the window title
        self._set_window_title("")

    @QtCore.Slot()
    def _active_filter_ui_switch(self):
        # Enable Actions
        self.actionInitiate_Bathymetry.setEnabled(True)

    @QtCore.Slot()
    def _active_pipeline_ui_switch(self):
        # Close dialog
        self._db_selector.close()
        self._unset_database_properties()

        # Disable Actions
        self.actionInitiate_Pipeline.setDisabled(True)
        self.actionSelect_Database.setDisabled(True)

        # Enabale Actions
        self.actionAdd_Modules.setEnabled(True)
        self.actionAdd_Assessment.setEnabled(True)
        self.actionInitiate_Dataflow.setEnabled(True)

        # Update the pipeline
        fresh_branch_map = [
            {"hub": SectionControl, "name": "Configuration"},
            {
                "hub": HubControl,
                "name": "Scenario",
                "args": [
                    "project",
                    InputBranchControl,
                    True,
                    [
                        "System Type Selection",
                        "Database Filtering Interface",
                        "Project Boundaries Interface",
                    ],
                ],
            },
            {
                "hub": HubControl,
                "name": "Modules",
                "args": ["modules", InputBranchControl, False],
            },
            {
                "hub": HubControl,
                "name": "Assessment",
                "args": ["themes", InputBranchControl, False],
            },
        ]

        self._pipeline_dock._set_branch_map(fresh_branch_map)
        self._pipeline_dock._refresh(self._shell)

    @QtCore.Slot()
    def _active_bathymetry_ui_switch(self):
        # Disable Actions
        self.actionInitiate_Bathymetry.setDisabled(True)

        # Update the pipeline
        self._pipeline_dock._refresh(self._shell)

    @QtCore.Slot()
    def _active_dataflow_ui_switch(self):
        assert self._level_comparison is not None
        assert self._sim_comparison is not None

        self._pipeline_dock._refresh(self._shell)

        # Close dialogs
        self._module_shuttle.close()
        self._assessment_shuttle.close()

        # Enable the simulation widget
        self._simulation_dock.setEnabled(True)

        # Setup and enable comparison context
        self._level_comparison._set_interfaces(self._shell)
        self._sim_comparison._set_interfaces(self._shell, include_str=True)

        self.actionComparison.setEnabled(True)

        # Enable Actions
        self.actionSave.setEnabled(True)
        self.actionSave_As.setEnabled(True)
        self.actionAdd_Strategy.setEnabled(True)
        self._run_action_ui_switch()

        # Disable Actions
        self.actionAdd_Modules.setDisabled(True)
        self.actionAdd_Assessment.setDisabled(True)
        self.actionInitiate_Dataflow.setDisabled(True)
        self.actionInitiate_Bathymetry.setDisabled(True)

    @QtCore.Slot(str)
    def _current_scope_ui_switch(self, scope):
        sane_scope = str(scope)

        if sane_scope == "global":
            self._pipeline_dock.globalRadioButton.setChecked(True)

        elif sane_scope == "local":
            self._pipeline_dock.localRadioButton.setChecked(True)

        else:
            errStr = (
                "Valid scopes are 'local' or 'global'. Passed scope " "was {}"
            ).format(sane_scope)
            raise ValueError(errStr)

    @QtCore.Slot()
    def _run_action_ui_switch(self):
        modules_scheduled = self._shell.get_scheduled_modules()
        modules_completed = self._shell.get_completed_modules()
        themes_scheduled = self._shell.get_scheduled_themes()
        strategy_run = False

        if self._shell.strategy is not None:
            strategy_run = self._shell.strategy.allow_run(
                self._shell.core, self._shell.project
            )

        # Set the run action buttons
        if strategy_run:
            self.actionRun_Current.setDisabled(True)
            self.actionRun_Themes.setDisabled(True)

            if modules_scheduled:
                self.actionRun_Strategy.setEnabled(True)
            else:
                self.actionRun_Strategy.setDisabled(True)

        else:
            self.actionRun_Strategy.setDisabled(True)

            if modules_scheduled:
                self.actionRun_Current.setEnabled(True)
            else:
                self.actionRun_Current.setDisabled(True)

            if themes_scheduled:
                self.actionRun_Themes.setEnabled(True)
            else:
                self.actionRun_Themes.setDisabled(True)

        # Set the pipeline title
        if not modules_completed and modules_scheduled:
            pipeline_msg = "Define simulation inputs..."
        elif modules_completed and modules_scheduled:
            pipeline_msg = "Simulation in progress..."
        elif modules_completed and not modules_scheduled:
            pipeline_msg = "Simulation complete..."
        elif (
            not modules_completed and not modules_scheduled and themes_scheduled
        ):
            pipeline_msg = "Assessment only mode..."
        elif (
            not modules_completed
            and not modules_scheduled
            and not themes_scheduled
        ):
            pipeline_msg = "No modules or assessments selected..."
        else:
            errStr = "Whoa, take 'er easy there, Pilgrim"
            raise SystemError(errStr)

        self._pipeline_dock._set_title(pipeline_msg)

    @QtCore.Slot()
    def _strategy_box_ui_switch(self):
        assert self._level_comparison is not None
        assert self._sim_comparison is not None

        checked = True
        enabled = False

        if self._shell.strategy is not None:
            checked = False
            enabled = True

        self._level_comparison.strategyBox.setChecked(checked)
        self._level_comparison.strategyBox.setEnabled(enabled)

        self._sim_comparison.strategyBox.setChecked(checked)
        self._sim_comparison.strategyBox.setEnabled(enabled)

    @QtCore.Slot(int)
    def _sim_comparison_ui_switch(self, box_number):
        assert self._sim_comparison is not None

        if box_number == -1:
            self._sim_comparison.setDisabled(True)
        else:
            self._sim_comparison.setEnabled(True)

    @QtCore.Slot(object)
    def _tool_menu_ui_switch(self, shell):
        for tool_name, action in self._dynamic_actions.items():
            tool = self._tool_manager.get_tool(tool_name)

            if self._tool_manager.can_execute_tool(
                shell.core, shell.project, tool
            ):
                action.setEnabled(True)

            else:
                action.setDisabled(True)

    @QtCore.Slot()
    def _set_module_shuttle(self):
        self._module_shuttle._add_items_from_lists(
            self._shell.get_available_modules(),
            self._shell.get_active_modules(),
        )

        self._module_shuttle.show()

    @QtCore.Slot()
    def _set_assessment_shuttle(self):
        self._assessment_shuttle._add_items_from_lists(
            self._shell.get_available_themes(), self._shell.get_active_themes()
        )

        self._assessment_shuttle.show()

    @QtCore.Slot()
    def _set_strategy(self):
        self._strategy_manager.show()
        return

    @QtCore.Slot(object, int)
    def _set_details_widget(self, proxy_index):
        assert self._data_details is not None
        assert self._plot_details is not None

        controller = self._pipeline_dock._find_controller(proxy_index)

        if isinstance(controller, (InputVarControl, OutputVarControl)):
            # Collect the meta data from the variable
            meta = controller._variable.get_metadata(self._shell.core)
            title = meta.title
            description = meta.description

        else:
            title = None
            description = None

        self._data_details._set_details(title, description)
        self._plot_details._set_details(title, description)

    @QtCore.Slot(object, bool)
    def _set_context_widget(self, proxy_index_or_controller, reset=False):
        controller = None

        # reset all the stored controllers and update given controller
        if reset:
            self._last_tree_controller = None
            self._last_data_controller = None
            self._last_data_controller_status = None
            self._force_plot = True

            if proxy_index_or_controller is not None:
                model_index = (
                    proxy_index_or_controller._get_index_from_address()
                )
                proxy_index_or_controller = (
                    proxy_index_or_controller._proxy.mapFromSource(model_index)
                )

        # Return a controller class
        if proxy_index_or_controller is not None:
            # If this is a proxy index then get the controller
            if isinstance(proxy_index_or_controller, QtCore.QModelIndex):
                proxy_index = proxy_index_or_controller
                controller = self._pipeline_dock._find_controller(proxy_index)
            else:
                controller = proxy_index_or_controller

        # If given a hidden variable then reset to the pipeline root
        if controller is not None and controller._is_hidden():
            controller = self._pipeline_dock._controls[0]

        current_context_action = self.contextGroup.checkedAction()

        if current_context_action is None:
            pass

        elif str(current_context_action.text()) == "Data":
            self._set_data_widget(controller)
            self._set_file_manager_widget(controller)

        elif str(current_context_action.text()) == "Plots":
            self._set_plot_widget(controller, force_plot=self._force_plot)
            self._set_plot_manager_widget(controller)
            self._force_plot = False

        self._last_tree_controller = controller

    def _set_file_manager_widget(self, controller):
        # Avoid being in a race where the data file manager is None
        if self._data_file_manager is None:
            return

        current_context_action = self.contextGroup.checkedAction()

        if (
            current_context_action is None
            or str(current_context_action.text()) == "Plots"
        ):
            return

        variable = None

        load_ext_dict = {}

        if isinstance(controller, InputVarControl):
            variable = controller._variable

            interface_dict = controller._variable.get_file_input_interfaces(
                self._shell.core, include_auto=True
            )

            if interface_dict:
                for interface_name, ext_list in interface_dict.items():
                    repeated_exts = set(ext_list).intersection(
                        load_ext_dict.keys()
                    )

                    if repeated_exts:
                        extsStr = ", ".join(repeated_exts)
                        errStr = (
                            "Repeated interface extensions '{}'" "found"
                        ).format(extsStr)

                        raise RuntimeError(errStr)

                    interface_exts = {ext: interface_name for ext in ext_list}

                    load_ext_dict.update(interface_exts)

        save_ext_dict = {}

        if isinstance(controller, (InputVarControl, OutputVarControl)):
            variable = controller._variable

            interface_dict = controller._variable.get_file_output_interfaces(
                self._shell.core, self._shell.project, include_auto=True
            )

            if interface_dict:
                for interface_name, ext_list in interface_dict.items():
                    repeated_exts = set(ext_list).intersection(
                        save_ext_dict.keys()
                    )

                    if repeated_exts:
                        extsStr = ", ".join(repeated_exts)
                        errStr = (
                            "Repeated interface extensions '{}'" "found"
                        ).format(extsStr)

                        raise RuntimeError(errStr)

                    interface_exts = {ext: interface_name for ext in ext_list}

                    save_ext_dict.update(interface_exts)

        if not load_ext_dict:
            load_ext_dict = None
        if not save_ext_dict:
            save_ext_dict = None

        if self._data_file_manager._load_connected:
            self._data_file_manager.load_file.disconnect()
            self._data_file_manager._load_connected = False

        if self._data_file_manager._save_connected:
            self._data_file_manager.save_file.disconnect()
            self._data_file_manager._save_connected = False

        self._data_file_manager.set_files(
            variable, load_ext_dict, save_ext_dict
        )

        if self._data_file_manager._file_mode is None:
            return

        if isinstance(controller, InputVarControl):
            self._data_file_manager.load_file.connect(self._shell.read_file)
            self._data_file_manager._load_connected = True

        if isinstance(controller, (InputVarControl, OutputVarControl)):
            self._data_file_manager.save_file.connect(self._shell.write_file)
            self._data_file_manager._save_connected = True

    def _set_plot_manager_widget(self, controller):
        # Avoid race condition
        if self._plot_manager is None:
            return

        current_context_action = self.contextGroup.checkedAction()

        if (
            current_context_action is None
            or str(current_context_action.text()) == "Data"
        ):
            return

        plot_list = []
        plot_auto = False

        if isinstance(controller, (InputVarControl, OutputVarControl)):
            plot_list = controller._variable.get_available_plots(
                self._shell.core, self._shell.project
            )

            all_interfaces = controller._variable._get_receivers(
                self._shell.core,
                self._shell.project,
                "PlotInterface",
                "AutoPlot",
            )

            if set(all_interfaces) - set(plot_list):
                plot_auto = True

        if self._plot_manager._plot_connected:
            self._plot_manager.plot.disconnect()
            self._plot_manager.save.disconnect()
            self._plot_manager._plot_connected = False

        if not plot_list:
            plot_list = None

        self._plot_manager._set_plots(controller, plot_list, plot_auto)

        if plot_list is None and not plot_auto:
            return

        if isinstance(controller, (InputVarControl, OutputVarControl)):
            self._plot_manager.plot.connect(self._set_plot_widget)
            self._plot_manager.save.connect(self._save_plot)
            self._plot_manager._plot_connected = True

    def _set_data_widget(self, controller):
        if controller is None:
            if self._data_context._bottom_contents is not None:
                self._clear_bottom_contents(self._data_context)
                self._last_data_controller = None

            return

        if (
            self._last_data_controller is not None
            and controller._id == self._last_data_controller._id
            and type(controller) is type(self._last_data_controller)
        ):
            if (
                controller._status is not None
                and controller._status != self._last_data_controller_status
                and "unavailable" in controller._status
            ):
                assert self._data_context._bottom_contents is not None
                self._data_context._bottom_contents.setDisabled(True)
                self._last_data_controller_status = controller._status

            return

        if self._data_context._bottom_contents is not None:
            self._clear_bottom_contents(self._data_context)

        self._last_data_controller = controller

        widget = controller._get_data_widget(self._shell)

        if widget is None:
            return

        # Add the widget to the context
        self._data_context._bottom_box.addWidget(widget)
        self._data_context._bottom_contents = widget

        # Connect the widgets read and nullify events
        widget._get_read_event().connect(
            lambda: self._read_raw(controller._variable, widget._get_result())
        )

        widget._get_nullify_event().connect(
            lambda: self._read_raw(controller._variable, None)
        )

        if "unavailable" in controller._status:
            if "_disable" in dir(widget):
                widget._disable()
            else:
                widget.setDisabled(True)

    @QtCore.Slot(object, str)
    def _set_plot_widget(self, controller, plot_name=None, force_plot=False):
        if controller is None:
            if self._plot_context._bottom_contents is not None:
                self._clear_bottom_contents(self._plot_context)
                self._last_plot_id = None
                self._last_plot_name = "auto"

            return

        if (
            controller._id == self._last_plot_id
            and plot_name == self._last_plot_name
            and not force_plot
        ):
            return

        if controller._id == self._last_plot_id and plot_name is None:
            plot_name = self._last_plot_name

        if plot_name == "auto":
            plot_name = None

        if self._plot_context._bottom_contents is not None:
            self._clear_bottom_contents(self._plot_context)

        self._last_plot_id = controller._id
        self._last_plot_name = plot_name

        widget = controller._get_plot_widget(self._shell, plot_name)

        if widget is None:
            return

        # Add the widget to the context
        self._plot_context._bottom_box.addWidget(widget)
        self._plot_context._bottom_contents = widget

        # Draw the widget
        widget.draw_idle()

        if len(plt.get_fignums()) > 3:
            num_strs = ["{}".format(x) for x in plt.get_fignums()]
            num_str = ", ".join(num_strs)
            err_msg = (
                "Too many matplotlib figures detected. " "Numbers: {}"
            ).format(num_str)

            raise RuntimeError(err_msg)

        if "unavailable" in controller._status:
            widget.setDisabled(True)

    @QtCore.Slot(object, str, object, object)
    def _save_plot(self, controller, file_path, size, plot_name="auto"):
        if controller is None:
            return
        if plot_name == "auto":
            plot_name = None

        controller._save_plot(self._shell, file_path, size, plot_name)

        if len(plt.get_fignums()) > 3:
            num_strs = ["{}".format(x) for x in plt.get_fignums()]
            num_str = ", ".join(num_strs)
            err_msg = (
                "Too many matplotlib figures detected. " "Numbers: {}"
            ).format(num_str)

            raise RuntimeError(err_msg)

    @QtCore.Slot(str, bool)
    def _set_level_plot(self, var_id, ignore_strategy):
        assert self._level_comparison is not None
        assert self._sim_comparison is not None

        # Sanitise var_id
        var_id = str(var_id)

        # Collect the current scope
        if self._pipeline_dock.globalRadioButton.isChecked():
            scope = "global"
        elif self._pipeline_dock.localRadioButton.isChecked():
            scope = "local"
        else:
            errStr = "Feck!"
            raise SystemError(errStr)

        if self._comp_context._bottom_contents is not None:
            self._clear_bottom_contents(self._comp_context)

            # Switch off save button
            assert self._level_comparison is not None

            self._level_comparison.buttonBox.button(
                QtWidgets.QDialogButtonBox.StandardButton.Save
            ).setDisabled(True)

        # Collect the sim titles from the sim dock
        sim_titles = self._simulation_dock._get_list_values()

        # Get the plot figure
        widget = self._strategy_manager.get_level_values_plot(
            self._shell, var_id, scope, ignore_strategy, sim_titles
        )

        # Add the widget to the context
        self._comp_context._bottom_box.addWidget(widget)
        self._comp_context._bottom_contents = widget

        # Draw the widget
        widget.draw_idle()

        if len(plt.get_fignums()) > 3:
            num_strs = ["{}".format(x) for x in plt.get_fignums()]
            num_str = ", ".join(num_strs)
            err_msg = (
                "Too many matplotlib figures detected. " "Numbers: {}"
            ).format(num_str)

            raise RuntimeError(err_msg)

        # Switch on save button
        self._sim_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setDisabled(True)
        self._level_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setEnabled(True)

    @QtCore.Slot(str, bool)
    def _set_level_table(self, var_id, ignore_strategy):
        assert self._level_comparison is not None
        assert self._sim_comparison is not None

        # Sanitise var_id
        var_id = str(var_id)

        # Collect the current scope
        if self._pipeline_dock.globalRadioButton.isChecked():
            scope = "global"
        elif self._pipeline_dock.localRadioButton.isChecked():
            scope = "local"
        else:
            errStr = "Feck!"
            raise SystemError(errStr)

        if self._comp_context._bottom_contents is not None:
            self._clear_bottom_contents(self._comp_context)

            # Switch off save button
            self._level_comparison.buttonBox.button(
                QtWidgets.QDialogButtonBox.StandardButton.Save
            ).setDisabled(True)

        # Get the table widget
        widget = self._strategy_manager.get_level_values_df(
            self._shell, var_id, scope, ignore_strategy
        )

        # Add the widget to the context
        self._comp_context._bottom_box.addWidget(widget)
        self._comp_context._bottom_contents = widget

        # Switch on save button
        self._sim_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setDisabled(True)
        self._level_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setEnabled(True)

    @QtCore.Slot(str, str, bool)
    def _set_sim_plot(self, var_one_id, module, ignore_strategy):
        assert self._level_comparison is not None
        assert self._sim_comparison is not None

        # Sanitise strings
        var_one_id = str(var_one_id)
        module = str(module)

        # Get the first variable id from the level comparison widget
        var_two_name = str(self._level_comparison.varBox.currentText())
        var_two_id = self._level_comparison._get_var_id(var_two_name)

        # Collect the current scope
        if self._pipeline_dock.globalRadioButton.isChecked():
            scope = "global"
        elif self._pipeline_dock.localRadioButton.isChecked():
            scope = "local"
        else:
            errStr = "Feck!"
            raise SystemError(errStr)

        if self._comp_context._bottom_contents is not None:
            self._clear_bottom_contents(self._comp_context)

            # Switch off save button
            self._sim_comparison.buttonBox.button(
                QtWidgets.QDialogButtonBox.StandardButton.Save
            ).setDisabled(True)

        # Get the plot figure
        widget = self._strategy_manager.get_comparison_values_plot(
            self._shell, var_one_id, var_two_id, module, scope, ignore_strategy
        )

        # Add the widget to the context
        self._comp_context._bottom_box.addWidget(widget)
        self._comp_context._bottom_contents = widget

        # Draw the widget
        widget.draw_idle()

        if len(plt.get_fignums()) > 3:
            num_strs = ["{}".format(x) for x in plt.get_fignums()]
            num_str = ", ".join(num_strs)
            err_msg = (
                "Too many matplotlib figures detected. " "Numbers: {}"
            ).format(num_str)

            raise RuntimeError(err_msg)

        # Switch save buttons
        self._level_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setDisabled(True)
        self._sim_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setEnabled(True)

    @QtCore.Slot(str, str, bool)
    def _set_sim_table(self, var_one_id, module, ignore_strategy):
        assert self._level_comparison is not None
        assert self._sim_comparison is not None

        # Sanitise strings
        var_one_id = str(var_one_id)
        module = str(module)

        # Get the first variable id from the level comparison widget
        var_two_name = str(self._level_comparison.varBox.currentText())
        var_two_id = self._level_comparison._get_var_id(var_two_name)

        # Collect the current scope
        if self._pipeline_dock.globalRadioButton.isChecked():
            scope = "global"
        elif self._pipeline_dock.localRadioButton.isChecked():
            scope = "local"
        else:
            errStr = "Feck!"
            raise SystemError(errStr)

        if self._comp_context._bottom_contents is not None:
            self._clear_bottom_contents(self._comp_context)

            # Switch off save button
            self._sim_comparison.buttonBox.button(
                QtWidgets.QDialogButtonBox.StandardButton.Save
            ).setDisabled(True)

        # Get the table widget
        widget = self._strategy_manager.get_comparison_values_df(
            self._shell, var_one_id, var_two_id, module, scope, ignore_strategy
        )

        # Add the widget to the context
        self._comp_context._bottom_box.addWidget(widget)
        self._comp_context._bottom_contents = widget

        # Switch on save button
        self._sim_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setEnabled(True)
        self._level_comparison.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save
        ).setDisabled(True)

    @QtCore.Slot()
    def _save_comparison_plot(self):
        extlist = [
            "{} (*.{})".format(v, k) for k, v in get_current_filetypes().items()
        ]
        extStr = ";;".join(extlist)

        fdialog_msg = "Save plot"

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            fdialog_msg,
            HOME,
            extStr,
        )

        if save_path:
            save_current_figure(str(save_path))

    @QtCore.Slot()
    def _save_comparison_data(self):
        extlist = ["comma-separated values (*.csv)"]
        extStr = ";;".join(extlist)

        fdialog_msg = "Save data"

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            fdialog_msg,
            HOME,
            extStr,
        )

        if not save_path:
            return

        df = self._strategy_manager._last_df
        if df is None:
            return

        df.to_csv(str(save_path), index=False)

    @QtCore.Slot(object)
    def _read_raw(self, variable, value):
        self._shell.read_raw(variable, value)
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)

    @QtCore.Slot()
    def _new_project(self):
        self._shell.new_project()

    @QtCore.Slot()
    def _open_project(self):
        msg = "Open Project"
        valid_exts = "DTOcean Files (*.dto *.prj)"

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if not file_path:
            return

        if self._shell.project is not None:
            self._shell.close_project()

        self._waitcursor_open(file_path)

    @QtCore.Slot()
    def _open_project_finalize(self):
        if self._shell.project is None:
            return

        self._active_project_ui_switch()
        self._active_pipeline_ui_switch()

        # Recreate the existing branch map
        new_branch_map = [
            {"hub": SectionControl, "name": "Configuration"},
            {
                "hub": HubControl,
                "name": "Scenario",
                "args": [
                    "project",
                    InputBranchControl,
                    True,
                    [
                        "System Type Selection",
                        "Database Filtering Interface",
                        "Project Boundaries Interface",
                    ],
                ],
            },
            {
                "hub": HubControl,
                "name": "Modules",
                "args": ["modules", InputBranchControl, True],
            },
            {
                "hub": HubControl,
                "name": "Assessment",
                "args": ["themes", InputBranchControl, True],
            },
            {"hub": SectionControl, "name": "Results"},
            {
                "hub": HubControl,
                "name": "Assessment",
                "args": ["themes", OutputBranchControl, True],
            },
            {
                "hub": HubControl,
                "name": "Modules",
                "args": ["modules", OutputBranchControl, True],
            },
        ]

        self._pipeline_dock._set_branch_map(new_branch_map)
        self._active_dataflow_ui_switch()
        self._strategy_box_ui_switch()

        # Update the active project
        active_sim_title = self._shell.project.get_simulation_title()
        self._shell.project.active_title_changed.emit(active_sim_title)

        self._shell.core.status_updated.emit()
        self._set_project_saved()

    @QtCore.Slot()
    def _save_project(self):
        result = True

        if self._shell.project_path is None:
            result = self._saveas_project()
        else:
            self._waitcursor_save()

        return result

    @QtCore.Slot()
    def _saveas_project(self):
        msg = "Save Project"
        valid_exts = (
            "DTOcean Application File (*.dto);;" "DTOcean Project File (*.prj)"
        )

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        result = False

        if file_path:
            self._waitcursor_save(file_path)
            result = True

        return result

    @QtCore.Slot()
    def _close_project(self):
        reply = self._project_close_warning()

        if (
            reply == QtWidgets.QMessageBox.StandardButton.Save
            or reply == QtWidgets.QMessageBox.StandardButton.Discard
        ):
            self._shell.close_project()

    @QtCore.Slot(str, str, dict)
    def _dump_database(self, root_path, selected, credentials):
        self._shell.dump_database(root_path, selected, credentials)
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)

    @QtCore.Slot(str, str, dict)
    def _load_database(self, root_path, selected, credentials):
        self._shell.load_database(root_path, selected, credentials)
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)

    @QtCore.Slot()
    def _export_data(self):
        msg = "Export Data"
        valid_exts = "Datastate Files (*.dts)"

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if file_path:
            self._shell.export_data(file_path)

    @QtCore.Slot()
    def _export_data_mask(self):
        msg = "Export Data (Mask Outputs)"
        valid_exts = "Datastate Files (*.dts)"

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if file_path:
            self._shell.export_data(file_path, True)

    @QtCore.Slot()
    def _import_data(self):
        msg = "Import Data"
        valid_exts = "Datastate Files (*.dts)"

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if file_path:
            self._shell.import_data(file_path)

    @QtCore.Slot()
    def _import_data_skip(self):
        msg = "Import Data (Skip Satisfied)"
        valid_exts = "Datastate Files (*.dts)"

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if file_path:
            self._shell.import_data(file_path, True)

    @QtCore.Slot()
    def _initiate_pipeline(self):
        # Find the "System Type Selection" branch
        branch_control = self._pipeline_dock._find_controller(
            controller_title="System Type Selection",
            controller_class=InputBranchControl,
        )

        if branch_control is None:
            raise RuntimeError("Pipeline initiation failed")

        # Check for required values
        required_address = branch_control._get_required_address(self._shell)

        # Remap OK button
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.disconnect()
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._shell.initiate_pipeline)
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._data_check.accept)

        self._data_check.show(required_address)

    @QtCore.Slot()
    def _initiate_bathymetry(self):
        if self._shell.project_menu.is_executable(
            self._shell.core, self._shell.project, "Site Boundary Selection"
        ):
            required_address = None

        else:
            raw_required = {
                "Section": ["Scenario"],
                "Branch": ["Database Filtering Interface"],
                "Item": ["Selected Site"],
            }

            required_address = pd.DataFrame(raw_required)

        # Remap OK button
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.disconnect()
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._shell.initiate_bathymetry)
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._data_check.accept)

        self._data_check.show(required_address)

    @QtCore.Slot()
    def _initiate_dataflow(self):
        required_address = None

        # Check if filters can be initiated
        if (
            "Database Filtering Interface"
            in self._shell.project_menu.get_active(
                self._shell.core, self._shell.project
            )
        ):
            # Find the "Database Filtering Interface" branch
            branch_control = self._pipeline_dock._find_controller(
                controller_title="Database Filtering Interface",
                controller_class=InputBranchControl,
            )

            if branch_control is None:
                raise RuntimeError("Database filtering failed")

            # Check for required values
            required_address = branch_control._get_required_address(self._shell)

        # Remap OK button
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.disconnect()
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._progress_dataflow)
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._data_check.accept)

        self._data_check.show(required_address)

    @QtCore.Slot()
    def _execute_current(self):
        # Close the strategy manager
        self._strategy_manager.close()

        # Get the current module name
        current_mod = self._shell.get_current_module()

        # Find the module branch
        branch_control = self._pipeline_dock._find_controller(
            controller_title=current_mod, controller_class=InputBranchControl
        )

        if branch_control is None:
            raise RuntimeError("Module execution ordering failed")

        # Check for required values
        required_address = branch_control._get_required_address(self._shell)

        # Find any required values for any themes:
        all_themes = self._shell.get_active_themes()

        for theme_name in all_themes:
            branch_control = self._pipeline_dock._find_controller(
                controller_title=theme_name, controller_class=InputBranchControl
            )

            if branch_control is None:
                raise RuntimeError("Theme execution ordering failed")

            # Check for required values
            theme_address = branch_control._get_required_address(self._shell)

            # Loop if None
            if theme_address is None:
                continue

            # Otherwise merge
            if required_address is None:
                required_address = theme_address
            else:
                required_address = pd.concat(
                    [required_address, theme_address], ignore_index=True
                )

        # Remap OK button
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.disconnect()
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._progress_current)
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._data_check.accept)

        self._data_check.show(required_address)

    @QtCore.Slot()
    def _execute_themes(self):
        # Close the strategy manager
        self._strategy_manager.close()

        # Check for required values
        required_address = None

        # Find any required values for any themes:
        all_themes = self._shell.get_active_themes()

        for theme_name in all_themes:
            branch_control = self._pipeline_dock._find_controller(
                controller_title=theme_name, controller_class=InputBranchControl
            )

            if branch_control is None:
                raise RuntimeError("Theme execution ordering failed")

            # Check for required values
            theme_address = branch_control._get_required_address(self._shell)

            # Loop if None
            if theme_address is None:
                continue

            # Otherwise merge
            if required_address is None:
                required_address = theme_address
            else:
                required_address = pd.concat(
                    [required_address, theme_address], ignore_index=True
                )

        # Remap OK button
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.disconnect()
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._progress_themes)
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._data_check.accept)

        self._data_check.show(required_address)

    @QtCore.Slot()
    def _execute_strategy(self):
        # Close the strategy manager
        self._strategy_manager.close()

        # Get the current module name
        scheduled_mods = self._shell.get_scheduled_modules()

        required_address = None

        for scheduled_mod in scheduled_mods:
            # Find the module branch
            branch_control = self._pipeline_dock._find_controller(
                controller_title=scheduled_mod,
                controller_class=InputBranchControl,
            )

            if branch_control is None:
                raise RuntimeError("Strategy execution ordering failed")

            # Check for required values
            mod_address = branch_control._get_required_address(self._shell)

            # Loop if None
            if mod_address is None:
                continue

            # Otherwise merge
            if required_address is None:
                required_address = mod_address
            else:
                required_address = pd.concat(
                    [required_address, mod_address], ignore_index=True
                )

        # Find any required values for any themes:
        all_themes = self._shell.get_active_themes()

        for theme_name in all_themes:
            branch_control = self._pipeline_dock._find_controller(
                controller_title=theme_name, controller_class=InputBranchControl
            )

            if branch_control is None:
                raise RuntimeError("Theme execution ordering failed")

            # Check for required values
            theme_address = branch_control._get_required_address(self._shell)

            # Loop if None
            if theme_address is None:
                continue

            # Otherwise merge
            if required_address is None:
                required_address = theme_address
            else:
                required_address = pd.concat(
                    [required_address, theme_address], ignore_index=True
                )

        # Remap OK button
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.disconnect()
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._progress_strategy)
        self._data_check.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._data_check.accept)

        self._data_check.show(required_address)

    @QtCore.Slot(str)
    def _waitcursor_open(self, file_path):
        self.setEnabled(False)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(Qt.CursorShape.WaitCursor)
        )

        self._shell.open_project(file_path)
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)
        self._shell._active_thread.finished.connect(self._open_project_finalize)
        self._shell._active_thread.finished.connect(self._reset_cursor)

    @QtCore.Slot(str)
    def _waitcursor_save(self, file_path=None):
        self.setEnabled(False)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(Qt.CursorShape.WaitCursor)
        )

        self._shell.save_project(file_path)
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)
        self._shell._active_thread.finished.connect(self._reset_cursor)

    @QtCore.Slot()
    def _progress_dataflow(self):
        # Recreate the existing branch map
        new_branch_map = [
            {"hub": SectionControl, "name": "Configuration"},
            {
                "hub": HubControl,
                "name": "Scenario",
                "args": [
                    "project",
                    InputBranchControl,
                    True,
                    [
                        "System Type Selection",
                        "Database Filtering Interface",
                        "Project Boundaries Interface",
                    ],
                ],
            },
            {
                "hub": HubControl,
                "name": "Modules",
                "args": ["modules", InputBranchControl, True],
            },
            {
                "hub": HubControl,
                "name": "Assessment",
                "args": ["themes", InputBranchControl, True],
            },
            {"hub": SectionControl, "name": "Results"},
            {
                "hub": HubControl,
                "name": "Assessment",
                "args": ["themes", OutputBranchControl, True],
            },
            {
                "hub": HubControl,
                "name": "Modules",
                "args": ["modules", OutputBranchControl, True],
            },
        ]

        self._pipeline_dock._set_branch_map(new_branch_map)

        self._progress.allow_close = False
        self._progress.set_pulsing()

        self._shell.initiate_dataflow(self._pipeline_dock)
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)
        self._shell._active_thread.finished.connect(self._close_progress)

        self._progress.show()

    @QtCore.Slot()
    def _progress_current(self):
        self._progress.allow_close = False
        self._progress.set_pulsing()

        self._shell.execute_current()
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)
        self._shell._active_thread.finished.connect(self._close_progress)

        self._progress.show()

    @QtCore.Slot()
    def _progress_themes(self):
        self._progress.allow_close = False
        self._progress.set_pulsing()

        self._shell.execute_themes()
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)
        self._shell._active_thread.finished.connect(self._close_progress)

        self._progress.show()

    @QtCore.Slot()
    def _progress_strategy(self):
        self._last_stack_index = self.stackedWidget.currentIndex()
        self.stackedWidget.setCurrentIndex(0)

        self._progress.allow_close = False
        self._progress.set_pulsing()

        self._shell.execute_strategy()
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)
        self._shell._active_thread.finished.connect(self._close_progress)

        self._progress.show()

    @QtCore.Slot(str)
    def _waitcursor_scope(self, scope):
        self.setEnabled(False)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(Qt.CursorShape.WaitCursor)
        )

        self._shell.set_output_scope(scope)
        assert self._shell._active_thread is not None
        self._shell._active_thread.error_detected.connect(self._display_error)
        self._shell._active_thread.finished.connect(self._reset_cursor)

    @QtCore.Slot(str)
    def _open_tool(self, tool_name):
        if self._thread_tool is not None:
            return

        # Pick up the tool
        tool = self._tool_manager.get_tool(tool_name)

        self._thread_tool = ThreadTool(
            self._shell.core, self._shell.project, tool
        )
        self._thread_tool.start()
        self._thread_tool.error_detected.connect(self._display_error)
        self._thread_tool.finished.connect(lambda: self._close_tool(tool))

    @QtCore.Slot()
    def _reset_cursor(self):
        QtWidgets.QApplication.restoreOverrideCursor()
        self.setEnabled(True)

    @QtCore.Slot(object)
    def _close_tool(self, tool):
        if tool.has_widget():
            widget = tool.get_widget()

            if widget is not None:
                widget.setWindowModality(Qt.WindowModality.ApplicationModal)
                widget.show()
                widget.closing.connect(lambda: self._close_tool_widget(tool))
                self._tool_widget = widget

        self._thread_tool = None

    @QtCore.Slot(object)
    def _close_tool_widget(self, tool):
        self._tool_widget = None
        tool.destroy_widget()
        return

    @QtCore.Slot()
    def _close_progress(self):
        self._progress.allow_close = True
        self._progress.close()

    @QtCore.Slot(object, object, object)
    def _display_error(self, etype, evalue, etraceback):
        type_str = str(etype)
        type_strs = type_str.split(".")
        sane_type_str = type_strs[-1].replace("'>", "")

        if sane_type_str[0].lower() in "aeiou":
            article = "An"
        else:
            article = "A"

        errMsg = "{} {} occurred: {}".format(article, sane_type_str, evalue)

        module_logger.critical(errMsg)
        module_logger.critical("".join(traceback.format_tb(etraceback)))
        QtWidgets.QMessageBox.critical(self, "ERROR", errMsg)

    def _project_close_warning(self):
        if (
            self._shell.project is None
            or not self.actionSave.isEnabled()
            or not self._shell.project_unsaved
        ):
            return QtWidgets.QMessageBox.StandardButton.Discard

        qstr = "Do you want to save your changes?"

        reply = QtWidgets.QMessageBox.warning(
            self,
            "Project modified",
            qstr,
            QtWidgets.QMessageBox.StandardButton.Save
            | QtWidgets.QMessageBox.StandardButton.Discard
            | QtWidgets.QMessageBox.StandardButton.Cancel,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Save:
            if not self._save_project():
                reply = QtWidgets.QMessageBox.StandardButton.Cancel

        return reply

    def closeEvent(self, event):
        # Check for active thread
        if (
            self._shell._active_thread is not None
            or self._thread_tool is not None
        ):
            qstr = (
                "Quitting now may cause DATA CORRUPTION or\n"
                "LOSS OF RESULTS! Are you sure?"
            )

            reply = QtWidgets.QMessageBox.critical(
                self,
                "Active thread detected",
                qstr,
                QtWidgets.QMessageBox.StandardButton.Yes,
                QtWidgets.QMessageBox.StandardButton.No
                | QtWidgets.QMessageBox.StandardButton.Default,
            )

            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                sys.excepthook = sys.__excepthook__
                event.accept()
            elif reply == QtWidgets.QMessageBox.StandardButton.No:
                event.ignore()
                return
            else:
                err_msg = "Sooner or later, everyone comes to Babylon 5"
                raise ValueError(err_msg)

        # Check for open project
        reply = self._project_close_warning()

        if reply == QtWidgets.QMessageBox.StandardButton.Cancel:
            event.ignore()
        else:
            event.accept()

    @staticmethod
    def _clear_bottom_contents(context):
        context._bottom_box.removeWidget(context._bottom_contents)
        context._bottom_contents.setParent(None)

        if isinstance(context._bottom_contents, MPLWidget):
            fignum = context._bottom_contents.figure.number  # type: ignore
            n_figs = len(plt.get_fignums())

            log_msg = "Closing figure {} ({} open)".format(fignum, n_figs)
            module_logger.debug(log_msg)

            Shiboken.delete(context._bottom_contents)
            plt.close(fignum)

        else:
            Shiboken.delete(context._bottom_contents)

        context._bottom_contents = None
