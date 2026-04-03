import os
from copy import deepcopy
from pprint import pprint
from unittest.mock import MagicMock

import pandas as pd
import pytest
from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree, _get_connector

DIR_PATH = os.path.dirname(__file__)


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


def test_economics_inputs(theme_menu, core, tidal_project, var_tree):
    theme_name = "Economics"
    data_menu = DataMenu()

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)

    economics_branch = var_tree.get_branch(core, project, theme_name)
    economics_input_status = economics_branch.get_input_status(core, project)

    assert "project.estimate_energy_record" in economics_input_status


def test_get_economics_interface(
    inputs_economics,
    theme_menu,
    core,
    tidal_project,
    var_tree,
):
    theme_name = "Economics"

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)

    economics_branch = var_tree.get_branch(core, project, theme_name)
    economics_branch.read_test_data(core, project, inputs_economics)
    economics_branch.read_auto(core, project)

    can_execute = theme_menu.is_executable(core, project, theme_name)

    if not can_execute:
        inputs = economics_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core, project, theme_name)

    assert interface.data.electrical_bom is not None


def test_economics_interface_entry(
    mocker,
    inputs_economics,
    theme_menu,
    core,
    tidal_project,
    var_tree,
):
    _get_outputs: MagicMock = mocker.patch(
        "dtocean_plugins.themes.economics._get_outputs",
        autospec=True,
        return_value={},
    )

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)

    theme_name = "Economics"
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)

    economics_branch = var_tree.get_branch(core, project, theme_name)
    economics_branch.read_test_data(core, project, inputs_economics)
    economics_branch.read_auto(core, project)

    can_execute = theme_menu.is_executable(core, project, theme_name)

    if not can_execute:
        inputs = economics_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core, project, theme_name)

    interface.connect()

    _get_outputs.assert_called_once()
    _get_outputs_args = _get_outputs.call_args[0]

    capex_bom = _get_outputs_args[0]
    opex_bom = _get_outputs_args[1]
    energy_record = _get_outputs_args[2]
    print(capex_bom)

    capex_bom_elec = capex_bom[
        capex_bom["phase"] == "Electrical Sub-Systems"
    ].drop("phase", axis=1)
    assert len(capex_bom_elec) == 1
    assert capex_bom_elec.iloc[0]["quantity"] == 5

    expected_bom_mandf_dict = {
        "quantity": [5, 10],
        "unitary_cost": [100, 50],
        "project_year": [0, 0],
    }
    expected_bom_mandf = pd.DataFrame(expected_bom_mandf_dict).astype(
        pd.Int64Dtype
    )

    capex_bom_mandf = (
        capex_bom[capex_bom["phase"] == "Mooring and Foundations"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(expected_bom_mandf, capex_bom_mandf)

    print(opex_bom)
    print(energy_record)

    assert False


def test_get_economics_interface_estimate(
    inputs_economics_estimate,
    theme_menu,
    core,
    tidal_project,
    var_tree,
):
    theme_name = "Economics"

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)

    economics_branch = var_tree.get_branch(core, project, theme_name)
    economics_branch.read_test_data(core, project, inputs_economics_estimate)
    economics_branch.read_auto(core, project)

    can_execute = theme_menu.is_executable(core, project, theme_name)

    if not can_execute:
        inputs = economics_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core, project, theme_name)

    assert interface.data.electrical_estimate is not None


def test_economics_interface_entry_estimate(
    inputs_economics_estimate,
    theme_menu,
    core,
    tidal_project,
    var_tree,
):
    theme_name = "Economics"

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project)
    theme_menu.activate(core, project, theme_name)
    project_menu.initiate_dataflow(core, project)

    economics_branch = var_tree.get_branch(core, project, theme_name)
    economics_branch.read_test_data(core, project, inputs_economics_estimate)
    economics_branch.read_auto(core, project)

    can_execute = theme_menu.is_executable(core, project, theme_name)

    if not can_execute:
        inputs = economics_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute

    connector = _get_connector(project, "themes")
    interface = connector.get_interface(core, project, theme_name)

    interface.connect(debug_entry=True)

    assert True
