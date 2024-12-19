# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access

# Check for module
import pytest

pytest.importorskip("dtocean_hydro")

import sys

import numpy as np
import yaml
from shapely.geometry import Polygon

from dtocean_core.core import Core, OrderedSim, Project
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Strata
from dtocean_core.menu import ModuleMenu
from dtocean_core.pipeline import Branch
from dtocean_plugins.strategies.basic import BasicStrategy
from dtocean_plugins.strategies.position_optimiser.iterator import (  # pylint: disable=no-name-in-module
    _get_basic_strategy,
    _get_branch,
    get_positioner,
    interface,
    iterate,
    main,
    prepare,
    write_result_file,
)
from dtocean_plugins.strategies.position_optimiser.positioner import (
    ParaPositioner,
)


@pytest.fixture
def lease_polygon():
    return Polygon([(100, 50), (900, 50), (900, 250), (100, 250)])


@pytest.fixture
def layer_depths():
    x = np.linspace(0.0, 1000.0, 101)
    y = np.linspace(0.0, 300.0, 31)
    nx = len(x)
    ny = len(y)

    X, _ = np.meshgrid(x, y)
    Z = -X * 0.1 - 1
    depths = Z.T[:, :, np.newaxis]
    sediments = np.full((nx, ny, 1), "rock")

    raw = {
        "values": {"depth": depths, "sediment": sediments},
        "coords": [x, y, ["layer 1"]],
    }

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "layer", "depth", "sediment"],
        }
    )

    test = Strata()
    a = test.get_data(raw, meta)

    return test.get_value(a)


def test_get_branch():
    core = Core()
    project = Project("mock")
    new_sim = OrderedSim("Default")
    new_sim.set_inspection_level(core._markers["initial"])
    project.add_simulation(new_sim)
    core.register_level(project, core._markers["initial"], None)

    core.new_hub(project)  # project hub
    core.new_hub(project)  # modules hub

    branch_name = "Hydrodynamics"

    menu = ModuleMenu()
    menu.activate(core, project, branch_name)

    test = _get_branch(core, project, branch_name)

    assert isinstance(test, Branch)


def test_prepare(mocker, lease_polygon, layer_depths):
    modules = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    module_menu = mocker.MagicMock()
    module_menu.get_active.return_value = modules

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator." "ModuleMenu",
        return_value=module_menu,
        autospec=True,
    )

    mock_var = mocker.MagicMock()
    mock_branch = mocker.MagicMock()
    mock_branch.get_input_variable.return_value = mock_var

    _get_branch = mocker.patch(
        "dtocean_core.strategies.position_optimiser." "iterator._get_branch",
        return_value=mock_branch,
        autospec=True,
    )

    core = mocker.MagicMock()
    core.get_data_value.return_value = 1

    project = Project("mock")

    positioner = ParaPositioner(lease_polygon, layer_depths)

    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    t1 = 0.5
    t2 = 0.5
    n_nodes = 9
    dev_per_string = 5
    n_evals = 2

    prepare(
        core,
        project,
        positioner,
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
        n_evals,
    )

    expecteds = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Operations and Maintenance",
    ]

    for call, expected in zip(_get_branch.call_args_list, expecteds):
        assert call.args[2] == expected


def test_get_basic_strategy():
    basic_strategy = _get_basic_strategy()
    assert isinstance(basic_strategy, BasicStrategy)


def test_iterate(mocker):
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator." "prepare",
        autospec=True,
    )

    basic_strategy = mocker.MagicMock()

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator."
        "_get_basic_strategy",
        return_value=basic_strategy,
        autospec=True,
    )

    iterate(None, None, None, None, None, None, None, None, None)

    assert basic_strategy.execute.called


def test_get_positioner(mocker, lease_polygon, layer_depths):
    def get_data_value(dummy, var):  # pylint: disable=unused-argument
        if var == "site.lease_boundary":
            return lease_polygon

        if var == "bathymetry.layers":
            return layer_depths

        if var == "device.installation_depth_max":
            return None

        if var == "device.installation_depth_min":
            return None

        if var == "farm.nogo_areas":
            return (
                Polygon([(800, 0), (1000, 0), (1000, 150), (800, 150)]),
                Polygon([(800, 150), (1000, 150), (1000, 300), (800, 300)]),
            )

        if var == "options.boundary_padding":
            return 10

        if var == "device.turbine_interdistance":
            return 20

        return None

    core = mocker.MagicMock()
    core.has_data.return_value = True
    core.get_data_value = get_data_value

    positioner = get_positioner(core, None)

    assert isinstance(positioner, ParaPositioner)
    assert positioner._valid_poly.bounds == (120.0, 70.0, 780.0, 230.0)


def test_write_result_file_success(mocker, tmpdir):
    def has_data(dummy, var):  # pylint: disable=unused-argument
        if var == "mock1":
            return True

        return False

    def get_data_value(dummy, var):  # pylint: disable=unused-argument
        if var == "mock1":
            return 1

        return None

    results_control = "mock1\n" "mock2\n"

    p = tmpdir.join("results_control.txt")
    p.write(results_control)

    core = mocker.MagicMock()
    core.has_data = has_data
    core.get_data_value = get_data_value

    p = tmpdir.join("mock")
    prj_base_path = str(p)

    params_dict = {"mock0": 0}

    write_result_file(core, None, prj_base_path, params_dict, "Success", None)

    assert len(tmpdir.listdir()) == 2

    yaml_path = prj_base_path + ".yaml"

    with open(yaml_path, "r") as stream:
        data_loaded = yaml.safe_load(stream)

    assert data_loaded == {
        "status": "Success",
        "params": {"mock0": 0},
        "results": {"mock2": None, "mock1": 1},
    }


def test_write_result_file_exception(mocker, tmpdir):
    core = mocker.MagicMock()

    p = tmpdir.join("mock")
    prj_base_path = str(p)

    params_dict = {"mock0": 0}

    write_result_file(
        core,
        None,
        prj_base_path,
        params_dict,
        "Exception",
        RuntimeError("mock"),
    )

    assert len(tmpdir.listdir()) == 1

    yaml_path = prj_base_path + ".yaml"

    with open(yaml_path, "r") as stream:
        data_loaded = yaml.safe_load(stream)

    assert data_loaded == {
        "status": "Exception",
        "params": {"mock0": 0},
        "error": "mock",
    }


def test_write_result_file_bad_flag():
    with pytest.raises(RuntimeError) as excinfo:
        write_result_file(None, None, "mock", None, "mock", None)

    assert "Unrecognised flag" in str(excinfo)


def test_main(mocker):
    project = mocker.MagicMock()

    core = mocker.MagicMock()
    core.load_project.return_value = project

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator." "get_positioner",
        autospec=True,
    )

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator." "iterate",
        autospec=True,
    )

    write_result_file = mocker.patch(
        "dtocean_core.strategies."
        "position_optimiser.iterator."
        "write_result_file"
    )

    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = t2 = 0.5
    dev_per_string = 5
    n_evals = 2

    main(
        core,
        "mock.prj",
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
        n_evals,
        save_project=True,
    )

    write_result_file_args = write_result_file.call_args.args

    assert core.dump_project.called
    assert write_result_file_args[2] == "mock"
    assert write_result_file_args[3] == {
        "theta": float(grid_orientation),
        "dr": float(delta_row),
        "dc": float(delta_col),
        "n_nodes": n_nodes,
        "t1": t1,
        "t2": t2,
        "dev_per_string": dev_per_string,
        "n_evals": n_evals,
    }
    assert write_result_file_args[4] == "Success"


def test_main_exception(mocker):
    project = mocker.MagicMock()

    core = mocker.MagicMock()
    core.load_project.return_value = project

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator." "get_positioner",
        autospec=True,
    )

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator." "iterate",
        side_effect=RuntimeError("mock"),
        autospec=True,
    )

    write_result_file = mocker.patch(
        "dtocean_core.strategies."
        "position_optimiser.iterator."
        "write_result_file",
        autospec=True,
    )

    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = t2 = 0.5
    dev_per_string = 5
    n_evals = 2

    main(
        core,
        "mock.prj",
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
        n_evals,
        save_project=True,
    )

    write_result_file_args = write_result_file.call_args.args

    assert core.dump_project.called
    assert write_result_file_args[2] == "mock"
    assert write_result_file_args[3] == {
        "theta": float(grid_orientation),
        "dr": float(delta_row),
        "dc": float(delta_col),
        "n_nodes": n_nodes,
        "t1": t1,
        "t2": t2,
        "dev_per_string": dev_per_string,
        "n_evals": n_evals,
    }
    assert write_result_file_args[4] == "Exception"
    assert str(write_result_file_args[5]) == "mock"


def test_interface(mocker):
    prj_file_path = "mock.prj"
    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = t2 = 0.5

    arg_str = ("_dtocean-optim-pos {} {} {} {} {} {} " "{}").format(
        prj_file_path, grid_orientation, delta_row, delta_col, n_nodes, t1, t2
    )
    testargs = arg_str.split()

    mocker.patch.object(sys, "argv", testargs)

    test = mocker.patch(
        "dtocean_core.strategies.position_optimiser.iterator." "main",
        autospec=True,
    )

    interface()

    assert test.call_args.args[1:8] == (
        prj_file_path,
        str(grid_orientation),
        str(delta_row),
        str(delta_col),
        str(n_nodes),
        str(t1),
        str(t2),
    )
