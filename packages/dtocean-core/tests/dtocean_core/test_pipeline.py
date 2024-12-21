import os
from copy import deepcopy

import pytest

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import (
    InputVariable,
    OutputVariable,
    Tree,
    Variable,
    set_output_scope,
)
from dtocean_plugins.modules.modules import ModuleInterface
from dtocean_plugins.themes.themes import ThemeInterface

DIR_PATH = os.path.dirname(__file__)


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
            "bathymetry.layers",
            "device.cut_in_velocity",
            "device.system_type",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = [
            "device.power_rating",
            "project.layout",
            "project.annual_energy",
            "project.number_of_devices",
        ]

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "bathymetry.layers",
            "dummy2": "device.cut_in_velocity",
            "dummy3": "device.system_type",
            "dummy4": "device.power_rating",
            "dummy5": "project.layout",
            "dummy6": "project.annual_energy",
            "dummy7": "project.number_of_devices",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        self.data.dummy4 = 1.0
        self.data.dummy5 = {"device0": [0, 0]}
        self.data.dummy6 = 1.0
        self.data.dummy7 = 1

        return


class AnotherMockModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Module 2"

    @classmethod
    def declare_weight(cls):
        return 999

    @classmethod
    def declare_inputs(cls):
        input_list = [
            "device.power_rating",
            "project.layout",
            "project.number_of_devices",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = ["project.export_voltage"]

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "device.power_rating",
            "dummy2": "project.layout",
            "dummy3": "project.number_of_devices",
            "dummy4": "project.export_voltage",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        self.data.dummy4 = 1.0

        return


class MockTheme(ThemeInterface):
    @classmethod
    def get_name(cls):
        return "Mock Theme"

    @classmethod
    def declare_weight(cls):
        return 999

    @classmethod
    def declare_inputs(cls):
        input_list = [
            "project.discount_rate",
            "project.number_of_devices",
            "project.export_voltage",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = ["project.capex_total"]

        return output_list

    @classmethod
    def declare_optional(cls):
        option_list = [
            "project.discount_rate",
            "project.number_of_devices",
            "project.export_voltage",
        ]

        return option_list

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "project.discount_rate",
            "dummy2": "project.number_of_devices",
            "dummy3": "project.export_voltage",
            "dummy4": "project.capex_total",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        total = 0.0

        if self.data.dummy2 is not None:
            total += self.data.dummy2

        if self.data.dummy3 is not None:
            total += self.data.dummy3

        self.data.dummy4 = total

        return


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    """Share a Core object"""

    new_core = Core()

    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)
    socket.add_interface(AnotherMockModule)

    socket = new_core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)

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


@pytest.fixture(scope="module")
def module_menu(core):
    """Share a ModuleMenu object"""

    return ModuleMenu()


@pytest.fixture(scope="module")
def theme_menu(core):
    """Share a ModuleMenu object"""

    return ThemeMenu()


def test_Branch_get_input_status(core, project, module_menu, tree):
    mod_name = "Mock Module"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    inputs = hydro_branch.get_input_status(core, project)

    assert "bathymetry.layers" in inputs.keys()
    assert inputs["bathymetry.layers"] == "required"


def test_Branch_get_input_variable(core, project, module_menu, tree):
    mod_name = "Mock Module"
    var_id = "device.cut_in_velocity"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    assert isinstance(new_var, InputVariable)


def test_Branch_get_output_status(core, project, module_menu, tree):
    mod_name = "Mock Module"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    outputs = hydro_branch.get_output_status(core, project)

    assert "project.annual_energy" in outputs.keys()
    assert outputs["project.annual_energy"] == "unavailable"


def test_Branch_get_output_variable(core, project, module_menu, tree):
    mod_name = "Mock Module"
    var_id = "project.annual_energy"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_output_variable(core, project, var_id)

    assert isinstance(new_var, OutputVariable)


def test_Branch_get_input_status_overwritten(core, project, module_menu, tree):
    project = deepcopy(project)

    module_menu.activate(core, project, "Mock Module")
    module_menu.activate(core, project, "Mock Module 2")

    electric_branch = tree.get_branch(core, project, "Mock Module 2")

    inputs = electric_branch.get_input_status(core, project)

    assert inputs["device.power_rating"] == "overwritten"
    assert inputs["project.layout"] == "overwritten"


def test_Branch_get_output_status_overwritten(core, project, module_menu, tree):
    project = deepcopy(project)

    module_menu.activate(core, project, "Mock Module")
    module_menu.activate(core, project, "Mock Module 2")

    hydro_branch = tree.get_branch(core, project, "Mock Module")
    outputs = hydro_branch.get_output_status(core, project)

    assert outputs["project.number_of_devices"] == "unavailable"


def test_Branch_reset(core, project, module_menu, tree, inputs_wp2_tidal):
    project = deepcopy(project)

    module_menu.activate(core, project, "Mock Module")
    module_menu.activate(core, project, "Mock Module 2")

    mod1_branch = tree.get_branch(core, project, "Mock Module")
    mod1_branch.read_test_data(core, project, inputs_wp2_tidal)

    mod2_branch = tree.get_branch(core, project, "Mock Module 2")
    mod2_branch.read_test_data(core, project, inputs_wp2_tidal)

    module_menu.execute_current(core, project)
    module_menu.execute_current(core, project)

    simulation = project.get_simulation()

    assert simulation.get_inspection_level() == "mock module 2 start"

    mod1_branch.reset(core, project)

    assert simulation.get_inspection_level() == "mock module start"


def test_Variable_get_auto_raw_interfaces(core, project, module_menu, tree):
    project = deepcopy(project)

    mod_name = "Mock Module"
    var_id = "device.cut_in_velocity"

    module_menu.activate(core, project, mod_name)
    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)
    list_raw = new_var.get_raw_interfaces(core, include_auto=True)

    assert "device.cut_in_velocity AutoRaw Interface" in list_raw


def test_Variable_set_raw_interface(core, project, module_menu, tree):
    mod_name = "Mock Module"
    var_id = "device.system_type"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)

    new_var.set_raw_interface(core, "Tidal Fixed")
    new_var.read(core, project)

    inputs = hydro_branch.get_input_status(core, project)

    assert inputs["device.system_type"] == "satisfied"


def test_Variable_get_metadata(core, project, module_menu, tree):
    mod_name = "Mock Module"
    var_id = "device.system_type"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)
    metadata = new_var.get_metadata(core)

    assert metadata.title == "Device Technology Type"


def test_Variable_get_value(core, project, module_menu, tree):
    mod_name = "Mock Module"
    var_id = "device.system_type"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)

    hydro_branch = tree.get_branch(core, project, mod_name)
    new_var = hydro_branch.get_input_variable(core, project, var_id)
    new_var.set_raw_interface(core, "Tidal Fixed")
    new_var.read(core, project)

    value = new_var.get_value(core, project)

    assert value == "Tidal Fixed"


def test_Variable__select_interface_multiple_error(core):
    test = Variable("test")

    with pytest.raises(ValueError):
        test._select_interface(
            [MockModule(), AnotherMockModule()],
            "ModuleInterface",
            False,
            False,
        )


def test_set_output_scope(
    core,
    project,
    module_menu,
    theme_menu,
    tree,
    inputs_wp2_tidal,
):
    project = deepcopy(project)

    module_menu.activate(core, project, "Mock Module")
    module_menu.activate(core, project, "Mock Module 2")
    theme_menu.activate(core, project, "Mock Theme")

    mod1_branch = tree.get_branch(core, project, "Mock Module")
    mod1_branch.read_test_data(core, project, inputs_wp2_tidal)

    mod2_branch = tree.get_branch(core, project, "Mock Module 2")
    mod2_branch.read_test_data(core, project, inputs_wp2_tidal)

    module_menu.execute_current(core, project)
    module_menu.execute_current(core, project)

    theme_branch = tree.get_branch(core, project, "Mock Theme")
    new_var = theme_branch.get_output_variable(
        core, project, "project.capex_total"
    )
    value = new_var.get_value(core, project)

    assert value == 2

    set_output_scope(core, project, scope="local")

    value = new_var.get_value(core, project)

    assert value == 1

    assert value == 1
