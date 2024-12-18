import os
from copy import deepcopy
from pprint import pprint

import pkg_resources
import pytest
from polite_config.paths import Directory

from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree, _get_connector
from dtocean_core.utils.version import Version

# Check for module and version
pkg_title = "dtocean-maintenance"
pkg_import = "dtocean_maintenance"
major_version = 3

pytest.importorskip(pkg_import)
version = pkg_resources.get_distribution(pkg_title).version
pytestmark = pytest.mark.skipif(
    Version(version).major != major_version,
    reason="module has incorrect major version",
)

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


def test_maintenance_inputs(module_menu, core, wave_project, var_tree):
    mod_name = "Operations and Maintenance"
    data_menu = DataMenu()
    project_menu = ProjectMenu()

    project = deepcopy(wave_project)
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)

    operations_branch = var_tree.get_branch(core, project, mod_name)

    operations_input_status = operations_branch.get_input_status(core, project)

    assert "options.operations_inspections" in operations_input_status


def test_get_maintenance_interface(module_menu, core, wave_project, var_tree):
    mod_name = "Operations and Maintenance"

    project_menu = ProjectMenu()
    project = deepcopy(wave_project)
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    operations_branch = var_tree.get_branch(core, project, mod_name)
    operations_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp6.pkl")
    )
    operations_branch.read_auto(core, project)

    can_execute = module_menu.is_executable(core, project, mod_name)

    if not can_execute:
        inputs = operations_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core, project, mod_name)

    assert interface.data.system_type is not None


def test_maintenance_interface_entry(
    module_menu, core, wave_project, var_tree, mocker, tmpdir
):
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))

    mocker.patch(
        "dtocean_core.interfaces.maintenance.UserDataPath",
        return_value=mock_dir,
        autospec=True,
    )

    mod_name = "Operations and Maintenance"

    project_menu = ProjectMenu()
    project = deepcopy(wave_project)
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    operations_branch = var_tree.get_branch(core, project, mod_name)
    operations_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_wp6.pkl")
    )
    operations_branch.read_auto(core, project)

    can_execute = module_menu.is_executable(core, project, mod_name)

    if not can_execute:
        inputs = operations_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core, project, mod_name)

    interface.connect(debug_entry=True, export_data=True)

    debugdir = config_tmpdir.join("..", "debug")

    assert len(debugdir.listdir()) == 1
