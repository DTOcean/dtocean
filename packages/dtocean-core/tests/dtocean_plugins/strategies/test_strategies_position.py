# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access,bad-whitespace,no-member
import contextlib
import logging
import os
import pickle
import time

import numpy as np
import pytest
from yaml import dump

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from dtocean_core.core import Core, OrderedSim, Project
from dtocean_core.menu import ModuleMenu
from dtocean_plugins.strategies.position import (
    AdvancedPosition,
    PositionOptimiser,
    _get_results_table,
    _post_process,
    _read_yaml,
    _run_favorite,
)

dtocean_hydro = pytest.importorskip("dtocean_hydro")


@contextlib.contextmanager
def caplog_for_logger(caplog, logger_name, level=logging.DEBUG):
    caplog.handler.records = []
    logger = logging.getLogger(logger_name)
    logger.addHandler(caplog.handler)
    logger.setLevel(level)
    yield
    logger.removeHandler(caplog.handler)


@pytest.fixture()
def advanced():
    return AdvancedPosition()


def test_advanced_get_name():
    assert AdvancedPosition.get_name() == "Advanced Positioning"


def test_advanced_get_config_fname():
    assert AdvancedPosition.get_config_fname() == "config.yaml"


def test_advanced_dump_config_hook(advanced):
    mock = {"clean_existing_dir": True}
    test = advanced.dump_config_hook(mock)

    assert test["clean_existing_dir"] is None


def test_advanced_get_variables(advanced):
    assert advanced.get_variables() == [
        "options.user_array_layout",
        "project.rated_power",
    ]


@pytest.mark.parametrize(
    "param,            exp_status_str, exp_status_code",
    [(None, "incomplete", 0), ("results_params", "complete", 1)],
)
def test_advanced_get_config_status(param, exp_status_str, exp_status_code):
    keys = [
        "root_project_path",
        "worker_dir",
        "base_penalty",
        "n_threads",
        "parameters",
        "objective",
    ]

    if param is not None:
        keys.append(param)

    config = {key: 1 for key in keys}

    status_str, status_code = AdvancedPosition.get_config_status(config)

    assert exp_status_str in status_str
    assert status_code == exp_status_code


def test_advanced_configure(mocker, advanced):
    mocker.patch.object(
        advanced, "get_config_status", return_value=[None, 1], autospec=True
    )

    test = {"mock": "mock"}
    advanced.configure(**test)

    assert advanced._config == test


def test_advanced_configure_missing_keys(mocker, advanced):
    mocker.patch.object(
        advanced, "get_config_status", return_value=[None, 0], autospec=True
    )

    test = {"mock": "mock"}

    with pytest.raises(ValueError) as excinfo:
        advanced.configure(**test)

    assert "Required keys are missing" in str(excinfo)


def test_advanced_get_worker_directory_status_missing(tmpdir):
    config = {"worker_dir": os.path.join(str(tmpdir), "mock")}
    (status_str, status_code) = AdvancedPosition.get_worker_directory_status(
        config
    )

    assert status_code == 1
    assert "does not yet exist" in status_str


def test_advanced_get_worker_directory_status_empty(tmpdir):
    p = tmpdir.mkdir("mock")
    config = {"worker_dir": str(p)}
    (status_str, status_code) = AdvancedPosition.get_worker_directory_status(
        config
    )

    assert status_code == 1
    assert "empty" in status_str


@pytest.mark.parametrize(
    "clean_existing_dir, expected", [(False, 0), (True, 1)]
)
def test_advanced_get_worker_directory_status_contains_files(
    tmpdir, clean_existing_dir, expected
):
    p = tmpdir.mkdir("mock")
    f = p.join("hello.txt")
    f.write("content")

    config = {"worker_dir": str(p), "clean_existing_dir": clean_existing_dir}
    (status_str, status_code) = AdvancedPosition.get_worker_directory_status(
        config
    )

    assert status_code == expected
    assert "contains files" in status_str


def test_advanced_get_optimiser_status_none(tmpdir):
    config = {"worker_dir": os.path.join(str(tmpdir), "mock")}
    (status_str, status_code) = AdvancedPosition.get_optimiser_status(
        None, config
    )

    assert status_code == 0
    assert status_str is None


def test_advanced_get_optimiser_status_complete(tmpdir):
    p = tmpdir.join("mock_results.pkl")
    p.write("content")

    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": os.path.join(str(tmpdir), "mock.prj"),
    }
    (status_str, status_code) = AdvancedPosition.get_optimiser_status(
        None, config
    )

    assert status_str is not None
    assert status_code == 1
    assert "complete" in status_str


def test_advanced_get_optimiser_status_incomplete(mocker, tmpdir):
    mock_opt = mocker.patch(
        "dtocean_plugins.strategies.position.PositionOptimiser", autospec=True
    )
    mock_opt.is_restart.return_value = True

    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": os.path.join(str(tmpdir), "mock.prj"),
    }
    (status_str, status_code) = AdvancedPosition.get_optimiser_status(
        None, config
    )

    assert status_str is not None
    assert status_code == 2
    assert "incomplete" in status_str


def test_advanced_get_project_status_not_activated():
    mock_core = None
    mock_project = Project("mock")
    mock_config = None

    (status_str, status_code) = AdvancedPosition.get_project_status(
        mock_core, mock_project, mock_config
    )

    assert status_code == 0
    assert "not been activated" in status_str


def test_advanced_get_project_status_not_contain_module(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.ModuleMenu.get_active",
        return_value=["mock"],
        autospec=True,
    )

    mock_core = None
    mock_sim = OrderedSim("mock")
    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)
    mock_config = None

    (status_str, status_code) = AdvancedPosition.get_project_status(
        mock_core, mock_project, mock_config
    )

    assert status_code == 0
    assert "not contain the" in status_str


def test_advanced_get_project_status_requires_simulation(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.ModuleMenu.get_active",
        return_value=["Hydrodynamics"],
        autospec=True,
    )

    mock_core = None
    mock_sim = OrderedSim("mock")
    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)
    mock_config = None

    (status_str, status_code) = AdvancedPosition.get_project_status(
        mock_core, mock_project, mock_config
    )

    assert status_code == 0
    assert "requires a simulation" in status_str


def test_advanced_get_project_status_no_objective_variable(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.ModuleMenu.get_active",
        return_value=["Hydrodynamics"],
        autospec=True,
    )

    mock_core = None
    mock_sim = OrderedSim("Default")
    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)
    mock_config = {}

    (status_str, status_code) = AdvancedPosition.get_project_status(
        mock_core, mock_project, mock_config
    )

    assert status_code == 0
    assert "No 'objective' variable" in status_str


def test_advanced_get_project_status_not_an_output(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.ModuleMenu.get_active",
        return_value=["Hydrodynamics"],
        autospec=True,
    )

    mock_core = None
    mock_sim = OrderedSim("Default")
    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)
    mock_config = {"objective": "mock"}

    (status_str, status_code) = AdvancedPosition.get_project_status(
        mock_core, mock_project, mock_config
    )

    assert status_code == 0
    assert "not an output" in status_str


def test_advanced_get_project_status_ready(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.ModuleMenu.get_active",
        return_value=["Hydrodynamics"],
        autospec=True,
    )

    mock_core = None

    mock_sim = OrderedSim("Default")
    mocker.patch.object(
        mock_sim, "get_output_ids", return_value=["mock"], autospec=True
    )

    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)
    mock_config = {"objective": "mock"}

    (status_str, status_code) = AdvancedPosition.get_project_status(
        mock_core, mock_project, mock_config
    )

    assert status_code == 1
    assert "ready" in status_str


def test_advanced_prepare_project_error(mocker, advanced):
    mocker.patch.object(
        advanced, "get_project_status", return_value=["mock", 0], autospec=True
    )

    mock_core = None
    mock_project = None

    with pytest.raises(RuntimeError) as excinfo:
        advanced._prepare_project(mock_core, mock_project)

    assert "mock" in str(excinfo)


def test_advanced_prepare_project_active_simulation(caplog, mocker, advanced):
    mocker.patch("dtocean_plugins.strategies.position.Tree", autospec=True)

    mocker.patch.object(
        advanced, "get_project_status", return_value=["mock", 1], autospec=True
    )

    mock_core = None

    mock_sim = OrderedSim("Default")
    mock_sim_extra = OrderedSim("Mock")

    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)
    mock_project.add_simulation(mock_sim_extra, set_active=True)

    with caplog_for_logger(caplog, "dtocean_plugins"):
        advanced._prepare_project(mock_core, mock_project)

    assert "Setting active simulation" in caplog.text


def test_advanced_prepare_project_reset_level(caplog, mocker, advanced):
    mocker.patch.object(
        advanced,
        "get_project_status",
        return_value=["mock", 1],
        autospec=True,
    )

    mock_core = Core()
    mock_sim = OrderedSim("Default")
    mock_sim.set_inspection_level(mock_core._markers["initial"])

    mock_project = Project("mock")
    mock_project.add_simulation(mock_sim)

    # Try to fake completing the Hydrodynamics interaface
    mock_core.register_level(mock_project, mock_core._markers["initial"], None)

    mock_core.new_hub(mock_project)  # project hub
    mock_core.new_hub(mock_project)  # modules hub
    mock_core.new_hub(mock_project)  # themes hub

    interface_name = "Hydrodynamics"
    level = interface_name.lower()

    menu = ModuleMenu()
    menu.activate(mock_core, mock_project, interface_name)

    start_level = "{} {}".format(level, mock_core._markers["register"])
    mock_core.register_level(mock_project, start_level, interface_name)

    mock_core.control.set_interface_completed(
        mock_sim, "modules", interface_name
    )

    # Set a level for the datastate including the output marker
    output_level = "{} {}".format(level, mock_core._markers["output"])
    output_level = output_level.lower()

    mock_core.register_level(mock_project, output_level, interface_name)

    # Set the execution level to the output level
    mock_sim.set_execution_level(output_level)

    module_menu = ModuleMenu()

    assert module_menu.get_current(mock_core, mock_project) is None

    with caplog_for_logger(caplog, "dtocean_core"):
        advanced._prepare_project(mock_core, mock_project)

    assert "Hydrodynamics" in module_menu.get_current(mock_core, mock_project)
    assert "Attempting to reset simulation level" in caplog.text


def test_advanced_pre_execute_restart(caplog, mocker, advanced):
    mock_restart = mocker.patch(
        "dtocean_plugins.strategies.position.PositionOptimiser.restart",
        autospec=True,
    )

    mocker.patch.object(
        advanced,
        "get_worker_directory_status",
        return_value=["mock", 0],
        autospec=True,
    )

    mocker.patch.object(
        advanced,
        "get_optimiser_status",
        return_value=["mock", 2],
        autospec=True,
    )

    advanced._config = {"clean_existing_dir": "mock", "worker_dir": "mock"}

    mock_core = None
    mock_project = None

    with caplog_for_logger(caplog, "dtocean_core"):
        advanced._pre_execute(mock_core, mock_project)

    assert "Attempting restart" in caplog.text
    assert advanced._config["clean_existing_dir"] is None
    assert mock_restart.called


def test_advanced_pre_execute_start(mocker, advanced):
    mock_start = mocker.patch(
        "dtocean_plugins.strategies.position.PositionOptimiser.start",
        autospec=True,
    )

    mocker.patch.object(
        advanced,
        "get_worker_directory_status",
        return_value=["mock", 0],
        autospec=True,
    )

    mocker.patch.object(
        advanced,
        "get_optimiser_status",
        return_value=["mock", 1],
        autospec=True,
    )

    mocker.patch.object(advanced, "_prepare_project", autospec=True)

    advanced._config = {"clean_existing_dir": "mock", "worker_dir": "mock"}

    mock_core = None
    mock_project = None

    advanced._pre_execute(mock_core, mock_project)

    assert advanced._config["clean_existing_dir"] is None
    assert mock_start.called


def test_run_favorite_success(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.logging.disable", autospec=True
    )

    mock_core = mocker.MagicMock()
    mock_opt = PositionOptimiser(mock_core)

    mock_nh = mocker.MagicMock()
    mock_nh.last_n_evals = 7

    mocker.patch.object(mock_opt, "get_es", autospec=True)

    mocker.patch.object(mock_opt, "get_nh", return_value=mock_nh, autospec=True)

    mock_cma_main = mocker.patch("dtocean_core.utils.optimiser.Main")
    mocker.patch.object(
        mock_cma_main,
        "get_descaled_solutions",
        return_value=[[np.float64(1), 2, 3, 4, 5, 6, None]],
    )

    mock_project = Project("mock")

    mock_evaluator = mocker.patch(
        "dtocean_plugins.strategies.position_optimiser.PositionEvaluator",
        autospec=True,
    )
    mock_evaluator._base_project = mock_project
    mock_evaluator._positioner = None
    mock_evaluator._root_project_base_name = "mock"

    mock_cma_main.evaluator = mock_evaluator
    mock_opt._cma_main = mock_cma_main
    mock_opt._worker_directory = "mock"

    mock_iterate = mocker.patch(
        "dtocean_plugins.strategies.position.iterate", autospec=True
    )

    mock_write_result_file = mocker.patch(
        "dtocean_plugins.strategies.position.write_result_file", autospec=True
    )

    _run_favorite(mock_opt, save_prj=True)

    assert mock_core.dump_project.called

    assert isinstance(mock_iterate.call_args.args[1], Project)
    assert mock_iterate.call_args.args[1] != mock_project
    assert mock_iterate.call_args.args[3:] == (1.0, 2, 3, 4, 5, 6, None, 7)

    assert mock_write_result_file.call_args.args[2] == "mock\\mock_xfavorite"
    assert mock_write_result_file.call_args.args[3] == {
        "theta": 1.0,
        "dr": 2,
        "dc": 3,
        "n_nodes": 4,
        "t1": 5,
        "t2": 6,
        "n_evals": 7,
    }
    assert mock_write_result_file.call_args.args[4] == "Success"


def test_run_favorite_exception(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.logging.disable", autospec=True
    )

    mock_core = mocker.MagicMock()
    mock_opt = PositionOptimiser(mock_core)

    mock_nh = mocker.MagicMock()
    mock_nh.last_n_evals = 7

    mocker.patch.object(mock_opt, "get_es", autospec=True)

    mocker.patch.object(mock_opt, "get_nh", return_value=mock_nh, autospec=True)

    mock_cma_main = mocker.patch("dtocean_core.utils.optimiser.Main")
    mocker.patch.object(
        mock_cma_main,
        "get_descaled_solutions",
        return_value=[[np.float64(1), 2, 3, 4, 5, 6, None]],
    )

    mock_project = Project("mock")

    mock_evaluator = mocker.patch(
        "dtocean_plugins.strategies.position_optimiser.PositionEvaluator",
        autospec=True,
    )
    mock_evaluator._base_project = mock_project
    mock_evaluator._positioner = None
    mock_evaluator._root_project_base_name = "mock"

    mock_cma_main.evaluator = mock_evaluator
    mock_opt._cma_main = mock_cma_main
    mock_opt._worker_directory = "mock"

    expected = KeyError("bang!")
    mocker.patch(
        "dtocean_plugins.strategies.position.iterate",
        side_effect=expected,
        autospec=True,
    )

    mock_write_result_file = mocker.patch(
        "dtocean_plugins.strategies.position.write_result_file", autospec=True
    )

    _run_favorite(mock_opt)

    assert mock_write_result_file.call_args.args[2] == "mock\\mock_xfavorite"
    assert mock_write_result_file.call_args.args[3] == {
        "theta": 1.0,
        "dr": 2,
        "dc": 3,
        "n_nodes": 4,
        "t1": 5,
        "t2": 6,
        "n_evals": 7,
    }
    assert mock_write_result_file.call_args.args[4] == "Exception"

    e = mock_write_result_file.call_args.args[5]
    assert type(e) is type(expected) and e.args == expected.args


def test_run_favorite_raise_exc(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.logging.disable", autospec=True
    )

    mock_core = mocker.MagicMock()
    mock_opt = PositionOptimiser(mock_core)

    mock_nh = mocker.MagicMock()
    mock_nh.last_n_evals = 7

    mocker.patch.object(mock_opt, "get_es", autospec=True)

    mocker.patch.object(mock_opt, "get_nh", return_value=mock_nh, autospec=True)

    mock_cma_main = mocker.patch("dtocean_core.utils.optimiser.Main")
    mocker.patch.object(
        mock_cma_main,
        "get_descaled_solutions",
        return_value=[[np.float64(1), 2, 3, 4, 5, 6, None]],
    )

    mock_project = Project("mock")

    mock_evaluator = mocker.patch(
        "dtocean_plugins.strategies.position_optimiser.PositionEvaluator",
        autospec=True,
    )
    mock_evaluator._base_project = mock_project
    mock_evaluator._positioner = None

    mock_cma_main.evaluator = mock_evaluator
    mock_opt._cma_main = mock_cma_main

    expected = KeyError("bang!")
    mocker.patch(
        "dtocean_plugins.strategies.position.iterate",
        side_effect=expected,
        autospec=True,
    )

    with pytest.raises(KeyError) as excinfo:
        _run_favorite(mock_opt, raise_exc=True)

    assert "bang!" in str(excinfo)


def test_read_yaml_exception(mocker):
    mock_stg_dict = {"status": "Exception"}

    mocker.patch(
        "dtocean_plugins.strategies.position.open",
        mocker.mock_open(read_data=dump(mock_stg_dict, Dumper=Dumper)),
    )

    assert not _read_yaml(None, None, None)


def test_read_yaml_disjoint(mocker):
    mock_stg_dict = {
        "status": "Mock",
        "results": {"mock": 1},
        "params": {"mock1": 2},
    }

    mocker.patch(
        "dtocean_plugins.strategies.position.open",
        mocker.mock_open(read_data=dump(mock_stg_dict, Dumper=Dumper)),
    )

    read_params = ["mock2"]
    extract_vars = ["mock3"]

    assert not _read_yaml(None, read_params, extract_vars)


def test_read_yaml(mocker):
    mock_stg_dict = {
        "status": "Mock",
        "results": {"mock": 1},
        "params": {"n_nodes": 2},
    }

    mocker.patch(
        "dtocean_plugins.strategies.position.open",
        mocker.mock_open(read_data=dump(mock_stg_dict, Dumper=Dumper)),
    )

    read_params = ["n_nodes", "mock2"]
    extract_vars = ["mock", "mock3"]

    result = _read_yaml(None, read_params, extract_vars)

    assert result == {"n_nodes": 2, "mock": 1}


def test_post_process(caplog, tmpdir):
    root_project_base_name = "mock"
    sim_num = range(5)
    mock_val = [10, 20, 30, 40, 50]
    n_nodes_val = [15, 25, 35, 45, 55]

    for i, mock, n_node in zip(sim_num, mock_val, n_nodes_val):
        fname = "{}_{}.yaml".format(root_project_base_name, i)
        fpath = os.path.join(str(tmpdir), fname)

        mock_stg_dict = {
            "status": "Mock",
            "results": {"mock": mock, "objective": mock},
            "params": {"n_nodes": n_node},
        }

        with open(fpath, "w") as f:
            dump(mock_stg_dict, f, Dumper=Dumper)

    # Add an non integer file name
    fname = "{}_mock.yaml".format(root_project_base_name)
    p = tmpdir.join(fname)
    p.write("content")

    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
        "parameters": {"n_nodes": None},
        "results_params": ["mock"],
        "objective": "objective",
    }

    with caplog_for_logger(caplog, "dtocean_plugins"):
        _post_process(config, 2)

    p = tmpdir.join("mock_results.pkl")

    assert p in tmpdir.listdir()

    with open(str(p), "rb") as f:
        data = pickle.load(f)

    assert data == {
        "sim_number": list(sim_num),
        "n_nodes": n_nodes_val,
        "mock": mock_val,
        "objective": mock_val,
    }

    print(caplog.text)

    test = caplog.text.split()
    assert test.count("Processed") >= 3


def test_post_process_no_files(caplog, tmpdir):
    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
    }

    with caplog_for_logger(caplog, "dtocean_core"):
        _post_process(config, 1)

    assert "No files" in caplog.text


def test_advanced_post_process(mocker, advanced):
    mocker.patch(
        "dtocean_plugins.strategies.position._run_favorite", autospec=True
    )
    mocker.patch(
        "dtocean_plugins.strategies.position._post_process", autospec=True
    )

    advanced._post_process(None)


class MockOpt(PositionOptimiser):
    def __init__(self, core=None, countdown=2, sleep=100):
        super(MockOpt, self).__init__(core)
        self._countdown = countdown
        self._sleep = sleep

    def next(self):
        time.sleep(1e-3 * self._sleep)
        if self._countdown == 0:
            self.stop = True
            return
        self._countdown -= 1

    def get_es(self):
        return True


def test_advanced_execute(mocker, advanced):
    mock_core = mocker.MagicMock()
    mock_opt = MockOpt(mock_core)

    mocker.patch.object(
        advanced, "_pre_execute", return_value=mock_opt, autospec=True
    )

    mocker.patch.object(advanced, "_post_process", autospec=True)

    assert advanced.execute(None, None)


def test_advanced_execute_theaded(mocker, advanced):
    mock_core = mocker.MagicMock()
    mock_opt = MockOpt(mock_core)

    mocker.patch.object(
        advanced, "_pre_execute", return_value=mock_opt, autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position._run_favorite", autospec=True
    )
    mocker.patch(
        "dtocean_plugins.strategies.position._post_process", autospec=True
    )

    thread = advanced.execute_threaded(None, None)

    while not thread.stopped:
        time.sleep(0.5)

    assert thread.get_es()


def test_advanced_execute_theaded_stop(mocker, advanced):
    mock_core = mocker.MagicMock()
    mock_opt = MockOpt(mock_core, countdown=int(1e4))

    mocker.patch.object(
        advanced, "_pre_execute", return_value=mock_opt, autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position._run_favorite", autospec=True
    )
    mocker.patch(
        "dtocean_plugins.strategies.position._post_process", autospec=True
    )

    thread = advanced.execute_threaded(None, None)

    assert not thread.stopped

    thread.stop()

    while not thread.stopped:
        time.sleep(0.5)

    assert thread.get_es()


def test_advanced_execute_theaded_pause_resume_pause_stop(
    caplog, mocker, advanced
):
    mock_core = mocker.MagicMock()
    mock_opt = MockOpt(mock_core, countdown=50)

    mocker.patch.object(
        advanced, "_pre_execute", return_value=mock_opt, autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position._run_favorite", autospec=True
    )
    mocker.patch(
        "dtocean_plugins.strategies.position._post_process", autospec=True
    )

    thread = advanced.execute_threaded(None, None)

    with caplog_for_logger(caplog, "dtocean_core"):
        thread.pause()

        while not thread.paused:
            time.sleep(0.5)

    assert not thread.stopped
    assert "Pausing thread..." in caplog.text
    assert thread.get_es() is None

    with caplog_for_logger(caplog, "dtocean_core"):
        thread.resume()

        while thread.paused:
            time.sleep(0.5)

    assert "Resuming thread..." in caplog.text

    with caplog_for_logger(caplog, "dtocean_core"):
        thread.pause()

        while not thread.paused:
            time.sleep(0.5)

    assert "Pausing thread..." in caplog.text

    with caplog_for_logger(caplog, "dtocean_core"):
        thread.stop()

        while not thread.stopped:
            time.sleep(0.5)

    assert thread.get_es()
    assert "Stopping thread..." in caplog.text


def test_advanced_execute_theaded_exit_hook(caplog, mocker, advanced):
    def mock_exit_hook():
        logging.getLogger("dtocean_plugins").info("Exit Hook")

    mock_core = mocker.MagicMock()
    mock_opt = MockOpt(mock_core)

    mocker.patch.object(
        advanced, "_pre_execute", return_value=mock_opt, autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position._run_favorite", autospec=True
    )
    mocker.patch(
        "dtocean_plugins.strategies.position._post_process", autospec=True
    )

    thread = advanced.execute_threaded(None, None)
    thread.pause()

    while not thread.paused:
        time.sleep(0.5)

    thread.set_exit_hook(mock_exit_hook)

    with caplog_for_logger(caplog, "dtocean_plugins"):
        thread.resume()

        while not thread.stopped:
            time.sleep(0.5)

    print(caplog.text)

    assert "Exit Hook" in caplog.text


def test_advanced_execute_theaded_bad_exit_hook(caplog, mocker, advanced):
    def mock_exit_hook():
        raise KeyError("bang!")

    mock_core = mocker.MagicMock()
    mock_opt = MockOpt(mock_core)

    mocker.patch.object(
        advanced, "_pre_execute", return_value=mock_opt, autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position._run_favorite", autospec=True
    )
    mocker.patch(
        "dtocean_plugins.strategies.position._post_process", autospec=True
    )

    thread = advanced.execute_threaded(None, None)
    thread.pause()

    while not thread.paused:
        time.sleep(0.5)

    thread.set_exit_hook(mock_exit_hook)

    with caplog_for_logger(caplog, "dtocean_core"):
        thread.resume()

        while not thread.stopped:
            time.sleep(0.5)

    assert "bang!" in caplog.text


def test_advanced_execute_theaded_clear_exit_hook(caplog, mocker, advanced):
    def mock_exit_hook():
        logging.getLogger().info("Exit Hook")

    mock_core = mocker.MagicMock()
    mock_opt = MockOpt(mock_core)

    mocker.patch.object(
        advanced, "_pre_execute", return_value=mock_opt, autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position._run_favorite", autospec=True
    )
    mocker.patch(
        "dtocean_plugins.strategies.position._post_process", autospec=True
    )

    thread = advanced.execute_threaded(None, None)
    thread.pause()

    while not thread.paused:
        time.sleep(0.5)

    thread.set_exit_hook(mock_exit_hook)
    thread.clear_exit_hook()

    with caplog_for_logger(caplog, "dtocean_core"):
        thread.resume()

        while not thread.stopped:
            time.sleep(0.5)

    assert "Exit Hook" not in caplog.text


def test_get_results_table():
    config = {
        "results_params": ["mock", "mock_dict", "objective"],
        "objective": "objective",
    }

    sim_num = range(5)
    mock_val = [10, 20, 30, 40, 50]
    n_nodes_val = [15, 25, 35, 45, 55]
    mock_angles = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 0]

    mock_dict_val = [{"sub_mock1": x, "sub_mock2": x} for x in mock_val]

    results_dict = {
        "sim_number": sim_num,
        "n_nodes": n_nodes_val,
        "mock": mock_val,
        "objective": mock_val,
        "grid_orientation": mock_angles,
        "mock_dict": mock_dict_val,
    }

    result = _get_results_table(config, results_dict)

    assert len(result) == 5
    assert list(result.columns[:4]) == [
        "sim_number",
        "objective",
        "grid_orientation",
        "n_nodes",
    ]
    assert set(result.columns[4:]) == set(
        [
            "mock",
            "mock_dict [sub_mock1]",
            "mock_dict [sub_mock2]",
        ]
    )

    assert np.isclose(
        result["grid_orientation"].to_numpy(), [90, 0, 270, 180, 90]
    ).all()


def test_get_results_table_single():
    config = {
        "results_params": ["mock", "mock_dict", "objective"],
        "objective": "objective",
    }

    mock_dict_val = {"sub_mock1": 10, "sub_mock2": 10}

    results_dict = {
        "sim_number": 0,
        "n_nodes": 15,
        "mock": 10,
        "objective": 10,
        "grid_orientation": 0,
        "mock_dict": mock_dict_val,
    }

    result = _get_results_table(config, results_dict)

    assert len(result) == 1
    assert list(result.columns[:4]) == [
        "sim_number",
        "objective",
        "grid_orientation",
        "n_nodes",
    ]
    assert set(result.columns[4:]) == set(
        [
            "mock",
            "mock_dict [sub_mock1]",
            "mock_dict [sub_mock2]",
        ]
    )

    assert np.isclose(result["grid_orientation"].to_numpy(), 90)


def test_advanced_get_favorite_result_not_available(tmpdir):
    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
    }

    with pytest.raises(RuntimeError) as excinfo:
        AdvancedPosition.get_favorite_result(config)

    assert "Favorite results not available" in str(excinfo)


@pytest.fixture
def results_dict():
    return {
        "params": {
            "dc": 91.87437990957726,
            "dr": 376.4144695626817,
            "n_evals": 8,
            "n_nodes": 20,
            "t1": 0.6264260686933844,
            "t2": 0.2504965577804759,
            "theta": 4.011057385038693,
        },
        "results": {
            "project.annual_energy": 93793.46420275935,
            "project.capex_breakdown": {
                "Condition Monitoring": 0.0,
                "Devices": 39200000.0,
                "Electrical Sub-Systems": 1961702.5022926005,
                "Externalities": 41000000.0,
                "Installation": 12027920.821639307,
                "Mooring and Foundations": 9157019.149960496,
            },
            "project.capex_total": 103346642.47389239,
            "project.lcoe_median": 0.1902369213617428,
            "project.lcoe_mode": 0.19023011901773357,
            "project.lifetime_energy_mode": 1867252.5828924393,
            "project.lifetime_opex_mode": 32228981.221621606,
            "project.number_of_devices": 20,
            "project.q_factor": 0.9999999999999998,
        },
        "status": "Success",
    }


def test_advanced_get_favorite_result(tmpdir, results_dict):
    fpath = str(tmpdir.join("mock_xfavorite.yaml"))

    with open(fpath, "w") as f:
        dump(results_dict, f, Dumper=Dumper)

    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
        "parameters": {
            "grid_orientation": None,
            "delta_row": None,
            "delta_col": None,
            "n_nodes": None,
            "t1": None,
            "t2": None,
        },
        "results_params": [
            "project.number_of_devices",
            "project.annual_energy",
            "project.q_factor",
            "project.capex_total",
            "project.capex_breakdown",
            "project.lifetime_opex_mode",
            "project.lifetime_energy_mode",
            "project.lcoe_median",
            "project.lcoe_mode",
        ],
        "objective": "project.lcoe_median",
    }

    result = AdvancedPosition.get_favorite_result(config)

    assert set(result.columns) == set(
        [
            "project.lcoe_median",
            "grid_orientation",
            "delta_row",
            "delta_col",
            "n_nodes",
            "t1",
            "t2",
            "n_evals",
            "project.annual_energy",
            "project.lifetime_energy_mode",
            "project.q_factor",
            "project.lcoe_mode",
            "project.lifetime_opex_mode",
            "project.capex_breakdown [Installation]",
            "project.capex_breakdown [Condition Monitoring]",
            "project.capex_breakdown [Externalities]",
            "project.capex_breakdown [Mooring and Foundations]",
            "project.capex_breakdown [Devices]",
            "project.capex_breakdown [Electrical Sub-Systems]",
            "project.capex_total",
            "project.number_of_devices",
        ]
    )

    assert len(result) == 1


def test_advanced_get_all_results_not_available(tmpdir):
    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
    }

    with pytest.raises(RuntimeError) as excinfo:
        AdvancedPosition.get_all_results(config)

    assert "Results table not available" in str(excinfo)


def test_advanced_get_all_results(mocker, tmpdir):
    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
        "results_params": ["mock", "mock_dict", "objective"],
        "objective": "objective",
    }

    p = tmpdir.join("mock_results.pkl")
    p.write("content")

    sim_num = range(5)
    mock_val = [10, 20, 30, 40, 50]
    n_nodes_val = [15, 25, 35, 45, 55]
    mock_angles = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 0]

    mock_dict_val = [{"sub_mock1": x, "sub_mock2": x} for x in mock_val]

    results_dict = {
        "sim_number": sim_num,
        "n_nodes": n_nodes_val,
        "mock": mock_val,
        "objective": mock_val,
        "grid_orientation": mock_angles,
        "mock_dict": mock_dict_val,
    }

    mocker.patch(
        "dtocean_plugins.strategies.position.open",
        mocker.mock_open(read_data=pickle.dumps(results_dict, -1)),
    )

    result = AdvancedPosition.get_all_results(config)

    assert len(result) == 5
    assert list(result.columns[:4]) == [
        "sim_number",
        "objective",
        "grid_orientation",
        "n_nodes",
    ]
    assert set(result.columns[4:]) == set(
        [
            "mock",
            "mock_dict [sub_mock1]",
            "mock_dict [sub_mock2]",
        ]
    )

    assert np.isclose(
        result["grid_orientation"].to_numpy(), [90, 0, 270, 180, 90]
    ).all()


def test_advanced_import_simulation_file(mocker, advanced, results_dict):
    mocker.patch(
        "dtocean_plugins.strategies.position.open",
        mocker.mock_open(read_data=dump(results_dict, Dumper=Dumper)),
    )

    mock_core = Core()
    mock_project = Project("mock")
    yaml_file_path = os.path.join("directory", "mock_0.yaml")

    mocker.patch(
        "dtocean_plugins.strategies.position.get_positioner", autospec=True
    )

    mocker.patch("dtocean_plugins.strategies.position.prepare", autospec=True)

    mocker.patch.object(mock_core, "import_simulation", autospec=True)

    advanced.import_simulation_file(mock_core, mock_project, yaml_file_path)

    import_simulation_args = mock_core.import_simulation.call_args.args

    assert isinstance(import_simulation_args[0], Project)
    assert import_simulation_args[0] != mock_project
    assert import_simulation_args[1] == mock_project

    assert "mock_0" in advanced.get_simulation_record()


def test_advanced_load_simulation_ids(mocker, tmpdir, advanced, results_dict):
    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
    }
    advanced._config = config

    # Add some dummy files
    sim_ids = range(5)
    p = tmpdir.join("mock_0.prj")
    p.write("content")

    for i in sim_ids:
        p = tmpdir.join("mock_{}.yaml".format(i))
        p.write("content")

    mocker.patch(
        "dtocean_plugins.strategies.position.get_positioner", autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position.open",
        mocker.mock_open(read_data=dump(results_dict, Dumper=Dumper)),
    )

    mocker.patch(
        "dtocean_plugins.strategies.position.logging.disable", autospec=True
    )

    mocker.patch("dtocean_plugins.strategies.position.iterate", autospec=True)

    mock_project = Project("mock")
    mock_load_project = Project("load")

    mock_core = Core()
    mocker.patch.object(mock_core, "dump_project", autospec=True)
    mocker.patch.object(
        mock_core, "load_project", return_value=mock_load_project, autospec=True
    )
    mocker.patch.object(mock_core, "import_simulation", autospec=True)

    advanced.load_simulation_ids(mock_core, mock_project, sim_ids)

    test_project = mock_core.import_simulation.call_args_list[0].args[0]

    assert test_project.title == "load"
    assert advanced.get_simulation_record() == [
        "Simulation 0",
        "Simulation 1",
        "Simulation 2",
        "Simulation 3",
        "Simulation 4",
    ]


def test_advanced_load_simulation_ids_titles(
    mocker, tmpdir, advanced, results_dict
):
    config = {
        "worker_dir": str(tmpdir),
        "root_project_path": str(tmpdir.join("mock.prj")),
    }
    advanced._config = config

    # Add some dummy files
    sim_ids = range(5)
    p = tmpdir.join("mock_0.prj")
    p.write("content")

    for i in sim_ids:
        p = tmpdir.join("mock_{}.yaml".format(i))
        p.write("content")

    mocker.patch(
        "dtocean_plugins.strategies.position.get_positioner", autospec=True
    )

    mocker.patch(
        "dtocean_plugins.strategies.position.open",
        mocker.mock_open(read_data=dump(results_dict, Dumper=Dumper)),
    )

    mocker.patch(
        "dtocean_plugins.strategies.position.logging.disable", autospec=True
    )

    mocker.patch("dtocean_plugins.strategies.position.iterate", autospec=True)

    mock_project = Project("mock")
    mock_load_project = Project("load")

    mock_core = Core()
    mocker.patch.object(mock_core, "dump_project", autospec=True)
    mocker.patch.object(
        mock_core, "load_project", return_value=mock_load_project, autospec=True
    )
    mocker.patch.object(mock_core, "import_simulation", autospec=True)

    sim_titles = ["Mock 0", "Mock 1", "Mock 2", "Mock 3", "Mock 4"]

    advanced.load_simulation_ids(mock_core, mock_project, sim_ids, sim_titles)

    test_project = mock_core.import_simulation.call_args_list[0].args[0]

    assert test_project.title == "load"
    assert advanced.get_simulation_record() == sim_titles


@pytest.mark.parametrize(
    "exclude_default, expected", [(True, False), (False, True)]
)
def test_advanced_remove_simulations(
    mocker, advanced, exclude_default, expected
):
    mock_project = Project("mock")

    mock_sim = OrderedSim("Default")
    mock_project.add_simulation(mock_sim)

    sim_names = ["Mock {}".format(i) for i in range(5)]

    for sim_name in sim_names:
        mock_sim = OrderedSim(sim_name)
        mock_project.add_simulation(mock_sim)
        advanced.add_simulation_title(sim_name)

    for name in sim_names:
        assert name in advanced.get_simulation_record()

    mock_core = Core()
    remove_simulation = mocker.patch.object(
        mock_core, "remove_simulation", autospec=True
    )

    advanced.remove_simulations(
        mock_core, mock_project, exclude_default=exclude_default
    )

    for name in sim_names:
        assert name not in advanced.get_simulation_record()

    titles_removed = [
        call.kwargs["sim_title"] for call in remove_simulation.call_args_list
    ]

    assert ("Default" in titles_removed) is expected


def test_advanced_load_config(mocker):
    mocker.patch(
        "dtocean_plugins.strategies.position.load_config",
        return_value=True,
        autospec=True,
    )

    assert AdvancedPosition.load_config(None)


def test_advanced_dump_config(mocker, advanced):
    config = {"clean_existing_dir": True}
    advanced._config = config

    dump_config = mocker.patch(
        "dtocean_plugins.strategies.position.dump_config", autospec=True
    )

    mock_path = "mock"
    advanced.dump_config(mock_path)

    assert dump_config.called
    assert dump_config.call_args.args[0] == mock_path
    assert dump_config.call_args.args[1]["clean_existing_dir"] is None


def test_advanced_export_config_template(mocker, advanced):
    dump_config = mocker.patch(
        "dtocean_plugins.strategies.position.dump_config", autospec=True
    )

    mock_path = "mock"
    advanced.export_config_template(mock_path)

    assert dump_config.called
    assert dump_config.call_args.args[0] == mock_path


@pytest.mark.parametrize(
    "p_code, c_code, w_dir,  w_code, o_code, expected",
    [
        (0, None, None, None, None, False),
        (1, 0, None, None, None, False),
        (1, 1, None, None, None, False),
        (1, 1, "mock", 0, 1, False),
        (1, 1, "mock", 0, 2, True),
        (1, 1, "mock", 1, None, True),
    ],
)
def test_advanced_allow_run(
    mocker, p_code, c_code, w_dir, w_code, o_code, expected
):
    mocker.patch.object(
        AdvancedPosition,
        "get_project_status",
        return_value=("mock", p_code),
        autospec=True,
    )

    mocker.patch.object(
        AdvancedPosition,
        "get_config_status",
        return_value=("mock", c_code),
        autospec=True,
    )

    mocker.patch.object(
        AdvancedPosition,
        "get_worker_directory_status",
        return_value=("mock", w_code),
        autospec=True,
    )

    mocker.patch.object(
        AdvancedPosition,
        "get_optimiser_status",
        return_value=("mock", o_code),
        autospec=True,
    )

    config = {"worker_dir": w_dir}

    assert AdvancedPosition.allow_run(None, None, config) == expected
