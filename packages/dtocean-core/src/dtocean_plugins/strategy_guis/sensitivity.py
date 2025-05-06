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

from typing import TYPE_CHECKING

from dtocean_app.utils.display import is_high_dpi
from dtocean_app.widgets.extendedcombobox import ExtendedComboBox
from mdo_engine.utilities.misc import OrderedSet
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

from dtocean_core.pipeline import Tree
from dtocean_plugins.strategies.sensitivity import UnitSensitivity
from dtocean_plugins.strategy_guis.base import GUIStrategy, StrategyWidget

if is_high_dpi() or TYPE_CHECKING:
    from dtocean_app.designer.high.unitsensitivity import (
        Ui_UnitSensitivityWidget,
    )
else:
    from dtocean_app.designer.low.unitsensitivity import (
        Ui_UnitSensitivityWidget,
    )


class GUIUnitSensitivity(GUIStrategy, UnitSensitivity):
    """A sensitivity study on a single unit variables over a given range of
    values, adjusted before execution of a chosen module."""

    def __init__(self):
        UnitSensitivity.__init__(self)
        GUIStrategy.__init__(self)

    def allow_run(self, core, project):
        if len(project) > 1:
            return False
        return True

    def get_weight(self):
        """A method for getting the order of priority of the strategy.

        Returns:
          int
        """

        return 2

    def get_widget(self, parent, shell):
        widget = UnitSensitivityWidget(parent, shell)
        return widget


class UnitSensitivityWidget(
    QtWidgets.QWidget,
    Ui_UnitSensitivityWidget,
    StrategyWidget,
):
    config_set = QtCore.Signal()
    config_null = QtCore.Signal()
    reset = QtCore.Signal()

    def __init__(self, parent, shell):
        QtWidgets.QWidget.__init__(self, parent)
        Ui_UnitSensitivityWidget.__init__(self)
        StrategyWidget.__init__(self)

        self._var_ids = None
        self._mod_names: dict[int, str]

        self._init_ui()
        self._set_interfaces(shell)

    def _init_ui(self):
        self.setupUi(self)

        # Disble line edit
        self.lineEdit.setDisabled(True)

        # Custom boxes
        self.modBox = ExtendedComboBox(self)
        self.modBox.setObjectName("modBox")
        self.gridLayout.addWidget(self.modBox, 0, 1, 1, 1)

        self.varBox = ExtendedComboBox(self)
        self.varBox.setObjectName("varBox")
        self.gridLayout.addWidget(self.varBox, 1, 1, 1, 1)

        # Signals
        self.modBox.currentIndexChanged.connect(self._set_variables)
        self.varBox.currentIndexChanged.connect(self._line_edit_ui_switch)
        self.lineEdit.textChanged.connect(self._emit_config_signal)

    def _get_var_id(self, var_name):
        if self._var_ids is None:
            return var_name
        return self._var_ids[var_name]

    def _set_interfaces(self, shell, include_str=True):
        self._shell = shell

        self.modBox.clear()

        active_modules = shell.module_menu.get_active(shell.core, shell.project)

        self._mod_names = active_modules

        self.modBox.addItems(active_modules)
        self.modBox.setCurrentIndex(-1)

    @QtCore.Slot(int)
    def _set_variables(self, box_number):
        self.varBox.clear()

        if box_number < 0:
            return

        interface_name = self._mod_names[box_number]

        tree = Tree()

        var_id_dict = {}

        branch = tree.get_branch(
            self._shell.core, self._shell.project, interface_name
        )

        var_inputs = branch.get_inputs(self._shell.core, self._shell.project)

        unique_vars = OrderedSet(var_inputs)

        var_names = []

        for var_id in unique_vars:
            var_meta = self._shell.core.get_metadata(var_id)

            if "SimpleData" in var_meta.structure:
                if var_meta.types is None:
                    errStr = (
                        "Variable {} with SimpleData structure "
                        "requires types meta data to be "
                        "set"
                    ).format(var_id)
                    raise ValueError(errStr)

                if (
                    "int" in var_meta.types
                    or "float" in var_meta.types
                    or "str" in var_meta.types
                ):
                    title = var_meta.title

                    if var_meta.units is not None:
                        title = "{} ({})".format(title, var_meta.units[0])

                    var_names.append(title)

                if title not in var_id_dict:
                    var_id_dict[title] = var_id

        self._var_ids = var_id_dict

        self.varBox.addItems(var_names)
        self.varBox.setCurrentIndex(-1)

    @QtCore.Slot(int)
    def _line_edit_ui_switch(self, box_number):
        self.lineEdit.clear()

        if box_number != -1:
            self.lineEdit.setEnabled(True)
        else:
            self.lineEdit.setDisabled(True)

    @QtCore.Slot()
    def _emit_config_signal(self):
        line_config = str(self.lineEdit.text())

        if line_config:
            self.config_set.emit()
        else:
            self.config_null.emit()

    def get_configuration(self):
        mod_name = str(self.modBox.currentText())

        var_name = str(self.varBox.currentText())
        var_id = self._get_var_id(var_name)

        var_values = self.string2types(str(self.lineEdit.text()))

        conf_dict = {
            "module_name": mod_name,
            "variable_name": var_id,
            "variable_values": var_values,
        }

        return conf_dict

    def set_configuration(self, config_dict=None):
        if config_dict is None:
            return

        mod_name = config_dict["module_name"]
        var_id = config_dict["var_name"]
        var_values = config_dict["var_values"]

        sane_var_values = [str(x) for x in var_values]
        var_values_str = ", ".join(sane_var_values)

        index = self.modBox.findText(mod_name, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.modBox.setCurrentIndex(index)
        else:
            errStr = "Module {} not found in modBox".format(mod_name)
            raise ValueError(errStr)

        self._set_variables(index)

        var_meta = self._shell.core.get_metadata(var_id)
        title = var_meta.title

        if var_meta.units is not None:
            title = "{} ({})".format(title, var_meta.units[0])

        index = self.varBox.findText(title, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.varBox.setCurrentIndex(index)
        else:
            errStr = "Variable {} not found in varBox".format(title)
            raise ValueError(errStr)

        self.lineEdit.setText(var_values_str)
