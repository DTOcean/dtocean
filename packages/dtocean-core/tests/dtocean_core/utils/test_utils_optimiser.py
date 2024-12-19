# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access

import contextlib
import logging
import queue
import threading
from collections import namedtuple
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pytest

from dtocean_core.utils.optimiser import (
    Counter,
    Evaluator,
    Main,
    NormScaler,
    SafeCMAEvolutionStrategy,
    _get_match_process,
    _get_scale_factor,
    dump_outputs,
    init_evolution_strategy,
    load_outputs,
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
def norm_scaler():
    return NormScaler(0, 12, 9)


def test_NormScaler_bad_x0():
    with pytest.raises(ValueError) as excinfo:
        NormScaler(0, 1, -1)

    assert "x0 must lie between" in str(excinfo)


def test_NormScaler_x0(norm_scaler):
    assert np.isclose(norm_scaler.x0, 3)


@pytest.mark.parametrize("value", range(13))
def test_NormScaler_scaling(norm_scaler, value):
    scaled = norm_scaler.scaled(value)
    assert np.isclose(norm_scaler.inverse(scaled), value)


class MockParams(namedtuple("MockParams", ["cost", "x"])):
    def __eq__(self, other):
        a = self.cost
        b = other.cost
        return (a == b) | (np.isnan(a) & np.isnan(b)) and self.x == other.x


class MockCounter(Counter):
    def _set_params(self, *args):
        """Build a params (probably namedtuple) object to record evaluation."""
        return MockParams(args[0], args[1:])

    def _get_cost(self, params, *args):
        isclose = np.isclose(params.x, args)

        if isclose.size > 0 and isclose.all():
            return params.cost

        return None


def test_Counter_set_params():
    counter = MockCounter()
    evaluation = counter.next_evaluation()
    counter.set_params(evaluation, 11, 1)
    evaluation = counter.next_evaluation()
    counter.set_params(evaluation, 12, 2)

    search_dict = counter.search_dict

    assert len(search_dict) == 2
    assert search_dict[1] == MockParams(12, (2,))


def test_Counter_set_params_bad_iter():
    counter = MockCounter()
    evaluation = counter.next_evaluation()
    counter.set_params(evaluation, 1, 11)

    with pytest.raises(ValueError) as excinfo:
        counter.set_params(evaluation, 2, 12)

    assert "has already been recorded" in str(excinfo)


@pytest.mark.parametrize("value, expected", [(1, 11), (2, 12), (3, False)])
def test_Counter_get_cost(value, expected):
    counter = MockCounter()
    evaluation = counter.next_evaluation()
    counter.set_params(evaluation, 11, 1)
    evaluation = counter.next_evaluation()
    counter.set_params(evaluation, 12, 2)

    assert counter.get_cost(value) == expected


def sphere_cost(x, c=0.0):
    #    The BSD 3-Clause License
    #    Copyright (c) 2014 Inria
    #    Author: Nikolaus Hansen, 2008-
    #    Author: Petr Baudis, 2014
    #    Author: Youhei Akimoto, 2016-
    #
    #    Redistribution and use in source and binary forms, with or without
    #    modification, are permitted provided that the following conditions
    #    are met:
    #
    #    1. Redistributions of source code must retain the above copyright and
    #       authors notice, this list of conditions and the following disclaimer.
    #
    #    2. Redistributions in binary form must reproduce the above copyright
    #       and authors notice, this list of conditions and the following
    #       disclaimer in the documentation and/or other materials provided with
    #       the distribution.
    #
    #    3. Neither the name of the copyright holder nor the names of its
    #       contributors nor the authors names may be used to endorse or promote
    #       products derived from this software without specific prior written
    #       permission.
    #
    #    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    #    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    #    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    #    AUTHORS OR CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
    #    OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    #    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    #    DEALINGS IN THE SOFTWARE.

    # Sphere (squared norm) test objective function

    if (x < c).any():
        cost = np.nan
    else:
        cost = -(c**2) + sum((x + 0) ** 2)

    return cost


class MockEvaluator(Evaluator):
    def __init__(self, *args, **kwargs):
        super(MockEvaluator, self).__init__(*args, **kwargs)
        self.scaler: Optional[NormScaler] = None
        self._args = None

    def _init_counter(self):
        return MockCounter()

    def _get_popen_args(self, worker_project_path, n_evals, *args):
        "Return the arguments to create a new process thread using Popen"
        if self.scaler is not None:
            args = [self.scaler.inverse(x) for x in args]
        self._args = args
        return ["python", "-V"]

    def _get_worker_results(self, evaluation):
        """Return the results for the given evaluation as a dictionary that
        must include the key "cost". For constraint violation the cost key
        should be set to np.nan"""

        x = np.array(self._args)
        return {"cost": sphere_cost(x)}

    def _set_counter_params(
        self, evaluation, worker_project_path, results, flag, n_evals, *args
    ):
        """Update the counter object with new data."""

        cost = np.nan
        if results is not None:
            cost = results["cost"]

        self._counter.set_params(evaluation, cost, *args)

        return


#    def _log_exception(self, e, flag):
#
#        print flag
#        print e
#
#        raise e


def test_evaluator(mocker):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    test = MockEvaluator(mock_core, None, "mock", "mock")

    thread_queue = queue.Queue()
    result_queue = queue.Queue()

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])

    thread_queue.put(item)

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([10])
    item.append(["mock2"])

    thread_queue.put(item)

    test(thread_queue, stop_empty=True)

    assert result_queue.get() == (1.0, ["mock1"])
    assert result_queue.get() == (100.0, ["mock2"])


def test_evaluator_threaded(mocker):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    test = MockEvaluator(mock_core, None, "mock", "mock")

    thread_queue = queue.Queue()
    result_queue = queue.Queue()

    worker = threading.Thread(target=test, args=(thread_queue,))
    worker.setDaemon(True)
    worker.start()

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])

    thread_queue.put(item)

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([10])
    item.append(["mock2"])

    thread_queue.put(item)

    thread_queue.join()

    assert result_queue.get() == (1.0, ["mock1"])
    assert result_queue.get() == (100.0, ["mock2"])


def test_evaluator_previous_cost(mocker):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    test = MockEvaluator(mock_core, None, "mock", "mock")

    mocker.patch.object(
        test._counter, "get_cost", side_effect=[False, "match"], autospec=True
    )

    thread_queue = queue.Queue()
    result_queue = queue.Queue()

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])

    thread_queue.put(item)

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock2"])

    thread_queue.put(item)

    test(thread_queue, stop_empty=True)

    assert result_queue.get() == (1.0, ["mock1"])
    assert result_queue.get() == ("match", ["mock2"])


def test_evaluator_fail_send(caplog, mocker):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    exc_msg = "Bang!"
    mock_core.dump_project.side_effect = KeyError(exc_msg)

    test = MockEvaluator(mock_core, None, "mock", "mock")

    thread_queue = queue.Queue()
    result_queue = queue.Queue()

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])

    thread_queue.put(item)

    with caplog_for_logger(caplog, "dtocean_core"):
        test(thread_queue, stop_empty=True)

    assert result_queue.get() == (np.nan, ["mock1"])
    assert "Fail Send" in caplog.text
    assert exc_msg in caplog.text


def test_evaluator_fail_execute(caplog, mocker):
    mock_process = mocker.MagicMock()
    mock_process.wait.return_value = 1

    mocker.patch(
        "dtocean_core.utils.optimiser.Popen",
        return_value=mock_process,
        autospec=True,
    )

    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)

    mock_core = mocker.MagicMock()
    test = MockEvaluator(mock_core, None, "mock", "mock")

    thread_queue = queue.Queue()
    result_queue = queue.Queue()

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])

    thread_queue.put(item)

    with caplog_for_logger(caplog, "dtocean_core"):
        test(thread_queue, stop_empty=True)

    assert result_queue.get() == (np.nan, ["mock1"])
    assert "Fail Execute" in caplog.text
    assert "External process failed to open" in caplog.text


def test_evaluator_fail_receive(caplog, mocker):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    test = MockEvaluator(mock_core, None, "mock", "mock")

    exc_msg = "Bang!"
    mocker.patch.object(
        test,
        "_get_worker_results",
        side_effect=KeyError(exc_msg),
        autospec=True,
    )

    thread_queue = queue.Queue()
    result_queue = queue.Queue()

    item: list[Any] = [result_queue]
    item.append(None)
    item.append([1])
    item.append(["mock1"])

    thread_queue.put(item)

    with caplog_for_logger(caplog, "dtocean_core"):
        test(thread_queue, stop_empty=True)

    assert result_queue.get() == (np.nan, ["mock1"])
    assert "Fail Receive" in caplog.text
    assert exc_msg in caplog.text


def test_init_evolution_strategy(tmpdir):
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        integer_variables=[0],
        max_simulations=10,
        popsize=9,
        timeout=1,
        tolfun=1e-9,
        logging_directory=str(tmpdir),
    )

    assert isinstance(es, SafeCMAEvolutionStrategy)


def test_main_max_resample_loop_factor_negative(tmpdir):
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    with pytest.raises(ValueError) as excinfo:
        Main(es, None, None, None, max_resample_loop_factor=-1)

    assert "must be greater than or equal to zero" in str(excinfo)


def test_main_max_auto_resample_iterations_zero(tmpdir):
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    with pytest.raises(ValueError) as excinfo:
        Main(es, None, None, None, auto_resample_iterations=0)

    assert "must be greater than zero" in str(excinfo)


def test_main_max_resample_loops(tmpdir):
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    popsize = 4
    max_resample_loop_factor = 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        popsize=popsize,
        logging_directory=str(tmpdir),
    )

    test = Main(
        es, None, None, None, max_resample_loop_factor=max_resample_loop_factor
    )

    expected = 2 * popsize * max_resample_loop_factor
    assert test.get_max_resample_factor() == expected


def test_main_get_max_resample_factor_auto(tmpdir):
    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    auto_resample_iterations = 2

    es = init_evolution_strategy(
        xhat0, xhat_low_bound, xhat_high_bound, logging_directory=str(tmpdir)
    )

    test = Main(
        es, None, None, None, auto_resample_iterations=auto_resample_iterations
    )

    expected = "auto{}".format(auto_resample_iterations)
    assert test.get_max_resample_factor() == expected


def test_main(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    test = Main(es, mock_eval, scaled_vars, x_ops, base_penalty=1e4)

    while not test.stop:
        test.next()

    sol = np.array([scaler.inverse(x) for x in es.result.xfavorite])

    assert (sol >= x_range[0]).all()
    assert (sol <= x_range[1]).all()
    assert (sol**2).sum() < 1e-1


def test_main_fixed(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2
    fixed_index_map = {2: scaler.scaled(1)}

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    test = Main(
        es,
        mock_eval,
        scaled_vars,
        x_ops,
        fixed_index_map=fixed_index_map,
        base_penalty=1e4,
    )

    while not test.stop:
        test.next()

    assert abs(es.result.fbest - 1) < 1e-1


class MockEvaluatorPenalty(MockEvaluator):
    def __init__(self, *args, **kwargs):
        super(MockEvaluatorPenalty, self).__init__(*args, **kwargs)
        self.popsize: Optional[int] = None
        self._evaluation = None

    def pre_constraints_hook(self, *args):
        if self._evaluation is None:
            return False
        if self._evaluation > self.popsize:
            return True
        return False

    def _get_worker_results(self, evaluation):
        self._evaluation = evaluation
        return super(MockEvaluatorPenalty, self)._get_worker_results(evaluation)


def test_main_apply_constraints_penalty(caplog, mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluatorPenalty(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)

    popsize = 5
    mock_eval.scaler = scaler
    mock_eval.popsize = popsize

    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        popsize=popsize,
        logging_directory=str(tmpdir),
    )

    test = Main(
        es,
        mock_eval,
        scaled_vars,
        x_ops,
        base_penalty=1e4,
        max_resample_loop_factor=1,
    )

    i = 0

    with caplog_for_logger(caplog, "dtocean_core"):
        while i < 3:
            test.next()
            i += 1

    expected = "Only 0 of {} required solutions were found".format(popsize * 2)
    assert expected in caplog.text


def test_main_auto_resample_iterations(caplog, mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    test = Main(
        es,
        mock_eval,
        scaled_vars,
        x_ops,
        base_penalty=1e4,
        auto_resample_iterations=2,
    )

    i = 0

    with caplog_for_logger(caplog, "dtocean_core"):
        while i < 4:
            test.next()
            i += 1

    assert "following iteration 2" in caplog.text


def test_main_no_feasible_solutions(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    mocker.patch.object(
        mock_eval,
        "_get_worker_results",
        return_value={"cost": np.nan},
        autospec=True,
    )

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    test = Main(es, mock_eval, scaled_vars, x_ops, base_penalty=1e4)

    with pytest.raises(RuntimeError) as excinfo:
        test.next()

    assert "no feasible solutions" in str(excinfo)


def test_SafeCMAEvolutionStrategy_plot(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    test = Main(
        es,
        mock_eval,
        scaled_vars,
        x_ops,
        base_penalty=1e4,
        auto_resample_iterations=2,
    )

    i = 0

    while i < 4:
        test.next()
        i += 1

    es.plot()

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_get_scale_factor_bad_sigma():
    with pytest.raises(ValueError) as excinfo:
        _get_scale_factor(0, 2, 1, 0, 1)

    assert "sigma must be positive" in str(excinfo)


@pytest.mark.parametrize("n_sigmas", [-1, 2.1])
def test_get_scale_factor_bad_n_sigmas(n_sigmas):
    with pytest.raises(ValueError) as excinfo:
        _get_scale_factor(0, 2, 1, 1, n_sigmas)

    assert "must be a positive whole number" in str(excinfo)


def test_get_match_process():
    a = [[1, 1], [2, 2], [2, 2], [2, 2], [3, 3]]
    b = ["a", "b", "b", "b", "c"]
    c = [True, False, False, False, True]

    run_idxs, match_dict = _get_match_process(a, b, c)

    assert run_idxs == [0, 1, 4]
    assert 1 in match_dict
    assert match_dict[1] == [(2, "b", False), (3, "b", False)]


def test_dump_load_outputs(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    scaled_vars = [scaler] * 2
    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2
    x_ops = [None] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-1,
        logging_directory=str(tmpdir),
    )

    test = Main(
        es,
        mock_eval,
        scaled_vars,
        x_ops,
        base_penalty=1e4,
        auto_resample_iterations=2,
    )

    i = 0

    while i < 4:
        test.next()
        i += 1

    counter_dict = mock_eval.get_counter_search_dict()
    pre_dump = len(tmpdir.listdir())

    dump_outputs(str(tmpdir), es, mock_eval)

    assert len(tmpdir.listdir()) == pre_dump + 2

    new_es, new_counter_dict, new_nh = load_outputs(str(tmpdir))

    assert es.fit.hist == new_es.fit.hist  # type: ignore
    assert new_counter_dict == counter_dict
    assert new_nh is None
    assert new_counter_dict == counter_dict
    assert new_nh is None
