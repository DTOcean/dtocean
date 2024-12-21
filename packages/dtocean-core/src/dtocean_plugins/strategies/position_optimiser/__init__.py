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

import glob
import logging
import numbers
import os
import re
from collections import namedtuple
from copy import deepcopy
from typing import Any

import numpy as np
import yaml
from natsort import natsorted
from ruamel.yaml import YAML

from dtocean_core.core import Core
from dtocean_core.extensions import ToolManager
from dtocean_core.menu import ModuleMenu
from dtocean_core.utils import optimiser as opt
from dtocean_core.utils.files import remove_retry
from dtocean_core.utils.maths import bearing_to_radians

from .iterator import get_positioner

# Set up logging
module_logger = logging.getLogger(__name__)

# Get this directory
THIS_DIR = os.path.dirname(os.path.realpath(__file__))


PositionParams = namedtuple(
    "PositionParams",
    [
        "grid_orientation",
        "delta_row",
        "delta_col",
        "n_nodes",
        "t1",
        "t2",
        "dev_per_string",
        "n_evals",
        "cost",
        "flag",
        "prj_file_path",
        "yaml_file_path",
    ],
)


class PositionCounter(opt.Counter):
    def _set_params(
        self,
        worker_project_path,  # pylint: disable=arguments-differ
        worker_results_path,
        cost,
        flag,
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
        n_evals,
    ):
        """Build a params (probably namedtuple) object to record evaluation."""

        params = PositionParams(
            grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string,
            n_evals,
            cost,
            flag,
            worker_project_path,
            worker_results_path,
        )

        return params

    def _get_cost(self, *args):  # pylint: disable=arguments-differ
        """Return cost if parameters in params object match input args, else
        return None."""

        return None


class PositionEvaluator(opt.Evaluator):
    def __init__(
        self,
        core,
        base_project,
        root_project_base_name,
        worker_directory,
        objective_var,
        restart=False,
        clean_existing_dir=False,
        violation_log_name="violations.txt",
    ):
        super(PositionEvaluator, self).__init__(
            core,
            base_project,
            root_project_base_name,
            worker_directory,
            restart,
            clean_existing_dir,
        )

        self._tool_man = ToolManager()
        self._positioner = get_positioner(self._core, self._base_project)
        self._violation_log_path = os.path.join(
            self._worker_directory, violation_log_name
        )
        self._objective_var = None

        self._set_objective_var(objective_var)

    def _set_objective_var(self, objective_var):
        sim = self._base_project.get_simulation(title="Default")

        if objective_var not in sim.get_output_ids():
            err_str = (
                "Objective {} is not an output of the base project's "
                "default simulation"
            ).format(objective_var)
            raise RuntimeError(err_str)

        self._objective_var = objective_var

    def _init_counter(self):
        return PositionCounter()

    def _get_popen_args(self, worker_project_path, n_evals, *args):
        "Return the arguments to create a new process thread using Popen"

        popen_args = ["_dtocean-optim-pos", worker_project_path]
        popen_args += [str(x) for x in args[:6]]

        if args[6] is not None:
            popen_args.extend(["--dev_per_string", "{:d}".format(int(args[6]))])

        if n_evals is not None:
            popen_args.extend(["--n_evals", "{:d}".format(int(n_evals))])

        return popen_args

    def _get_worker_results(self, evaluation):
        """Return the results for the given evaluation as a dictionary that
        must include the key "cost". For constraint violation the cost key
        should be set to np.nan"""

        worker_file_root_path = "{}_{}".format(
            self._root_project_base_name, evaluation
        )
        worker_results_name = "{}.yaml".format(worker_file_root_path)
        worker_results_path = os.path.join(
            self._worker_directory, worker_results_name
        )

        with open(worker_results_path, "r") as stream:
            results = yaml.load(stream, Loader=yaml.FullLoader)

        flag = results["status"]
        cost = np.nan

        if flag == "Exception":
            details = results["error"]
            module_logger.debug(flag)
            module_logger.debug(details)

        elif flag == "Success":
            cost = results["results"][self._objective_var]

            if not isinstance(cost, numbers.Number):
                warn_msg = (
                    "Detected cost is not a number, returning "
                    "np.nan. Detected type is "
                    "'{}'"
                ).format(type(cost).__name__)
                module_logger.warning(warn_msg)

        else:
            raise RuntimeError("Unrecognised flag '{}'".format(flag))

        results["worker_results_path"] = worker_results_path
        results["cost"] = cost

        return results

    def _set_counter_params(
        self, evaluation, worker_project_path, results, flag, n_evals, *args
    ):
        """Update the counter object with new data."""

        args += (n_evals,)
        worker_results_path = None
        cost = np.nan

        if results is not None:
            worker_results_path = results["worker_results_path"]
            cost = results["cost"]

        self._counter.set_params(
            evaluation,
            worker_project_path,
            worker_results_path,
            cost,
            flag,
            *args,
        )

    def pre_constraints_hook(self, *args):
        (grid_orientation, delta_row, delta_col, n_nodes, t1, t2, _) = args

        beta = 90 * np.pi / 180
        psi = 0 * np.pi / 180

        try:
            positions = self._positioner(
                grid_orientation,
                delta_row,
                delta_col,
                beta,
                psi,
                t1,
                t2,
                int(n_nodes),
            )

        except RuntimeError as e:
            details = str(e)

            if (
                "Expected number of nodes not found" in details
                or "lies outside of valid domain" in details
            ):
                self._log_violation(details, *args)
                return True

            raise RuntimeError(e)

        spacing_tool = self._tool_man.get_tool("Device Minimum Spacing Check")
        spacing_tool.configure(positions)

        try:
            self._tool_man.execute_tool(
                self._core, self._base_project, spacing_tool
            )

        except RuntimeError as e:
            details = str(e)

            if "Violation of the minimum distance constraint" in details:
                self._log_violation(details, *args)
                return True

            raise RuntimeError(e)

        return False

    def _cleanup_hook(self, worker_project_path, flag, lines):  # pylint: disable=arguments-differ,unused-argument
        """Hook to clean up simulation files as required"""
        remove_retry(worker_project_path)

    def _log_violation(self, details, *args):
        largs = [str(arg) for arg in args]
        largs.insert(0, details)
        log_str = ", ".join(largs) + "\n"

        with open(self._violation_log_path, "a") as f:
            f.write(log_str)


class PositionOptimiser:
    def __init__(
        self,
        core=None,
        config_fname="config.yaml",
        default_project_fname="worker.prj",
    ):
        if core is None:
            core = Core()

        self.stop = False
        self._core = core
        self._config_fname = config_fname
        self._default_project_fname = default_project_fname
        self._dump_config = False
        self._worker_directory = None
        self._cma_main = None

    def start(self, config, project=None):
        module_logger.info("Beginning position optimisation")

        self.stop = False
        self._worker_directory = config["worker_dir"]

        base_penalty = config["base_penalty"]
        n_threads = config["n_threads"]
        results_params = config["results_params"]
        objective = config["objective"]

        # Defaults
        clean_existing_dir = False
        maximise = False
        max_simulations = None
        popsize = None
        timeout = None
        tolfun = None
        min_evals = None
        max_evals = 128
        max_resample_factor = "auto2"
        max_resample_loop_factor = None
        auto_resample_iterations = None

        if _is_option_set(config, "clean_existing_dir"):
            clean_existing_dir = config["clean_existing_dir"]

        if _is_option_set(config, "maximise"):
            maximise = config["maximise"]

        if _is_option_set(config, "max_simulations"):
            max_simulations = config["max_simulations"]

        if _is_option_set(config, "popsize"):
            popsize = config["popsize"]

        if _is_option_set(config, "timeout"):
            timeout = config["timeout"]

        if _is_option_set(config, "tolfun"):
            tolfun = config["tolfun"]

        if _is_option_set(config, "min_evals"):
            min_evals = config["min_evals"]

        if _is_option_set(config, "max_evals"):
            max_evals = config["max_evals"]

        if _is_option_set(config, "max_resample_factor"):
            max_resample_factor = config["max_resample_factor"]

        # Check for use of auto setting
        auto_match = re.match(r"auto([0-9]+)", str(max_resample_factor), re.I)

        if auto_match:
            items = auto_match.groups()
            auto_resample_iterations = int(items[0])
            self._dump_config = True
        else:
            max_resample_loop_factor = max_resample_factor
            self._dump_config = False

        if project is None:
            root_project_path = config["root_project_path"]
            project = self._core.load_project(root_project_path)
            archive_project = False
        else:
            root_project_path = os.path.join(
                self._worker_directory, self._default_project_fname
            )
            config["root_project_path"] = root_project_path
            archive_project = True

        _, root_project_name = os.path.split(root_project_path)
        root_project_base_name, _ = os.path.splitext(root_project_name)

        control_dict = _get_param_control(self._core, project, config)

        ranges = control_dict["ranges"]
        x0s = control_dict["x0s"]

        scaled_vars = [
            opt.NormScaler(x[0], x[1], y) for x, y in zip(ranges, x0s)
        ]
        x0 = [scaled.x0 for scaled in scaled_vars]
        low_bound = [
            scaler.scaled(x[0]) for x, scaler in zip(ranges, scaled_vars)
        ]
        high_bound = [
            scaler.scaled(x[1]) for x, scaler in zip(ranges, scaled_vars)
        ]

        integer_variables = control_dict["integer_variables"]
        if not integer_variables:
            integer_variables = None

        es = opt.init_evolution_strategy(
            x0,
            low_bound,
            high_bound,
            integer_variables=integer_variables,
            max_simulations=max_simulations,
            popsize=popsize,
            timeout=timeout,
            tolfun=tolfun,
            logging_directory=self._worker_directory,
        )

        if min_evals is None:
            complex_stats = ["interval_lower", "interval_upper", "mode"]
            simple_stats = ["mean"]

            if any(word in objective for word in complex_stats):
                min_evals = 4
            elif any(word in objective for word in simple_stats):
                min_evals = 1

        if min_evals is None or min_evals < 1:
            min_evals = 1
        if max_evals < min_evals:
            max_evals = min_evals

        menu = ModuleMenu()
        active_modules = menu.get_active(self._core, project)

        if (
            "Operations and Maintenance" in active_modules
            and min_evals is not None
        ):
            nh = opt.NoiseHandler(
                es.N, maxevals=[min_evals, min_evals, max_evals]
            )
        else:
            nh = None

        evaluator = PositionEvaluator(
            self._core,
            project,
            root_project_base_name,
            self._worker_directory,
            objective,
            clean_existing_dir=clean_existing_dir,
        )

        # Store the base project for potential restart (if necessary)
        if archive_project:
            self._core.dump_project(project, root_project_path)

        # Store copy of config for potential restart
        config_path = os.path.join(self._worker_directory, self._config_fname)
        safe_config = deepcopy(config)
        safe_config["clean_existing_dir"] = None
        dump_config(config_path, config)

        # Store the es object and counter search dict for potential restart
        opt.dump_outputs(self._worker_directory, es, evaluator, nh)

        # Write the results params control file for workers
        results_params = list(set(results_params).union([objective]))
        _dump_results_control(results_params, self._worker_directory)

        self._cma_main = opt.Main(
            es,
            evaluator,
            scaled_vars,
            control_dict["x_ops"],
            nh=nh,
            fixed_index_map=control_dict["fixed_params"],
            base_penalty=base_penalty,
            num_threads=n_threads,
            maximise=maximise,
            max_resample_loop_factor=max_resample_loop_factor,
            auto_resample_iterations=auto_resample_iterations,
        )

        # Disable logging rollovers
        opt.set_TimedRotatingFileHandler_rollover(timeout)

    def is_restart(self, worker_directory):
        config_path = os.path.join(worker_directory, self._config_fname)

        try:
            config = load_config(config_path)
            opt.load_outputs(worker_directory)
        except:  # pylint: disable=bare-except  # noqa: E722
            log_msg = "Can not find state of previous optimisation"
            module_logger.debug(log_msg, exc_info=True)
            return False

        required_keys = set(
            ["root_project_path", "base_penalty", "n_threads", "objective"]
        )

        if not set(config) >= required_keys:
            missing = [str(key) for key in required_keys - set(config)]
            missing_line = ", ".join(missing)
            log_str = (
                "Required keys '{}' are missing from the config " "file"
            ).format(missing_line)
            module_logger.debug(log_str)

            return False

        return True

    def restart(self, worker_directory):
        if not self.is_restart(worker_directory):
            log_str = "Restarting position optimisation not possible"
            module_logger.warning(log_str)
            return

        module_logger.info("Restart position optimisation")

        self._worker_directory = worker_directory
        self.stop = False

        # Reload the config in the worker directory
        config_path = os.path.join(self._worker_directory, self._config_fname)
        config = load_config(config_path)

        # Reload outputs
        es, counter_dict, nh = opt.load_outputs(self._worker_directory)

        root_project_path = config["root_project_path"]
        base_penalty = config["base_penalty"]
        n_threads = config["n_threads"]
        objective = config["objective"]

        # Defaults
        maximise = False
        timeout = None
        max_resample_loop_factor = None
        auto_resample_iterations = None

        if _is_option_set(config, "maximise"):
            maximise = config["maximise"]

        if _is_option_set(config, "timeout"):
            timeout = config["timeout"]

        if _is_option_set(config, "max_resample_factor"):
            max_resample_factor = config["max_resample_factor"]

            # Check for use of auto setting
            auto_match = re.match(
                r"auto([0-9]+)", str(max_resample_factor), re.I
            )

            if auto_match:
                items = auto_match.groups()
                auto_resample_iterations = int(items[0])
                self._dump_config = True
            else:
                max_resample_loop_factor = max_resample_factor
                self._dump_config = False

        # Remove files above last recorded iteration
        if counter_dict:
            last_iter = max(counter_dict)
        else:
            last_iter = -1

        _, root_project_name = os.path.split(root_project_path)
        root_project_base_name, _ = os.path.splitext(root_project_name)

        yaml_pattern = "{}_*.yaml".format(root_project_base_name)
        prj_pattern = "{}_*.prj".format(root_project_base_name)

        _clean_numbered_files_above(
            self._worker_directory, yaml_pattern, last_iter
        )
        _clean_numbered_files_above(
            self._worker_directory, prj_pattern, last_iter
        )

        project = self._core.load_project(root_project_path)

        _, root_project_name = os.path.split(root_project_path)
        root_project_base_name, _ = os.path.splitext(root_project_name)

        control_dict = _get_param_control(self._core, project, config)

        ranges = control_dict["ranges"]
        x0s = control_dict["x0s"]

        scaled_vars = [
            opt.NormScaler(x[0], x[1], y) for x, y in zip(ranges, x0s)
        ]

        evaluator = PositionEvaluator(
            self._core,
            project,
            root_project_base_name,
            self._worker_directory,
            objective,
            restart=True,
        )

        self._cma_main = opt.Main(
            es,
            evaluator,
            scaled_vars,
            control_dict["x_ops"],
            nh=nh,
            fixed_index_map=control_dict["fixed_params"],
            base_penalty=base_penalty,
            num_threads=n_threads,
            maximise=maximise,
            max_resample_loop_factor=max_resample_loop_factor,
            auto_resample_iterations=auto_resample_iterations,
        )

        # Disable logging rollovers
        opt.set_TimedRotatingFileHandler_rollover(timeout)

    def next(self):
        if self._cma_main is None:
            err_msg = (
                "Optimiser is not configured. Call 'start' or "
                "'restart' first"
            )
            raise RuntimeError(err_msg)

        if self._cma_main.stop:
            module_logger.info("Position optimisation complete")
            self.stop = True
            return

        self._cma_main.next()
        opt.dump_outputs(
            self._worker_directory,
            self._cma_main.es,
            self._cma_main.evaluator,
            self._cma_main.nh,
        )

        if not self._dump_config:
            return

        max_resample_factor = self._cma_main.get_max_resample_factor()

        assert self._worker_directory is not None
        config_path = os.path.join(self._worker_directory, self._config_fname)
        config = load_config(config_path)
        config["max_resample_factor"] = self._cma_main.max_resample_loops
        dump_config(config_path, config)

        if "auto" not in str(max_resample_factor):
            self._dump_config = False

    def get_es(self):
        if self._cma_main is None:
            return None
        return self._cma_main.es

    def get_nh(self):
        if self._cma_main is None:
            return None
        return self._cma_main.nh


def _get_param_control(core, project, config):
    ranges = []
    x0s = []
    x_ops = []
    integer_variables = []
    fixed_params = {}

    result: dict[str, Any] = {
        "ranges": ranges,
        "x0s": x0s,
        "x_ops": x_ops,
        "integer_variables": integer_variables,
    }

    param_names = [
        "grid_orientation",
        "delta_row",
        "delta_col",
        "n_nodes",
        "t1",
        "t2",
        "dev_per_string",
    ]

    optional_map = {"dev_per_string": None}
    conversions = {"grid_orientation": bearing_to_radians}

    for i, param_name in enumerate(param_names):
        if param_name not in config["parameters"]:
            if param_name in optional_map:
                fixed_value = optional_map[param_name]

                if param_name in conversions:
                    fixed_value = conversions[param_name](fixed_value)

                fixed_params[i] = fixed_value

                continue

            else:
                err_msg = (
                    "Parameter '{}' must be included in the "
                    "'parameters' section of the "
                    "configuration"
                ).format(param_name)
                raise KeyError(err_msg)

        parameter = config["parameters"][param_name]

        if "fixed" in parameter:
            fixed_value = parameter["fixed"]

            if param_name in conversions:
                fixed_value = conversions[param_name](fixed_value)

            fixed_params[i] = fixed_value

            continue

        crange = parameter["range"]

        if crange["type"] == "fixed":
            prange = _get_range_fixed(crange["min"], crange["max"])
        elif crange["type"] == "multiplier":
            prange = _get_range_multiplier(
                core,
                project,
                crange["variable"],
                crange["min_multiplier"],
                crange["max_multiplier"],
            )

        if param_name in conversions:
            prange = [conversions[param_name](x) for x in prange]
            prange = sorted(prange)

        if "integer" in parameter and parameter["integer"]:
            x_op = np.floor
            integer_variables.append(i - len(fixed_params))
        else:
            x_op = None

        if "x0" in parameter:
            x0 = parameter["x0"]
            if param_name in conversions:
                x0 = conversions[param_name](x0)
        else:
            x0 = None

        ranges.append(prange)
        x0s.append(x0)
        x_ops.append(x_op)

    if not fixed_params:
        fixed_params = None

    result["fixed_params"] = fixed_params

    return result


def _get_range_fixed(rmin, rmax):
    return (rmin, rmax)


def _get_range_multiplier(core, project, variable, mmin, mmax):
    value = core.get_data_value(project, variable)
    return (mmin * value, mmax * value)


def _dump_results_control(
    params, worker_directory, fname="results_control.txt"
):
    dump_str = "\n".join(params)
    fpath = os.path.join(worker_directory, fname)

    with open(fpath, "w") as f:
        f.write(dump_str)


def load_config(config_path):
    ruyaml = YAML()

    with open(config_path, "r") as stream:
        config = ruyaml.load(stream)

    return config


def dump_config(config_path, config=None, use_template=True):
    if config is None:
        config = {}

    if use_template:
        config_template = _load_config_template()

        # Strip any keys not in the template
        for key in config.keys():
            if key not in config_template:
                config.pop(key)

        config_template.update(config)

    else:
        config_template = config

    ruyaml = YAML()

    with open(config_path, "w") as stream:
        ruyaml.dump(config_template, stream)


def _load_config_template(config_name="config.yaml"):
    config_path = os.path.join(THIS_DIR, config_name)
    config = load_config(config_path)

    return config


def _clean_numbered_files_above(directory, search_pattern, highest_valid):
    search_str = os.path.join(directory, search_pattern)
    file_paths = natsorted(glob.glob(search_str))
    file_numbers = map(_extract_number, map(os.path.basename, file_paths))

    paths_to_clean = [
        x for x, y in zip(file_paths, file_numbers) if y > highest_valid
    ]

    for path in paths_to_clean:
        remove_retry(path)


def _extract_number(f):
    s = re.findall(r"(\d+).", f)
    return int(s[0]) if s else -1


def _is_option_set(config, key):
    result = key in config and config[key] is not None
    return result
    return result
