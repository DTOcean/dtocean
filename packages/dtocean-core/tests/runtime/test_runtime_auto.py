# pylint: disable=redefined-outer-name

import os
from copy import deepcopy

import matplotlib.pyplot as plt
import pytest

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import InputVariable, Tree
from dtocean_plugins.modules.base import ModuleInterface


class MockModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Module"

    @classmethod
    def declare_weight(cls):
        return 998

    @classmethod
    def declare_inputs(cls):
        input_list = [
            "device.turbine_performance",
            "device.cut_in_velocity",
            "device.system_type",
        ]

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
        id_map = {
            "dummy1": "device.turbine_performance",
            "dummy2": "device.cut_in_velocity",
            "dummy3": "device.system_type",
        }

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


def test_NumpyLine_has_plot(core, project):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    module_menu.activate(core, project, "Mock Module")

    project_menu.initiate_dataflow(core, project)

    test = InputVariable("device.turbine_performance")
    result = test._find_receiving_interface(core, "AutoPlot")

    assert result is not None
    assert "device.turbine_performance AutoPlot Interface" == result.get_name()


def test_auto_plot(core, project, tree, inputs_wp2_tidal):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core, project, inputs_wp2_tidal)

    cp_curve = hydro_branch.get_input_variable(
        core, project, "device.turbine_performance"
    )
    cp_curve.plot(core, project)

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_set_auto_raw(core, project, tree):
    mod_name = "Mock Module"
    var_id = "device.system_type"

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    new_var.set_raw_interface(core, "Tidal Fixed")

    assert new_var._interface.data.result == "Tidal Fixed"


def test_get_file_input_interfaces(core, project, tree):
    mod_name = "Mock Module"
    var_id = "device.turbine_performance"

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    new_var.get_file_input_interfaces(core)

    assert new_var


def test_set_file_input_interface(core, project, tree):
    mod_name = "Mock Module"
    var_id = "device.turbine_performance"

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    new_var.set_file_interface(core, "some/path/to/some/file")

    assert new_var


def test_auto_file_read(core, project, tree, test_data_path):
    mod_name = "Mock Module"
    var_id = "device.turbine_performance"

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    assert isinstance(new_var, InputVariable)
    new_var.read_file(core, project, test_data_path / "tidal_performance.csv")

    inputs = hydro_branch.get_input_status(core, project)

    assert inputs[var_id] == "satisfied"


def test_get_file_output_interfaces(core, project, tree):
    mod_name = "Mock Module"
    var_id = "device.turbine_performance"

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    new_var.get_file_output_interfaces(core, project)

    assert new_var


def test_auto_write_file(tmpdir, core, project, tree, test_data_path):
    mod_name = "Mock Module"
    var_id = "device.turbine_performance"

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    new_var.set_file_interface(core, test_data_path / "tidal_performance.csv")
    new_var.read(core, project)

    output_path = str(tmpdir.join("tidal_performance_copy.csv"))
    new_var.write_file(core, project, output_path)

    assert os.path.exists(output_path)
