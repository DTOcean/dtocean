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

"""
Created on Thu Apr 23 12:51:14 2015

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import logging
import re

from PySide6 import QtCore, QtWidgets

from .widgets.docks import ListDock

module_logger = logging.getLogger(__name__)


class SimulationDock(ListDock):
    name_changed = QtCore.Signal(str, str)
    active_changed = QtCore.Signal(str)

    def __init__(self, parent):
        super(SimulationDock, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self._init_title()
        self.listWidget.itemDelegate().closeEditor.connect(self._catch_edit)
        self.listWidget.itemClicked.connect(self._set_active_simulation)

        # Allow drag and drop sorting
        self.listWidget.setDragDropMode(
            QtWidgets.QAbstractItemView.DragDropMode.InternalMove
        )

    def _init_title(self):
        self.setWindowTitle("Simulations")

    def _update_list(self, names=None, bold_signal=None):
        self.listWidget.clear()

        if names is None:
            return

        for name in names:
            sim_item = SimulationItem(self.listWidget, name)

            if bold_signal is not None:
                bold_signal.connect(sim_item._set_bold)

            self.listWidget.addItem(sim_item)

    def _make_menus(self, shell, position):
        menu = QtWidgets.QMenu()

        menu.addAction("Clone", lambda: self._clone_current(shell))
        delete = menu.addAction("Delete", lambda: self._delete_current(shell))

        if len(shell.project) < 2:
            delete.setEnabled(False)

        menu.exec_(self.listWidget.mapToGlobal(position))

    @QtCore.Slot(object)
    def _update_simulations(self, project):
        if project is None:
            self._update_list()
            return

        sim_titles = project.get_simulation_titles()
        self._update_list(sim_titles, project.active_title_changed)

        active_sim_title = project.get_simulation_title()

        if active_sim_title is not None:
            project.active_title_changed.emit(active_sim_title)

    @QtCore.Slot(object)
    def _set_active_simulation(self, item):
        currentItem = self.listWidget.currentItem()
        title = currentItem._get_title()

        self.active_changed.emit(title)

    @QtCore.Slot(object, object)
    def _catch_edit(self, editor, hint):
        currentItem = self.listWidget.currentItem()
        old_title = currentItem._get_title()

        new_title = str(editor.text())

        self.name_changed.emit(old_title, new_title)

    @QtCore.Slot(object)
    def _clone_current(self, shell):
        currentItem = self.listWidget.currentItem()
        title = currentItem._get_title()

        clones = re.findall(r"Clone \d+$", title)

        if clones:
            clone = clones[-1]
            clone_number = int(clone.split()[1]) + 1

            clone_search = r"{}$".format(clone)
            clone_replace = r"Clone {}".format(clone_number)

            clone_title = re.sub(clone_search, clone_replace, title)

        else:
            clone_title = "{} Clone 1".format(title)

        msg = "Cloning simulation '{}' as '{}'".format(title, clone_title)
        module_logger.debug(msg)

        shell.core.clone_simulation(shell.project, clone_title, sim_title=title)

    @QtCore.Slot(object)
    def _delete_current(self, shell):
        currentItem = self.listWidget.currentItem()
        title = currentItem._get_title()

        msg = "Deleting simulation '{}'".format(title)
        module_logger.debug(msg)

        shell.core.remove_simulation(shell.project, sim_title=title)

        self._update_simulations(shell.project)


class SimulationItem(QtWidgets.QListWidgetItem):
    def __init__(self, parent, title):
        super(SimulationItem, self).__init__(parent)
        self._title = None

        self._init_ui(title)

    def _init_ui(self, title):
        self.setFlags(self.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self._set_title(title)

    def _get_title(self):
        return self._title

    def _set_title(self, title):
        self.setText(title)
        self._title = title

    @QtCore.Slot(str)
    def _set_bold(self, value):
        if value == self._get_title():
            x = True
        else:
            x = False

        item_font = self.font()
        item_font.setBold(x)
        self.setFont(item_font)
