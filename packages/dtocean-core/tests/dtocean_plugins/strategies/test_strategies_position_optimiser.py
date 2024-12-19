# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access,bad-whitespace,no-member

import pytest

pytest.importorskip("dtocean-hydro")

import contextlib
import logging
import os

import numpy as np
from shapely.geometry import Polygon
from yaml import dump

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

import dtocean_core.utils.optimiser as opt
from dtocean_core.core import Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Strata
from dtocean_plugins.strategies.position_optimiser import (
    PositionCounter,
    PositionEvaluator,
    PositionOptimiser,
    PositionParams,
    _clean_numbered_files_above,
    _dump_results_control,
    _get_param_control,
    _get_range_fixed,
    _get_range_multiplier,
    dump_config,
    load_config,
)
from dtocean_plugins.strategies.position_optimiser.positioner import (
    ParaPositioner,
)


@contextlib.contextmanager
def caplog_for_logger(caplog, logger_name, level=logging.DEBUG):
    caplog.handler.records = []
    logger = logging.getLogger(logger_name)
    logger.addHandler(caplog.handler)
    logger.setLevel(level)
    yield
    logger.removeHandler(caplog.handler)


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


def test_PositionCounter_set_params():
    counter = PositionCounter()
    evaluation = counter.next_evaluation()
    mock = ["mock"] * 12
    counter.set_params(evaluation, *mock)

    search_dict = counter.search_dict
    params = search_dict[evaluation]

    assert isinstance(params, PositionParams)
    assert params.grid_orientation == "mock"


def test_PositionCounter_get_cost():
    counter = PositionCounter()
    evaluation = counter.next_evaluation()
    mock = ["mock"] * 12
    counter.set_params(evaluation, *mock)

    assert not counter.get_cost(mock)


def test_PositionEvaluator_init_bad_objective(
    mocker, lease_polygon, layer_depths
):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    positioner = ParaPositioner(lease_polygon, layer_depths)

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.get_positioner",
        return_value=positioner,
        autospec=True,
    )

    mock_core = mocker.MagicMock()

    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = ["mock"]

    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation

    with pytest.raises(RuntimeError) as excinfo:
        PositionEvaluator(mock_core, mock_project, "mock", "mock", "not_mock")

    assert "is not an output of the base" in str(excinfo)


@pytest.fixture
def evaluator(mocker, lease_polygon, layer_depths):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    positioner = ParaPositioner(lease_polygon, layer_depths)

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.get_positioner",
        return_value=positioner,
        autospec=True,
    )

    mock_core = mocker.MagicMock()

    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = ["mock"]

    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation

    test = PositionEvaluator(mock_core, mock_project, "mock", "mock", "mock")

    return test


def test_PositionEvaluator_init(evaluator):
    assert evaluator._objective_var == "mock"
    assert evaluator._violation_log_path == os.path.join(
        "mock", "violations.txt"
    )


def test_PositionEvaluator_init_counter(evaluator):
    counter = evaluator._init_counter()
    assert isinstance(counter, PositionCounter)


def test_PositionEvaluator_get_popen_args(evaluator):
    worker_project_path = "mock"
    n_evals = 1.0
    args = ["mock"] * 6 + [1.0]

    popen_args = evaluator._get_popen_args(worker_project_path, n_evals, *args)

    assert popen_args == ["_dtocean-optim-pos"] + ["mock"] * 7 + [
        "--dev_per_string",
        "1",
        "--n_evals",
        "1",
    ]


def test_PositionEvaluator_get_worker_results_success(mocker, evaluator):
    mock_stg_dict = {"status": "Success", "results": {"mock": 1}}

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.open",
        mocker.mock_open(read_data=dump(mock_stg_dict, Dumper=Dumper)),
    )

    results = evaluator._get_worker_results(1)

    assert results == {
        "status": "Success",
        "worker_results_path": os.path.join("mock", "mock_1.yaml"),
        "cost": 1,
        "results": {"mock": 1},
    }


def test_PositionEvaluator_get_worker_results_exception(mocker, evaluator):
    mock_stg_dict = {"status": "Exception", "error": "mock"}

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.open",
        mocker.mock_open(read_data=dump(mock_stg_dict, Dumper=Dumper)),
    )

    results = evaluator._get_worker_results(1)

    assert results == {
        "status": "Exception",
        "worker_results_path": os.path.join("mock", "mock_1.yaml"),
        "cost": np.nan,
        "error": "mock",
    }


def test_PositionEvaluator_get_worker_results_bad_flag(mocker, evaluator):
    mock_stg_dict = {"status": "mock"}

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.open",
        mocker.mock_open(read_data=dump(mock_stg_dict, Dumper=Dumper)),
    )

    with pytest.raises(RuntimeError) as excinfo:
        evaluator._get_worker_results(1)

    assert "Unrecognised flag" in str(excinfo)


def test_PositionEvaluator_get_worker_results_not_number(
    caplog, mocker, evaluator
):
    mock_stg_dict = {"status": "Success", "results": {"mock": "mock"}}

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.open",
        mocker.mock_open(read_data=dump(mock_stg_dict, Dumper=Dumper)),
    )

    with caplog_for_logger(caplog, "dtocean_core"):
        evaluator._get_worker_results(1)

    assert "cost is not a number" in caplog.text


def test_PositionEvaluator_set_counter_params_no_results(evaluator):
    evaluation = 1
    worker_project_path = "mock"
    results = None
    flag = "mock"
    n_evals = 1
    args = ["mock"] * 7

    evaluator._set_counter_params(
        evaluation, worker_project_path, results, flag, n_evals, *args
    )

    search_dict = evaluator._counter.search_dict
    params = search_dict[evaluation]

    assert params.n_evals == n_evals
    assert params.yaml_file_path is None
    assert np.isnan(params.cost)


def test_PositionEvaluator_set_counter_params_results(evaluator):
    evaluation = 1
    worker_project_path = "mock"
    cost = 1
    results = {"worker_results_path": "mock", "cost": cost}
    flag = "mock"
    n_evals = 1
    args = ["mock"] * 7

    evaluator._set_counter_params(
        evaluation, worker_project_path, results, flag, n_evals, *args
    )

    search_dict = evaluator._counter.search_dict
    params = search_dict[evaluation]

    assert params.n_evals == n_evals
    assert params.yaml_file_path == "mock"
    assert params.cost == cost


def test_PositionEvaluator_pre_constraints_hook(mocker, tmpdir, evaluator):
    evaluator._violation_log_path = os.path.join(str(tmpdir), "violations.txt")

    mocker.patch.object(evaluator._tool_man, "execute_tool", autospec=True)

    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5

    args = (
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
    )

    assert not evaluator.pre_constraints_hook(*args)
    assert not tmpdir.listdir()


@pytest.mark.parametrize(
    "n_nodes, t1,  expected",
    [
        (2000, 0.5, "number of nodes not found"),
        (5, 1.5, "lies outside of valid domain"),
    ],
)
def test_PositionEvaluator_pre_constraints_hook_position_true(
    mocker, tmpdir, evaluator, n_nodes, t1, expected
):
    evaluator._violation_log_path = os.path.join(str(tmpdir), "violations.txt")

    mocker.patch.object(evaluator._tool_man, "execute_tool", autospec=True)

    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    t2 = 0.5
    dev_per_string = 5

    args = (
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
    )

    assert evaluator.pre_constraints_hook(*args)
    assert len(tmpdir.listdir()) == 1

    with open(evaluator._violation_log_path, "r") as f:
        line = f.readline()

    assert expected in line


def test_PositionEvaluator_pre_constraints_hook_position_error(
    mocker, tmpdir, evaluator
):
    evaluator._violation_log_path = os.path.join(str(tmpdir), "violations.txt")

    expected = "mock_positioner"
    mocker.patch.object(
        evaluator,
        "_positioner",
        side_effect=RuntimeError(expected),
        autospec=True,
    )

    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5

    args = (
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
    )

    with pytest.raises(RuntimeError) as excinfo:
        evaluator.pre_constraints_hook(*args)

    assert not tmpdir.listdir()
    assert expected in str(excinfo)


def test_PositionEvaluator_pre_constraints_hook_spacing_true(
    mocker, tmpdir, evaluator
):
    evaluator._violation_log_path = os.path.join(str(tmpdir), "violations.txt")

    expected = "Violation of the minimum distance constraint"
    mocker.patch.object(
        evaluator._tool_man,
        "execute_tool",
        side_effect=RuntimeError(expected),
        autospec=True,
    )

    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5

    args = (
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
    )

    assert evaluator.pre_constraints_hook(*args)
    assert len(tmpdir.listdir()) == 1

    with open(evaluator._violation_log_path, "r") as f:
        line = f.readline()

    assert expected in line


def test_PositionEvaluator_pre_constraints_hook_spacing_error(
    mocker, tmpdir, evaluator
):
    evaluator._violation_log_path = os.path.join(str(tmpdir), "violations.txt")

    expected = "mock_spacing"
    mocker.patch.object(
        evaluator._tool_man,
        "execute_tool",
        side_effect=RuntimeError(expected),
        autospec=True,
    )

    grid_orientation = 0
    delta_row = 10
    delta_col = 20
    n_nodes = 5
    t1 = 0.5
    t2 = 0.5
    dev_per_string = 5

    args = (
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
    )

    with pytest.raises(RuntimeError) as excinfo:
        evaluator.pre_constraints_hook(*args)

    assert not tmpdir.listdir()
    assert expected in str(excinfo)


def test_PositionEvaluator_cleanup_hook(tmpdir, evaluator):
    p = tmpdir.join("mock.txt")
    p.write("content")

    assert len(tmpdir.listdir()) == 1

    evaluator._cleanup_hook(str(p), None, None)

    assert not tmpdir.listdir()


def test_get_range_fixed():
    a = 1
    b = 2
    assert _get_range_fixed(a, b) == (a, b)


@pytest.fixture
def mock_core_get_data_value(mocker):
    mock_core = Core()

    mocker.patch.object(
        mock_core, "get_data_value", return_value=2, autospec=True
    )

    return mock_core


def test_get_range_multiplier(mock_core_get_data_value):
    (a, b) = _get_range_multiplier(mock_core_get_data_value, None, None, 1, 2)

    assert a == 2
    assert b == 4


def test_get_param_control(mock_core_get_data_value):
    param_fixed = {"fixed": 0}
    param_range_fixed = {"range": {"type": "fixed", "min": 1, "max": 2}}
    param_range_fixed_x0 = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "x0": 1.5,
    }
    param_range_fixed_int = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "integer": True,
    }
    param_range_multiplier = {
        "range": {
            "type": "multiplier",
            "variable": "mock",
            "min_multiplier": 1,
            "max_multiplier": 2,
        }
    }
    parameters = {
        "grid_orientation": param_fixed,
        "delta_row": param_range_fixed,
        "delta_col": param_range_fixed_x0,
        "n_nodes": param_range_fixed_int,
        "t1": param_range_multiplier,
        "t2": param_range_multiplier,
    }

    config = {"parameters": parameters}

    result = _get_param_control(mock_core_get_data_value, None, config)

    assert result == {
        "ranges": [(1, 2), (1, 2), (1, 2), (2, 4), (2, 4)],
        "x0s": [None, 1.5, None, None, None],
        "fixed_params": {0: np.pi / 2, 6: None},
        "x_ops": [None, None, np.floor, None, None],
        "integer_variables": [2],
    }


def test_get_param_control_more():
    param_range_fixed = {"range": {"type": "fixed", "min": 1, "max": 2}}
    param_range_fixed_x0 = {
        "range": {"type": "fixed", "min": -90, "max": 90},
        "x0": 0,
    }
    param_range_fixed_int = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "integer": True,
    }
    parameters = {
        "grid_orientation": param_range_fixed_x0,
        "delta_row": param_range_fixed,
        "delta_col": param_range_fixed,
        "n_nodes": param_range_fixed_int,
        "t1": param_range_fixed,
        "t2": param_range_fixed,
        "dev_per_string": param_range_fixed_int,
    }

    config = {"parameters": parameters}

    result = _get_param_control(None, None, config)

    assert result == {
        "ranges": [[0, np.pi]] + [(1, 2)] * 6,
        "x0s": [np.pi / 2, None, None, None, None, None, None],
        "fixed_params": None,
        "x_ops": [None, None, None, np.floor, None, None, np.floor],
        "integer_variables": [3, 6],
    }


def test_get_param_control_bad_parameter():
    parameters = {"mock": None}
    config = {"parameters": parameters}

    with pytest.raises(KeyError) as excinfo:
        _get_param_control(None, None, config)

    assert "must be included in the 'parameters' section" in str(excinfo)


def test_dump_results_control(tmpdir):
    params = ["mock", "mock"]
    _dump_results_control(params, str(tmpdir))

    expected_fname = str(tmpdir.join("results_control.txt"))

    assert len(tmpdir.listdir()) == 1
    assert expected_fname in tmpdir.listdir()

    with open(expected_fname, "r") as f:
        lines = f.readlines()

    assert len(lines) == 2
    assert all(["mock" for line in lines])


@pytest.mark.parametrize(
    "mock_var,    minevals", [("mock", 1), ("mock_mode", 4), ("mock_mean", 1)]
)
def test_PositionOptimiser_start(
    mocker, tmpdir, lease_polygon, layer_depths, mock_var, minevals
):
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.ModuleMenu." "get_active",
        return_value=["Operations and Maintenance"],
        autospec=True,
    )

    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    positioner = ParaPositioner(lease_polygon, layer_depths)

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.get_positioner",
        return_value=positioner,
        autospec=True,
    )

    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = [mock_var]

    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation

    mock_core = Core()

    mocker.patch.object(
        mock_core, "get_data_value", return_value=2, autospec=True
    )

    mocker.patch.object(
        mock_core, "load_project", return_value=mock_project, autospec=True
    )

    mocker.patch.object(mock_core, "dump_project", autospec=True)

    worker_dir = str(tmpdir)
    base_penalty = 1
    num_threads = 2
    maximise = False

    config = {
        "worker_dir": worker_dir,
        "base_penalty": base_penalty,
        "n_threads": num_threads,
        "results_params": mock_var,
        "objective": mock_var,
        "clean_existing_dir": False,
        "maximise": maximise,
        "max_simulations": 1,
        "popsize": 8,
        "timeout": 1,
        "tolfun": 1,
        "max_evals": 0,
        "max_resample_factor": "auto2",
        "root_project_path": "mock",
    }

    param_fixed = {"fixed": 0}
    param_range_fixed = {"range": {"type": "fixed", "min": 1, "max": 2}}
    param_range_fixed_x0 = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "x0": 1.5,
    }
    param_range_multiplier = {
        "range": {
            "type": "multiplier",
            "variable": "mock",
            "min_multiplier": 1,
            "max_multiplier": 2,
        }
    }
    parameters = {
        "grid_orientation": param_fixed,
        "delta_row": param_range_fixed,
        "delta_col": param_range_fixed_x0,
        "n_nodes": param_range_fixed,
        "t1": param_range_multiplier,
        "t2": param_range_multiplier,
    }

    config["parameters"] = parameters

    test = PositionOptimiser(core=mock_core)
    test.start(config)

    assert not test.stop
    assert test._worker_directory == worker_dir
    assert test._dump_config

    assert isinstance(test._cma_main, opt.Main)
    assert isinstance(test._cma_main.evaluator, PositionEvaluator)
    assert [scaler.x0 for scaler in test._cma_main._scaled_vars] == [9] * 5
    assert test._cma_main._base_penalty == base_penalty
    assert test._cma_main._num_threads == num_threads
    assert test._cma_main._maximise == maximise
    assert test._cma_main._n_record_resample == 2

    assert test._cma_main.nh is not None
    assert test._cma_main.nh.minevals == minevals
    assert test._cma_main.nh.maxevals == minevals

    assert len(tmpdir.listdir()) == 5
    assert not mock_core.dump_project.called


def test_PositionOptimiser_start_more(
    mocker, tmpdir, lease_polygon, layer_depths
):
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.ModuleMenu." "get_active",
        return_value=[],
        autospec=True,
    )

    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    positioner = ParaPositioner(lease_polygon, layer_depths)

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.get_positioner",
        return_value=positioner,
        autospec=True,
    )

    mock_var = "mock"

    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = [mock_var]

    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation

    mock_core = Core()

    mocker.patch.object(
        mock_core, "get_data_value", return_value=2, autospec=True
    )

    mocker.patch.object(mock_core, "dump_project", autospec=True)

    mocker.patch("dtocean_core.strategies.position_optimiser.Core", mock_core)

    worker_dir = str(tmpdir)
    base_penalty = 1
    num_threads = 2
    maximise = False
    max_resample_factor = 20
    popsize = 8

    config = {
        "worker_dir": worker_dir,
        "base_penalty": base_penalty,
        "n_threads": num_threads,
        "results_params": mock_var,
        "objective": mock_var,
        "clean_existing_dir": False,
        "maximise": maximise,
        "max_simulations": 1,
        "popsize": popsize,
        "timeout": 1,
        "tolfun": 1,
        "min_evals": 1,
        "max_evals": 2,
        "max_resample_factor": max_resample_factor,
    }

    param_fixed = {"fixed": 0}
    param_range_fixed = {"range": {"type": "fixed", "min": 1, "max": 2}}
    param_range_fixed_x0 = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "x0": 1.5,
    }
    param_range_multiplier = {
        "range": {
            "type": "multiplier",
            "variable": "mock",
            "min_multiplier": 1,
            "max_multiplier": 2,
        }
    }
    parameters = {
        "grid_orientation": param_fixed,
        "delta_row": param_range_fixed,
        "delta_col": param_range_fixed_x0,
        "n_nodes": param_range_fixed,
        "t1": param_range_multiplier,
        "t2": param_range_multiplier,
    }

    config["parameters"] = parameters

    test = PositionOptimiser(core=mock_core)
    test.start(config, mock_project)

    assert config["root_project_path"] == str(tmpdir.join("worker.prj"))

    assert not test.stop
    assert test._worker_directory == worker_dir
    assert not test._dump_config

    assert isinstance(test._cma_main, opt.Main)
    assert isinstance(test._cma_main.evaluator, PositionEvaluator)
    assert [scaler.x0 for scaler in test._cma_main._scaled_vars] == [9] * 5
    assert test._cma_main._base_penalty == base_penalty
    assert test._cma_main._num_threads == num_threads
    assert test._cma_main._maximise == maximise
    assert (
        test._cma_main._max_resample_loops == 2 * max_resample_factor * popsize
    )
    assert test._cma_main.nh is None

    assert len(tmpdir.listdir()) == 4
    assert mock_core.dump_project.called


def test_dump_load_dump_load_config(tmpdir):
    config_path = str(tmpdir.join("config.yaml"))
    dump_config(config_path)
    config = load_config(config_path)

    expected_keys = [
        "worker_dir",
        "base_penalty",
        "n_threads",
        "results_params",
        "objective",
        "clean_existing_dir",
        "maximise",
        "max_simulations",
        "popsize",
        "timeout",
        "tolfun",
        "min_evals",
        "max_evals",
        "max_resample_factor",
        "parameters",
    ]

    assert set(expected_keys) <= set(config)

    expected_params = [
        "grid_orientation",
        "delta_row",
        "delta_col",
        "n_nodes",
        "t1",
        "t2",
    ]

    assert set(expected_params) <= set(config["parameters"])

    dump_config(config_path, config, use_template=False)
    new_config = load_config(config_path)

    assert new_config == config


def test_PositionOptimiser_is_restart(mocker, tmpdir):
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.opt.load_outputs",
        autospec=True,
    )

    mock_core = mocker.MagicMock()
    config_fname = "mock.yaml"

    config_path = str(tmpdir.join(config_fname))
    dump_config(config_path)

    test = PositionOptimiser(mock_core, config_fname)

    assert test.is_restart(str(tmpdir))


def test_dump_config_extra_keys(tmpdir):
    config_path = str(tmpdir.join("config.yaml"))
    dump_config(config_path)
    config = load_config(config_path)

    config["mock"] = "mock"

    dump_config(config_path, config)
    new_config = load_config(config_path)

    assert "mock" not in new_config


def test_PositionOptimiser_is_restart_no_state(caplog, mocker, tmpdir):
    err_msg = "bang!"
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.opt.load_outputs",
        side_effect=IOError(err_msg),
        autospec=True,
    )

    mock_core = mocker.MagicMock()
    config_fname = "mock.yaml"

    config_path = str(tmpdir.join(config_fname))
    dump_config(config_path)

    test = PositionOptimiser(mock_core, config_fname)

    with caplog_for_logger(caplog, "dtocean_core"):
        result = test.is_restart(str(tmpdir))

    assert not result
    assert err_msg in caplog.text


def test_PositionOptimiser_is_restart_missing_keys(caplog, mocker, tmpdir):
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.opt.load_outputs",
        autospec=True,
    )

    mock_core = mocker.MagicMock()
    config_fname = "mock.yaml"

    config_path = str(tmpdir.join(config_fname))

    mock_config = {
        "root_project_path": None,
        "base_penalty": None,
        "n_threads": None,
    }

    dump_config(config_path, mock_config, use_template=False)
    test = PositionOptimiser(mock_core, config_fname)

    with caplog_for_logger(caplog, "dtocean_core"):
        result = test.is_restart(str(tmpdir))

    assert not result
    assert "'objective' are missing" in caplog.text


def test_clean_numbered_files_above(tmpdir):
    for i in range(10):
        fname = "mock{}.txt".format(i)
        p = tmpdir.join(fname)
        p.write("content")

    assert len(tmpdir.listdir()) == 10

    _clean_numbered_files_above(str(tmpdir), "mock*.txt", 4)

    assert len(tmpdir.listdir()) == 5


def test_PositionOptimiser_restart(mocker, tmpdir, lease_polygon, layer_depths):
    for i in range(10):
        fname = "mock_{}.yaml".format(i)
        p = tmpdir.join(fname)
        p.write("content")

        fname = "mock_{}.prj".format(i)
        p = tmpdir.join(fname)
        p.write("content")

    assert len(tmpdir.listdir()) == 20

    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    positioner = ParaPositioner(lease_polygon, layer_depths)

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.get_positioner",
        return_value=positioner,
        autospec=True,
    )

    counter_dict = {0: "mock", 1: "mock", 2: "mock", 3: "mock", 4: "mock"}

    mock_es = mocker.MagicMock()

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.opt.load_outputs",
        return_value=[mock_es, counter_dict, None],
        autospec=True,
    )

    mock_var = "mock"

    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = [mock_var]

    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation

    mock_core = Core()

    mocker.patch.object(
        mock_core, "get_data_value", return_value=2, autospec=True
    )

    mocker.patch.object(
        mock_core, "load_project", return_value=mock_project, autospec=True
    )

    base_penalty = 1
    num_threads = 2
    maximise = True
    timeout = 3

    config = {
        "root_project_path": "mock.prj",
        "base_penalty": base_penalty,
        "n_threads": num_threads,
        "objective": mock_var,
        "maximise": maximise,
        "timeout": timeout,
        "max_resample_factor": "auto1",
    }

    param_fixed = {"fixed": 0}
    param_range_fixed = {"range": {"type": "fixed", "min": 1, "max": 2}}
    param_range_fixed_x0 = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "x0": 1.5,
    }
    param_range_multiplier = {
        "range": {
            "type": "multiplier",
            "variable": "mock",
            "min_multiplier": 1,
            "max_multiplier": 2,
        }
    }
    parameters = {
        "grid_orientation": param_fixed,
        "delta_row": param_range_fixed,
        "delta_col": param_range_fixed_x0,
        "n_nodes": param_range_fixed,
        "t1": param_range_multiplier,
        "t2": param_range_multiplier,
    }

    config["parameters"] = parameters

    load_config = mocker.patch(
        "dtocean_core.strategies.position_optimiser." "load_config",
        return_value=config,
        autospec=True,
    )

    worker_dir = str(tmpdir)
    test = PositionOptimiser(core=mock_core)
    test.restart(worker_dir)

    assert load_config.call_args.args[0] == str(tmpdir.join(test._config_fname))
    assert len(tmpdir.listdir()) == 10

    assert not test.stop
    assert test._worker_directory == worker_dir
    assert test._dump_config

    assert isinstance(test._cma_main, opt.Main)
    assert isinstance(test._cma_main.evaluator, PositionEvaluator)
    assert test._cma_main.es == mock_es
    assert [scaler.x0 for scaler in test._cma_main._scaled_vars] == [9] * 5
    assert test._cma_main._base_penalty == base_penalty
    assert test._cma_main._num_threads == num_threads
    assert test._cma_main._maximise == maximise
    assert test._cma_main._n_record_resample == 1
    assert test._cma_main.nh is None


def test_PositionOptimiser_restart_more(
    mocker, tmpdir, lease_polygon, layer_depths
):
    for i in range(10):
        fname = "mock_{}.yaml".format(i)
        p = tmpdir.join(fname)
        p.write("content")

        fname = "mock_{}.prj".format(i)
        p = tmpdir.join(fname)
        p.write("content")

    assert len(tmpdir.listdir()) == 20

    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    positioner = ParaPositioner(lease_polygon, layer_depths)

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.get_positioner",
        return_value=positioner,
        autospec=True,
    )

    popsize = 8
    mock_es = mocker.MagicMock()
    mock_es.popsize = popsize

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.opt.load_outputs",
        return_value=[mock_es, {}, None],
        autospec=True,
    )

    mock_var = "mock"

    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = [mock_var]

    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation

    mock_core = Core()

    mocker.patch.object(
        mock_core, "get_data_value", return_value=2, autospec=True
    )

    mocker.patch.object(
        mock_core, "load_project", return_value=mock_project, autospec=True
    )

    base_penalty = 1
    num_threads = 2
    maximise = True
    timeout = 3
    max_resample_factor = 20

    config = {
        "root_project_path": "mock.prj",
        "base_penalty": base_penalty,
        "n_threads": num_threads,
        "objective": mock_var,
        "maximise": maximise,
        "timeout": timeout,
        "max_resample_factor": max_resample_factor,
    }

    param_fixed = {"fixed": 0}
    param_range_fixed = {"range": {"type": "fixed", "min": 1, "max": 2}}
    param_range_fixed_x0 = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "x0": 1.5,
    }
    param_range_multiplier = {
        "range": {
            "type": "multiplier",
            "variable": "mock",
            "min_multiplier": 1,
            "max_multiplier": 2,
        }
    }
    parameters = {
        "grid_orientation": param_fixed,
        "delta_row": param_range_fixed,
        "delta_col": param_range_fixed_x0,
        "n_nodes": param_range_fixed,
        "t1": param_range_multiplier,
        "t2": param_range_multiplier,
    }

    config["parameters"] = parameters

    load_config = mocker.patch(
        "dtocean_core.strategies.position_optimiser." "load_config",
        return_value=config,
        autospec=True,
    )

    worker_dir = str(tmpdir)
    test = PositionOptimiser(core=mock_core)
    test.restart(worker_dir)

    assert load_config.call_args.args[0] == str(tmpdir.join(test._config_fname))
    assert not tmpdir.listdir()

    assert not test.stop
    assert test._worker_directory == worker_dir
    assert not test._dump_config

    assert isinstance(test._cma_main, opt.Main)
    assert isinstance(test._cma_main.evaluator, PositionEvaluator)
    assert test._cma_main.es == mock_es
    assert [scaler.x0 for scaler in test._cma_main._scaled_vars] == [9] * 5
    assert test._cma_main._base_penalty == base_penalty
    assert test._cma_main._num_threads == num_threads
    assert test._cma_main._maximise == maximise
    assert (
        test._cma_main._max_resample_loops == 2 * max_resample_factor * popsize
    )
    assert test._cma_main.nh is None


def test_PositionOptimiser_restart_not_possible(caplog, mocker):
    err_msg = "bang!"
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.opt.load_outputs",
        side_effect=IOError(err_msg),
        autospec=True,
    )

    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    with caplog_for_logger(caplog, "dtocean_core"):
        test.restart("mock")

    assert test._cma_main is None
    assert "Restarting position optimisation not possible" in caplog.text


def test_PositionOptimiser_next_not_configured(mocker):
    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    with pytest.raises(RuntimeError) as excinfo:
        test.next()

    assert "Optimiser is not configured" in str(excinfo)


def test_PositionOptimiser_next_stop(caplog, mocker):
    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    mock_cma_main = mocker.MagicMock()
    mock_cma_main.stop = True
    test._cma_main = mock_cma_main

    with caplog_for_logger(caplog, "dtocean_core"):
        test.next()

    assert test.stop
    assert "Position optimisation complete" in caplog.text


def test_PositionOptimiser_next_dump(
    mocker, tmpdir, lease_polygon, layer_depths
):
    mocker.patch(
        "dtocean_core.strategies.position_optimiser.ModuleMenu." "get_active",
        return_value=["Operations and Maintenance"],
        autospec=True,
    )

    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    positioner = ParaPositioner(lease_polygon, layer_depths)

    mocker.patch(
        "dtocean_core.strategies.position_optimiser.get_positioner",
        return_value=positioner,
        autospec=True,
    )

    mock_var = "mock"

    mock_simulation = mocker.MagicMock()
    mock_simulation.get_output_ids.return_value = [mock_var]

    mock_project = mocker.MagicMock()
    mock_project.get_simulation.return_value = mock_simulation

    mock_core = Core()

    mocker.patch.object(
        mock_core, "get_data_value", return_value=2, autospec=True
    )

    mocker.patch.object(
        mock_core, "load_project", return_value=mock_project, autospec=True
    )

    mocker.patch.object(mock_core, "dump_project", autospec=True)

    worker_dir = str(tmpdir)
    base_penalty = 1
    num_threads = 2
    maximise = False

    config = {
        "worker_dir": worker_dir,
        "base_penalty": base_penalty,
        "n_threads": num_threads,
        "results_params": mock_var,
        "objective": mock_var,
        "clean_existing_dir": False,
        "maximise": maximise,
        "max_simulations": 1,
        "popsize": 8,
        "timeout": 1,
        "tolfun": 1,
        "max_evals": 0,
        "max_resample_factor": "auto2",
        "root_project_path": "mock",
    }

    param_fixed = {"fixed": 0}
    param_range_fixed = {"range": {"type": "fixed", "min": 1, "max": 2}}
    param_range_fixed_x0 = {
        "range": {"type": "fixed", "min": 1, "max": 2},
        "x0": 1.5,
    }
    param_range_multiplier = {
        "range": {
            "type": "multiplier",
            "variable": "mock",
            "min_multiplier": 1,
            "max_multiplier": 2,
        }
    }
    parameters = {
        "grid_orientation": param_fixed,
        "delta_row": param_range_fixed,
        "delta_col": param_range_fixed_x0,
        "n_nodes": param_range_fixed,
        "t1": param_range_multiplier,
        "t2": param_range_multiplier,
    }

    config["parameters"] = parameters

    test = PositionOptimiser(core=mock_core)
    test.start(config)

    p_cma = tmpdir.join("saved-cma-object.pkl")
    cma_before_time = p_cma.mtime()

    p_config = tmpdir.join("config.yaml")
    config_before_time = p_config.mtime()

    mock_next = mocker.patch.object(test._cma_main, "next", autospec=True)

    mocker.patch.object(
        test._cma_main, "get_max_resample_factor", return_value=1, autospec=True
    )

    test.next()

    cma_after_time = p_cma.mtime()
    config_after_time = p_config.mtime()
    new_config = load_config(str(p_config))

    assert mock_next.called
    assert cma_after_time > cma_before_time
    assert config_after_time > config_before_time
    assert not test._dump_config
    assert "max_resample_factor" in new_config


def test_PositionOptimiser_next_no_dump(mocker):
    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    mock_cma_main = mocker.MagicMock()
    mock_cma_main.stop = False
    test._cma_main = mock_cma_main

    mock_dump_outputs = mocker.patch(
        "dtocean_core.strategies." "position_optimiser.opt.dump_outputs",
        autospec=True,
    )

    test.next()

    assert mock_cma_main.next.called
    assert mock_dump_outputs.called


def test_PositionOptimiser_get_es_none(mocker):
    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    assert test.get_es() is None


def test_PositionOptimiser_get_es(mocker):
    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    mock_cma_main = mocker.MagicMock()
    test._cma_main = mock_cma_main

    assert isinstance(test.get_es(), mocker.MagicMock)


def test_PositionOptimiser_get_nh_none(mocker):
    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    assert test.get_nh() is None


def test_PositionOptimiser_get_nh(mocker):
    mock_core = mocker.MagicMock()
    test = PositionOptimiser(core=mock_core)

    mock_cma_main = mocker.MagicMock()
    test._cma_main = mock_cma_main

    assert isinstance(test.get_nh(), mocker.MagicMock)

    assert isinstance(test.get_nh(), mocker.MagicMock)
    assert isinstance(test.get_nh(), mocker.MagicMock)
    assert isinstance(test.get_nh(), mocker.MagicMock)
