import os
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
import pytest

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree
from dtocean_plugins.modules.modules import ModuleInterface

dir_path = os.path.dirname(__file__)


class MockModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Module"

    @classmethod
    def declare_weight(cls):
        return 999

    @classmethod
    def declare_inputs(cls):
        input_list = ["farm.wave_series"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = ["farm.wave_occurrence", "device.wave_power_matrix"]

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(self):
        id_map = {
            "dummy": "farm.wave_series",
            "dummy1": "device.wave_power_matrix",
            "dummy2": "farm.wave_occurrence",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        return


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    """Share a Core object"""

    new_core = Core()
    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)

    return new_core


@pytest.fixture(scope="module")
def tree():
    """Share a Tree object"""

    new_tree = Tree()

    return new_tree


@pytest.fixture(scope="module")
def project(core, tree):
    """Share a Project object"""

    project_title = "Test"

    project_menu = ProjectMenu()

    new_project = project_menu.new_project(core, project_title)

    options_branch = tree.get_branch(core, new_project, "System Type Selection")
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )
    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    return new_project


def test_TeHm0Plot_available(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp2_wave.pkl")
    )

    wave_series = mod_branch.get_input_variable(
        core, project, "farm.wave_series"
    )
    result = wave_series.get_available_plots(core, project)

    assert "Te & Hm0 Time Series" in result


def test_TeHm0Plot(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp2_wave.pkl")
    )

    wave_series = mod_branch.get_input_variable(
        core, project, "farm.wave_series"
    )
    wave_series.plot(core, project, "Te & Hm0 Time Series")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_WaveOccurrencePlot_available(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    # Force addition of occurance matrix
    occurrence_matrix_coords = [[0.0, 1], [0.0, 1], [0.0, 1]]
    matrix_xgrid = {
        "values": np.ones([2, 2, 2]),
        "coords": occurrence_matrix_coords,
    }

    core.add_datastate(
        project, identifiers=["farm.wave_occurrence"], values=[matrix_xgrid]
    )

    mod_branch = tree.get_branch(core, project, mod_name)
    wave_occurrence = mod_branch.get_output_variable(
        core, project, "farm.wave_occurrence"
    )
    result = wave_occurrence.get_available_plots(core, project)

    assert "Wave Resource Occurrence Matrix" in result


def test_WaveOccurrencePlot(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    # Force addition of occurance matrix
    occurrence_matrix_coords = [[0.0, 1], [0.0, 1], [0.0, 1]]
    matrix_xgrid = {
        "values": np.ones([2, 2, 2]),
        "coords": occurrence_matrix_coords,
    }

    core.add_datastate(
        project, identifiers=["farm.wave_occurrence"], values=[matrix_xgrid]
    )

    mod_branch = tree.get_branch(core, project, mod_name)
    wave_occurrence = mod_branch.get_output_variable(
        core, project, "farm.wave_occurrence"
    )
    wave_occurrence.plot(core, project, "Wave Resource Occurrence Matrix")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_PowerMatrixPlot_available(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    # Force addition of power matrix
    power_matrix_coords = [[0.0, 1], [0.0, 1], [0.0, 1]]
    matrix_xgrid = {"values": np.ones([2, 2, 2]), "coords": power_matrix_coords}

    core.add_datastate(
        project, identifiers=["device.wave_power_matrix"], values=[matrix_xgrid]
    )

    mod_branch = tree.get_branch(core, project, mod_name)
    power_matrix = mod_branch.get_output_variable(
        core, project, "device.wave_power_matrix"
    )
    result = power_matrix.get_available_plots(core, project)

    assert "Single Wave Device Power Matrix" in result


def test_PowerMatrixPlot(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    # Force addition of power matrix
    power_matrix_coords = [[0.0, 1], [0.0, 1], [0.0, 1]]
    matrix_xgrid = {"values": np.ones([2, 2, 2]), "coords": power_matrix_coords}

    core.add_datastate(
        project, identifiers=["device.wave_power_matrix"], values=[matrix_xgrid]
    )

    mod_branch = tree.get_branch(core, project, mod_name)
    power_matrix = mod_branch.get_output_variable(
        core, project, "device.wave_power_matrix"
    )
    power_matrix.plot(core, project, "Single Wave Device Power Matrix")

    assert len(plt.get_fignums()) == 1

    plt.close("all")
