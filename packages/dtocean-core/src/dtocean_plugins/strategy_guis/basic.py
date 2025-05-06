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


from dtocean_app.widgets.dialogs import Message
from PySide6 import QtCore

from dtocean_plugins.strategies.basic import BasicStrategy
from dtocean_plugins.strategy_guis.base import GUIStrategy, StrategyWidget


class GUIBasicStrategy(GUIStrategy, BasicStrategy):
    """A basic strategy which will run all selected modules and themes in
    sequence."""

    def __init__(self):
        BasicStrategy.__init__(self)
        GUIStrategy.__init__(self)

    def allow_run(self, core, project):
        return True

    def get_weight(self):
        """A method for getting the order of priority of the strategy.

        Returns:
          int
        """

        return 1

    def get_widget(self, parent, shell):
        widget = BasicWidget(parent, "No Configuration Required")

        return widget


class BasicWidget(Message, StrategyWidget):
    config_set = QtCore.Signal()
    config_null = QtCore.Signal()
    reset = QtCore.Signal()

    def __init__(self, parent, text):
        super(BasicWidget, self).__init__(parent, text)

    def get_configuration(self):
        return {}

    def set_configuration(self, *args):
        return

    def paintEvent(self, event):
        super(BasicWidget, self).paintEvent(event)
        self.config_set.emit()
