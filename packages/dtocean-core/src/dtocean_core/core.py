#    Copyright (C) 2016-2024 Mathew Topper
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

import json
import logging
import os
import pickle
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
from mdo_engine.boundary.data import SerialBox
from mdo_engine.boundary.interface import (
    AutoInterface,
    MetaInterface,
    QueryInterface,
    RawInterface,
)
from mdo_engine.control.data import DataStorage, DataValidation
from mdo_engine.control.factory import InterfaceFactory
from mdo_engine.control.pipeline import Sequencer
from mdo_engine.control.simulation import Controller, Loader
from mdo_engine.control.sockets import NamedSocket, Socket
from mdo_engine.entity.data import DataCatalog, DataPool
from mdo_engine.entity.simulation import Simulation
from mdo_engine.utilities.data import check_integrity
from mdo_engine.utilities.misc import OrderedSet

import dtocean_plugins.core as core_interfaces
import dtocean_plugins.modules as module_interfaces
import dtocean_plugins.plots as plot_interfaces
import dtocean_plugins.themes as theme_interfaces
from dtocean_plugins.core import FileInputInterface, FileOutputInterface
from dtocean_plugins.plots.plots import PlotInterface

from . import data as core_data
from .utils.database import get_database
from .utils.files import package_dir, unpack_archive

StrOrPath = Union[str, Path]

MODULE_LOGGER = logging.getLogger(__name__)
INTERFACE_MODULES = [
    core_interfaces,
    module_interfaces,
    plot_interfaces,
    theme_interfaces,
]


class AutoRaw(AutoInterface, RawInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        RawInterface.__init__(self)

    @classmethod
    def get_connect_name(cls):
        return None


class AutoQuery(AutoInterface, QueryInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        QueryInterface.__init__(self)

    @classmethod
    def get_connect_name(cls):
        return "auto_db"


class AutoPlot(AutoInterface, PlotInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        PlotInterface.__init__(self)

    @classmethod
    def get_connect_name(cls):
        return "auto_plot"


class AutoFileInput(AutoInterface, FileInputInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        FileInputInterface.__init__(self)

    @classmethod
    def get_connect_name(cls):
        return "auto_file_input"

    @classmethod
    def get_method_names(cls):
        return ["get_valid_extensions"]


class AutoFileOutput(AutoInterface, FileOutputInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        FileOutputInterface.__init__(self)

    @classmethod
    def get_connect_name(cls):
        return "auto_file_output"

    @classmethod
    def get_method_names(cls):
        return ["get_valid_extensions"]


class OrderedSim(Simulation):
    """The main class is the simulation which holds all of the information
    about the system."""

    _hub_defs = [
        {
            "name": "project",
            "interface": "ProjectInterface",
            "type": "Hub",
            "force unavailable": None,
            "no complete": False,
        },
        {
            "name": "modules",
            "interface": "ModuleInterface",
            "type": "Pipeline",
            "force unavailable": None,
            "no complete": False,
        },
        {
            "name": "themes",
            "interface": "ThemeInterface",
            "type": "Hub",
            "force unavailable": ("modules",),
            "no complete": True,
        },
    ]

    def __init__(self, title=None):
        super(OrderedSim, self).__init__(title)
        self.level_map = {}
        self.output_scope = None
        self._execution_level = None
        self._inspection_level = None
        self._hub_order = []
        self._hub_input_status = None
        self._hub_output_status = None
        self._hub_queue = None
        self._force_unvailable = None

        # Functional initialisation
        self._hub_queue = self._init_hub_queue()

    def _init_hub_queue(self):
        result = deepcopy(self._hub_defs)

        return result

    def set_unavailable_variables(self, variable_names=None):
        self._force_unvailable = variable_names

    def get_unavailable_variables(self):
        return self._force_unvailable

    def set_inspection_level(self, level):
        MODULE_LOGGER.debug("Setting inspection level to {}".format(level))

        self._inspection_level = level

    def get_inspection_level(self):
        return self._inspection_level

    def set_execution_level(self, level):
        MODULE_LOGGER.debug("Setting execution level to {}".format(level))

        self._execution_level = level

    def get_execution_level(self):
        return self._execution_level

    def next_hub_definition(self):
        if not self._hub_queue:
            errStr = "No Hubs are queued for creation."
            raise RuntimeError(errStr)

        return self._hub_queue.pop(0)

    def set_hub(self, hub_id, hub):
        self._hubs[hub_id] = hub
        self._hub_order.append(hub_id)

    def get_hub_order(self):
        if not self._hub_order:
            result = None
        else:
            result = self._hub_order

        return result

    def set_input_status(self, hub_input_status):
        self._hub_input_status = hub_input_status

    def set_output_status(self, hub_output_status):
        self._hub_output_status = hub_output_status

    def get_input_ids(
        self, hub_id=None, interface_name=None, valid_statuses=None
    ):
        result = self._get_ids(
            self._hub_input_status, hub_id, interface_name, valid_statuses
        )

        return result

    def get_output_ids(
        self, hub_id=None, interface_name=None, valid_statuses=None
    ):
        result = self._get_ids(
            self._hub_output_status, hub_id, interface_name, valid_statuses
        )

        return result

    def get_input_status(self, hub_id, interface_name):
        if self._hub_input_status is None:
            return None

        return self._hub_input_status[hub_id][interface_name]

    def get_output_status(self, hub_id, interface_name):
        if self._hub_output_status is None:
            return None

        return self._hub_output_status[hub_id][interface_name]

    def stamp(self, simulation):
        simulation.level_map = deepcopy(self.level_map)
        simulation._execution_level = deepcopy(self._execution_level)
        simulation._inspection_level = deepcopy(self._inspection_level)
        simulation._hub_order = deepcopy(self._hub_order)
        simulation._hub_input_status = deepcopy(self._hub_input_status)
        simulation._hub_output_status = deepcopy(self._hub_output_status)
        simulation._hub_queue = deepcopy(self._hub_queue)
        simulation._force_unvailable = deepcopy(self._force_unvailable)

        return simulation

    def _get_ids(
        self, sim_status, hub_id=None, interface_name=None, valid_statuses=None
    ):
        if sim_status is None:
            return []

        if hub_id is None:
            hub_ids = sim_status.keys()
        else:
            hub_ids = [hub_id]

        all_ids = []

        for this_hub_id in hub_ids:
            hub_status = sim_status[this_hub_id]

            if interface_name is None:
                interface_names = hub_status.keys()
            else:
                interface_names = [interface_name]

            for this_interface_name in interface_names:
                input_status = hub_status[this_interface_name]

                if valid_statuses is not None:
                    all_ids += [
                        k
                        for k, v in input_status.items()
                        if any(x == v for x in valid_statuses)
                    ]

                else:
                    all_ids += input_status.keys()

        return list(set(all_ids))


class Project:
    """Class to store simulations, data pool and other project related data."""

    def __init__(self, title):
        self.title = title
        self._pool = DataPool()
        self._simulations = []
        self._active_index = None
        self._db_cred = None

    def is_active(self):
        result = False
        if self._active_index is not None:
            result = True

        return result

    def get_active_index(self):
        return self._active_index

    def set_active_index(self, index=None, title=None):
        if index is None and title is None:
            errStr = "Either an index or simulation title is required"
            raise ValueError(errStr)

        if index is None:
            index = self._get_index(title)

        n_sims = len(self._simulations)

        if index is None or index > n_sims or index < 0:
            name = index
            if title:
                name = title

            errStr = "Simulation {} not found".format(name)
            raise ValueError(errStr)

        if index == self._active_index:
            return

        self._set_active_index(index)

    def add_simulation(self, simulation, set_active=False):
        index = self._set_simulation(simulation)

        if self._active_index is None or set_active:
            self._set_active_index(index)

    def remove_simulation(self, index=None, title=None, active_index=None):
        if index is None and title is None:
            errStr = "Either an index or simulation title is required"
            raise ValueError(errStr)

        if index is None:
            index = self._get_index(title)
            assert index is not None

        if active_index is None:
            active_index = 0

        simulation = self._simulations.pop(index)
        self._set_active_index(active_index)

        return simulation

    def get_simulation_indexes(self, titles, raise_if_missing=True):
        sim_indexes = [self._get_index(x, raise_if_missing) for x in titles]

        return sim_indexes

    def get_simulation_titles(self, indexes=None):
        if not self.is_active():
            return None

        if indexes is None:
            sim_titles = [
                x.get_title()
                for x in self._simulations
                if x.get_title() is not None
            ]
        else:
            sim_titles = [self.get_simulation_title(index=x) for x in indexes]

        if not sim_titles:
            sim_titles = None

        return sim_titles

    def get_simulation_title(self, index=None, title=None):
        if not self.is_active():
            return None

        simulation = self._get_simulation(index, title)
        sim_title = simulation.get_title()

        return sim_title

    def set_simulation_title(self, new_title, index=None, title=None):
        simulation = self._get_simulation(index, title)

        if title is None:
            title = simulation.get_title()

        # Skip matching simulation titles
        if index is None and title is not None and title == new_title:
            return

        # Check if the title is unique. None removes title
        if new_title is not None:
            all_titles = self.get_simulation_titles()

            if all_titles is not None and new_title in all_titles:
                errStr = ("Simulation with title {} already " "exists").format(
                    new_title
                )
                raise ValueError(errStr)

        simulation.set_title(new_title)

        self._set_simulation(simulation)

    def get_pool(self):
        return self._pool

    def get_simulation(self, index=None, title=None):
        return self._get_simulation(index, title)

    def set_database_credentials(self, database_cred):
        self._db_cred = database_cred

    def get_database_credentials(self):
        return self._db_cred

    def check_integrity(self):
        result = check_integrity(self._pool, self._simulations)

        return result

    def to_project(self):
        new_project = Project(self.title)

        new_project._pool = deepcopy(self._pool)  # pylint: disable=protected-access
        new_project._simulations = deepcopy(self._simulations)  # pylint: disable=protected-access
        new_project._active_index = self._active_index  # pylint: disable=protected-access
        new_project._db_cred = deepcopy(self._db_cred)  # pylint: disable=protected-access

        return new_project

    def _get_index(self, title, raise_if_missing=True):
        sim_index = None

        for i, simulation in enumerate(self._simulations):
            sim_title = simulation.get_title()

            if title == sim_title:
                sim_index = i
                break

        if sim_index is None and raise_if_missing:
            errStr = "Simualtion {} not found".format(title)
            raise ValueError(errStr)

        return sim_index

    def _set_active_index(self, index):
        n_sims = len(self._simulations)

        if n_sims == 0:
            self._active_index = None
            return

        if index > n_sims or index < 0:
            errStr = "Index {} is out of range".format(index)
            raise ValueError(errStr)

        self._active_index = index

    def _get_simulation(self, index=None, title=None):
        """If both index and title are none then return the active simulation."""

        if index is not None:
            n_sims = len(self._simulations)

            if index > n_sims or index < 0:
                errStr = "Simulation index out of range."
                raise ValueError(errStr)

            sim_index = index

        elif title is not None:
            sim_index = self._get_index(title)
            assert sim_index is not None

        else:
            if not self.is_active():
                errStr = ("Project {} has no active " "simulation").format(
                    self.title
                )
                raise RuntimeError(errStr)

            sim_index = self._active_index
            assert sim_index is not None

        return self._simulations[sim_index]

    def _set_simulation(self, simulation, index=None):
        n_sims = len(self._simulations)

        if index is not None and (index > n_sims or index < 0):
            errStr = "Simulation index out of range."
            raise ValueError(errStr)

        if index is None:
            # Check for a matching title
            title = simulation.get_title()

            for i, sim in enumerate(self._simulations):
                sim_title = sim.get_title()

                if title == sim_title:
                    index = i
                    break

        if index is None:
            self._simulations.append(simulation)
            index = len(self._simulations) - 1
        else:
            self._simulations[index] = simulation

        return index

    def __len__(self):
        return len(self._simulations)


class Core:
    """Class to initiate and manipulate projects."""

    # Socket configuration constants
    _hub_sockets = ("ProjectInterface", "ModuleInterface", "ThemeInterface")

    _ext_sockets = (
        "FileInputInterface",
        "FileOutputInterface",
        "QueryInterface",
        "RawInterface",
        "PlotInterface",
    )

    _auto_classes = (
        AutoFileInput,
        AutoFileOutput,
        AutoPlot,
        AutoRaw,
        AutoQuery,
    )

    _markers = {
        "initial": "initial",
        "register": "start",
        "output": "output",
        "local": "local",
        "global": "global",
    }

    def __init__(self):
        self.data_catalog = self._create_data_catalog()
        self.loader, self.control = self._create_control()
        self.socket_map = self._create_sockets()

        # Set up plotting (must happen after sockets are created)
        self._init_plots()

    def _create_control(self):
        data_store = DataStorage(core_data)
        sequencer = Sequencer(
            self._hub_sockets, INTERFACE_MODULES, warn_import=True
        )

        loader = Loader(data_store)
        control = Controller(data_store, sequencer)

        return loader, control

    def _create_data_catalog(self):
        catalog = DataCatalog()
        validation = DataValidation(core_data.CoreMetaData)
        validation.update_data_catalog_from_definitions(catalog, core_data)

        return catalog

    def _create_sockets(self) -> dict[str, Socket]:
        socket_dict = {}

        for socket_str in self._ext_sockets:
            socket = self._build_named_socket(socket_str)
            socket_dict[socket_str] = socket

        for auto_cls in self._auto_classes:
            socket = self._build_auto_socket(auto_cls)
            socket_dict[auto_cls.__name__] = socket

        return socket_dict

    def _init_plots(self):
        """Set matplotlib to non-interactive (in case it is set to interactive
        in an imported module)"""

        plt.ioff()

    def new_project(self, project_title, simulation_title="Default"):
        new_project = Project(project_title)
        self.new_simulation(new_project, simulation_title)

        return new_project

    def dump_project(self, project, dump_path: StrOrPath):
        dump_path = Path(dump_path)

        # A data store is required
        data_store = DataStorage(core_data)

        prj_dir_path = tempfile.mkdtemp()

        # Copy the project before editing and ensure type Project
        project_copy = project.to_project()

        # Serialise the pool
        pool_dir = os.path.join(prj_dir_path, "pool")

        if os.path.exists(pool_dir):
            shutil.rmtree(pool_dir)
        os.makedirs(pool_dir)

        pool = project_copy.get_pool()
        data_store.serialise_pool(pool, pool_dir, root_dir=prj_dir_path)

        # Now iterate through the simulations
        sim_boxes = []

        for i, simulation in enumerate(project_copy._simulations):
            sim_dir_name = "simulation_{}".format(i)
            sim_dir = os.path.join(prj_dir_path, sim_dir_name)

            if os.path.exists(sim_dir):
                shutil.rmtree(sim_dir)
            os.makedirs(sim_dir)

            sim_file_name = "{}.pkl".format(sim_dir_name)
            sim_file_path = os.path.join(sim_dir, sim_file_name)

            self.control.serialise_states(
                simulation, sim_dir, root_dir=prj_dir_path
            )

            with open(sim_file_path, "wb") as fstream:
                pickle.dump(simulation, fstream, -1)

            sim_store_path = os.path.join(sim_dir_name, sim_file_name)
            sim_dict = {"file_path": sim_store_path}
            sim_box = SerialBox(sim_dir_name, sim_dict)

            sim_boxes.append(sim_box)

        # Replace the simulations with the sim boxes
        project_copy._simulations = sim_boxes

        # Now pickle the project
        project_file_path = os.path.join(prj_dir_path, "project.pkl")

        with open(project_file_path, "wb") as fstream:
            pickle.dump(project_copy, fstream, -1)

        # OK need to consider if we want a prj file or a directory first.
        if dump_path.suffix == ".prj":
            archive = True
        elif dump_path.is_dir():
            archive = False
        else:
            errStr = (
                "Argument dump_path must either be an existing "
                "directory or a file path with .prj extension"
            )
            raise ValueError(errStr)

        # Package the directory
        package_dir(prj_dir_path, dump_path, archive)

    def load_project(self, load_path):
        # A data store is required
        data_store = DataStorage(core_data)

        # A sequencer is also required
        sequencer = Sequencer(
            self._hub_sockets, INTERFACE_MODULES, warn_import=True
        )

        # Flag to remove project directory
        remove_prj_dir = False

        # OK need to consider if we have a prj file or a directory first.
        # If its a prj file them unzip it.
        if os.path.isfile(load_path) and ".prj" in load_path:
            # Unzip the file to a temporary directory
            prj_dir_path = tempfile.mkdtemp()
            unpack_archive(load_path, prj_dir_path)
            remove_prj_dir = True

        elif os.path.isdir(load_path):
            prj_dir_path = load_path

        else:
            errStr = (
                "Argument load_path must either be a directory or a "
                "file with .prj extension"
            )
            raise ValueError(errStr)

        # Now unpickle the project
        project_file_path = os.path.join(prj_dir_path, "project.pkl")

        with open(project_file_path, "rb") as fstream:
            load_project = pickle.load(fstream)

        # Now iterate through the serial boxes
        simulations = []

        for i, sim_box in enumerate(load_project._simulations):
            sim_file_relative = sim_box.load_dict["file_path"]
            sim_file_path = os.path.join(prj_dir_path, sim_file_relative)

            with open(sim_file_path, "rb") as fstream:
                simulation = pickle.load(fstream)

            self.control.deserialise_states(simulation, root_dir=prj_dir_path)

            # Replace interface objects in hubs for backwards compatibility
            hub_ids = simulation.get_hub_ids()

            for hub_id in hub_ids:
                hub = simulation.get_hub(hub_id)
                sequencer.refresh_interfaces(hub)

            simulations.append(simulation)

        # Replace the sim boxes with the simulations
        load_project._simulations = simulations

        # Deserialise the pool
        pool = load_project.get_pool()
        data_store.deserialise_pool(
            self.data_catalog,
            pool,
            root_dir=prj_dir_path,
            warn_missing=True,
            warn_unpickle=True,
        )

        # Remove the project directory if necessary
        if remove_prj_dir:
            shutil.rmtree(prj_dir_path)

        # Reset the input / output statuses
        for simulation in simulations:
            self.set_interface_status(load_project, simulation)

        return load_project

    def new_simulation(self, project, title=None):
        # If given, check if the title is unique
        if title is not None:
            all_titles = project.get_simulation_titles()

            if all_titles is not None and title in all_titles:
                errStr = ("Simulation with title {} already " "exists").format(
                    title
                )
                raise ValueError(errStr)

        new_sim = OrderedSim(title)
        new_sim.set_execution_level(self._markers["initial"])
        new_sim.set_inspection_level(self._markers["initial"])
        project.add_simulation(new_sim)

        self.register_level(project, self._markers["initial"], None)

    def clone_simulation(
        self,
        project,
        title=None,
        sim_index=None,
        sim_title=None,
        set_active=True,
    ):
        pool = project.get_pool()
        simulation = project.get_simulation(sim_index, sim_title)

        force_title = None
        null_title = False

        if title is None:
            null_title = True
        else:
            force_title = title

        simulation_clone = self.control.copy_simulation(
            pool, simulation, force_title, null_title
        )

        project.add_simulation(simulation_clone, set_active)

    def import_simulation(
        self,
        src_project,
        dst_project,
        dst_sim_title,
        src_sim_index=None,
        src_sim_title=None,
        set_active=True,
    ):
        src_pool = src_project.get_pool()
        dst_pool = dst_project.get_pool()

        src_simulation = src_project.get_simulation(
            src_sim_index, src_sim_title
        )

        dst_simulation = self.control.import_simulation(
            src_pool, dst_pool, src_simulation, dst_sim_title
        )

        dst_project.add_simulation(dst_simulation, set_active)

    def remove_simulation(
        self, project, sim_index=None, sim_title=None, active_index=None
    ):
        pool = project.get_pool()
        simulation = project.remove_simulation(
            sim_index, sim_title, active_index
        )

        self.control.remove_simulation(pool, simulation)

    def new_hub(self, project):
        # For DTOcean the hubs are assumed to come one after another, but this
        # is not a requirement of mdo_engine. To facilitate this we consume the
        # _hub_queue attribute of the Project object
        simulation = project.get_simulation()

        hub_definition = simulation.next_hub_definition()

        if hub_definition["type"] == "Hub":
            self.control.create_new_hub(
                simulation,
                hub_definition["interface"],
                hub_definition["name"],
                hub_definition["no complete"],
            )

        elif hub_definition["type"] == "Pipeline":
            self.control.create_new_pipeline(
                simulation,
                hub_definition["interface"],
                hub_definition["name"],
                hub_definition["no complete"],
            )

        else:
            raise ValueError

    def get_metadata(self, identifier):
        self.check_valid_variable(identifier)
        metadata = self.data_catalog.get_metadata(identifier)

        return metadata

    def is_valid_variable(self, identifier):
        all_vars = self.data_catalog.get_variable_identifiers()

        result = False

        if identifier in all_vars:
            result = True

        return result

    def check_valid_variable(self, identifier):
        if not self.is_valid_variable(identifier):
            errStr = (
                "Variable with identifier {} is not contained in the "
                "data catalogue"
            ).format(identifier)
            raise ValueError(errStr)

    def has_data(self, project, identifier):
        self.check_valid_variable(identifier)
        simulation = project.get_simulation()

        return self.control.has_data(simulation, identifier)

    def get_data_value(self, project, identifier):
        self.check_valid_variable(identifier)
        pool = project.get_pool()
        simulation = project.get_simulation()

        if not self.has_data(project, identifier):
            errStr = (
                'Variable ID "{}" is not contained in the active data ' "state."
            ).format(identifier)
            raise ValueError(errStr)

        data_value = self.control.get_data_value(pool, simulation, identifier)

        return data_value

    def add_datastate(
        self,
        project,
        level=None,
        identifiers=None,
        values=None,
        update_status=True,
        use_objects=False,
        log_exceptions=False,
    ):
        pool = project.get_pool()
        simulation = project.get_simulation()

        self.control.add_datastate(
            pool,
            simulation,
            level,
            self.data_catalog,
            identifiers,
            values,
            use_objects=use_objects,
            log_exceptions=log_exceptions,
        )

        # Log the identifiers added
        if level is None:
            msg_str = "Data added for "
        else:
            msg_str = "Data added with level '{}' for ".format(level)

        if identifiers is not None:
            # Filter data with non-None values
            log_identifiers = []

            assert values is not None
            for identifier, value in zip(identifiers, values):
                if value is not None:
                    log_identifiers.append(identifier)

            if len(log_identifiers) == 1:
                msg_str += "identifier '{}'".format(log_identifiers[0])

            elif len(log_identifiers) > 1:
                id_tabs = ["    {}".format(x) for x in log_identifiers]
                id_str = "\n".join(id_tabs)
                msg_str += "identifiers:\n{}".format(id_str)

            if log_identifiers:
                MODULE_LOGGER.info(msg_str)

        if not update_status:
            return

        self.set_interface_status(project)

    def mask_states(
        self,
        project,
        simulation=None,
        search_str=None,
        mask_after=None,
        no_merge=False,
        update_status=True,
    ):
        if simulation is None:
            simulation = project.get_simulation()

        # Mask all output states after the given level
        n_masks = self.control.mask_states(
            simulation, search_str, mask_after, no_merge
        )

        if not update_status or n_masks == 0:
            return

        self.set_interface_status(project)

    def unmask_states(
        self,
        project,
        simulation=None,
        search_str=None,
        no_merge=False,
        update_status=True,
    ):
        if simulation is None:
            simulation = project.get_simulation()

        # Remove all existing masks
        n_unmasks = self.control.unmask_states(simulation, search_str, no_merge)

        if not update_status or n_unmasks == 0:
            return

        self.set_interface_status(project)

    def dump_datastate(self, project, dump_path, mask=None):
        data_store = DataStorage(core_data)

        def get_subsets():
            pool = project.get_pool()
            simulation = project.get_simulation()

            merged_state = self.loader.create_merged_state(simulation)
            save_pool, save_state = data_store.create_pool_subset(
                pool, merged_state
            )

            return save_pool, save_state

        # Allow a mask to applied before dumping
        if mask is not None:
            self.mask_states(project, search_str=mask)

        # Get the pool and datastate subsets
        save_pool, save_state = get_subsets()

        if mask is not None:
            self.unmask_states(project)

        # Serialise the pool
        dts_dir_path = tempfile.mkdtemp()
        pool_dir = os.path.join(dts_dir_path, "pool")

        if os.path.exists(pool_dir):
            shutil.rmtree(pool_dir)
        os.makedirs(pool_dir)

        data_store.serialise_pool(save_pool, pool_dir, root_dir=dts_dir_path)

        # Now pickle the pool
        pool_file_path = os.path.join(dts_dir_path, "pool.pkl")

        with open(pool_file_path, "wb") as fstream:
            pickle.dump(save_pool, fstream, -1)

        # Serialise the datastate
        file_path = os.path.join(dts_dir_path, "datastate_dump.json")
        state_dict = save_state.dump()

        with open(file_path, "w") as json_file:
            json.dump(state_dict, json_file)

        # OK need to consider if we want a file or a directory first.
        errStr = (
            "Argument dump_path must either be an existing "
            "directory or a file path with .dts extension"
        )

        if os.path.splitext(dump_path)[1] == ".dts":
            archive = True
        elif os.path.isdir(dump_path):
            archive = False
        else:
            raise ValueError(errStr)

        # Package the directory
        package_dir(dts_dir_path, dump_path, archive)

    def load_datastate(self, project, load_path, exclude=None, overwrite=True):
        # A data store is required
        data_store = DataStorage(core_data)

        # Get the input ids in the active simulation
        simulation = project.get_simulation()

        # Avoid filling unavailable or overwritten inputs
        valid_statuses = ["required", "optional"]
        if overwrite:
            valid_statuses.append("satisfied")

        input_ids = simulation.get_input_ids(valid_statuses=valid_statuses)

        # Flag to remove datastate directory
        remove_dts_dir = False

        # OK need to consider if we have a prj file or a directory first.
        # If its a prj file them unzip it.
        if os.path.isfile(load_path) and ".dts" in load_path:
            # Unzip the file to a temporary directory
            dts_dir_path = tempfile.mkdtemp()
            unpack_archive(load_path, dts_dir_path)
            remove_dts_dir = True

        elif os.path.isdir(load_path):
            dts_dir_path = load_path

        else:
            errStr = (
                "Argument load_path must either be a directory or a file"
                "with .dts extension"
            )
            raise ValueError(errStr)

        # Load datastate json
        load_path = os.path.join(dts_dir_path, "datastate_dump.json")

        with open(load_path, "rb") as json_file:
            dump_dict = json.load(json_file)

        state_data: dict = dump_dict["data"]

        # Now unpickle the pool
        pool_file_path = os.path.join(dts_dir_path, "pool.pkl")

        with open(pool_file_path, "rb") as fstream:
            temp_pool = pickle.load(fstream)

        # Deserialise the pool
        data_store.deserialise_pool(
            self.data_catalog,
            temp_pool,
            root_dir=dts_dir_path,
            warn_missing=True,
            warn_unpickle=True,
        )

        # Remove the project directory if necessary
        if remove_dts_dir:
            shutil.rmtree(dts_dir_path)

        # Create a new datastate in the existing pool with the loaded data
        var_ids = []
        var_objs = []

        for var_id, data_index in state_data.items():
            if not self.is_valid_variable(var_id):
                msgStr = (
                    'Variable ID "{}" is not contained in the data ' "catalog"
                ).format(var_id)
                MODULE_LOGGER.warning(msgStr)

                continue

            if var_id not in input_ids:
                msgStr = (
                    'Variable ID "{}" is not an input to the current '
                    "simulation"
                ).format(var_id)
                MODULE_LOGGER.info(msgStr)

                continue

            if exclude is not None and exclude in var_id:
                continue

            data_obj = temp_pool.get(data_index)

            var_ids.append(var_id)
            var_objs.append(data_obj)

        self.add_datastate(
            project, identifiers=var_ids, values=var_objs, use_objects=True
        )

    def get_levels(
        self, project, show_masked=True, sim_index=None, sim_title=None
    ):
        simulation = project.get_simulation(sim_index, sim_title)
        levels = OrderedSet(
            simulation.get_active_levels(show_masked=show_masked)
        )

        return levels

    def get_level_values(
        self,
        project,
        data_identity,
        levels=None,
        force_masks=None,
        sim_index=None,
        sim_title=None,
    ):
        pool = project.get_pool()
        simulation = project.get_simulation(sim_index, sim_title)

        level_results = self.control.get_level_values(
            pool,
            simulation,
            data_identity,
            levels=levels,
            force_masks=force_masks,
        )

        return level_results

    def get_project_values(
        self,
        project,
        data_identity,
        level,
        force_indexes=None,
        allow_none=False,
    ):
        """Collect the value of a given identity at a given level for all
        simulations in the project"""

        pool = project.get_pool()
        project_values = []

        if force_indexes is None:
            sim_indexes = range(len(project))
        else:
            sim_indexes = force_indexes

        for i in sim_indexes:
            simulation = project.get_simulation(index=i)
            sim_title = simulation.get_title()

            sim_value = self.control.get_data_value(
                pool,
                simulation,
                data_identity,
                level=level,
                check_identity=True,
            )

            if sim_value is None and not allow_none:
                continue

            project_values.append((sim_title, sim_value))

        if not project_values:
            project_values = None

        return project_values

    def register_level(self, project, level, interface_name):
        pool = project.get_pool()
        simulation = project.get_simulation()

        self.control.add_datastate(pool, simulation, level)

        simulation.level_map[level] = interface_name

    def inspect_level(
        self,
        project,
        level,
        inspection_level=None,
        update_status=True,
        skip_missing=False,
        force=False,
    ):
        """Inspect the data at a level, masking all output levels after
        it"""

        simulation = project.get_simulation()

        # Sanitise the level
        level = level.lower()

        if not force and level == simulation.get_inspection_level():
            return

        # Check if state is in the active levels
        if level not in self.get_levels(project):
            active_level_str = ", ".join(self.get_levels(project))
            errStr = (
                "Level {} is not available. Active levels are " "{}"
            ).format(level, active_level_str)
            raise ValueError(errStr)

        if inspection_level is None:
            inspection_level = level

        if inspection_level not in simulation.level_map:
            level_str = ", ".join(simulation.level_map.keys())
            msgStr = (
                "System level '{}' not valid for inspection. Must be "
                "one of {}"
            ).format(level, level_str)

            if skip_missing:
                msgStr += ". Skipping"
                MODULE_LOGGER.debug(msgStr)
                return

            raise RuntimeError(msgStr)

        MODULE_LOGGER.info("Inspecting level {}".format(level))

        # Remove all existing masks
        self.unmask_states(project, no_merge=True, update_status=False)

        # Mask all output states after the given level
        self.mask_states(
            project,
            search_str=self._markers["output"],
            mask_after=level,
            update_status=False,
        )

        simulation.set_inspection_level(inspection_level)

        if not update_status:
            return

        self.set_interface_status(project)

    def reset_level(
        self,
        project,
        level=None,
        preserve_level=False,
        force_scheduled=None,
        skip_missing=False,
    ):
        """Prepare the simulation for re-execution at the given level"""

        pool = project.get_pool()
        simulation = project.get_simulation()

        if level == simulation.get_execution_level():
            return

        if level is None:
            level = simulation.get_inspection_level()

        else:
            level = level.lower()

            # Bring the hubs to the correct position if the inspection level
            # has been changed. Inspection level must match a module name
            # unless skip_missing flag is True
            if level not in simulation.level_map:
                level_str = ", ".join(simulation.level_map.keys())
                msgStr = (
                    "System level '{}' not valid for execution. Must be "
                    "one of {}"
                ).format(level, level_str)

                if skip_missing:
                    msgStr += ". Skipping"
                    MODULE_LOGGER.debug(msgStr)
                    return

                raise RuntimeError(msgStr)

        self.inspect_level(project, level, update_status=False, force=True)

        MODULE_LOGGER.info("Resetting to level {}".format(level))

        # Mask all register states after the given level
        self.mask_states(
            project,
            search_str=self._markers["register"],
            mask_after=level,
            no_merge=True,
            update_status=False,
        )

        # Mask the given level
        if not preserve_level:
            self.mask_states(
                project, search_str=level, no_merge=True, update_status=False
            )

        interface_name = simulation.level_map[level]
        self._schedule_interface(project, interface_name)

        # Later interfaces can now not be scheduled so delete the masked
        # states.
        self.control.delete_masked_states(pool, simulation)

        simulation.set_execution_level(level)

        # Switch the force available flag on a given hub
        if force_scheduled is not None:
            hub = simulation.get_hub(force_scheduled)
            hub.force_completed = False

        self.set_interface_status(project)

    def set_interface_status(self, project, simulation=None):
        # This order is important as the input status relies on the output
        # status
        self._set_outputs_status(project, simulation)
        self._set_inputs_status(project, simulation)

    def can_load_interface(self, project: Project, interface, check_id=None):
        pool = project.get_pool()
        simulation = project.get_simulation()

        if check_id:
            if not self.loader.input_available(
                pool, simulation, interface, check_id
            ):
                return False

        result = self.loader.can_load(pool, simulation, interface)

        return result

    def load_interface(self, project, interface, skip_vars=None):
        pool = project.get_pool()
        simulation = project.get_simulation()

        interface = self.loader.load_interface(
            pool, simulation, interface, skip_vars
        )

        return interface

    def connect_interface(self, project, interface):
        # TODO: Is this pre-population something to do in mdo_engine?
        # If its a QueryInterface try to connect the database
        if (
            isinstance(interface, QueryInterface)
            and project.get_database_credentials() is not None
        ):
            credentials = project.get_database_credentials()
            database = get_database(credentials, timeout=60, echo=False)
            interface.put_database(database)

        # If its a MetaInterface try to add meta data
        if isinstance(interface, MetaInterface):
            input_vars, _ = interface.get_inputs(True)
            output_vars = interface.get_outputs()
            all_vars = set(input_vars) | set(output_vars)

            for var in all_vars:
                meta = self.get_metadata(var)
                interface.put_meta(var, meta)

        if isinstance(interface, QueryInterface):
            interface.safe_connect()
            interface._db = None

        else:
            interface.connect()

        return interface

    def _build_named_socket(self, socket_str):
        socket = NamedSocket(socket_str)
        for interface_module in INTERFACE_MODULES:
            socket.discover_interfaces(interface_module)

        return socket

    def _build_auto_socket(self, auto_cls):
        auto_socket = Socket()
        interface_factory = InterfaceFactory(auto_cls)

        for var_id in self.data_catalog.get_variable_identifiers():
            metadata = self.data_catalog.get_metadata(var_id)

            # Catch errors here for more informative reporting:
            try:
                data_obj = self.control.get_structure(metadata.structure)
            except KeyError:
                errStr = ("Structure {} not found for variable " "{}").format(
                    metadata.structure, var_id
                )
                raise ValueError(errStr)

            # Allow auto classes with no method to pass
            if (
                auto_cls.get_connect_name() is not None
                and not interface_factory.has_connect_method(data_obj)
            ):
                continue

            AutoCls = interface_factory(metadata, data_obj)

            auto_socket.add_interface(AutoCls)

        return auto_socket

    def _get_force_unavailable(self, simulation):
        hub_force_available = {}

        for hub_definition in simulation._hub_defs:
            hub_name = hub_definition["name"]
            unavailable_hubs = hub_definition["force unavailable"]

            if unavailable_hubs is None:
                hub_force_available[hub_name] = []
            else:
                hub_force_available[hub_name] = unavailable_hubs

        return hub_force_available

    def _schedule_interface(self, project, interface_name=None):
        """Check if any of the hubs have the expected interface scheduled."""

        simulation = project.get_simulation()

        hub_ids = simulation.get_hub_order()
        other_hub_ids = hub_ids[1:]

        # If the interface name is None then reset all the connectors
        if interface_name is None:
            for hub_id in hub_ids:
                self.control.reset_hub(simulation, hub_id)

            return

        # Using a hub_id will reset all the hubs after and including the given
        # id
        elif interface_name in hub_ids:
            hub_index = hub_ids.index(interface_name)
            reset_hub_ids = hub_ids[hub_index:]

            for hub_id in reset_hub_ids:
                self.control.reset_hub(simulation, hub_id)

            return

        for hub_id in hub_ids:
            if self.control.has_interface(simulation, hub_id, interface_name):
                self.control.check_next_interface(
                    simulation, hub_id, interface_name
                )

                # It is assumed that all connectors after the rescheduled one
                # are dependent and therefore should be reset
                for other_hub_id in other_hub_ids:
                    self.control.reset_hub(simulation, other_hub_id)

                return

            else:
                other_hub_ids.pop(0)

        errStr = "Interface {} not in any Hub".format(interface_name)
        raise ValueError(errStr)

    def _set_outputs_status(self, project, simulation=None):
        if simulation is None:
            simulation = project.get_simulation()

        hub_dict = {}

        for hub_id in simulation.get_hub_order():
            if hub_id == "modules":
                inspection_interface_name = simulation.level_map[
                    simulation._inspection_level
                ]

            else:
                inspection_interface_name = None

            interface_dict = {}

            sequenced_interfaces = self.control.get_sequenced_interfaces(
                simulation, hub_id
            )

            for interface_name in sequenced_interfaces:
                outputs_status = self.control.get_output_status(
                    simulation,
                    hub_id,
                    interface_name,
                    force_last_completed=inspection_interface_name,
                )

                interface_dict[interface_name] = outputs_status

            hub_dict[hub_id] = interface_dict

        simulation.set_output_status(hub_dict)

    def _set_inputs_status(self, project, simulation=None):
        pool = project.get_pool()
        if simulation is None:
            simulation = project.get_simulation()

        hub_dict = {}
        hub_force_available = self._get_force_unavailable(simulation)

        for hub_id in simulation.get_hub_order():
            all_unavailable = []

            for hub_name in hub_force_available[hub_id]:
                hub_unavailable = self._get_unavailable_outputs(
                    project, hub_name, simulation
                )
                all_unavailable.extend(hub_unavailable)

            force_unavailable = simulation.get_unavailable_variables()

            if force_unavailable is not None:
                all_unavailable.extend(force_unavailable)

            if not all_unavailable:
                all_unavailable = None

            interface_dict = {}

            sequenced_interfaces = self.control.get_sequenced_interfaces(
                simulation, hub_id
            )

            for interface_name in sequenced_interfaces:
                inputs_status = self.control.get_input_status(
                    pool, simulation, hub_id, interface_name, all_unavailable
                )

                interface_dict[interface_name] = inputs_status

            hub_dict[hub_id] = interface_dict

        simulation.set_input_status(hub_dict)

    def _get_unavailable_outputs(self, project, hub_id, simulation=None):
        # Collect the not satisfied outputs of the modules for the input
        # status of the themes.
        if simulation is None:
            simulation = project.get_simulation()

        all_scheduled_outputs = []

        scheduled_interfaces = self.control.get_scheduled_interfaces(
            simulation, hub_id
        )

        for interface_name in scheduled_interfaces:
            out_status = simulation.get_output_status(hub_id, interface_name)

            all_scheduled_outputs.extend(out_status.keys())

        unavailable_set = set(all_scheduled_outputs)

        return list(unavailable_set)


class Connector:
    """Class for working with interface hubs."""

    def __init__(self, hub_name):
        self._hub = hub_name

    def get_force_completed(self, project):
        simulation = project.get_simulation()
        hub = simulation.get_hub(self._hub)

        return hub.force_completed

    def set_force_completed(self, core, project, value=True):
        simulation = project.get_simulation()
        hub = simulation.get_hub(self._hub)
        hub.force_completed = value

        core.set_interface_status(project)

    def get_available_interfaces(self, core, project):
        simulation = project.get_simulation()
        names = core.control.get_available_interfaces(simulation, self._hub)

        return names

    def get_active_interface_names(self, core, project):
        simulation = project.get_simulation()
        interface_names = core.control.get_sequenced_interfaces(
            simulation, self._hub
        )

        return interface_names

    def has_interface(self, core, project, interface_name):
        interface_names = self.get_active_interface_names(core, project)

        result = False
        if interface_name in interface_names:
            result = True

        return result

    def get_scheduled_interface_names(self, core, project):
        simulation = project.get_simulation()
        interface_names = core.control.get_scheduled_interfaces(
            simulation, self._hub
        )

        return interface_names

    def any_scheduled(self, core, project):
        interface_names = self.get_scheduled_interface_names(core, project)

        result = False
        if interface_names:
            result = True

        return result

    def get_current_interface_name(self, core, project):
        simulation = project.get_simulation()
        interface_name = core.control.get_next_interface(simulation, self._hub)

        return interface_name

    def get_completed_interface_names(self, core, project):
        simulation = project.get_simulation()
        interface_names = core.control.get_completed_interfaces(
            simulation, self._hub
        )

        return interface_names

    def get_interface_inputs(self, core, project, interface_name):
        simulation = project.get_simulation()
        pool = project.get_pool()

        interface = core.control.get_interface_obj(
            simulation, self._hub, interface_name
        )
        input_declaration, _ = interface.get_inputs()

        active_inputs = core.control._get_active_inputs(
            pool, simulation, input_declaration
        )

        return active_inputs

    def get_interface_inputs_status(self, project, interface_name):
        simulation = project.get_simulation()
        inputs_status = simulation.get_input_status(self._hub, interface_name)

        return inputs_status

    def get_interface_outputs(self, core, project, interface_name):
        simulation = project.get_simulation()
        interface = core.control.get_interface_obj(
            simulation, self._hub, interface_name
        )

        output_declaration = interface.get_outputs()

        return output_declaration

    def get_interface_outputs_status(self, project, interface_name):
        simulation = project.get_simulation()
        outputs_status = simulation.get_output_status(self._hub, interface_name)

        return outputs_status

    def get_interface_weight(self, core, project, interface_name):
        """Get the weighting of the interface if set"""

        simulation = project.get_simulation()
        result = core.control.get_interface_weight(
            simulation, self._hub, interface_name
        )

        return result

    def is_interface_executable(
        self, core, project, interface_name, allow_unavailable=False
    ):
        # For the data requirments to be met all the inputs should list
        # as satisfied.
        input_status = self.get_interface_inputs_status(project, interface_name)

        if len(input_status) == 0:
            return True

        status_values = set(input_status.values())

        result = True

        if "required" in status_values:
            result = False

        if "unavailable" in status_values and not allow_unavailable:
            result = False

        return result

    def is_auto_executable(self, core, project, allow_unavailable=False):
        # For the data requirments to be met all the inputs should list
        # as satisfied.
        scheduled_interfaces = self.get_scheduled_interface_names(core, project)

        result = True

        # Try to execute all the interfaces
        for interface_name in scheduled_interfaces:
            # Test for inputs
            can_execute = self.is_interface_executable(
                core,
                project,
                interface_name,
                allow_unavailable=allow_unavailable,
            )

            result = result & can_execute

        return result

    def is_interface_completed(self, core, project, interface_name):
        simulation = project.get_simulation()
        result = core.control.is_interface_completed(
            simulation, self._hub, interface_name
        )

        return result

    def activate_interface(
        self, core, project, interface_name, update_status=True
    ):
        simulation = project.get_simulation()

        core.control.sequence_interface(simulation, self._hub, interface_name)

        if not update_status:
            return

        core.set_interface_status(project)

    def get_interface(
        self, core, project, interface_name, allow_unavailable=False
    ):
        # Only return an interface if it can be exectuted
        if not self.is_interface_executable(
            core, project, interface_name, allow_unavailable
        ):
            errStr = (
                "Input data for interface {} can not be " "provided"
            ).format(interface_name)
            raise RuntimeError(errStr)

        simulation = project.get_simulation()
        interface = core.control.get_interface_obj(
            simulation, self._hub, interface_name
        )

        interface = self._set_inputs(core, project, interface, interface_name)

        return interface

    def execute_interface(
        self,
        core,
        project,
        interface_name,
        level=None,
        register_level=True,
        allow_unavailable=False,
        set_output_level=True,
    ):
        """Add the data required for connecting the interface and then
        connect it"""

        simulation = project.get_simulation()

        # Check the inputs
        self._test_exectuable(core, project, interface_name, allow_unavailable)

        # If level is None build a level name based on the interface name
        # and record the interface name as the current level in the core
        if level is None:
            level = interface_name.lower()
        else:
            level = level.lower()

        # Add an empty datastate at this level
        if register_level:
            registered_level = "{} {}".format(level, core._markers["register"])

            simulation.set_inspection_level(registered_level)

            core.register_level(project, registered_level, interface_name)

        # Get the inteface populated with data
        interface = self.get_interface(
            core, project, interface_name, allow_unavailable
        )

        # Execute the interface.
        interface = core.connect_interface(project, interface)

        # Get outputs from the interface
        checked_vars, checked_values = self._get_outputs(
            core, project, interface
        )

        # Mark interface completed
        core.control.set_interface_completed(
            simulation, self._hub, interface_name
        )

        # Set a level for the datastate including the output marker
        if set_output_level:
            output_level = "{} {}".format(level, core._markers["output"])
            output_level = output_level.lower()
        else:
            output_level = None

        core.add_datastate(project, output_level, checked_vars, checked_values)

        # Set the execution level to the output level
        if register_level and output_level is not None:
            simulation.set_execution_level(output_level)

    def auto_execute(
        self,
        core,
        project,
        force_level=None,
        register_level=True,
        allow_non_execution=False,
    ):
        scheduled_interfaces = self.get_scheduled_interface_names(core, project)

        # Try to execute all the interfaces
        for interface_name in scheduled_interfaces:
            # Test for inputs
            can_execute = self.is_interface_executable(
                core, project, interface_name
            )

            if not can_execute:
                if not allow_non_execution:
                    errStr = (
                        "Required inputs for interface {} are not " "satisfied."
                    ).format(interface_name)
                    raise ValueError(errStr)

                else:
                    log_msg = "Skipping interface {}".format(interface_name)
                    MODULE_LOGGER.info(log_msg)
                    continue

            log_msg = "Auto executing interface {}".format(interface_name)
            MODULE_LOGGER.info(log_msg)

            # Execute the interface
            self.execute_interface(
                core, project, interface_name, force_level, register_level
            )

    def _set_inputs(self, core, project, interface, interface_name):
        (_, optional_inputs) = interface.get_inputs()

        skip_optional = []

        if optional_inputs:
            for putvar in optional_inputs:
                # Test if the data is in the core
                if not core.has_data(project, putvar):
                    skip_optional.append(putvar)

        interface = core.load_interface(
            project, interface, skip_vars=skip_optional
        )

        return interface

    def _get_outputs(self, core, project, interface, filter_none=False):
        """Add variables from the interface into the active data state"""

        checked_vars = []
        checked_values = []

        variables = interface.get_outputs()

        # If there are no output varibles then add an empty state
        if not variables:
            return (None, None)

        raw_data = []

        for getvar in variables:
            raw_data.append(interface.get_data(getvar))

        if not filter_none:
            return variables, raw_data

        # Filter out any None values
        for var, value in zip(variables, raw_data):
            if value is not None:
                checked_vars.append(var)
                checked_values.append(value)

        return checked_vars, checked_values

    def _test_exectuable(
        self, core, project, interface_name, allow_unavailable=False
    ):
        if not self.is_interface_executable(
            core, project, interface_name, allow_unavailable
        ):
            errStr = (
                "Not all inputs of interface {} have been " "satisfied."
            ).format(interface_name)
            raise ValueError(errStr)
