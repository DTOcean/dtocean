# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2025 Mathew Topper
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

from dtocean_plugins.tools.base import Tool


class GUITool(Tool):
    """Plugin Discovery"""

    def __init__(self):
        self.parent = None

    @abc.abstractmethod
    def get_weight(self):
        """A method for getting the order of priority of the tool.

        Returns:
          int
        """

    @abc.abstractmethod
    def has_widget(self):
        """A method for indicating if the tool creates a widget

        Returns:
          bool
        """
