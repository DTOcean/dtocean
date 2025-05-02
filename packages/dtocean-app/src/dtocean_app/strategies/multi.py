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

import pandas as pd
from dtocean_core.pipeline import Tree
from dtocean_plugins.strategies.multi import MultiSensitivity
from mdo_engine.utilities.misc import OrderedSet
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

from ..utils.display import is_high_dpi
from ..widgets.extendedcombobox import ExtendedComboBox
from . import GUIStrategy, StrategyWidget

if is_high_dpi() or TYPE_CHECKING:
    from ..designer.high.multisensitivity import Ui_MultiSensitivityWidget
else:
    from ..designer.low.multisensitivity import Ui_MultiSensitivityWidget


class GUIMultiSensitivity(GUIStrategy, MultiSensitivity):
    """A multi-variable sensitivity study over a given range of
    values, adjusted before execution of a chosen module."""

    def __init__(self):
        MultiSensitivity.__init__(self)
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

        return 3

    def get_widget(self, parent, shell):
        widget = MultiSensitivityWidget(parent, shell)
        return widget


class MultiSensitivityWidget(
    QtWidgets.QWidget,
    Ui_MultiSensitivityWidget,
    StrategyWidget,
):
    config_set = QtCore.Signal()
    config_null = QtCore.Signal()
    reset = QtCore.Signal()

    def __init__(self, parent, shell):
        QtWidgets.QWidget.__init__(self, parent)
        Ui_MultiSensitivityWidget.__init__(self)
        StrategyWidget.__init__(self)

        self._var_ids = None
        self._mod_names

        self._sim_info_str = (
            "The number of simulations which will be run " "is: {}"
        )

        self._init_ui()
        self._set_interfaces(shell)

    def _init_ui(self):
        self.setupUi(self)

        # Custom boxes
        self.modBox = ExtendedComboBox(self)
        self.modBox.setObjectName("modBox")
        self.gridLayout.addWidget(self.modBox, 0, 1, 1, 1)

        self.varBox = ExtendedComboBox(self)
        self.varBox.setObjectName("varBox")
        self.gridLayout.addWidget(self.varBox, 1, 1, 1, 1)

        # Disble
        self.lineEdit.setDisabled(True)
        self.addButton.setDisabled(True)
        self.removeButton.setDisabled(True)
        self.infoLabel.clear()

        # Set up table model
        tablemodel = SimTableModel(parent=self)
        self.tableView.setModel(tablemodel)

        # Signals
        self.modBox.currentIndexChanged.connect(self._set_variables)
        self.varBox.currentIndexChanged.connect(self._line_edit_ui_switch)
        self.lineEdit.textChanged.connect(self._text_changed_ui_switch)
        self.tableView.clicked.connect(self._table_clicked_ui_switch)
        self.addButton.clicked.connect(self._add_row)
        self.removeButton.clicked.connect(self._remove_row)

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

        if self._var_ids is None:
            var_id_dict = {}
        else:
            var_id_dict = self._var_ids

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
    def _text_changed_ui_switch(self):
        sane_str = str(self.lineEdit.text())

        if sane_str:
            self.addButton.setEnabled(True)
        else:
            self.addButton.setDisabled(True)

    @QtCore.Slot()
    def _table_clicked_ui_switch(self):
        selected_rows = self._get_selected_rows()

        if not selected_rows:
            self.removeButton.setDisabled(True)
        else:
            self.removeButton.setEnabled(True)

    @QtCore.Slot()
    def _add_row(self):
        last_row = self.tableView.model().rowCount()
        conf_record = self._get_conf_record()
        self.tableView.model().insertRows(last_row, [conf_record])

        self._emit_config_signal()
        self._clear_selections()

    @QtCore.Slot()
    def _remove_row(self):
        selected_row = self._get_selected_rows()[0]
        self.tableView.model().removeRows(selected_row.row())

        self._table_clicked_ui_switch()
        self._emit_config_signal()

    def _emit_config_signal(self):
        df = self.tableView.model().array_df

        if not df.empty:
            self.config_set.emit()
        else:
            self.config_null.emit()

    def _get_conf_record(self):
        mod_name = str(self.modBox.currentText())
        var_name = str(self.varBox.currentText())
        var_values = str(self.lineEdit.text())

        conf_record = (mod_name, var_name, var_values)

        return conf_record

    def _get_selected_rows(self):
        indexes = self.tableView.selectionModel().selectedRows()

        return indexes

    def _clear_selections(self):
        self.modBox.setCurrentIndex(-1)
        self.varBox.clear()
        self.lineEdit.clear()

    def _get_var_title(self, var_id):
        var_meta = self._shell.core.get_metadata(var_id)
        var_title = var_meta.title

        if var_meta.units is not None:
            var_title = "{} ({})".format(var_title, var_meta.units[0])

        return var_title

    def _list2string(self, typed_list):
        sane_var_values = [str(x) for x in typed_list]
        var_values_str = ", ".join(sane_var_values)

        return var_values_str

    def get_configuration(self):
        df = self.tableView.model().array_df.copy()
        df["Variable"] = df["Variable"].apply(self._get_var_id)
        df["Values"] = df["Values"].apply(lambda x: self.string2types(x))

        subsp_ratio = self.subsetSpinBox.value() / 100.0

        conf_dict = {"inputs_df": df, "subspacing_ratio": subsp_ratio}

        nsims = MultiSensitivity.count_selections(df, subsp_ratio)
        info_str = self._sim_info_str.format(nsims)

        self.infoLabel.setText(info_str)

        return conf_dict

    def set_configuration(self, config_dict=None):
        if config_dict is None:
            return

        df = config_dict["inputs_df"]
        subsp_ratio = config_dict["subsp_ratio"]
        nsims = MultiSensitivity.count_selections(df, subsp_ratio)

        df["Variable"] = df["Variable"].apply(lambda x: self._get_var_title(x))
        df["Values"] = df["Values"].apply(lambda x: self._list2string(x))

        self.tableView.model().array_df = df
        self.subsetSpinBox.setValue(subsp_ratio * 100.0)

        info_str = self._sim_info_str.format(nsims)
        self.infoLabel.setText(info_str)

        self._emit_config_signal()


class SimTableModel(QtCore.QAbstractTableModel):
    header_labels = ["Module", "Variable", "Values"]

    def __init__(self, init_data=None, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.array_df = self._init_df(init_data)

    def _init_df(self, init_records=None):
        new_df = pd.DataFrame(columns=self.header_labels)

        if init_records is None:
            return new_df

        new_df = self._add_records(new_df, init_records)

        return new_df

    def headerData(
        self,
        section,
        orientation: Qt.Orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.header_labels[section]

        return QtCore.QAbstractTableModel.headerData(
            self, section, orientation, role
        )

    def insertRows(self, position, records, rows=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(
            QtCore.QModelIndex(), position, position + rows - 1
        )

        self.array_df = self._add_records(self.array_df, records)

        self.endInsertRows()

        return True

    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        self.beginRemoveRows(
            QtCore.QModelIndex(), position, position + rows - 1
        )

        drop_range = range(position, position + rows)
        drop_indexes = self.array_df.index[drop_range]
        self.array_df = self.array_df.drop(drop_indexes)

        self.endRemoveRows()

        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.array_df)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def data(self, index, role):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        value = self.array_df.iloc[index.row(), index.column()]

        return value

    def _add_records(self, df: pd.DataFrame, records):
        for record in records:
            s2 = pd.Series(record, index=self.header_labels)
            df = pd.concat([df, s2], ignore_index=True)

        return df
