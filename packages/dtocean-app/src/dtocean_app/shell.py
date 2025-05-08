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

import json
import logging
import os
import shutil
import sys
import tarfile
import tempfile
import threading
from collections import namedtuple
from typing import Any, Optional

from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import set_output_scope
from dtocean_core.utils.database import (
    database_from_files,
    database_to_files,
    filter_map,
    get_database,
    get_table_map,
)
from PySide6 import QtCore

from dtocean_plugins.strategy_guis.base import GUIStrategy

from .core import GUICore, GUIProject
from .extensions import GUIStrategyManager

# Set up logging
module_logger = logging.getLogger(__name__)

# Check if running coverage
RUNNING_COVERAGE = "coverage" in sys.modules


class ThreadReadRaw(QtCore.QThread):
    """QThread for reading raw data"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, shell, variable, value):
        super().__init__()
        self._shell = shell
        self._variable = variable
        self._value = value

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            self._variable.set_raw_interface(self._shell.core, self._value)
            self._variable.read(self._shell.core, self._shell.project)
            self.taskFinished.emit()
        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)
            self.taskFinished.emit()


class ThreadReadTest(QtCore.QThread):
    """QThread for reading test data"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, shell, control, path, overwrite):
        super().__init__()
        self.shell = shell
        self.control = control
        self.path = path
        self.overwrite = overwrite

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            self.control._read_test_data(self.shell, self.path, self.overwrite)
            self.taskFinished.emit()
        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)
            self.taskFinished.emit()


class ThreadOpen(QtCore.QThread):
    """QThread for opening save files"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, core, file_path):
        super().__init__()
        self._core = core
        self._file_path = file_path
        self._project = None
        self._current_scope = None
        self._activated_interfaces: dict[str, list[Any]] = {}
        self._strategy = None
        self._project_path = None

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            load_path = str(self._file_path)
            dto_dir_path = None
            prj_file_path = None
            sco_file_path = None
            stg_file_path = None
            int_file_path = None

            # Check the extension
            if os.path.splitext(load_path)[1] == ".dto":
                dto_dir_path = tempfile.mkdtemp()
                tar = tarfile.open(load_path)
                tar.extractall(dto_dir_path, filter="data")

                prj_file_path = os.path.join(dto_dir_path, "project.prj")
                sco_file_path = os.path.join(dto_dir_path, "scope.json")
                stg_file_path = os.path.join(dto_dir_path, "strategy.pkl")
                int_file_path = os.path.join(dto_dir_path, "interfaces.json")

                if not os.path.isfile(stg_file_path):
                    stg_file_path = None
                if not os.path.isfile(int_file_path):
                    int_file_path = None

            elif os.path.splitext(load_path)[1] == ".prj":
                prj_file_path = load_path

            else:
                errStr = (
                    "The file path must be a file with either .dto or "
                    ".prj extension"
                )
                raise ValueError(errStr)

            # Load up the project
            load_project = self._core.load_project(prj_file_path)
            self._project = load_project

            # Load up the scope if one was found
            if sco_file_path is not None:
                with open(sco_file_path, "rb") as json_file:
                    self._current_scope = json.load(json_file)

            else:
                self._current_scope = "global"

            # Load up the activated interfaces if found
            if int_file_path is not None:
                with open(int_file_path, "rb") as json_file:
                    self._activated_interfaces = json.load(json_file)

            else:
                self._activated_interfaces = {}

            # Load up the strategy if one was found
            if stg_file_path is not None:
                strategy_manager = GUIStrategyManager(None)
                self._strategy = strategy_manager.load_strategy(
                    stg_file_path, load_project
                )

            else:
                self._strategy = None

            # Record the path after a successful load
            self._project_path = load_path

            # Delete temp directory
            if dto_dir_path is not None:
                shutil.rmtree(dto_dir_path)

            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)

            self.taskFinished.emit()


class ThreadSave(QtCore.QThread):
    """QThread for saving files"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(
        self,
        core,
        project,
        save_path,
        current_scope,
        activated_interfaces,
        strategy,
    ):
        super().__init__()
        self._core = core
        self._project = project
        self._save_path = save_path
        self._current_scope = current_scope
        self._activated_interfaces = activated_interfaces
        self._strategy = strategy

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            if self._save_path is None:
                errStr = (
                    "A file path must be provided in order to save a " "project"
                )
                raise ValueError(errStr)

            # Check the extension
            if os.path.splitext(self._save_path)[1] not in [".dto", ".prj"]:
                errStr = (
                    "The file path must be a file with either .dto or "
                    ".prj extension"
                )
                raise ValueError(errStr)

            dto_dir_path = tempfile.mkdtemp()

            # Dump the project
            prj_file_path = os.path.join(dto_dir_path, "project.prj")
            self._core.dump_project(self._project, prj_file_path)

            # If saving a project file only
            if os.path.splitext(self._save_path)[1] == ".prj":
                shutil.move(prj_file_path, self._save_path)
                shutil.rmtree(dto_dir_path)

                self.taskFinished.emit()

                return

            # Dump the output scope
            sco_file_path = os.path.join(dto_dir_path, "scope.json")

            with open(sco_file_path, "w") as json_file:
                json.dump(self._current_scope, json_file)

            # Set the standard archive contents
            arch_files = [prj_file_path, sco_file_path]
            arch_paths = ["project.prj", "scope.json"]

            # Dump the activated interfaces
            if self._activated_interfaces:
                int_file_path = os.path.join(dto_dir_path, "interfaces.json")

                with open(int_file_path, "w") as json_file:
                    json.dump(self._activated_interfaces, json_file)

                # Set the standard archive contents
                arch_files.append(int_file_path)
                arch_paths.append("interfaces.json")

            # Dump the strategy (if there is one)
            if self._strategy is not None:
                strategy_manager = GUIStrategyManager(None)
                stg_file_path = os.path.join(dto_dir_path, "strategy.pkl")
                strategy_manager.dump_strategy(self._strategy, stg_file_path)

                arch_files.append(stg_file_path)
                arch_paths.append("strategy.pkl")

            # Now tar the files together
            dto_file_name = os.path.split(self._save_path)[1]
            tar_file_name = "{}.tar".format(dto_file_name)

            archive = tarfile.open(tar_file_name, "w")

            for arch_file, arch_path in zip(arch_files, arch_paths):
                archive.add(arch_file, arcname=arch_path)

            archive.close()

            shutil.move(tar_file_name, self._save_path)
            shutil.rmtree(dto_dir_path)

            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)

            self.taskFinished.emit()


class ThreadDataFlow(QtCore.QThread):
    """QThread for initiating the dataflow"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, pipeline, shell):
        super().__init__()
        self.pipeline = pipeline
        self.shell = shell

        self.project_menu = ProjectMenu()

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            # Activate modules and themes
            self.shell.activate_module_queue()
            self.shell.activate_theme_queue()

            # Check if filters can be initiated
            if (
                "Database Filtering Interface"
                in self.shell.project_menu.get_active(
                    self.shell.core, self.shell.project
                )
            ):
                self.project_menu.initiate_filter(
                    self.shell.core, self.shell.project
                )

            self.project_menu.initiate_dataflow(
                self.shell.core, self.shell.project
            )

            # Execute the project boundaries interface
            if (
                "Project Boundaries Interface"
                in self.shell.project_menu.get_active(
                    self.shell.core, self.shell.project
                )
            ):
                self.shell.project_menu._execute(
                    self.shell.core,
                    self.shell.project,
                    "Project Boundaries Interface",
                )

            self.pipeline._read_auto(self.shell)

            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)
            self.taskFinished.emit()


class ThreadCurrent(QtCore.QThread):
    """QThread for executing the current module"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, core, project):
        super().__init__()
        self._core = core
        self._project = project

        self._module_menu = ModuleMenu()

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            # Block signals
            self._core.blockSignals(True)
            self._project.blockSignals(True)

            self._module_menu.execute_current(self._core, self._project)

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()


class ThreadThemes(QtCore.QThread):
    """QThread for executing all themes"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, core, project):
        super().__init__()
        self._core = core
        self._project = project

        self._theme_menu = ThemeMenu()

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            # Block signals
            self._core.blockSignals(True)
            self._project.blockSignals(True)

            self._theme_menu.execute_all(self._core, self._project)

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()


class ThreadStrategy(QtCore.QThread):
    """QThread for executing a strategy"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, core, project, strategy):
        super().__init__()
        self._core = core
        self._project = project
        self._strategy = strategy

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            # Block signals
            self._core.blockSignals(True)
            self._project.blockSignals(True)

            self._strategy.execute(self._core, self._project)

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()


class ThreadDump(QtCore.QThread):
    """QThread for executing database dump"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, credentials, root_path, selected):
        super().__init__()
        self._credentials = credentials
        self._root_path = root_path
        self._selected = selected

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            db = get_database(self._credentials, timeout=60)
            table_list = get_table_map()

            # Filter the table if required
            selected = str(self._selected).lower()

            if selected != "all":
                filtered_dict = filter_map(table_list, selected)
                table_list = [filtered_dict]

            # make a directory if required
            root_path = str(self._root_path)

            if not os.path.exists(root_path):
                os.makedirs(root_path)

            database_to_files(
                root_path, table_list, db, print_function=module_logger.info
            )

            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)
            self.taskFinished.emit()


class ThreadLoad(QtCore.QThread):
    """QThread for executing database dump"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, credentials, root_path, selected):
        super().__init__()
        self._credentials = credentials
        self._root_path = root_path
        self._selected = selected

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            db = get_database(self._credentials, timeout=60)
            table_list = get_table_map()

            # Filter the table if required
            selected = str(self._selected).lower()

            if selected != "all":
                filtered_dict = filter_map(table_list, selected)
                table_list = [filtered_dict]

            database_from_files(
                str(self._root_path),
                table_list,
                db,
                print_function=module_logger.info,
            )

            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)
            self.taskFinished.emit()


class ThreadScope(QtCore.QThread):
    """QThread for setting the output scope"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, core, project, scope):
        super().__init__()
        self._core = core
        self._project = project
        self._scope = scope

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            # Block signals
            self._core.blockSignals(True)
            self._project.blockSignals(True)

            # Switch the output scope on all simulations
            for sim_idx in range(len(self._project)):
                set_output_scope(
                    self._core, self._project, self._scope, sim_index=sim_idx
                )

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)

            # Reinstate signals and emit
            self._core.blockSignals(False)
            self._project.blockSignals(False)
            self.taskFinished.emit()


class Shell(QtCore.QObject):
    # Signals
    project_activated = QtCore.Signal()
    project_title_change = QtCore.Signal(str)
    project_saved = QtCore.Signal()
    project_closed = QtCore.Signal()
    strategy_loaded = QtCore.Signal(object)
    modules_queued = QtCore.Signal()
    themes_queued = QtCore.Signal()
    update_pipeline = QtCore.Signal(object)
    update_scope = QtCore.Signal(str)
    reset_widgets = QtCore.Signal()
    update_run_action = QtCore.Signal()
    database_updated = QtCore.Signal(str)
    pipeline_active = QtCore.Signal()
    bathymetry_active = QtCore.Signal()
    filter_active = QtCore.Signal()
    dataflow_active = QtCore.Signal()
    module_executed = QtCore.Signal()
    themes_executed = QtCore.Signal()
    strategy_selected = QtCore.Signal()
    strategy_executed = QtCore.Signal()
    database_convert_active = QtCore.Signal()
    database_convert_complete = QtCore.Signal()

    def __init__(self, core: GUICore):
        super().__init__()

        self.project: Optional[GUIProject] = None
        self.project_path: Optional[str] = None
        self.project_unsaved: bool = True
        self.strategy: Optional[GUIStrategy] = None
        self.queued_interfaces: dict[str, Optional[list[Any]]] = {
            "modules": None,
            "themes": None,
        }
        self.activated_interfaces: dict[str, list[Any]] = {}
        self._active_thread = None
        self._current_scope = None

        self.core = self._init_core(core)
        self.project_menu = self._init_project_menu()
        self.module_menu = self._init_module_menu()
        self.theme_menu = self._init_theme_menu()
        self.data_menu = self._init_data_menu()

        # Clean up after thread execution
        self.database_convert_complete.connect(self._clear_active_thread)
        self.dataflow_active.connect(self._clear_active_thread)
        self.module_executed.connect(self._finalize_core)
        self.themes_executed.connect(self._finalize_core)
        self.strategy_executed.connect(self._finalize_project)

    def _init_core(self, core):
        # Relay status updated signal
        core.status_updated.connect(self._emit_update_pipeline)
        core.status_updated.connect(lambda: self.reset_widgets.emit())

        # Relay pipeline reset signal
        core.pipeline_reset.connect(lambda: self.update_run_action.emit())

        return core

    def _init_project_menu(self):
        return ProjectMenu()

    def _init_module_menu(self):
        return ModuleMenu()

    def _init_theme_menu(self):
        return ThemeMenu()

    def _init_data_menu(self):
        return DataMenu()

    def set_project_title(self, title):
        if self.project is None:
            return

        self.project.title = title
        self.project_title_change.emit(title)

    def get_available_modules(self):
        available_modules = self.module_menu.get_available(
            self.core,
            self.project,
        )

        return available_modules

    def get_active_modules(self):
        if self.queued_interfaces["modules"] is not None:
            active_modules = self.queued_interfaces["modules"]
        else:
            active_modules = self.module_menu.get_active(
                self.core, self.project
            )

        return active_modules

    def get_current_module(self):
        module_name = self.module_menu.get_current(self.core, self.project)
        return module_name

    def get_scheduled_modules(self):
        module_names = self.module_menu.get_scheduled(self.core, self.project)
        return module_names

    def get_completed_modules(self):
        module_names = self.module_menu.get_completed(self.core, self.project)
        return module_names

    def get_available_themes(self):
        available_themes = self.theme_menu.get_available(
            self.core,
            self.project,
        )

        return available_themes

    def get_active_themes(self):
        if self.queued_interfaces["themes"] is not None:
            active_themes = self.queued_interfaces["themes"]
        else:
            active_themes = self.theme_menu.get_active(self.core, self.project)

        return active_themes

    def get_scheduled_themes(self):
        theme_names = self.theme_menu.get_scheduled(self.core, self.project)
        return theme_names

    @QtCore.Slot()
    def new_project(self, title="Untitled project"):
        self.project = self.project_menu.new_project(self.core, title)
        self.project_path = None

        # Update the active project
        self.project_activated.emit()

        # Relay active simulation change
        self.project.active_index_changed.connect(self._emit_update_pipeline)
        self.project.active_index_changed.connect(self.check_active_simulation)
        self.project.active_index_changed.connect(
            lambda: self.reset_widgets.emit()
        )
        self.project.active_index_changed.connect(
            lambda: self.update_run_action.emit()
        )

        self._current_scope = "global"

        # Update the scope widget
        self.update_scope.emit(self._current_scope)

    @QtCore.Slot(str)
    def open_project(self, file_path):
        self._active_thread = ThreadOpen(self.core, file_path)
        self._active_thread.taskFinished.connect(self._finalize_open_project)
        self._active_thread.start()

    #    @QtCore.Slot(str)
    #    def save_project(self, file_path=None):
    #        """An example of profiling"""
    #        import cProfile
    #        cProfile.runctx("self.save_project_(file_path)",
    #                        globals(),
    #                        locals(),
    #                        "profile.stat")

    @QtCore.Slot(str)
    def save_project(self, file_path=None):
        if self._active_thread is not None:
            self._active_thread.wait()

        if file_path is None:
            save_path = self.project_path
        else:
            save_path = str(file_path)

        self._active_thread = ThreadSave(
            self.core,
            self.project,
            save_path,
            self._current_scope,
            self.activated_interfaces,
            self.strategy,
        )
        self._active_thread.taskFinished.connect(self._finalize_save_project)
        self._active_thread.start()

    @QtCore.Slot()
    def close_project(self):
        if self._active_thread is not None:
            self._active_thread.wait()

        self.project = None
        self.project_path = None
        self.strategy = None

        self.project_closed.emit()
        self.project_title_change.emit("")
        self.database_updated.emit("None")
        self.update_pipeline.disconnect()

    @QtCore.Slot(str, str)
    def set_simulation_title(self, old_title, new_title):
        if self.project is None:
            return

        if self._active_thread is not None:
            self._active_thread.wait()
        if old_title == new_title:
            return

        msg = "Changing title of simulation {} to {}".format(
            old_title, new_title
        )
        module_logger.debug(msg)

        current_sim_titles = self.project.get_simulation_titles()

        if new_title in current_sim_titles:
            logMsg = (
                "Simulation title '{}' is already in list of current " "titles"
            ).format(new_title)
            module_logger.error(logMsg)

            # Reset the list in the simulation dock
            self.project.sims_updated.emit()

            # Simulation dock needs informed which is active after item reset
            active_sim_title = self.project.get_simulation_title()
            self.project.active_title_changed.emit(active_sim_title)

        else:
            self.project.set_simulation_title(new_title, title=old_title)

    @QtCore.Slot(str)
    def set_active_simulation(self, title):
        if self.project is None:
            return

        if self._active_thread is not None:
            self._active_thread.wait()

        msg = "Setting simulation '{}' as active".format(title)
        module_logger.debug(msg)

        self.project.set_active_index(title=title)

    @QtCore.Slot()
    def check_active_simulation(self):
        if not self.activated_interfaces:
            return

        if (
            "modules" not in self.activated_interfaces
            or self.activated_interfaces["modules"] is None
        ):
            activated_modules = []
        else:
            activated_modules = self.activated_interfaces["modules"]

        if (
            "themes" not in self.activated_interfaces
            or self.activated_interfaces["themes"] is None
        ):
            activated_themes = []
        else:
            activated_themes = self.activated_interfaces["themes"]

        # Check modules and themes of the simulation
        active_mods = self.module_menu.get_active(self.core, self.project)
        active_themes = self.theme_menu.get_active(self.core, self.project)

        warn = False

        if set(activated_modules) != set(active_mods):
            warn = True

        if set(activated_themes) != set(active_themes):
            warn = True

        if warn:
            msg_str = (
                "The modules or themes of the active simulation "
                "differ from those originally selected. Unexpected "
                "behaviour may occur!"
            )
            module_logger.warning(msg_str)

    @QtCore.Slot(str, dict)
    def select_database(self, identifier, credentials):
        if identifier is None:
            identifier = "Unnamed"

        self.data_menu.select_database(self.project, credentials=credentials)
        self.database_updated.emit(identifier)

    @QtCore.Slot()
    def deselect_database(self):
        self.data_menu.deselect_database(self.project)
        self.database_updated.emit("None")

    @QtCore.Slot(str, str, dict)
    def dump_database(self, root_path, selected, credentials):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadDump(credentials, root_path, selected)
        self._active_thread.start()

        self.database_convert_active.emit()
        self._active_thread.taskFinished.connect(
            lambda: self.database_convert_complete.emit()
        )

    @QtCore.Slot(str, str, dict)
    def load_database(self, root_path, selected, credentials):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadLoad(credentials, root_path, selected)
        self._active_thread.start()

        self.database_convert_active.emit()
        self._active_thread.taskFinished.connect(
            lambda: self.database_convert_complete.emit()
        )

    @QtCore.Slot()
    def initiate_pipeline(self):
        self.project_menu.initiate_pipeline(self.core, self.project)

        sites_available = self.core.has_data(
            self.project, "hidden.available_sites"
        )
        systems_available = self.core.has_data(
            self.project, "hidden.available_systems"
        )

        if sites_available or systems_available:
            self.project_menu.initiate_options(self.core, self.project)

        if sites_available:
            self.filter_active.emit()

        self.pipeline_active.emit()

    @QtCore.Slot()
    def initiate_bathymetry(self):
        self.project_menu.initiate_bathymetry(self.core, self.project)
        self.bathymetry_active.emit()

    @QtCore.Slot(list)
    def queue_module_list(self, module_list):
        all_mods = self.module_menu.get_available(self.core, self.project)
        ordered_mods = [x for x in all_mods if x in module_list]

        self.queued_interfaces["modules"] = ordered_mods
        self.modules_queued.emit()

    @QtCore.Slot(list)
    def queue_theme_list(self, theme_list):
        all_themes = self.theme_menu.get_available(self.core, self.project)
        ordered_themes = [x for x in all_themes if x in theme_list]

        self.queued_interfaces["themes"] = ordered_themes
        self.themes_queued.emit()

    def activate_module_queue(self):
        if self.queued_interfaces["modules"] is None:
            return

        active_mods = self.module_menu.get_active(self.core, self.project)

        for module_name in self.queued_interfaces["modules"]:
            if module_name not in active_mods:
                self.module_menu.activate(self.core, self.project, module_name)

        self.activated_interfaces["modules"] = self.queued_interfaces["modules"]
        self.queued_interfaces["modules"] = None

    def activate_theme_queue(self):
        if self.queued_interfaces["themes"] is None:
            return

        active_themes = self.theme_menu.get_active(self.core, self.project)

        for theme_name in self.queued_interfaces["themes"]:
            if theme_name not in active_themes:
                self.theme_menu.activate(self.core, self.project, theme_name)

        self.activated_interfaces["themes"] = self.queued_interfaces["themes"]
        self.queued_interfaces["themes"] = None

    @QtCore.Slot(object)
    def select_strategy(self, strategy: Optional[GUIStrategy]):
        if self.project is None:
            return

        if self._active_thread is not None:
            self._active_thread.wait()

        if strategy is None:
            logMsg = "Null strategy detected"
        else:
            logMsg = "Strategy {} detected".format(strategy.get_name())

        module_logger.debug(logMsg)

        self.strategy = strategy
        simulation = self.project.get_simulation()

        if self.strategy is None:
            simulation.set_unavailable_variables(None)
        else:
            force_unavailable = self.strategy.get_variables()
            simulation.set_unavailable_variables(force_unavailable)

        self.core.set_interface_status(self.project)

        self.strategy_selected.emit()
        self.update_run_action.emit()

    @QtCore.Slot(object)
    def initiate_dataflow(self, pipeline):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadDataFlow(pipeline, self)

        self._active_thread.taskFinished.connect(
            lambda: self.dataflow_active.emit()
        )

        self._active_thread.start()

    @QtCore.Slot(str, bool)
    def export_data(self, file_path, mask_outputs=False):
        self.data_menu.export_data(
            self.core, self.project, str(file_path), bool(mask_outputs)
        )

    @QtCore.Slot(str, bool)
    def import_data(self, file_path, skip_satisfied=False):
        if self._active_thread is not None:
            self._active_thread.wait()

        self.data_menu.import_data(
            self.core, self.project, str(file_path), bool(skip_satisfied)
        )

    @QtCore.Slot(object, str, str)
    def read_file(self, variable, interface_name, file_path):
        if self._active_thread is not None:
            self._active_thread.wait()

        variable.read_file(
            self.core, self.project, str(file_path), str(interface_name)
        )

    @QtCore.Slot(object, str, str)
    def write_file(self, variable, interface_name, file_path):
        variable.write_file(
            self.core, self.project, str(file_path), str(interface_name)
        )

    def read_raw(self, variable, value):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadReadRaw(self, variable, value)
        self._active_thread.taskFinished.connect(self._clear_active_thread)
        self._active_thread.start()

    def read_test_data(self, control, path, overwrite):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadReadTest(self, control, path, overwrite)
        self._active_thread.taskFinished.connect(self._clear_active_thread)
        self._active_thread.start()

    @QtCore.Slot()
    def execute_current(self):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadCurrent(self.core, self.project)

        self._active_thread.taskFinished.connect(
            lambda: self.module_executed.emit()
        )

        self._active_thread.start()

    @QtCore.Slot()
    def execute_themes(self):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadThemes(self.core, self.project)

        self._active_thread.taskFinished.connect(
            lambda: self.themes_executed.emit()
        )

        self._active_thread.start()

    @QtCore.Slot()
    def execute_strategy(self):
        if self.strategy is None:
            return

        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadStrategy(
            self.core, self.project, self.strategy
        )

        self._active_thread.taskFinished.connect(
            lambda: self.strategy_executed.emit()
        )

        self._active_thread.start()

    @QtCore.Slot(str)
    def set_output_scope(self, scope):
        if self._active_thread is not None:
            self._active_thread.wait()

        self._active_thread = ThreadScope(self.core, self.project, scope)

        self._active_thread.taskFinished.connect(
            lambda: self._finalize_scope(scope)
        )

        self._active_thread.start()

    @QtCore.Slot()
    def _finalize_open_project(self):
        assert isinstance(self._active_thread, ThreadOpen)

        if self._active_thread._project is None:
            self._clear_active_thread()
            return

        assert isinstance(self._active_thread._project, GUIProject)
        self.project = self._active_thread._project
        self.project_path = self._active_thread._project_path
        self.activated_interfaces = self._active_thread._activated_interfaces
        self.strategy = self._active_thread._strategy
        self._current_scope = self._active_thread._current_scope

        self.project_title_change.emit(self.project.title)

        # Relay active simulation change
        self.project.active_index_changed.connect(self._emit_update_pipeline)
        self.project.active_index_changed.connect(self.check_active_simulation)
        self.project.active_index_changed.connect(
            lambda: self.reset_widgets.emit()
        )
        self.project.active_index_changed.connect(
            lambda: self.update_run_action.emit()
        )

        # Relay strategy change
        if self.strategy is not None:
            self.strategy_loaded.emit(self.strategy)

        # Update the scope widget
        self.update_scope.emit(self._current_scope)

        # Release the active thread
        self._clear_active_thread()

    @QtCore.Slot()
    def _finalize_save_project(self):
        assert isinstance(self._active_thread, ThreadSave)
        self.project_path = self._active_thread._save_path
        self.project_saved.emit()

        # Release the active thread
        self._clear_active_thread()

    @QtCore.Slot()
    def _finalize_project(self):
        # Emit signals on project
        assert self.project is not None
        assert self.strategy is not None

        self.project.sims_updated.emit()
        self.project.active_index_changed.emit()

        active_sim_title = self.project.get_simulation_title()

        if active_sim_title is not None:
            self.project.active_title_changed.emit(active_sim_title)

        # Assertain if the strategy can be released
        allow_run = self.strategy.allow_run(self.core, self.project)

        # If the strategy is no longer active release the hidden variables
        if not allow_run:
            [
                sim.set_unavailable_variables()
                for sim in self.project._simulations
            ]

        # Emit signals on core
        self._finalize_core()

    @QtCore.Slot(str)
    def _finalize_scope(self, scope):
        # Record the scope
        self._current_scope = scope

        # Emit signals on core
        self._finalize_core()

    @QtCore.Slot()
    def _finalize_core(self):
        # Update the interface status
        self.core.set_interface_status(self.project)

        # Release the active thread
        self._clear_active_thread()

    @QtCore.Slot()
    def _clear_active_thread(self):
        if self._active_thread is None:
            return

        self._active_thread.wait()
        self._active_thread = None

    @QtCore.Slot(object)
    def _emit_update_pipeline(self):
        Husk = namedtuple("Husk", ["core", "project"])
        husk = Husk(self.core, self.project)

        self.update_pipeline.emit(husk)
