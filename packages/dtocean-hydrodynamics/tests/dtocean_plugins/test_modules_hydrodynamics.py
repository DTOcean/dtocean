import os
from copy import deepcopy
from pprint import pprint

import pytest

pytest.importorskip("dtocean_core")

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree, _get_connector

dir_path = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def core():
    """Share a Core object"""

    new_core = Core()

    return new_core


@pytest.fixture(scope="module")
def var_tree():
    return Tree()


@pytest.fixture(scope="module")
def module_menu(core):
    """Share a ModuleMenu object"""

    return ModuleMenu()


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def tidal_project(core, var_tree):
    """Share a Project object"""

    project_menu = ProjectMenu()

    new_project = project_menu.new_project(core, "test tidal")

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


@pytest.fixture(scope="module")
def wave_project(core, var_tree):
    """Share a Project object"""

    project_menu = ProjectMenu()

    new_project = project_menu.new_project(core, "test wave")

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )
    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    return new_project


def test_wave_not_inputs(module_menu, core, wave_project, var_tree):
    mod_name = "Hydrodynamics"
    #    project_menu = ProjectMenu()

    project = deepcopy(wave_project)
    module_menu.activate(core, project, mod_name)
    #    project = project_menu.initiate_filter(core, project)

    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_input_status = hydro_branch.get_input_status(core, project)

    assert "device.cut_in_velocity" not in hydro_input_status


def test_get_wave_interface(module_menu, core, wave_project, var_tree):
    mod_name = "Hydrodynamics"
    #    project_menu = ProjectMenu()

    project = deepcopy(wave_project)
    module_menu.activate(core, project, mod_name)
    #    project = project_menu.initiate_filter(core, project)

    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp2_wave.pkl")
    )

    can_execute = module_menu.is_executable(core, project, mod_name)

    if not can_execute:
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core, project, mod_name)

    assert interface.data.wave_data_directory is not None


def test_wave_interface_entry(
    module_menu,
    core,
    wave_project,
    var_tree,
    mocker,
    tmp_path,
):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.interfaces.hydrodynamics.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    mod_name = "Hydrodynamics"

    project = deepcopy(wave_project)
    module_menu.activate(core, project, mod_name)
    #    project_menu.initiate_filter(core, project)

    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp2_wave.pkl")
    )

    can_execute = module_menu.is_executable(core, project, mod_name)

    if not can_execute:
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core, project, mod_name)

    interface.connect(debug_entry=True, export_data=True)

    debugdir = config_tmpdir.join("..", "debug")

    assert len(debugdir.listdir()) == 1


def test_tidal_inputs(module_menu, core, tidal_project, var_tree):
    mod_name = "Hydrodynamics"
    #    project_menu = ProjectMenu()

    project = deepcopy(tidal_project)
    module_menu.activate(core, project, mod_name)
    #    project_menu.initiate_filter(core, project)

    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_input_status = hydro_branch.get_input_status(core, project)

    assert "device.cut_in_velocity" in hydro_input_status


def test_get_tidal_interface(module_menu, core, tidal_project, var_tree):
    mod_name = "Hydrodynamics"
    #    project_menu = ProjectMenu()

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp2_tidal.pkl")
    )

    can_execute = module_menu.is_executable(core, project, mod_name)

    if not can_execute:
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core, project, mod_name)

    assert interface.data.perf_curves is not None


def test_tidal_interface_entry(
    module_menu,
    core,
    tidal_project,
    var_tree,
    mocker,
    tmp_path,
):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.interfaces.hydrodynamics.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    mod_name = "Hydrodynamics"

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp2_tidal.pkl")
    )

    can_execute = module_menu.is_executable(core, project, mod_name)

    if not can_execute:
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core, project, mod_name)

    interface.connect(debug_entry=True, export_data=True)

    debugdir = config_tmpdir.join("..", "debug")

    assert len(debugdir.listdir()) == 1


def test_tidal_interface_entry_fail(module_menu, core, tidal_project, var_tree):
    mod_name = "Hydrodynamics"

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = var_tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp2_tidal.pkl")
    )

    user_layout = hydro_branch.get_input_variable(
        core, project, "options.user_array_layout"
    )
    user_layout.set_raw_interface(core, None)
    user_layout.read(core, project)

    can_execute = module_menu.is_executable(core, project, mod_name)

    if not can_execute:
        inputs = hydro_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core, project, mod_name)

    with pytest.raises(ValueError):
        interface.connect(debug_entry=True)
