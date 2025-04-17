# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Vincenzo Nava
#    Copyright (C) 2017-2024 Mathew Topper
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

import itertools
import logging
import math
import random

import pandas as pd

from .base import Strategy
from .basic import BasicStrategy

# Set up logging
module_logger = logging.getLogger(__name__)


class MultiSensitivity(Strategy):
    """A multi-variable sensitivity study  over a given range of
    values, adjusted before execution of a chosen module."""

    @classmethod
    def get_name(cls):
        return "Multi Sensitivity"

    @classmethod
    def count_selections(cls, inputs_df, subsp_ratio):
        sorted_df = inputs_df.copy()

        # Create a multi-index & get selections
        sorted_df = sorted_df.set_index(["Module", "Variable"])
        selections = cls._get_selections(sorted_df, subsp_ratio)

        return len(selections)

    def configure(self, inputs_df, subspacing_ratio, skip_errors=True):
        config_dict = {
            "inputs_df": inputs_df,
            "subsp_ratio": subspacing_ratio,
            "skip_errors": skip_errors,
        }

        self.set_config(config_dict)

    def get_variables(self):
        if self._config is None:
            return None

        df = self._config["inputs_df"]
        result = df["Variable"].values

        return result

    def execute(self, core, project):
        # Test for Nones
        if (
            self._config is None
            or self._config["inputs_df"] is None
            or self._config["subsp_ratio"] is None
        ):
            errStr = (
                "The configuration values are None. Have you called "
                "the configure method?"
            )
            raise ValueError(errStr)

        inputs_df = self._config["inputs_df"]
        subsp_ratio = self._config["subsp_ratio"]

        # Check subspacing ratio
        if subsp_ratio is None or subsp_ratio > 1:
            subsp_ratio = 1.0
        elif subsp_ratio < 0:
            subsp_ratio = 0.0
        else:
            subsp_ratio = subsp_ratio

        # Sort the input frame and bulld the selection pool
        sorted_df = self._get_sorted_inputs(core, project, inputs_df)
        selections = self._get_selections(sorted_df, subsp_ratio)

        # Reset the index on the dataframe
        sorted_df = sorted_df.reset_index()

        # Get a branch to the first module to appear
        module_0 = sorted_df["Module"][0]
        mod_branch = self._tree.get_branch(core, project, module_0)

        # Check the project is active and record the simulation number
        sim_index = project.get_active_index()

        if sim_index is None:
            errStr = "Project has not been activated."
            raise RuntimeError(errStr)

        sim_keys = []
        sim_frames = []

        for i, selection_case in enumerate(selections[:-1]):
            # Create a dummy frame for building the simulations
            sim_df = sorted_df.copy()

            # Set the required values for the run
            sim_title = "Simulation {}".format(i)
            sim_df["Values"] = selection_case

            # Execute the simulation
            success_flag = self._safe_exe(core, project, sim_df, sim_title)

            # Create a new simulation clone and move to the required branch
            if success_flag:
                self.add_simulation_title(sim_title)
                sim_keys.append(sim_title)
                sim_frames.append(sim_df)

                core.clone_simulation(project)
                sim_index = project.get_active_index()

            mod_branch.reset(core, project)

        # Create a dummy frame for building the simulations
        sim_df = sorted_df.copy()

        # Complete the last simulation
        sim_title = "Simulation {}".format(i + 1)
        sim_df["Values"] = selections[-1]

        # Execute the simulation
        success_flag = self._safe_exe(core, project, sim_df, sim_title)

        if success_flag:
            self.add_simulation_title(sim_title)
            sim_keys.append(sim_title)
            sim_frames.append(sim_df)

        # Build the simulation details frame
        self.sim_details = pd.concat(sim_frames, keys=sim_keys)

    def _get_title_str(self, meta, value):
        title_str = "{} = {}".format(meta.title, value)

        if meta.units is not None:
            title_str = "{} ({})".format(title_str, meta.units[0])

        return title_str

    def _get_sorted_inputs(self, core, project, inputs_df):
        # Categorise module column by available modules
        list_modules = self._module_menu.get_available(core, project)

        sorted_df = inputs_df.copy()
        sorted_df["Module"] = pd.Categorical(sorted_df["Module"], list_modules)

        # Create a multi-index & sort
        sorted_df = sorted_df.set_index(["Module", "Variable"])
        sorted_df = sorted_df.sort_index(level=0)

        return sorted_df

    @classmethod
    def _get_selections(cls, sorted_df, subsp_ratio):
        # Generate simulation pool and selection
        values = sorted_df["Values"].tolist()
        pool = list(itertools.product(*values))

        pool_size = len(pool)
        number_samples = math.ceil(subsp_ratio * pool_size)

        random_selection = random.sample(
            range(0, pool_size), int(number_samples)
        )
        selections = [pool[x] for x in random_selection]

        return selections

    def _safe_exe(self, core, project, sim_df: pd.DataFrame, sim_title):
        success_flag = True

        assert self._config is not None
        if self._config["skip_errors"]:
            try:
                self._run_simulation(core, project, sim_df, sim_title)

            except (KeyboardInterrupt, SystemExit) as e:
                raise e

            except BaseException as e:
                msg = ("Passing exception '{}' for simulation " "{}").format(
                    type(e).__name__, sim_title
                )
                module_logger.exception(msg)

                success_flag = False

        else:
            # Execute the simulation
            self._run_simulation(core, project, sim_df, sim_title)

        return success_flag

    def _run_simulation(self, core, project, table_cs: pd.DataFrame, sim_title):
        # Set the simulation title
        project.set_simulation_title(sim_title)

        module_logger.info("Executing simulation '{}'".format(sim_title))

        # Set each variable
        for index, row in table_cs.iterrows():
            module = row["Module"]
            variable = row["Variable"]
            value = row["Values"]

            # Pick up the branch
            if module not in self._module_menu.get_available(core, project):
                errStr = "Module {} does not exist".format(module)
                raise ValueError(errStr)

            if module not in self._module_menu.get_active(core, project):
                errStr = "Module {} has not been activated".format(module)
                raise ValueError(errStr)

            mod_branch = self._tree.get_branch(core, project, module)

            # Check for existance of the variable
            module_inputs = mod_branch.get_input_status(core, project)

            if variable not in module_inputs.keys():
                msgStr = (
                    "Variable {} is not an input to module " "{}."
                ).format(variable, module)
                raise ValueError(msgStr)

            multi_var = mod_branch.get_input_variable(core, project, variable)

            assert multi_var is not None
            multi_var.set_raw_interface(core, value)
            multi_var.read(core, project)

        # Borrow the Basic strategy
        basic = BasicStrategy()

        # Run the simulation
        basic.execute(core, project)
