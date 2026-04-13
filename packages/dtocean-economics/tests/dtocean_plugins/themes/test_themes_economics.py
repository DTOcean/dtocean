import os
from copy import deepcopy
from pprint import pprint
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree, _get_connector

from dtocean_plugins.themes.economics import _get_outputs

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

    capex_bom_elec = capex_bom[
        capex_bom["phase"] == "Electrical Sub-Systems"
    ].drop("phase", axis=1)
    assert len(capex_bom_elec) == 1
    capex_bom_elec_i = capex_bom_elec.iloc[0]

    assert capex_bom_elec_i["quantity"] == 5
    assert capex_bom_elec_i["unitary_cost"] == 100
    assert capex_bom_elec_i["project_year"] == 0

    expected_bom_mandf_dict = {
        "quantity": [5, 10],
        "unitary_cost": [100, 50],
        "project_year": [0, 0],
    }
    expected_bom_mandf = pd.DataFrame(expected_bom_mandf_dict).astype(
        pd.Int64Dtype()
    )

    capex_bom_mandf = (
        capex_bom[capex_bom["phase"] == "Mooring and Foundations"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(expected_bom_mandf, capex_bom_mandf)

    expected_bom_inst_dict = {
        "quantity": [1, 1],
        "unitary_cost": [1000, 2000],
        "project_year": [1, 2],
    }
    expected_bom_inst = pd.DataFrame(expected_bom_inst_dict).astype(
        pd.Int64Dtype()
    )

    capex_bom_inst = (
        capex_bom[capex_bom["phase"] == "Installation"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(expected_bom_inst, capex_bom_inst)

    capex_bom_cond = (
        capex_bom[capex_bom["phase"] == "Condition Monitoring"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    )
    assert len(capex_bom_cond) == 1
    capex_bom_cond_i = capex_bom_cond.iloc[0]

    assert capex_bom_cond_i["quantity"] == 1
    assert capex_bom_cond_i["unitary_cost"] == 100
    assert capex_bom_cond_i["project_year"] == 0

    capex_bom_ext = (
        capex_bom[capex_bom["phase"] == "Externalities"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    )
    assert len(capex_bom_ext) == 1
    capex_bom_ext_i = capex_bom_ext.iloc[0]

    assert capex_bom_ext_i["quantity"] == 1
    assert capex_bom_ext_i["unitary_cost"] == 1e6
    assert capex_bom_ext_i["project_year"] == 0

    expected_opex_bom_dict = {
        "project_year": [3, 4],
        "Cost": [1000.0, 2000.0],
    }
    expected_opex_bom = pd.DataFrame(expected_opex_bom_dict)
    pd.testing.assert_frame_equal(expected_opex_bom, opex_bom)

    expected_energy_record_dict = {
        "project_year": [3, 4],
        "Energy": [10000.0, 20000.0],
    }
    expected_energy_record = pd.DataFrame(expected_energy_record_dict)
    expected_energy_record["Energy"] = (
        expected_energy_record["Energy"] * 0.99 * 1e6
    )
    pd.testing.assert_frame_equal(expected_energy_record, energy_record)


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
    mocker,
    inputs_economics_estimate,
    theme_menu,
    core,
    tidal_project,
    var_tree,
):
    _get_outputs: MagicMock = mocker.patch(
        "dtocean_plugins.themes.economics._get_outputs",
        autospec=True,
    )

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

    interface.connect()

    _get_outputs.assert_called_once()
    _get_outputs_args = _get_outputs.call_args[0]

    capex_bom = _get_outputs_args[0]
    opex_bom = _get_outputs_args[1]
    energy_record = _get_outputs_args[2]

    capex_bom_dev = (
        capex_bom[capex_bom["phase"] == "Devices"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    ).iloc[0]

    assert capex_bom_dev["quantity"] == 5
    assert capex_bom_dev["unitary_cost"] == 1e6
    assert capex_bom_dev["project_year"] == 0

    capex_bom_elec = (
        capex_bom[capex_bom["phase"] == "Electrical Sub-Systems"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    ).iloc[0]

    assert capex_bom_elec["quantity"] == 1
    assert capex_bom_elec["unitary_cost"] == 1e5
    assert capex_bom_elec["project_year"] == 0

    capex_bom_moor = (
        capex_bom[capex_bom["phase"] == "Mooring and Foundations"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    ).iloc[0]

    assert capex_bom_moor["quantity"] == 1
    assert capex_bom_moor["unitary_cost"] == 1e5
    assert capex_bom_moor["project_year"] == 0

    capex_bom_inst = (
        capex_bom[capex_bom["phase"] == "Installation"]
        .drop("phase", axis=1)
        .reset_index(drop=True)
    ).iloc[0]

    assert capex_bom_inst["quantity"] == 1
    assert capex_bom_inst["unitary_cost"] == 1e5
    assert capex_bom_inst["project_year"] == 0

    assert opex_bom["costs"].iloc[0] == 0
    opex_bom_one = opex_bom[opex_bom["project_year"] != 0]

    opex_bom_costs = set(opex_bom_one["costs"])
    assert len(opex_bom_costs) == 1

    opex_bom_cost = opex_bom_costs.pop()
    assert opex_bom_cost == 10000.0 + 2 * 10000.0

    assert energy_record["energy"].iloc[0] == 0
    energy_record_one = energy_record[energy_record["project_year"] != 0]

    energy_record_energies = set(energy_record_one["energy"])
    assert len(energy_record_energies) == 1

    energy_record_energy = energy_record_energies.pop()
    assert energy_record_energy == 10000 * 1e6 * 0.95


# These factors become 1 when used with a 1 / 5 discount rate in the respective
# year
YEAR_ONE = 6 / 5
YEAR_TWO = 36 / 25
YEAR_THREE = 216 / 125


@pytest.fixture()
def bom():
    bom_dict = {
        "phase": [
            "Devices",
            "Electrical Sub-Systems",
            "Installation",
            "Installation",
            "Condition Monitoring",
            "Condition Monitoring",
            "Externalities",
        ],
        "unitary_cost": [
            1e6,
            5e6,
            YEAR_ONE * 1e5,
            YEAR_TWO * 1e5,
            YEAR_ONE * 1e4,
            YEAR_TWO * 1e4,
            1e6,
        ],
        "project_year": [0, 0, 1, 2, 1, 2, 0],
        "quantity": [10, 1, 1, 1, 1, 1, 1],
    }

    bom_df = pd.DataFrame(bom_dict)

    return bom_df


@pytest.fixture()
def opex_costs_0_externalities():
    opex_externalities = 216
    opex_dict = {
        "project_year": [0, 1, 2, 3],
        "cost 0": [
            1 + opex_externalities,
            YEAR_ONE + opex_externalities,
            YEAR_TWO + opex_externalities,
            YEAR_THREE + opex_externalities,
        ],
    }

    opex_df = pd.DataFrame(opex_dict)

    return opex_df


@pytest.fixture()
def energy_record_0():
    energy_dict = {
        "project_year": [0, 1, 2, 3],
        "energy 0": [1e6, YEAR_ONE * 1e6, YEAR_TWO * 1e6, YEAR_THREE * 1e6],
    }

    energy_df = pd.DataFrame(energy_dict)

    return energy_df


def test_get_outputs_0_externalities(
    bom,
    opex_costs_0_externalities,
    energy_record_0,
):
    discount_rate = 1 / 5
    outputs = _get_outputs(
        bom,
        opex_costs_0_externalities,
        energy_record_0,
        discount_rate,
        1e6,
        216,
    )

    none_outputs = [
        "confidence_density",
        "discounted_energy_lower",
        "discounted_energy_mode",
        "discounted_energy_upper",
        "discounted_lifetime_cost_mode",
        "discounted_opex_lower",
        "discounted_opex_mode",
        "discounted_opex_upper",
        "lcoe_lower",
        "lcoe_mode",
        "lcoe_pdf",
        "lcoe_upper",
        "lifetime_cost_mode",
        "lifetime_opex_lower",
        "lifetime_opex_mode",
        "lifetime_opex_upper",
    ]
    for key in none_outputs:
        if outputs[key] is not None:
            print(key)
        assert outputs[key] is None

    non_none_outputs = set(outputs.keys()) - set(none_outputs)
    for key in non_none_outputs:
        if outputs[key] is None:
            print(key)
        assert outputs[key] is not None

    capex_breakdown = outputs["capex_breakdown"]

    assert capex_breakdown["Devices"] == 10 * 1e6
    assert capex_breakdown["Electrical Sub-Systems"] == 5e6
    assert capex_breakdown["Externalities"] == 1e6
    assert np.isclose(
        capex_breakdown["Installation"],
        (YEAR_ONE + YEAR_TWO) * 1e5,
    )
    assert np.isclose(
        capex_breakdown["Condition Monitoring"],
        (YEAR_ONE + YEAR_TWO) * 1e4,
    )

    capex_total = outputs["capex_total"]
    capex_no_externalities = outputs["capex_no_externalities"]

    expected_capex_no_externalities = (
        10 * 1e6
        + 5e6
        + (YEAR_ONE + YEAR_TWO) * 1e5
        + (YEAR_ONE + YEAR_TWO) * 1e4
    )
    assert capex_no_externalities == expected_capex_no_externalities
    assert capex_total == expected_capex_no_externalities + 1e6

    discounted_capex = outputs["discounted_capex"]
    discounted_capex_expected = 10 * 1e6 + 5e6 + 1e6 + 2 * (1e5 + 1e4)
    assert discounted_capex == discounted_capex_expected

    economics_metrics = outputs["economics_metrics"]
    economics_metric = economics_metrics.iloc[0]

    opex_metric = economics_metric["OPEX"]
    opex_metric_expected = 1 + YEAR_ONE + YEAR_TWO + YEAR_THREE + 4 * 216
    assert np.isclose(opex_metric, opex_metric_expected)

    discounted_opex_metric = economics_metric["Discounted OPEX"]
    discounted_opex_metric_expected = 4 + 216 + 180 + 150 + 125
    assert discounted_opex_metric == discounted_opex_metric_expected

    energy_metric = economics_metric["Energy"]
    energy_metric_expected = 1 + YEAR_ONE + YEAR_TWO + YEAR_THREE
    assert np.isclose(energy_metric, energy_metric_expected)

    discounted_energy_metric = economics_metric["Discounted Energy"]
    discounted_energy_metric_expected = 4
    assert discounted_energy_metric == discounted_energy_metric_expected

    lcoe_capex_metric = economics_metric["LCOE CAPEX"]
    lcoe_capex_metric_expected = (
        discounted_capex / discounted_energy_metric / 1000
    )
    assert np.isclose(lcoe_capex_metric, lcoe_capex_metric_expected)

    lcoe_opex_metric = economics_metric["LCOE OPEX"]
    lcoe_opex_metric_expected = (
        discounted_opex_metric / discounted_energy_metric / 1000
    )
    assert np.isclose(lcoe_opex_metric, lcoe_opex_metric_expected)

    lcoe_metric = economics_metric["LCOE"]
    lcoe_metric_expected = (
        lcoe_capex_metric_expected + lcoe_opex_metric_expected
    )
    assert np.isclose(lcoe_metric, lcoe_metric_expected)

    assert outputs["lifetime_cost_mean"] == capex_total + opex_metric_expected
    assert (
        outputs["discounted_lifetime_cost_mean"]
        == discounted_capex_expected + discounted_opex_metric_expected
    )

    assert np.isclose(outputs["lifetime_opex_mean"], opex_metric_expected)
    assert outputs["discounted_opex_mean"] == discounted_opex_metric_expected

    assert (
        outputs["discounted_energy_mean"] == discounted_energy_metric_expected
    )
    assert outputs["lcoe_mean"] == lcoe_metric_expected

    cost_breakdown = outputs["cost_breakdown"]
    assert cost_breakdown["Discounted CAPEX"] == discounted_capex_expected
    assert cost_breakdown["Discounted OPEX"] == discounted_opex_metric_expected

    opex_breakdown = outputs["opex_breakdown"]
    assert opex_breakdown["Externalities"] == 216 + 180 + 150 + 125
    assert opex_breakdown["Maintenance"] == 4

    capex_lcoe_breakdown = outputs["capex_lcoe_breakdown"]

    # Factor of 1e-1 to get to cent/kWh from Euro/MWh
    assert (
        capex_lcoe_breakdown["Devices"]
        == 10 * 1e6 / discounted_energy_metric_expected * 1e-1
    )
    assert (
        capex_lcoe_breakdown["Electrical Sub-Systems"]
        == 5e6 / discounted_energy_metric_expected * 1e-1
    )
    assert (
        capex_lcoe_breakdown["Externalities"]
        == 1e6 / discounted_energy_metric_expected * 1e-1
    )
    assert (
        capex_lcoe_breakdown["Installation"]
        == 2e5 / discounted_energy_metric_expected * 1e-1
    )
    assert (
        capex_lcoe_breakdown["Condition Monitoring"]
        == 2e4 / discounted_energy_metric_expected * 1e-1
    )

    opex_lcoe_breakdown = outputs["opex_lcoe_breakdown"]

    # TODO: fix this rounding error
    expected = round(
        (216 + 180 + 150 + 125) / discounted_energy_metric_expected * 1e-1,
        2,
    )
    assert abs(opex_lcoe_breakdown["Externalities"] - expected) < 0.02

    expected = round(
        4 / discounted_energy_metric_expected * 1e-1,
        2,
    )
    assert opex_lcoe_breakdown["Maintenance"] == expected

    lcoe_breakdown = outputs["lcoe_breakdown"]
    assert np.isclose(lcoe_breakdown["CAPEX"], lcoe_capex_metric * 100)

    # TODO: fix this rounding error
    expected = round(lcoe_opex_metric * 100, 2)
    assert abs(lcoe_breakdown["OPEX"] - expected) < 0.02
