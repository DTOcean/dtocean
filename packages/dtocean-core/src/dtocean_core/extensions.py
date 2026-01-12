#    Copyright (C) 2016-2024 Mathew Topper
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

import json
import logging
import os
from collections import OrderedDict
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colormaps
from mdo_engine.utilities.plugins import Plugin

import dtocean_plugins.strategies as strategies
import dtocean_plugins.tools as tools
from dtocean_core.core import Core, Project
from dtocean_plugins.strategies.base import Strategy
from dtocean_plugins.tools.base import Tool

from .menu import ModuleMenu

# Set up logging
module_logger = logging.getLogger(__name__)


class ExtensionManager(Plugin):
    """Extension framework discovery"""

    def __init__(self, module, cls_name):
        super(ExtensionManager, self).__init__()
        self._plugin_classes = self._discover_classes(module, cls_name)
        self._plugin_names = self._discover_names()

    def get_available(self) -> list[str]:
        plugin_names = self._plugin_names.keys()
        return list(plugin_names)

    def _get_plugin(self, plugin_name):
        if plugin_name not in self.get_available():
            errStr = ("Name {} is not a recognised " "plugin").format(
                plugin_name
            )
            raise KeyError(errStr)

        cls_name = self._plugin_names[plugin_name]
        ExtensionCls = self._plugin_classes[cls_name]
        ext_obj = ExtensionCls()

        return ext_obj

    def _discover_classes(self, module, cls_name):
        """Retrieve all of the available plugin classes"""

        log_msg = "Searching for {} classes".format(cls_name)
        module_logger.debug(log_msg)

        cls_map = self._discover_plugins(module, cls_name, warn_import=True)

        return cls_map

    def _discover_names(self):
        plugin_names = {}

        # Work through the interfaces
        for cls_name, cls_attr in self._plugin_classes.items():
            name = cls_attr.get_name()
            plugin_names[name] = cls_name

        return plugin_names


class StrategyManager(ExtensionManager):
    """Strategy discovery"""

    def __init__(self, module=strategies, cls_name="Strategy"):
        super(StrategyManager, self).__init__(module, cls_name)

        self._module_menu = ModuleMenu()

    def get_strategy(self, strategy_name) -> Strategy:
        if strategy_name not in self.get_available():
            errStr = ("Name {} is not a recognised " "strategy").format(
                strategy_name
            )
            raise KeyError(errStr)

        strategy_obj = self._get_plugin(strategy_name)

        return strategy_obj

    def get_level_values(
        self,
        core,
        project,
        var_id,
        strategy=None,
        sim_titles=None,
        scope="global",
    ):
        if scope not in ["global", "local"]:
            errStr = (
                "Argument 'scope' must have value 'global' or 'local', "
                "not {}"
            ).format(scope)
            raise ValueError(errStr)

        chosen_modules = self._module_menu.get_active(core, project)
        output_levels = [
            "{} {} output".format(x, scope).lower() for x in chosen_modules
        ]

        # Mask all the global and local output levels before getting the
        # required output level
        force_masks = ["local", "global"]

        if strategy is not None:
            sim_titles = strategy.get_simulation_record()

        if sim_titles is None:
            sim_indexes = range(len(project))
            sim_titles = [
                project.get_simulation_title(index=x) for x in sim_indexes
            ]

        else:
            sim_indexes = project.get_simulation_indexes(
                sim_titles, raise_if_missing=False
            )

        sim_levels = OrderedDict()

        for sim_title, sim_index in zip(sim_titles, sim_indexes):
            if sim_index is None:
                continue
            if sim_title is None:
                sim_title = sim_index

            level_values = core.get_level_values(
                project, var_id, output_levels, force_masks, sim_index=sim_index
            )

            sim_levels[sim_title] = level_values

        return sim_levels

    def get_level_values_df(
        self,
        core,
        project,
        var_id,
        strategy=None,
        sim_titles=None,
        scope="global",
    ):
        sim_levels = self.get_level_values(
            core, project, var_id, strategy, sim_titles, scope
        )
        done_levels = self._module_menu.get_completed(core, project)

        # Check the number of levels in each simulation
        sim_lengths = []

        for level_values in sim_levels.values():
            sim_lengths.append(len(level_values.values()))

        level_set = set(sim_lengths)

        if len(level_set) != 1:
            errStr = "The number of levels in each simulation is not equal"
            raise ValueError(errStr)

        sim_names = []
        level_lists = {k: [] for k in done_levels}

        for sim_key, level_values in sim_levels.items():
            sim_names.append(sim_key)

            for name in done_levels:
                find_levels = [
                    level for level in level_values if name.lower() in level
                ]

                if len(find_levels) > 1:
                    errStr = (
                        "More than one level matches module name " "{}"
                    ).format(name)
                    raise RuntimeError(errStr)

                if len(find_levels) == 0:
                    value = np.nan
                else:
                    found_level = find_levels[0]
                    value = level_values[found_level]

                level_lists[name].append(value)

        raw_dict = {"Simulation Name": sim_names}
        raw_dict.update(level_lists)

        raw_cols = ["Simulation Name"]
        raw_cols.extend(done_levels)

        df = pd.DataFrame(raw_dict)
        df = df[raw_cols]

        return df

    def get_level_values_plot(
        self,
        core,
        project,
        var_id,
        strategy=None,
        sim_titles=None,
        scope="global",
        legend_loc="upper left",
        max_lines=10,
    ):
        sim_levels = self.get_level_values(
            core, project, var_id, strategy, sim_titles, scope
        )
        done_levels = self._module_menu.get_completed(core, project)

        # Check the number of levels in each simulation
        sim_lengths = []

        for level_values in sim_levels.values():
            sim_lengths.append(len(level_values.values()))

        level_set = set(sim_lengths)

        if len(level_set) != 1:
            errStr = "The number of levels in each simulation is not equal"
            raise ValueError(errStr)

        fig = plt.figure()
        ax = fig.gca()

        if len(sim_levels) < 10:
            num_plots = len(sim_levels)
        else:
            num_plots = 10

        colormap = colormaps["Set1"]
        colors = [colormap(i) for i in np.linspace(0, 1, num_plots)]
        ax.set_prop_cycle(color=colors)

        x = range(len(done_levels))
        metadata = core.get_metadata(var_id)

        for i, (sim_key, level_values) in enumerate(sim_levels.items()):
            # Do not exceed the maximum number of lines
            if i == max_lines:
                break

            sane_values = []

            for name in done_levels:
                find_levels = [
                    level for level in level_values if name.lower() in level
                ]

                if len(find_levels) > 1:
                    errStr = (
                        "More than one level matches module name " "{}"
                    ).format(name)
                    raise RuntimeError(errStr)

                if len(find_levels) == 0:
                    value = np.nan
                else:
                    found_level = find_levels[0]
                    value = level_values[found_level]

                sane_values.append(value)

            plt.plot(x, sane_values, "-o", label=sim_key)
            plt.ylabel(metadata.title)

        plt.xticks(x, done_levels, rotation="vertical")

        y_label = metadata.title

        if metadata.units is not None:
            y_label = "{} ({})".format(y_label, metadata.units[0])

        plt.ylabel(y_label)
        plt.legend(loc=legend_loc)
        plt.title("Module Comparison ({} Scope)".format(scope.capitalize()))

        plt.tight_layout()

        return plt.gcf()

    def get_comparison_values(
        self,
        core,
        project,
        var_one_id,
        var_two_id,
        module=None,
        strategy=None,
        scope="global",
        sort=True,
    ):
        if scope not in ["global", "local"]:
            errStr = (
                "Argument 'scope' must have value 'global' or 'local', "
                "not {}"
            ).format(scope)
            raise ValueError(errStr)

        all_modules = self._module_menu.get_active(core, project)

        # Determine at which module to carry out the comparison
        if module is None:
            module = all_modules[-1]

        elif module not in all_modules:
            errStr = (
                "Module '{}' is not in the list of active " "modules"
            ).format(module)
            raise ValueError(errStr)

        output_level = "{} {} output".format(module, scope).lower()

        # If a strategy is given then just use its simulation indexes
        if strategy is None:
            sim_indexes = None
        else:
            sim_titles = strategy.get_simulation_record()
            sim_indexes = project.get_simulation_indexes(sim_titles)

        var_one_values = core.get_project_values(
            project,
            var_one_id,
            output_level,
            force_indexes=sim_indexes,
            allow_none=True,
        )

        var_two_values = core.get_project_values(
            project,
            var_two_id,
            output_level,
            force_indexes=sim_indexes,
            allow_none=True,
        )

        if var_one_values is None or var_two_values is None:
            x = []
            y = []
        else:
            x = [v for (n, v) in var_one_values]
            y = [v for (n, v) in var_two_values]

        if not sort:
            return x, y

        # Sort by the x value
        points = zip(x, y)
        sorted_points = sorted(points)
        new_x = [point[0] for point in sorted_points]
        new_y = [point[1] for point in sorted_points]

        return new_x, new_y

    def get_comparison_values_df(
        self,
        core,
        project,
        var_one_id,
        var_two_id,
        module=None,
        strategy=None,
        scope="global",
    ):
        # Get the comparison values
        x, y = self.get_comparison_values(
            core,
            project,
            var_one_id,
            var_two_id,
            module=module,
            strategy=strategy,
            scope=scope,
        )

        # Redetermine the module used
        if module is None:
            all_modules = self._module_menu.get_active(core, project)
            module = all_modules[-1]

        var_one_meta = core.get_metadata(var_one_id)
        var_two_meta = core.get_metadata(var_two_id)

        var_one_str = var_one_meta.title

        if var_one_meta.units is not None:
            var_one_str = "{} ({})".format(var_one_str, var_one_meta.units[0])

        var_two_str = var_two_meta.title

        if var_two_meta.units is not None:
            var_two_str = "{} ({})".format(var_two_str, var_two_meta.units[0])

        raw_dict = {var_one_str: x, var_two_str: y}
        raw_cols = [var_one_str, var_two_str]

        df = pd.DataFrame(raw_dict)
        df = df[raw_cols]

        return df

    def get_comparison_values_plot(
        self,
        core,
        project,
        var_one_id,
        var_two_id,
        module=None,
        strategy=None,
        scope="global",
    ):
        # Get the comparison values
        x, y = self.get_comparison_values(
            core,
            project,
            var_one_id,
            var_two_id,
            module=module,
            strategy=strategy,
            scope=scope,
        )

        # Convert any string x-values to a numerical range and add ticks later
        x_ticks = None

        if any(isinstance(i, str) for i in x):
            x_ticks = x
            x = range(len(x))

        plt.figure()

        # Redetermine the module used
        if module is None:
            all_modules = self._module_menu.get_active(core, project)
            module = all_modules[-1]

        var_one_meta = core.get_metadata(var_one_id)
        var_two_meta = core.get_metadata(var_two_id)

        var_one_str = var_one_meta.title

        if var_one_meta.units is not None:
            var_one_str = "{} ({})".format(var_one_str, var_one_meta.units[0])

        var_two_str = var_two_meta.title

        if var_two_meta.units is not None:
            var_two_str = "{} ({})".format(var_two_str, var_two_meta.units[0])

        if x_ticks is None:
            if len(x) == 1:
                plt.plot(x, y, marker="o", ls="")
            else:
                plt.plot(x, y)

        else:
            plt.bar(x, y, align="center")
            plt.xticks(x, x_ticks, rotation="vertical")

        plt.xlabel(var_one_str)
        plt.ylabel(var_two_str)
        plt.title(
            "Simulation Comparison at Module: {} " "({} Scope)".format(
                module, scope.capitalize()
            ),
            y=1.08,
        )

        plt.tight_layout()

        return plt.gcf()

    def dump_strategy(self, strategy: Strategy, dump_path):
        if os.path.splitext(dump_path)[1] != ".json":
            errStr = "Argument dump_path must be a file with .json extension"
            raise ValueError(errStr)

        stg_dict = self._get_dump_dict(strategy)

        with open(dump_path, "w") as fstream:
            json.dump(stg_dict, fstream)

    def load_strategy(self, load_path):
        # OK need to consider if we have a json file
        if not os.path.isfile(load_path) and ".json" not in load_path:
            errStr = "Argument load_path must be a file with .json extension"
            raise ValueError(errStr)

        # Load the strategy file
        with open(load_path, "r") as fstream:
            stg_dict = json.load(fstream)

        # Now deserialise the data
        new_strategy = self._set_load_dict(stg_dict)

        return new_strategy

    def _get_dump_dict(self, strategy: Strategy):
        # Now store the strategy information
        stg_name_str = strategy.get_name()

        stg_dict = {
            "name": stg_name_str,
            "sim_record": strategy._sim_record,
            "config": {
                "version": strategy.version,
                "data": strategy.dump_config(strategy._config),
            },
            "sim_details": strategy.dump_sim_details(strategy.sim_details),
            "version": 1,
        }

        return stg_dict

    def _set_load_dict(self, stg_dict):
        if stg_dict["version"] != 1:
            raise RuntimeError("Data version not recognised")

        # Now build the strategy
        new_strategy = self.get_strategy(stg_dict["name"])

        # Now deserialise the data
        sim_titles = stg_dict["sim_record"]
        new_strategy._sim_record = sim_titles
        new_strategy._config = new_strategy.load_config(
            stg_dict["config"]["data"],
            stg_dict["config"]["version"],
        )
        new_strategy.sim_details = new_strategy.load_sim_details(
            stg_dict["sim_details"]
        )

        return new_strategy


class ToolManager(ExtensionManager):
    """Tool discovery and execution"""

    def __init__(self, module=tools, cls_name="Tool"):
        super(ToolManager, self).__init__(module, cls_name)

    def get_tool(self, tool_name) -> Tool:
        if tool_name not in self.get_available():
            errStr = ("Name {} is not a recognised " "tool").format(tool_name)
            raise KeyError(errStr)

        tool_obj = self._get_plugin(tool_name)

        return tool_obj

    def can_execute_tool(
        self,
        core: Core,
        project: Optional[Project],
        tool: Tool,
    ) -> bool:
        if project is None:
            return False

        result = False

        if core.can_load_interface(project, tool):
            result = True

        return result

    def execute_tool(self, core: Core, project: Project, tool: Tool):
        if not core.can_load_interface(project, tool):
            errStr = ("The inputs to tool {} are not " "satisfied.").format(
                tool.get_name()
            )
            raise ValueError(errStr)

        interface = core.load_interface(project, tool)
        core.connect_interface(project, interface)
