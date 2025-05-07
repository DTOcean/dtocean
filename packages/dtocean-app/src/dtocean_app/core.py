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

import logging

from dtocean_core.core import (
    AutoFileInput,
    AutoFileOutput,
    AutoPlot,
    AutoQuery,
    AutoRaw,
    Core,
    Project,
)
from mdo_engine.boundary.interface import AutoInterface, MetaInterface
from mdo_engine.control.data import DataStorage
from mdo_engine.control.pipeline import Sequencer
from mdo_engine.control.simulation import Controller, Loader
from PySide6 import QtCore

import dtocean_plugins.core as core_interfaces

# from dtocean_core.menu import ConnectorMenu
from . import data as gui_data
from . import interfaces as gui_interfaces

module_logger = logging.getLogger(__name__)


class WidgetInterface(MetaInterface):
    """Interface with a widget"""

    def __init__(self):
        super(WidgetInterface, self).__init__()
        self.parent = None


class InputWidgetInterface(WidgetInterface):
    """Interface for the dynnamic input widget"""


class OutputWidgetInterface(WidgetInterface):
    """Interface for the dynnamic output widget"""


class AutoInput(AutoInterface, InputWidgetInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        InputWidgetInterface.__init__(self)

    @classmethod
    def get_connect_name(cls):
        return "auto_input"


class AutoOutput(AutoInterface, OutputWidgetInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        OutputWidgetInterface.__init__(self)

    @classmethod
    def get_connect_name(cls):
        return "auto_output"


class GUIProject(QtCore.QObject, Project):
    sims_updated = QtCore.Signal()
    active_index_changed = QtCore.Signal()
    active_title_changed = QtCore.Signal(str)

    """Project class with signals"""

    def __init__(self, title):
        QtCore.QObject.__init__(self)
        Project.__init__(self, title)

    def add_simulation(self, simulation, set_active=False):
        super(GUIProject, self).add_simulation(simulation, set_active)
        self.sims_updated.emit()

    def set_simulation_title(self, new_title, index=None, title=None):
        super(GUIProject, self).set_simulation_title(new_title, index, title)
        self.sims_updated.emit()

    def _set_active_index(self, index):
        super(GUIProject, self)._set_active_index(index)
        self.active_index_changed.emit()

        active_sim_title = self.get_simulation_title()

        if active_sim_title is not None:
            self.active_title_changed.emit(active_sim_title)

    def _load(self, project):
        self.title = project.title
        self._pool = project._pool
        self._simulations = project._simulations
        self._active_index = project._active_index
        self._db_cred = project._db_cred


class GUICore(Core, QtCore.QObject):
    """Class to initiate and manipulate projects with a GUI environment."""

    # PyQt signals
    status_updated = QtCore.Signal()
    pipeline_reset = QtCore.Signal()

    # Extend the sockets for widgets
    _ext_sockets = (
        "FileInputInterface",
        "FileOutputInterface",
        "QueryInterface",
        "RawInterface",
        "PlotInterface",
        "InputWidgetInterface",
        "OutputWidgetInterface",
    )

    # Extend the auto classes for widgets
    _auto_classes = (
        AutoInput,
        AutoOutput,
        AutoFileInput,
        AutoFileOutput,
        AutoPlot,
        AutoRaw,
        AutoQuery,
    )

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.data_catalog = None
        self.loader = None
        self.control = None
        self.socket_map = None
        self._input_parent = None

    def _create_data_catalog(self):
        catalog = super(GUICore, self)._create_data_catalog()
        self.data_catalog = catalog

    def _create_control(self):
        """Overload the structures base class"""

        data_store = DataStorage(gui_data, super_cls="GUIStructure")
        sequencer = Sequencer(
            self._hub_sockets,
            [core_interfaces],
            warn_import=True,
        )

        loader = Loader(data_store)
        control = Controller(data_store, sequencer)

        self.loader = loader
        self.control = control

    def _create_sockets(self):
        socket_map = super(GUICore, self)._create_sockets()
        self.socket_map = socket_map

    def new_project(self, project_title, simulation_title="Default"):
        new_project = GUIProject(project_title)
        self.new_simulation(new_project, simulation_title)

        return new_project

    def load_project(self, load_path):
        core_project = super(GUICore, self).load_project(load_path)

        gui_project = GUIProject("temp")
        gui_project._load(core_project)

        return gui_project

    def set_input_parent(self, widget):
        self._input_parent = widget

    def reset_level(
        self,
        project,
        level=None,
        preserve_level=False,
        force_scheduled=None,
        skip_missing=False,
    ):
        """Prepare the simulation for re-execution at the given level"""

        super(GUICore, self).reset_level(
            project, level, preserve_level, force_scheduled, skip_missing
        )

        self.pipeline_reset.emit()

    def set_interface_status(self, project, simulation=None):
        """Emit a signal on status update"""

        super(GUICore, self).set_interface_status(project, simulation)
        self.status_updated.emit()

    def connect_interface(self, project, interface):
        """Add parent widget to widget interfaces"""

        if (
            isinstance(interface, InputWidgetInterface)
            and self._input_parent is not None
        ):
            interface.parent = self._input_parent

        interface = super(GUICore, self).connect_interface(project, interface)

        return interface

    def _build_named_socket(self, socket_str):
        socket = super(GUICore, self)._build_named_socket(socket_str)
        socket.discover_interfaces(gui_interfaces)

        return socket


# class HubMenu(ConnectorMenu):
#
#    def __init__(self, hub_name):
#
#        super(HubMenu, self).__init__()
#        self._hidden_hub_name = hub_name
#
#    @property
#    def _hub_name(self):
#
#        return self._hidden_hub_name
