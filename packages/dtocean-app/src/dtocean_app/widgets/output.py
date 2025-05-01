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

import re

import pandas as pd
from dtocean_qt.models.DataFrameModel import DataFrameModel
from PySide6 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


from ..utils.display import is_high_dpi
from .datatable import DataTableWidget

if is_high_dpi():
    from ..designer.high.labeloutput import Ui_LabelOutput
    from ..designer.high.textoutput import Ui_TextOutput

else:
    from ..designer.low.labeloutput import Ui_LabelOutput
    from ..designer.low.textoutput import Ui_TextOutput


# DOCK WINDOW OUTPUT WIDGETS


class LabelOutput(QtGui.QWidget, Ui_LabelOutput):
    null_signal = QtCore.Signal()

    def __init__(self, parent, units=None):
        QtGui.QWidget.__init__(self, parent)
        Ui_LabelOutput.__init__(self)

        self.setupUi(self)
        self._init_ui(units)

    def _init_ui(self, units):
        if units is None:
            unitsStr = ""
        else:
            unitsStr = "({})".format(units)

        self.unitsLabel.setText(unitsStr)

    def _set_value(self, value):
        valueStr = str(value)
        self.valueLabel.setText(valueStr)

    def _get_read_event(self):
        return self.null_signal

    def _get_nullify_event(self):
        return self.null_signal


class OutputDataTable(QtGui.QWidget):
    null_signal = QtCore.Signal()

    def __init__(self, parent, columns, units=None):
        QtGui.QWidget.__init__(self, parent)
        self._columns = columns
        self._units = units

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName(_fromUtf8("dataTableObject"))

        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))

        self.datatable = DataTableWidget(self, edit_rows=False, edit_cols=False)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )
        self.datatable.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.datatable)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.Slot(object)
    def _set_value(self, value):
        if self._units is None:
            units = [None] * len(self._columns)
        else:
            units = self._units

        # Build new columns
        new_cols = []

        for col, unit in zip(self._columns, units):
            if unit is not None:
                new_col = "{} [{}]".format(col, unit)
            else:
                new_col = col

            new_cols.append(new_col)

        # setup a new empty model
        model = DataFrameModel()

        # set table view widget model
        self.datatable.setViewModel(model)

        # No data is stored
        if value is None:
            data = pd.DataFrame(columns=new_cols)
            model.setDataFrame(data)

            return

        # Check the columns of the stored data against the expected, for
        # legacy support
        if len(value.columns) == len(new_cols):
            safe_cols = new_cols

        elif len(value.columns) < len(new_cols):
            # Strip any units
            clean_cols = [re.sub(r"\s\[[^)]*\]", "", x) for x in new_cols]

            safe_cols = []

            for col in value.columns:
                match = [
                    new_cols[clean_cols.index(x)]
                    for x in clean_cols
                    if col == x
                ]

                if len(match) == 0:
                    continue

                safe_cols.append(match[0])

        else:
            extra_cols = len(value.columns) - len(new_cols)
            err_str = (
                "Input data has {} more column(s) than defined in "
                "columns argument"
            ).format(extra_cols)
            raise ValueError(err_str)

        data = value
        data.columns = safe_cols

        # fill the model with data
        model.setDataFrame(data)

    def _get_read_event(self):
        return self.null_signal

    def _get_nullify_event(self):
        return self.null_signal


class TextOutput(QtGui.QWidget, Ui_TextOutput):
    null_signal = QtCore.Signal()

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        Ui_TextOutput.__init__(self)

        self.setupUi(self)

    def _set_value(self, value):
        valueStr = str(value)
        self.textBrowser.setText(valueStr)

    def _get_read_event(self):
        return self.null_signal

    def _get_nullify_event(self):
        return self.null_signal


def test():
    import sys

    from mainwidgets import InOutPane
    from PySide6 import QtGui

    app = QtGui.QApplication(sys.argv)
    dialog = QtGui.QDialog()
    dialog._pane = InOutPane(dialog)
    dialog._output = LabelOutput(dialog._pane, "Hello", "20", "Cats")
    dialog._output._init_ui()
    dialog.resize(400, 275)
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test()
