import os
from copy import deepcopy

import matplotlib.pyplot as plt
import pytest

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import InputVariable, Tree
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
        input_list = ["bathymetry.layers", "corridor.layers"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = None

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {"dummy1": "bathymetry.layers", "dummy2": "corridor.layers"}

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


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
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    return new_project


def test_CombinedBathyPlot_available(core, project, tree, inputs_wp3):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core, project, inputs_wp3)
    bathy = mod_branch.get_input_variable(core, project, "bathymetry.layers")

    assert isinstance(bathy, InputVariable)
    result = bathy.get_available_plots(core, project)

    assert "Combined Bathymetry" in result


def test_CombinedBathyPlot(core, project, tree, inputs_wp3):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core, project, inputs_wp3)

    bathy = mod_branch.get_input_variable(core, project, "bathymetry.layers")
    bathy.plot(core, project, "Combined Bathymetry")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_CombinedSedimentPlot_available(core, project, tree, inputs_wp3):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core, project, inputs_wp3)

    bathy = mod_branch.get_input_variable(core, project, "bathymetry.layers")
    result = bathy.get_available_plots(core, project)

    assert "Combined Sediment (First Layer)" in result


def test_CombinedSedimentPlot(core, project, tree, inputs_wp3):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core, project, inputs_wp3)

    bathy = mod_branch.get_input_variable(core, project, "bathymetry.layers")
    bathy.plot(core, project, "Combined Sediment (First Layer)")

    assert len(plt.get_fignums()) == 1

    plt.close("all")
