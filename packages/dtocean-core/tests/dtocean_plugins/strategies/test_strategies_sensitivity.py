# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access

import pytest

from dtocean_core.core import OrderedSim, Project
from dtocean_plugins.strategies.sensitivity import UnitSensitivity  # pylint: disable=no-name-in-module


@pytest.fixture()
def unit():
    return UnitSensitivity()


def test_unit_get_name():
    assert UnitSensitivity.get_name() == "Unit Sensitivity"


def test_unit_configure(unit):
    unit.configure("a", "b", [1, 2, 3], skip_errors=False)

    assert unit._config == {
        "module_name": "a",
        "var_name": "b",
        "var_values": [1, 2, 3],
        "skip_errors": False,
    }


def test_unit_get_variables(unit):
    unit.configure("a", "b", [1, 2, 3])
    assert unit.get_variables() == ["b"]


def test_unit_execute(mocker, unit):
    modules = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        unit._module_menu, "get_available", return_value=modules, autospec=True
    )

    mocker.patch.object(
        unit._module_menu, "get_active", return_value=modules, autospec=True
    )

    mock_meta = mocker.Mock()
    mock_meta.title = "Mock"
    mock_meta.units = "m"

    mock_var = mocker.MagicMock()
    mock_var.get_metadata.return_value = mock_meta

    mock_branch = mocker.MagicMock()
    mock_branch.get_input_status.return_value = {"device.power_rating": ""}
    mock_branch.get_input_variable.return_value = mock_var

    mocker.patch.object(
        unit._tree, "get_branch", return_value=mock_branch, autospec=True
    )

    mocker.patch.object(unit, "_safe_exe", return_value=True, autospec=True)

    core = mocker.MagicMock()
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))

    unit.configure("Hydrodynamics", "device.power_rating", [1, 1, 2])
    unit.execute(core, project)

    assert unit._sim_record == [
        "Mock = 1 (m)",
        "Mock = 1 (m) [repeat 1]",
        "Mock = 2 (m)",
    ]


def test_unit_execute_no_config(unit):
    with pytest.raises(ValueError) as excinfo:
        unit.execute(None, None)

    assert "configuration values are None" in str(excinfo)


def test_unit_execute_no_module(mocker, unit):
    modules = [
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        unit._module_menu, "get_available", return_value=modules, autospec=True
    )

    core = mocker.MagicMock()
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))

    unit.configure("Hydrodynamics", "device.power_rating", [1, 2, 3])

    with pytest.raises(ValueError) as excinfo:
        unit.execute(core, project)

    assert "does not exist" in str(excinfo)


def test_unit_execute_not_activated(mocker, unit):
    available_modules = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        unit._module_menu,
        "get_available",
        return_value=available_modules,
        autospec=True,
    )

    active_modules = [
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        unit._module_menu,
        "get_active",
        return_value=active_modules,
        autospec=True,
    )

    core = mocker.MagicMock()
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))

    unit.configure("Hydrodynamics", "device.power_rating", [1, 2, 3])

    with pytest.raises(ValueError) as excinfo:
        unit.execute(core, project)

    assert "has not been activated" in str(excinfo)


def test_unit_execute_not_input(mocker, unit):
    modules = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        unit._module_menu, "get_available", return_value=modules, autospec=True
    )

    mocker.patch.object(
        unit._module_menu, "get_active", return_value=modules, autospec=True
    )

    mock_branch = mocker.MagicMock()
    mock_branch.get_input_status.return_value = {"device.power_factor": ""}

    mocker.patch.object(
        unit._tree, "get_branch", return_value=mock_branch, autospec=True
    )

    core = mocker.MagicMock()
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))

    unit.configure("Hydrodynamics", "device.power_rating", [1, 2, 3])

    with pytest.raises(ValueError) as excinfo:
        unit.execute(core, project)

    assert "not an input to module" in str(excinfo)


def test_unit_execute_no_simulation(mocker, unit):
    modules = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        unit._module_menu, "get_available", return_value=modules, autospec=True
    )

    mocker.patch.object(
        unit._module_menu, "get_active", return_value=modules, autospec=True
    )

    mock_branch = mocker.MagicMock()
    mock_branch.get_input_status.return_value = {"device.power_rating": ""}

    mocker.patch.object(
        unit._tree, "get_branch", return_value=mock_branch, autospec=True
    )

    core = mocker.MagicMock()
    project = Project("mock")
    unit.configure("Hydrodynamics", "device.power_rating", [1, 2, 3])

    with pytest.raises(RuntimeError) as excinfo:
        unit.execute(core, project)

    assert "Project has not been activated." in str(excinfo)


@pytest.mark.parametrize("skip_errors", [True, False])
def test_unit_safe_exe(mocker, unit, skip_errors):
    mocker.patch.object(unit._basic, "execute", autospec=True)

    unit.configure(None, None, None, skip_errors)
    success_flag = unit._safe_exe(None, None, None)

    assert success_flag


def test_unit_safe_exe_raise(mocker, unit):
    mocker.patch.object(
        unit._basic, "execute", side_effect=SystemExit("foo"), autospec=True
    )

    unit.configure(None, None, None)

    with pytest.raises(SystemExit) as excinfo:
        unit._safe_exe(None, None, None)

    assert "foo" in str(excinfo)


def test_unit_safe_exe_pass(mocker, unit):
    mocker.patch.object(
        unit._basic, "execute", side_effect=ValueError("foo"), autospec=True
    )

    unit.configure(None, None, None)
    success_flag = unit._safe_exe(None, None, None)

    assert not success_flag

    assert not success_flag
