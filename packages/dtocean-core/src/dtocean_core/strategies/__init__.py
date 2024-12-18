# -*- coding: utf-8 -*-

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

import abc
from copy import deepcopy

from polite_config.abc import abstractclassmethod

from ..menu import ModuleMenu, ThemeMenu
from ..pipeline import Tree


class Strategy:
    """The base abstract class for all strategy classes"""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """The init method should never have arguments. Provided for all
        subclasses are:

            self._module_menu: a ModuleMenu object
            self._theme_menu: a ThemeMenu object
            self._tree: a Tree object

        """

        self._module_menu = ModuleMenu()
        self._theme_menu = ThemeMenu()
        self._tree = Tree()

        # Record the simulation titles used in the strategy
        self._sim_record = []

        # Record the configuration dictionary of the strategy (assume this
        # is picklable)
        self._config = None

        # Record any detailed information about the simulation (assume this
        # is picklable)
        self.sim_details = None

        return

    @abstractclassmethod
    def get_name(cls):
        """A class method for the common name of the strategy.

        Returns:
          str: A unique string
        """

        return cls()

    @abc.abstractmethod
    def configure(self):
        """The configure method is collect information required for executing
        the strategy.
        """

        return

    @abc.abstractmethod
    def get_variables(self):
        """The get_variables method returns the list of any variables that
        will be set by the strategy
        """

        return

    @abc.abstractmethod
    def execute(self, core, project):
        """The execute method is used to execute the strategy. It should always
        take a Core and a Project class as the only inputs.
        """

        return

    def get_config(self):
        return deepcopy(self._config)

    def dump_config_hook(self, config):  # pylint: disable=no-self-use
        return config

    def set_config(self, config_dict):
        self._config = config_dict

    def add_simulation_title(self, sim_title):
        self._sim_record.append(sim_title)

    def remove_simulation_title(self, sim_title):
        self._sim_record.pop(self._sim_record.index(sim_title))

    def get_simulation_record(self):
        return self._sim_record[:]

    def restart(self):
        self._sim_record = []
        self.sim_details = None
