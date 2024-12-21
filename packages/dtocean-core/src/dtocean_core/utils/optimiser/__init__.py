# -*- coding: utf-8 -*-

#    Copyright (C) 2021-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import abc
import logging
import os
import pickle
import queue
import sys
import threading
import time
import traceback
from collections import OrderedDict
from copy import deepcopy
from logging import handlers
from math import ceil
from subprocess import Popen
from typing import Any, Sequence

import cma
import numpy as np
from numpy.linalg import norm

from ..files import init_dir

# Convenience import
from .noisehandler import NoiseHandler  # noqa: F401

# Set up logging
module_logger = logging.getLogger(__name__)


class SafeCMAEvolutionStrategy(cma.CMAEvolutionStrategy):
    def plot(self):
        cma.plot(self.logger.name_prefix)


class NormScaler:
    sigma = 1.0
    range_n_sigmas = 3

    def __init__(self, range_min, range_max, x0=None):
        if x0 is None:
            x0 = 0.5 * (range_min + range_max)

        self._scale_factor = _get_scale_factor(
            range_min, range_max, x0, self.sigma, self.range_n_sigmas
        )
        self._x0 = self.scaled(x0)

    @property
    def x0(self):
        return self._x0

    def scaled(self, value):
        return value * self._scale_factor

    def inverse(self, value):
        return value / self._scale_factor


class Counter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, search_dict=None):
        if search_dict is None or not search_dict:
            evaluation = 0
            search_dict = {}
        else:
            evaluation = max(search_dict) + 1

        self._evaluation = evaluation
        self._search_dict = search_dict
        self._lock = threading.Lock()

    @property
    def search_dict(self):
        self._lock.acquire()

        try:
            result = deepcopy(self._search_dict)
        finally:
            self._lock.release()

        return result

    def set_params(self, evaluation, *args):
        params = self._set_params(*args)

        self._lock.acquire()

        try:
            if evaluation in self._search_dict:
                err_str = ("Evaluation {} has already been " "recorded").format(
                    evaluation
                )
                raise ValueError(err_str)

            self._search_dict[evaluation] = params

        finally:
            self._lock.release()

    @abc.abstractmethod
    def _set_params(self, *args):
        """Build a params (probably namedtuple) object to record evaluation."""
        pass

    def get_cost(self, *args):
        self._lock.acquire()
        cost = None

        try:
            for params in self._search_dict.values():
                cost = self._get_cost(params, *args)
                if cost is not None:
                    break

        finally:
            self._lock.release()

        if cost is None:
            cost = False

        return cost

    @abc.abstractmethod
    def _get_cost(self, params, *args):  # pylint: disable=unused-argument
        """Return cost if parameters in params object match input args, else
        return None."""
        pass

    def next_evaluation(self):
        self._lock.acquire()

        try:
            result = self._evaluation
            self._evaluation += 1

        finally:
            self._lock.release()

        return result


class Evaluator:
    __metaclass__ = abc.ABCMeta

    def __init__(
        self,
        core,
        base_project,
        root_project_base_name,
        worker_directory,
        restart=False,
        clean_existing_dir=False,
    ):
        self._core = core
        self._base_project = base_project
        self._root_project_base_name = root_project_base_name
        self._worker_directory = worker_directory
        self._counter: Counter = self._init_counter()

        if not restart:
            init_dir(worker_directory, clean_existing_dir)

    @abc.abstractmethod
    def _init_counter(self) -> Counter:
        "Initialise and return the counter stored in the _counter attr"
        pass

    @abc.abstractmethod
    def _get_popen_args(
        self,
        worker_project_path,
        n_evals,
        *args,
    ) -> Sequence[str]:
        "Return the arguments to create a new process thread using Popen"
        pass

    @abc.abstractmethod
    def _get_worker_results(self, evaluation) -> dict[str, Any]:
        """Return the results for the given evaluation as a dictionary that
        must include the key "cost". For constraint violation the cost key
        should be set to np.nan"""
        pass

    @abc.abstractmethod
    def _set_counter_params(
        self, evaluation, worker_project_path, results, flag, n_evals, *args
    ):
        """Update the counter object with new data."""
        pass

    def pre_constraints_hook(self, *args):  # pylint: disable=no-self-use,unused-argument
        """Allows checking of constraints prior to execution. Should return
        True if violated otherwise False"""
        return False

    def _cleanup_hook(self, worker_project_path, flag, results):  # pylint: disable=no-self-use,unused-argument
        """Hook to clean up simulation files as required"""
        pass

    def get_counter_search_dict(self):
        return self._counter.search_dict

    def _iterate(self, results_queue, n_evals, x, *extra):
        previous_cost = self._counter.get_cost(*x)

        if previous_cost:
            results_queue.put((previous_cost,) + extra)
            return

        flag = ""
        evaluation = self._counter.next_evaluation()

        worker_file_root_path = "{}_{}".format(
            self._root_project_base_name, evaluation
        )
        worker_project_name = "{}.prj".format(worker_file_root_path)
        worker_project_path = os.path.join(
            self._worker_directory, worker_project_name
        )

        results = None
        cost = np.nan

        try:
            self._core.dump_project(self._base_project, worker_project_path)

        except Exception as e:  # pylint: disable=broad-except
            flag = "Fail Send"
            _log_exception(e, flag)

        try:
            popen_args = self._get_popen_args(worker_project_path, n_evals, *x)
            process = Popen(popen_args, close_fds=True)
            exit_code = process.wait()

            if exit_code != 0:
                args_str = ", ".join(popen_args)
                err_str = (
                    "External process failed to open. Arguments were: " "{}"
                ).format(args_str)

                raise RuntimeError(err_str)

        except Exception as e:  # pylint: disable=broad-except
            flag = "Fail Execute"
            _log_exception(e, flag)

        if "Fail" not in flag:
            try:
                results = self._get_worker_results(evaluation)
                cost = results["cost"]

            except Exception as e:  # pylint: disable=broad-except
                flag = "Fail Receive"
                _log_exception(e, flag)

        self._set_counter_params(
            evaluation, worker_project_path, results, flag, n_evals, *x
        )
        self._cleanup_hook(worker_project_path, flag, results)

        results_queue.put((cost,) + extra)

    def __call__(self, q, stop_empty=False):
        """Call the evaluator with a queue.Queue() where index 0 is another
        queue to collect results, index 1 is the number of evaluations for
        noisy cost functions, index 2 is the solution to solve and any extra
        indices are added to the result queue following the calculated cost.
        """

        def check1():
            return not q.empty()

        def check2():
            return True

        if stop_empty:
            check = check1
        else:
            check = check2

        while check():
            item = q.get()
            self._iterate(*item)
            q.task_done()


class Main:
    def __init__(
        self,
        es,
        evaluator,
        scaled_vars,
        x_ops,
        nh=None,
        fixed_index_map=None,
        base_penalty=None,
        num_threads=None,
        maximise=False,
        max_resample_loop_factor=None,
        auto_resample_iterations=None,
    ):
        # Defaults
        if base_penalty is None:
            base_penalty = 1.0
        if num_threads is None:
            num_threads = 1

        self.es = es
        self.nh = nh
        self.evaluator = evaluator
        self._scaled_vars = scaled_vars
        self._x_ops = x_ops
        self._fixed_index_map = fixed_index_map
        self._base_penalty = base_penalty
        self._num_threads = num_threads
        self._maximise = maximise
        self._spare_sols = 1
        self._n_hist = int(10 + 30 * self.es.N / self.es.sp.popsize)
        self._stop = False
        self._sol_penalty = False
        self._dirty_restart = False
        self._sol_feasible = None
        self._max_resample_loops: int
        self._n_record_resample: int
        self._thread_queue: queue.Queue

        self._init_resamples(max_resample_loop_factor, auto_resample_iterations)
        self._init_threads()

    @property
    def stop(self):
        return self._stop

    @property
    def max_resample_loops(self):
        return self._max_resample_loops

    def _init_resamples(
        self, max_resample_loop_factor, auto_resample_iterations
    ):
        if auto_resample_iterations is None:
            if max_resample_loop_factor is None:
                max_resample_loop_factor = 20

            if max_resample_loop_factor < 0:
                err_msg = (
                    "Argument max_resample_loop_factor must be greater "
                    "than or equal to zero"
                )
                raise ValueError(err_msg)

            self._n_record_resample = 0

            n_default = self.es.popsize
            needed_solutions = (1 + self._spare_sols) * n_default
            self._max_resample_loops = int(
                ceil(max_resample_loop_factor * needed_solutions)
            )

            log_msg = ("Setting maximum resamples to " "{}").format(
                self._max_resample_loops
            )
            module_logger.debug(log_msg)

        else:
            if auto_resample_iterations <= 0:
                err_msg = (
                    "Argument auto_resample_iterations must be greater "
                    "than zero"
                )
                raise ValueError(err_msg)

            self._max_resample_loops = 0
            self._n_record_resample = auto_resample_iterations

    def _init_threads(self):
        self._thread_queue = queue.Queue()

        for _ in range(self._num_threads):
            worker = threading.Thread(
                target=self.evaluator, args=(self._thread_queue,)
            )
            worker.daemon = True
            worker.start()

    def next(self):
        if self.es.stop():
            self._stop = True
            return

        if self.nh is None:
            self._next()
        else:
            self._next_nh()

        tolfun = max(self.es.fit.fit) - min(self.es.fit.fit)
        tolfunhist = max(self.es.fit.hist) - min(self.es.fit.hist)

        msg_str = ("Minimum fitness for iteration {}: " "{:.15e}").format(
            self.es.countiter, min(self.es.fit.fit)
        )
        module_logger.info(msg_str)

        msg_str = ("Fitness value range (last iteration): " "{}").format(tolfun)
        module_logger.info(msg_str)

        msg_str = (
            "Minimum fitness value range (last {} iterations): " "{}"
        ).format(self._n_hist, tolfunhist)
        module_logger.info(msg_str)

    def _next(self):
        default, _ = self._get_solutions_costs(self.es)
        self.es.tell(default["solutions"], default["costs"])
        self.es.logger.add()

    def _next_nh(self):
        assert self.nh is not None

        # self._sol_penalty is set by self._get_solutions_costs
        if self.es.countiter == 0 or self._sol_penalty or self._dirty_restart:
            scaled_solutions_extra = None
            last_n_evals = None
            self._dirty_restart = False
        else:
            scaled_solutions_extra = self.nh.ask(self.es.ask)
            last_n_evals = self.nh.last_n_evals

        default, extra = self._get_solutions_costs(
            self.es, scaled_solutions_extra, self.nh.n_evals, last_n_evals
        )

        self.es.tell(default["solutions"], default["costs"])
        self.nh.tell(extra["solutions"], extra["costs"])

        self.es.sigma *= self.nh.sigma_fac
        self.es.countevals += self.nh.evaluations_just_done

        noise = self.nh.get_predicted_noise()

        msg = "Last true noise: {}".format(self.nh.noiseS)
        module_logger.info(msg)

        msg = "Predicted noise: {}".format(noise)
        module_logger.info(msg)

        if abs(noise) <= 1e-12:
            log_noise = 1
        elif noise <= -1e-12:
            log_noise = 0.1
        else:
            log_noise = 10

        self.es.logger.add(more_data=[self.nh.evaluations, log_noise])
        self.nh.prepare(default["solutions"], default["costs"])

    def _get_solutions_costs(
        self,
        asktell,
        scaled_solutions_extra=None,
        n_evals=None,
        n_evals_extra=None,
    ):
        self._sol_penalty = False

        final_solutions = []
        final_costs = []
        final_solutions_extra = []
        final_costs_extra = []

        result_default = {"solutions": final_solutions, "costs": final_costs}
        result_extra = {
            "solutions": final_solutions_extra,
            "costs": final_costs_extra,
        }

        n_default = asktell.popsize
        needed_solutions = (1 + self._spare_sols) * n_default
        xmean = None

        run_solutions = []
        run_descaled_solutions = []
        resample_loops = -1

        while len(run_solutions) < needed_solutions:
            # If the maximum number of resamples is reached apply a
            # penalty value to a new set of solutions
            if (
                self._n_record_resample == 0
                and resample_loops == self._max_resample_loops
            ):
                log_msg = (
                    "Maximum of {} resamples reached. Only {} of {} "
                    "required solutions were found. Applying "
                    "penalty values."
                ).format(
                    self._max_resample_loops,
                    len(run_solutions),
                    needed_solutions,
                )
                module_logger.info(log_msg)

                run_solutions = []
                run_descaled_solutions = []
                final_solutions.extend(asktell.ask(n_default))
                final_costs.extend(self._get_penalty(final_solutions))

                n_default = 0

                # Do not assess noise
                self._sol_penalty = True

                break

            scaled_solutions = asktell.ask(asktell.popsize, xmean)

            # Store xmean for resamples
            if xmean is None:
                xmean = asktell.mean.copy()

            descaled_solutions = self.get_descaled_solutions(scaled_solutions)

            checked_solutions = []
            checked_descaled_solutions = []

            for sol, des_sol in zip(scaled_solutions, descaled_solutions):
                if self.evaluator.pre_constraints_hook(*des_sol):
                    continue

                checked_solutions.append(sol)
                checked_descaled_solutions.append(des_sol)

                solution_str = ", ".join(str(xi) for xi in des_sol)
                log_msg = "Solution found: " + solution_str
                module_logger.debug(log_msg)

            max_sols = needed_solutions - len(run_solutions)
            checked_solutions = checked_solutions[:max_sols]
            checked_descaled_solutions = checked_descaled_solutions[:max_sols]

            run_solutions.extend(checked_solutions)
            run_descaled_solutions.extend(checked_descaled_solutions)

            resample_loops += 1

            if resample_loops > 0 and checked_solutions:
                log_msg = (
                    "{} of {} solutions found after {} resampling " "loops"
                ).format(len(run_solutions), needed_solutions, resample_loops)
                module_logger.debug(log_msg)

        if not self._sol_penalty and resample_loops > 0:
            log_msg = (
                "{} resamples required to generate {} " "solutions"
            ).format(resample_loops, needed_solutions)
            module_logger.info(log_msg)

        if self._n_record_resample > 0:
            if resample_loops > self._max_resample_loops:
                self._max_resample_loops = resample_loops

            self._n_record_resample -= 1

            if self._n_record_resample == 0:
                log_msg = (
                    "Setting maximum resamples to {} following " "iteration {}"
                ).format(self._max_resample_loops, self.es.countiter + 1)
                module_logger.info(log_msg)

        categories = ["default"] * len(run_descaled_solutions)
        all_n_evals = [n_evals] * len(run_descaled_solutions)

        n_extra = 0
        run_solutions_extra = []
        run_descaled_solutions_extra = []
        categories_extra = []
        all_n_evals_extra = []

        if scaled_solutions_extra is not None:
            descaled_solutions_extra = self.get_descaled_solutions(
                scaled_solutions_extra
            )

            for sol, des_sol in zip(
                scaled_solutions_extra, descaled_solutions_extra
            ):
                if self.evaluator.pre_constraints_hook(*des_sol):
                    final_solutions_extra.append(sol)
                    final_costs_extra.append(np.nan)
                else:
                    run_solutions_extra.append(sol)
                    run_descaled_solutions_extra.append(des_sol)
                    categories_extra.append("extra")
                    n_extra += 1

            all_n_evals_extra = [n_evals_extra] * n_extra

        if n_extra + n_default == 0:
            return result_default, result_extra

        run_solutions = run_solutions_extra + run_solutions
        run_descaled_solutions = (
            run_descaled_solutions_extra + run_descaled_solutions
        )
        categories = categories_extra + categories
        all_n_evals = all_n_evals_extra + all_n_evals

        assert (
            len(run_solutions)
            == len(run_descaled_solutions)
            == len(categories)
            == len(all_n_evals)
        )

        # Reuse previous costs if the function is not noisy
        if self.nh is None:
            run_idxs, match_dict = _get_match_process(
                run_descaled_solutions, categories, run_solutions
            )

        else:
            run_idxs = range(len(run_solutions))
            match_dict = {}

        result_queue = queue.Queue()

        for i in range(n_extra + n_default):
            if i not in run_idxs:
                continue

            descaled_sol = run_descaled_solutions[i]
            local_n_evals = all_n_evals[i]
            category = categories[i]
            sol = run_solutions[i]

            item: list[Any] = [result_queue]
            item.append(local_n_evals)
            item.append(descaled_sol)
            item.extend([i, category, sol])

            self._thread_queue.put(item)

        store_results = {}
        min_i = 0
        next_i = n_extra + n_default
        results_found = 0

        while results_found < n_extra + n_default:
            cost, i, category, sol = result_queue.get()

            if i in match_dict:
                all_i = [(i, category, sol)] + match_dict[i]
                all_cost = [cost] * (1 + len(match_dict[i]))
            else:
                all_i = [(i, category, sol)]
                all_cost = [cost]

            for k, kcost in zip(all_i, all_cost):
                i, category, sol = k
                store_results[i] = (category, sol, kcost)

            for check_i in range(min_i, next_i):
                if check_i not in store_results:
                    continue
                if check_i == min_i:
                    min_i += 1

                result = store_results.pop(check_i)

                if result[0] == "extra":
                    extra_cost = result[2]
                    if self._maximise:
                        extra_cost *= -1

                    final_solutions_extra.append(result[1])
                    final_costs_extra.append(extra_cost)
                    results_found += 1
                    continue

                assert result[0] == "default"

                sol = result[1]
                sol_cost = result[2]

                if np.isnan(sol_cost):
                    if next_i == len(run_descaled_solutions):
                        log_msg = (
                            "Maximum number of retry solutions "
                            "reached. Applying penalty value."
                        )
                        module_logger.info(log_msg)

                        sol_cost = self._get_penalty([sol])[0]

                    else:
                        if next_i not in run_idxs:
                            next_i += 1
                            continue

                        run_descaled_sol = run_descaled_solutions[next_i]
                        run_category = categories[next_i]
                        run_sol = run_solutions[next_i]

                        item = [result_queue]
                        item.append(n_evals)
                        item.append(run_descaled_sol)
                        item.extend([next_i, run_category, run_sol])

                        self._thread_queue.put(item)

                        next_i += 1
                        continue

                if self._maximise:
                    sol_cost *= -1
                final_solutions.append(sol)
                final_costs.append(sol_cost)

                results_found += 1

        self._thread_queue.join()

        return result_default, result_extra

    def get_descaled_solutions(self, scaled_solutions):
        descaled_solutions = []

        for solution in scaled_solutions:
            new_solution = [
                scaler.inverse(x)
                for x, scaler in zip(solution, self._scaled_vars)
            ]
            new_solution = [
                op(x) if op is not None else x
                for x, op in zip(new_solution, self._x_ops)
            ]

            descaled_solutions.append(new_solution)

        if self._fixed_index_map is not None:
            ordered_index_map = OrderedDict(
                sorted(self._fixed_index_map.items(), key=lambda t: t[0])
            )

            for solution in descaled_solutions:
                for idx, val in ordered_index_map.items():  # pylint: disable=no-member
                    solution.insert(idx, val)

        return descaled_solutions

    def _get_penalty(self, sols):
        if self._sol_feasible is None:
            if self.es.countiter == 0:
                err_msg = (
                    "There are no feasible solutions to "
                    "use for penalty calculation. Problem "
                    "is likely ill-posed."
                )
                raise RuntimeError(err_msg)

            self._sol_feasible = self.es.best.x.copy()

        costs = [
            self._base_penalty + norm(sol - self._sol_feasible) for sol in sols
        ]

        return costs

    def get_max_resample_factor(self):
        if self._n_record_resample > 0:
            return "auto{}".format(self._n_record_resample)

        return self._max_resample_loops


def init_evolution_strategy(
    x0,
    low_bound,
    high_bound,
    integer_variables=None,
    max_simulations=None,
    popsize=None,
    timeout=None,
    tolfun=None,
    logging_directory=None,
):
    opts = {"bounds": [low_bound, high_bound]}  # ,
    #            'verbose': -3}

    if integer_variables is not None:
        opts["integer_variables"] = integer_variables

    if max_simulations is not None:
        opts["maxfevals"] = max_simulations

    if popsize is not None:
        opts["popsize"] = popsize

    if timeout is not None:
        opts["timeout"] = timeout

    if tolfun is not None:
        opts["tolfun"] = tolfun

    if logging_directory is not None:
        opts["verb_filenameprefix"] = logging_directory + os.sep

    es = SafeCMAEvolutionStrategy(x0, NormScaler.sigma, opts)

    return es


def dump_outputs(worker_directory, es, evaluator, nh=None):
    counter_dict = evaluator.get_counter_search_dict()

    es_path = os.path.join(worker_directory, "saved-cma-object.pkl")
    counter_dict_path = os.path.join(
        worker_directory, "saved-counter-search-dict.pkl"
    )

    pickle.dump(es, open(es_path, "wb"), -1)
    pickle.dump(counter_dict, open(counter_dict_path, "wb"), -1)

    if nh is None:
        return

    nh_path = os.path.join(worker_directory, "saved-nh-object.pkl")
    pickle.dump(nh, open(nh_path, "wb"), -1)


def load_outputs(worker_directory):
    es_path = os.path.join(worker_directory, "saved-cma-object.pkl")
    nh_path = os.path.join(worker_directory, "saved-nh-object.pkl")
    counter_dict_path = os.path.join(
        worker_directory, "saved-counter-search-dict.pkl"
    )

    es = pickle.load(open(es_path, "rb"))
    counter_dict = pickle.load(open(counter_dict_path, "rb"))

    if os.path.isfile(nh_path):
        nh = pickle.load(open(nh_path, "rb"))
    else:
        nh = None

    return es, counter_dict, nh


def set_TimedRotatingFileHandler_rollover(timeout=None):
    # If theres no timeout choose a big number
    if timeout is None:
        timeout = sys.maxsize

    logger = logging.Logger.manager.loggerDict["dtocean_core"]
    assert isinstance(logger, logging.Logger)

    for handler in logger.handlers:
        if isinstance(handler, handlers.TimedRotatingFileHandler):
            handler.interval = timeout
            handler.rolloverAt = handler.computeRollover(int(time.time()))


def _get_scale_factor(range_min, range_max, x0, sigma, n_sigmas):
    if x0 < range_min or x0 > range_max:
        err_str = "x0 must lie between range_min and range_max"
        raise ValueError(err_str)

    if sigma <= 0:
        err_str = "sigma must be positive"
        raise ValueError(err_str)

    if n_sigmas % 1 != 0 or int(n_sigmas) <= 0:
        err_str = "n_sigmas must be a positive whole number"
        raise ValueError(err_str)

    max_half_range = max(range_max - x0, x0 - range_min)
    half_scaled_range = sigma * int(n_sigmas)

    return half_scaled_range / max_half_range


def _get_match_process(values, *args):
    def expand_args(x, args):
        if not args:
            return x

        result = [x]

        for arg in args:
            result.append(arg[x])

        return tuple(result)

    match_dict = {}
    all_matches = []

    for i in range(len(values) - 1):
        if i in all_matches:
            continue

        key = i
        base = values[i]
        match_list = []

        for j in range(i + 1, len(values)):
            test = values[j]

            if all([x == y for x, y in zip(base, test)]):
                match_list.append(j)

        all_matches.extend(match_list)

        if match_list:
            match_list = [expand_args(k, args) for k in match_list]
            match_dict[key] = match_list

    process_set = set(range(len(values))) - set(all_matches)

    return list(process_set), match_dict


def _log_exception(e, flag):
    module_logger.debug(flag)
    module_logger.debug(e)

    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg_strs = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg_str = "".join(msg_strs)
    module_logger.debug(msg_str)
