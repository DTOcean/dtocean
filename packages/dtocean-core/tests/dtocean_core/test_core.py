# pylint: disable=redefined-outer-name,protected-access

import json
import os
import shutil
from copy import deepcopy

import pytest

from dtocean_core.core import Connector, Core, OrderedSim, Project
from dtocean_core.menu import ModuleMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree
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
            "device.system_type",
            "device.power_rating",
            "device.cut_in_velocity",
            "device.turbine_interdistance",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = [
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
            "dummy8": "device.turbine_interdistance",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
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
        input_list = ["project.discount_rate"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = ["project.capex_total"]

        return output_list

    @classmethod
    def declare_optional(cls):
        option_list = ["project.discount_rate"]

        return option_list

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "project.discount_rate",
            "dummy2": "project.capex_total",
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

    socket = new_core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)

    return new_core


@pytest.fixture(scope="module")
def var_tree():
    return Tree()


@pytest.fixture(scope="module")
def project(core, var_tree):
    """Share a Project object"""

    project_title = "Test"

    project_menu = ProjectMenu()

    new_project = project_menu.new_project(core, project_title)

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    return new_project


def test_init_core():
    new_core = Core()

    assert isinstance(new_core, Core)


def test_init_project():
    new_project = Project("Test")

    assert isinstance(new_project, Project)


def test_is_valid_variable():
    core = Core()
    test_var = "device.selected_name"

    result = core.is_valid_variable(test_var)

    assert result


def test_execute_output_level(core, var_tree):
    project_title = "Test"

    project_menu = ProjectMenu()

    new_project = project_menu.new_project(core, project_title)

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)

    project_menu._execute(core, new_project, "System Type Selection")

    current_sim = new_project.get_simulation()
    output_level = "System Type Selection {}".format(core._markers["output"])

    assert current_sim._execution_level == output_level.lower()


def test_dump_project(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, "Mock Module")
    hydro_branch.read_test_data(core, project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, project, "Mock Theme")
    eco_branch.read_test_data(core, project, inputs_economics)
    core.dump_project(project, str(tmpdir))
    project_file_path = os.path.join(str(tmpdir), "project.pkl")

    assert os.path.isfile(project_file_path)


def test_dump_project_archive(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, "Mock Module")
    hydro_branch.read_test_data(core, project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, project, "Mock Theme")
    eco_branch.read_test_data(core, project, inputs_economics)

    project_file_name = "my_project.prj"
    project_file_path = os.path.join(str(tmpdir), project_file_name)

    core.dump_project(project, project_file_path)

    assert os.path.isfile(project_file_path)


def test_dump_project_nodir(core, project, var_tree):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    with pytest.raises(ValueError):
        core.dump_project(project, "some_path")


def test_load_project_archive(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, "Mock Module")
    hydro_branch.read_test_data(core, project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, project, "Mock Theme")
    eco_branch.read_test_data(core, project, inputs_economics)

    project_file_name = "my_project.prj"
    project_file_path = os.path.join(str(tmpdir), project_file_name)

    core.dump_project(project, project_file_path)

    del project

    assert os.path.isfile(project_file_path)

    new_root = os.path.join(str(tmpdir), "test")
    os.makedirs(new_root)

    move_file_path = os.path.join(str(tmpdir), "test", project_file_name)

    shutil.copy2(project_file_path, move_file_path)

    loaded_project = core.load_project(move_file_path)
    active_sim = loaded_project.get_simulation()

    assert loaded_project.check_integrity()
    assert active_sim.get_title() == "Default"
    assert "Mock Module" in module_menu.get_scheduled(core, loaded_project)


def test_load_project_bad_ext(core):
    with pytest.raises(ValueError):
        core.load_project("bad_ext.bad")


def test_dump_datastate(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, "Mock Module")
    hydro_branch.read_test_data(core, project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, project, "Mock Theme")
    eco_branch.read_test_data(core, project, inputs_economics)
    core.dump_datastate(project, str(tmpdir))

    datastate_file_path = os.path.join(str(tmpdir), "datastate_dump.json")
    pool_file_path = os.path.join(str(tmpdir), "pool.pkl")

    assert os.path.isfile(datastate_file_path)
    assert os.path.isfile(pool_file_path)


def test_dump_datastate_archive(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, "Mock Module")
    hydro_branch.read_test_data(core, project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, project, "Mock Theme")
    eco_branch.read_test_data(core, project, inputs_economics)

    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)

    core.dump_datastate(project, datastate_file_path)

    assert os.path.isfile(datastate_file_path)


def test_dump_datastate_nodir(core, project, var_tree):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    with pytest.raises(ValueError):
        core.dump_datastate(project, "some_path")


def test_load_datastate_archive(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    temp_project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, temp_project, "Mock Module")
    theme_menu.activate(core, temp_project, "Mock Theme")

    project_menu.initiate_dataflow(core, temp_project)

    hydro_branch = var_tree.get_branch(core, temp_project, "Mock Module")
    hydro_branch.read_test_data(core, temp_project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, temp_project, "Mock Theme")
    eco_branch.read_test_data(core, temp_project, inputs_economics)

    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)

    core.dump_datastate(temp_project, datastate_file_path)

    del temp_project

    assert os.path.isfile(datastate_file_path)

    new_root = os.path.join(str(tmpdir), "test")
    os.makedirs(new_root)

    move_file_path = os.path.join(str(tmpdir), "test", datastate_file_name)
    shutil.copy2(datastate_file_path, move_file_path)

    temp_project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, temp_project, "Mock Module")

    project_menu.initiate_dataflow(core, temp_project)

    assert not core.has_data(temp_project, "device.turbine_interdistance")

    core.load_datastate(temp_project, move_file_path)

    assert temp_project.check_integrity()
    assert core.has_data(temp_project, "device.turbine_interdistance")


def test_load_datastate_archive_exclude(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    temp_project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, temp_project, "Mock Module")
    theme_menu.activate(core, temp_project, "Mock Theme")

    project_menu.initiate_dataflow(core, temp_project)

    hydro_branch = var_tree.get_branch(core, temp_project, "Mock Module")
    hydro_branch.read_test_data(core, temp_project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, temp_project, "Mock Theme")
    eco_branch.read_test_data(core, temp_project, inputs_economics)

    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)

    core.dump_datastate(temp_project, datastate_file_path)

    del temp_project

    assert os.path.isfile(datastate_file_path)

    new_root = os.path.join(str(tmpdir), "test")
    os.makedirs(new_root)

    move_file_path = os.path.join(str(tmpdir), "test", datastate_file_name)
    shutil.copy2(datastate_file_path, move_file_path)

    temp_project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, temp_project, "Mock Module")

    project_menu.initiate_dataflow(core, temp_project)

    assert not core.has_data(temp_project, "device.turbine_interdistance")
    assert not core.has_data(temp_project, "device.power_rating")

    core.load_datastate(
        temp_project, move_file_path, exclude="turbine_interdistance"
    )

    assert temp_project.check_integrity()
    assert not core.has_data(temp_project, "device.turbine_interdistance")
    assert core.has_data(temp_project, "device.power_rating")


def test_load_datastate_bad_id(
    core,
    project,
    var_tree,
    tmpdir,
    inputs_wp2_tidal,
    inputs_economics,
):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, "Mock Module")
    hydro_branch.read_test_data(core, project, inputs_wp2_tidal)

    eco_branch = var_tree.get_branch(core, project, "Mock Theme")
    eco_branch.read_test_data(core, project, inputs_economics)
    core.dump_datastate(project, str(tmpdir))

    # Modify the json file with an entry not in the catalogue
    datastate_file_path = os.path.join(str(tmpdir), "datastate_dump.json")

    with open(datastate_file_path, "r") as f:
        data = json.load(f)
        data["data"]["fake.entry"] = ""

    # Rewrite the file
    os.remove(datastate_file_path)

    with open(datastate_file_path, "w") as f:
        json.dump(data, f)

    # Try to load the datastate
    core.load_datastate(project, str(tmpdir))

    assert True


def test_OrderedSim_get_output_ids(core, project):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)
    test = project.get_simulation()

    result = test.get_output_ids()

    assert set(result) == set(
        [
            "project.annual_energy",
            "hidden.pipeline_active",
            "project.number_of_devices",
            "project.capex_total",
            "project.layout",
        ]
    )


def test_OrderedSim_get_output_ids_hub_id(core, project):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)
    test = project.get_simulation()

    result = test.get_output_ids(hub_id="modules")

    assert set(result) == set(
        ["project.annual_energy", "project.number_of_devices", "project.layout"]
    )


def test_OrderedSim_get_output_ids_interface_name(core, project):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)
    test = project.get_simulation()

    result = test.get_output_ids(hub_id="modules", interface_name="Mock Module")

    assert set(result) == set(
        ["project.annual_energy", "project.number_of_devices", "project.layout"]
    )


def test_OrderedSim_get_output_ids_valid_statuses(core, project):
    project = deepcopy(project)

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    module_menu.activate(core, project, "Mock Module")
    theme_menu.activate(core, project, "Mock Theme")

    project_menu.initiate_dataflow(core, project)
    test = project.get_simulation()

    result = test.get_output_ids(valid_statuses=["satisfied"])

    assert set(result) == set(["hidden.pipeline_active"])


def test_Project_add_simulation(project):
    project = deepcopy(project)

    new_sim = OrderedSim("test")
    project.add_simulation(new_sim, True)

    assert project.get_simulation_title() == "test"


def test_Project_remove_simulation_by_title(project):
    project = deepcopy(project)

    new_sim = OrderedSim("test")
    project.add_simulation(new_sim, True)

    assert project.get_simulation_title() == "test"
    assert len(project) == 2

    simulation = project.remove_simulation(title="test")

    assert simulation.get_title() == "test"
    assert project.get_simulation_title() == "Default"
    assert len(project) == 1


def test_Project_remove_simulation_by_index(project):
    project = deepcopy(project)

    new_sim = OrderedSim("test")
    project.add_simulation(new_sim, True)

    assert project.get_simulation_title() == "test"
    assert len(project) == 2

    simulation = project.remove_simulation(index=0)

    assert simulation.get_title() == "Default"
    assert project.get_simulation_title() == "test"
    assert len(project) == 1


def test_Project_remove_simulation_error(project):
    project = deepcopy(project)

    new_sim = OrderedSim("test")
    project.add_simulation(new_sim, True)

    assert project.get_simulation_title() == "test"
    assert len(project) == 2

    with pytest.raises(ValueError) as excinfo:
        project.remove_simulation()

    assert "an index or simulation title is required" in str(excinfo)


def test_Project_set_simulation_title(project):
    project = deepcopy(project)
    project.set_simulation_title("test")

    assert project.get_simulation_title() == "test"


def test_Project_set_simulation_title_identical(project):
    project = deepcopy(project)

    assert project.get_simulation_title() == "Default"

    project.set_simulation_title("Default")

    assert True


def test_Project_set_simulation_title_used(project):
    project = deepcopy(project)

    new_sim = OrderedSim("test")
    project.add_simulation(new_sim, True)

    with pytest.raises(ValueError):
        project.set_simulation_title("Default")


def test_Project_active_index_none():
    mock_sim = OrderedSim("mock")
    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)

    assert mock_project._active_index == 0

    mock_project.remove_simulation(0)

    assert mock_project._active_index is None


def test_Connector_force_completed(core, project):
    project = deepcopy(project)

    connector = Connector("project")
    connector.set_force_completed(core, project)

    assert connector.get_force_completed(project)


def test_Core_import_simulation_from_clone(core, project):
    src_project = deepcopy(project)
    dst_project = deepcopy(project)
    dst_pool = dst_project.get_pool()

    assert len(dst_project) == 1
    assert len(dst_pool) == 2
    assert src_project != dst_project

    core.import_simulation(src_project, dst_project, "Test")

    dst_pool = dst_project.get_pool()

    assert len(dst_project) == 2
    assert dst_project.title == "Test"
    assert len(dst_pool) == 2


def test_Core_import_simulation_from_new(core, project, var_tree):
    dst_project = deepcopy(project)
    dst_pool = dst_project.get_pool()

    assert len(dst_project) == 1
    assert len(dst_pool) == 2

    project_menu = ProjectMenu()
    src_project = project_menu.new_project(core, "New")

    options_branch = var_tree.get_branch(
        core, src_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, src_project, "device.system_type"
    )
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, src_project)

    project_menu.initiate_pipeline(core, src_project)

    src_pool = src_project.get_pool()

    assert len(src_project) == 1
    assert len(src_pool) == 2
    assert src_project != dst_project

    core.import_simulation(src_project, dst_project, "Test")

    dst_pool = dst_project.get_pool()

    assert len(dst_project) == 2
    assert dst_project.title == "Test"
    assert len(dst_pool) == 4


def test_Core_remove_simulation(core, project, var_tree):
    dst_project = deepcopy(project)
    dst_pool = dst_project.get_pool()

    assert len(dst_project) == 1
    assert len(dst_pool) == 2

    project_menu = ProjectMenu()
    src_project = project_menu.new_project(core, "New")

    options_branch = var_tree.get_branch(
        core, src_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, src_project, "device.system_type"
    )
    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, src_project)

    project_menu.initiate_pipeline(core, src_project)

    src_pool = src_project.get_pool()

    assert len(src_project) == 1
    assert len(src_pool) == 2
    assert src_project != dst_project

    core.import_simulation(src_project, dst_project, "Test")

    dst_pool = dst_project.get_pool()
    test_value = core.get_data_value(dst_project, "device.system_type")

    assert len(dst_project) == 2
    assert dst_project.title == "Test"
    assert len(dst_pool) == 4
    assert test_value == "Wave Floating"

    core.remove_simulation(dst_project, sim_title="Test")

    test_value = core.get_data_value(dst_project, "device.system_type")

    assert len(dst_project) == 1
    assert len(dst_pool) == 2
    assert project.get_simulation_title() == "Default"
    assert test_value == "Tidal Fixed"
