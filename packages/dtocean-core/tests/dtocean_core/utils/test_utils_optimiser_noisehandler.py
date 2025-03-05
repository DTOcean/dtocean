# -*- coding: utf-8 -*-

# pylint: disable=protected-access

import sys
from collections import namedtuple
from typing import Optional

import numpy as np
import pytest

from dtocean_core.utils.optimiser import (
    Counter,
    Evaluator,
    Main,
    NoiseHandler,
    NormScaler,
    dump_outputs,
    init_evolution_strategy,
    load_outputs,
)


class MockParams(namedtuple("MockParams", ["cost", "x"])):
    def __eq__(self, other):
        a = self.cost
        b = other.cost
        return (a == b) | (np.isnan(a) & np.isnan(b)) and self.x == other.x


class MockCounter(Counter):
    def _set_params(self, *args):
        """Build a params (probably namedtuple) object to record iteration."""
        return MockParams(args[0], args[1:])

    def _get_cost(self, params, *args):
        isclose = np.isclose(params.x, args)

        if isclose.size > 0 and isclose.all():
            return params.cost

        return None


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
        self._n_evals = None

    def _init_counter(self):
        return MockCounter()

    def _get_popen_args(self, worker_project_path, n_evals, *args):
        "Return the arguments to create a new process thread using Popen"
        if self.scaler is not None:
            args = [self.scaler.inverse(x) for x in args]
        self._args = args
        self._n_evals = n_evals
        return [sys.executable, "-V"]

    def _get_worker_results(self, iteration):  # pylint: disable=arguments-differ,unused-argument
        """Return the results for the given iteration as a dictionary that
        must include the key "cost". For constraint violation the cost key
        should be set to np.nan"""

        assert self._n_evals is not None
        x = np.array(self._args)
        all_costs = []

        for _ in range(self._n_evals):
            base = sphere_cost(x)
            noise = 0.5 * np.random.randn()
            cost = base + noise
            all_costs.append(cost)

        all_costs = np.array(all_costs)
        cost = (
            np.NaN if np.all(all_costs != all_costs) else np.nanmean(all_costs)
        )

        return {"cost": cost}

    def _set_counter_params(
        self, evaluation, worker_project_path, results, flag, n_evals, *args
    ):
        """Update the counter object with new data."""

        cost = np.nan
        if results is not None:
            cost = results["cost"]

        self._counter.set_params(evaluation, cost, *args)


#    def _log_exception(self, e, flag):
#
#        print flag
#        print e
#
#        raise e


def test_noisehandler_tell_empty(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-2,
        timeout=60,
        logging_directory=str(tmpdir),
    )

    nh = NoiseHandler(es.N, maxevals=[1, 1, 5])

    init_sols = [
        np.array([10, 10]),
        np.array([10, 10]),
        np.array([10, 10]),
        np.array([10, 10]),
    ]
    init_cost = [10, 10, 10, 10]

    nh.prepare(init_sols, init_cost)
    nh.ask(es.ask)
    nh.tell([], [])

    assert nh.fit is None
    assert nh.fitre is None
    assert nh._sigma_fac == 1.0


def test_noisehandler_tell_wrong_number(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-2,
        timeout=60,
        logging_directory=str(tmpdir),
    )

    nh = NoiseHandler(es.N, maxevals=[1, 1, 5])

    init_sols = [
        np.array([10, 10]),
        np.array([10, 10]),
        np.array([10, 10]),
        np.array([10, 10]),
    ]
    init_cost = [10, 10, 10, 10]

    nh.prepare(init_sols, init_cost)
    sols = nh.ask(es.ask)

    with pytest.raises(ValueError) as excinfo:
        nh.tell(sols, [10])

    expected = "Exactly {} solutions and function values".format(len(sols))
    assert expected in str(excinfo)


def test_noisehandler_tell_not_asked_for(mocker, tmpdir):
    mocker.patch("dtocean_core.utils.optimiser.init_dir", autospec=True)
    mock_core = mocker.MagicMock()

    mock_eval = MockEvaluator(mock_core, None, "mock", "mock")

    x0 = 5
    x_range = (-1, 10)
    scaler = NormScaler(x_range[0], x_range[1], x0)
    mock_eval.scaler = scaler

    xhat0 = [scaler.x0] * 2
    xhat_low_bound = [scaler.scaled(x_range[0])] * 2
    xhat_high_bound = [scaler.scaled(x_range[1])] * 2

    es = init_evolution_strategy(
        xhat0,
        xhat_low_bound,
        xhat_high_bound,
        tolfun=1e-2,
        timeout=60,
        logging_directory=str(tmpdir),
    )

    nh = NoiseHandler(es.N, maxevals=[1, 1, 5])

    init_sols = [
        np.array([10, 10]),
        np.array([10, 10]),
        np.array([10, 10]),
        np.array([10, 10]),
    ]
    init_cost = [10, 10, 10, 10]

    nh.prepare(init_sols, init_cost)
    sols = nh.ask(es.ask)
    fake_sol = [sol * 0 + 1 for sol in sols]
    fake_value = range(len(sols))

    with pytest.raises(RuntimeError) as excinfo:
        nh.tell(fake_sol, fake_value)

    assert "was not asked for" in str(excinfo)


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
        tolfun=1e-2,
        timeout=60,
        logging_directory=str(tmpdir),
    )

    nh = NoiseHandler(es.N, maxevals=[1, 1, 5], epsilon=1e-3)

    test = Main(es, mock_eval, scaled_vars, x_ops, nh=nh, base_penalty=1e4)

    max_noise = -np.inf
    costs = []

    while max_noise <= 0 and not test.stop:
        max_noise = max(max_noise, nh.get_predicted_noise())
        cost = es.result.fbest
        costs.append(cost)
        test.next()

    if max_noise <= 0:
        pytest.xfail("creating noise taking too long")

    first_cost = costs[0]
    last_cost = costs[-1]

    assert first_cost > last_cost


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

    nh = NoiseHandler(es.N, maxevals=[1, 1, 30])

    test = Main(
        es,
        mock_eval,
        scaled_vars,
        x_ops,
        nh=nh,
        base_penalty=1e4,
        auto_resample_iterations=2,
    )

    i = 0

    while i < 4:
        test.next()
        i += 1

    counter_dict = mock_eval.get_counter_search_dict()
    pre_dump = len(tmpdir.listdir())

    dump_outputs(str(tmpdir), es, mock_eval, nh)

    assert len(tmpdir.listdir()) == pre_dump + 3

    new_es, new_counter_dict, new_nh = load_outputs(str(tmpdir))

    assert es.fit.hist == new_es.fit.hist  # type: ignore
    assert new_counter_dict == counter_dict

    assert new_nh is not None
    assert new_nh._noise_predict() == nh._noise_predict()
