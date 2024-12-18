import os
from copy import deepcopy
from pprint import pprint

import pkg_resources
import pytest
from polite_config.paths import Directory

from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree, _get_connector
from dtocean_core.utils.version import Version

# Check for module and version
pkg_title = "dtocean-reliability"
pkg_import = "dtocean_reliability"
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
def theme_menu(core):
    """Share a ModuleMenu object"""

    return ThemeMenu()


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


def test_reliability_inputs(theme_menu, core, tidal_project, var_tree):
    theme_name = "Reliability"
    data_menu = DataMenu()

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)

    reliability_branch = var_tree.get_branch(core, project, theme_name)

    reliability_input_status = reliability_branch.get_input_status(
        core, project
    )

    assert reliability_input_status is not None


def test_get_reliability_interface(theme_menu, core, tidal_project, var_tree):
    theme_name = "Reliability"
    #    project_menu = ProjectMenu()

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)

    reliability_branch = var_tree.get_branch(core, project, theme_name)
    reliability_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_reliability.pkl")
    )
    reliability_branch.read_auto(core, project)

    can_execute = theme_menu.is_executable(core, project, theme_name)

    if not can_execute:
        inputs = reliability_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core, project, theme_name)

    assert interface.data.electrical_network is not None


def test_reliability_interface_entry(
    theme_menu, core, tidal_project, var_tree, mocker, tmpdir
):
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))

    mocker.patch(
        "dtocean_core.interfaces.reliability.UserDataPath",
        return_value=mock_dir,
        autospec=True,
    )

    theme_name = "Reliability"
    #    project_menu = ProjectMenu()

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)

    reliability_branch = var_tree.get_branch(core, project, theme_name)
    reliability_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_reliability.pkl")
    )
    reliability_branch.read_auto(core, project)

    can_execute = theme_menu.is_executable(core, project, theme_name)

    if not can_execute:
        inputs = reliability_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core, project, theme_name)

    interface.connect(debug_entry=True, export_data=True)

    debugdir = config_tmpdir.join("..", "debug")

    assert len(debugdir.listdir()) == 1
