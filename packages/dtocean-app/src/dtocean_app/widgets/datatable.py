# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Matthias Ludwig, Marcel Radischat, Mathew Topper
#    Copyright (C) 2017-2022 Mathew Topper
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
Created on Wed Aug 31 12:18:05 2016

This is a spin on the DataTableWidget defined in the dtocean-qt package in the
file: dtocean_qt\views\DataTableView.py

Converted to GPL under the terms of the original MIT Licence:
https://opensource.org/licenses/MIT

.. moduleauthor:: Matthias Ludwig
.. moduleauthor:: Marcel Radischat
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import io
import csv

from dtocean_qt.compat import QtCore, QtGui, Slot

from dtocean_qt.models.DataFrameModel import DataFrameModel
from dtocean_qt.views.CustomDelegates import createDelegate
from dtocean_qt.views.DataTableView import DragTable
from dtocean_qt.views.EditDialogs import (AddAttributesDialog,
                                          RemoveAttributesDialog)
from dtocean_qt.views._ui import icons_rc

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class DataTableWidget(QtGui.QWidget):
    """A Custom widget with a TableView and a toolbar.

    This widget shall display all `DataFrameModels` and
    enable the editing of this (edit data, adding/removing,
    rows).

    """
    def __init__(self, parent=None,
                       edit_rows=True,
                       edit_cols=True,
                       edit_cells=False,
                       iconSize=QtCore.QSize(36, 36)):
        """Constructs the object with the given parent.

        Args:
            parent (QObject, optional): Causes the objected to be owned
                by `parent` instead of Qt. Defaults to `None`.
            iconSize (QSize, optional): Size of edit buttons. Defaults to QSize(36, 36).

        """
        super(DataTableWidget, self).__init__(parent)
        self._iconSize = iconSize
        self.initUi(edit_rows, edit_cols, edit_cells)
        
        return

    def initUi(self, edit_rows, edit_cols, edit_cells=False):
        """Initalizes the Uuser Interface with all sub widgets.

        """
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        buttonFrame = QtGui.QFrame(self)
        #self.buttonFrame.setMinimumSize(QtCore.QSize(250, 50))
        #self.buttonFrame.setMaximumSize(QtCore.QSize(250, 50))
        buttonFrame.setFrameShape(QtGui.QFrame.NoFrame)
        spacerItemButton = QtGui.QSpacerItem(40,
                                             20,
                                             QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Minimum)
        
        if edit_rows:
        
            self.addRowButton = QtGui.QToolButton(buttonFrame)
            self.addRowButton.setObjectName('addrowbutton')
            self.addRowButton.setText(self.tr(u'+row'))
            self.addRowButton.setToolTip(self.tr(u'add new row'))
            icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(
                                ':/icons/edit-table-insert-row-below.png')))
    
            self.addRowButton.setIcon(icon)
            self.addRowButton.toggled.connect(self.addRow)
            
            self.removeRowButton = QtGui.QToolButton(buttonFrame)
            self.removeRowButton.setObjectName('removerowbutton')
            self.removeRowButton.setText(self.tr(u'-row'))
            self.removeRowButton.setToolTip(self.tr(u'remove selected rows'))
            icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(
                                    ':/icons/edit-table-delete-row.png')))
    
            self.removeRowButton.setIcon(icon)
            self.removeRowButton.toggled.connect(self.removeRow)

            row_buttons = [self.addRowButton, self.removeRowButton]
        
        if edit_cols:
            
            self.addColumnButton = QtGui.QToolButton(buttonFrame)
            self.addColumnButton.setObjectName('addcolumnbutton')
            self.addColumnButton.setText(self.tr(u'+col'))
            self.addColumnButton.setToolTip(self.tr(u'add new column'))
            icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(
                            ':/icons/edit-table-insert-column-right.png')))
    
            self.addColumnButton.setIcon(icon)
            self.addColumnButton.toggled.connect(self.showAddColumnDialog)

            self.removeColumnButton = QtGui.QToolButton(buttonFrame)
            self.removeColumnButton.setObjectName('removecolumnbutton')
            self.removeColumnButton.setText(self.tr(u'-col'))
            self.removeColumnButton.setToolTip(self.tr(u'remove a column'))
            icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(
                                ':/icons/edit-table-delete-column.png')))
    
            self.removeColumnButton.setIcon(icon)
            self.removeColumnButton.toggled.connect(self.showRemoveColumnDialog)
            
            col_buttons = [self.addColumnButton, self.removeColumnButton]
        
        if edit_rows or edit_cols or edit_cells:

            self.buttonFrameLayout = QtGui.QGridLayout(buttonFrame)
            self.buttonFrameLayout.setContentsMargins(0, 0, 0, 0)
    
            self.editButton = QtGui.QToolButton(buttonFrame)
            self.editButton.setObjectName('editbutton')
            self.editButton.setText(self.tr(u'edit'))
            self.editButton.setToolTip(self.tr(u'toggle editing mode'))
            icon = QtGui.QIcon(QtGui.QPixmap(
                                    _fromUtf8(':/icons/document-edit.png')))
    
            self.editButton.setIcon(icon)
            self.editButton.toggled.connect(self.enableEditing)
            
            edit_buttons = [self.editButton]
            
            if edit_rows and edit_cols:
                
                for x in zip(row_buttons, col_buttons):
                    edit_buttons.extend(x)
                    
            elif edit_rows:
                
                edit_buttons.extend(row_buttons)
                
            elif edit_cols:
                
                 edit_buttons.extend(col_buttons)
                 
            elif not edit_cells:
                
                errStr = "Ack! Ack! Ack!"
                raise SystemError(errStr)

            self.buttons = edit_buttons
    
            for index, button in enumerate(self.buttons):
                button.setMinimumSize(self._iconSize)
                button.setMaximumSize(self._iconSize)
                button.setIconSize(self._iconSize)
                button.setCheckable(True)
                self.buttonFrameLayout.addWidget(button, 0, index, 1, 1)
            self.buttonFrameLayout.addItem(spacerItemButton, 0, index+1, 1, 1)
    
            for button in self.buttons[1:]:
                button.setEnabled(False)
            
            self.buttonFrame = buttonFrame
            self.gridLayout.addWidget(self.buttonFrame, 0, 0, 1, 1)
            tab_layout_idx = 1
            
        else:
            
            self.buttonFrame = None
            self.buttons = None
            tab_layout_idx = 0

        #self.tableView = QtGui.QTableView(self)
        self.tableView = DragTable(self)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSortingEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.installEventFilter(self)
        
        self.gridLayout.addWidget(self.tableView, tab_layout_idx, 0, 1, 1)
        
        return

    def setButtonsVisible(self, visible):
        """hide/show the edit buttons"""
        self.buttonFrame.setVisible(visible)
        
    def hideVerticalHeader(self, arg=True):
        self.tableView.verticalHeader().setVisible(not arg)
        return
    
    def setViewModel(self, model):
        """Sets the model for the enclosed TableView in this widget.

        Args:
            model (DataFrameModel): The model to be displayed by
                the Table View.

        """
        if isinstance(model, DataFrameModel):
            
            self.enableEditing(False)
            self.uncheckButton()
            
            self.tableView.setModel(model)
            model.dtypeChanged.connect(self.updateDelegate)
            model.dataChanged.connect(self.updateDelegates)
            
            self.updateDelegates()
            
    def setModel(self, model):
        """Sets the model for the enclosed TableView in this widget.

        Args:
            model (DataFrameModel): The model to be displayed by
                the Table View.

        """
        self.setViewModel(model)

    def model(self):
        """Gets the viewModel"""
        return self.view().model()

    def viewModel(self):
        """Gets the viewModel"""
        return self.view().model()

    def view(self):
        """Gets the enclosed TableView

        Returns:
            QtGui.QTableView: A Qt TableView object.

        """
        return self.tableView

    def updateDelegate(self, column, dtype):
        """update the delegates for a specific column
        
        Args:
            column (int): column index.
            dtype (str): data type of column.
        
        """
        # as documented in the setDelegatesFromDtype function
        # we need to store all delegates, so going from
        # type A -> type B -> type A
        # would cause a segfault if not stored.
        createDelegate(dtype, column, self.tableView)

    def updateDelegates(self):
        """reset all delegates"""

        for index, column in enumerate(
                self.tableView.model().dataFrame().columns):

            dtype = self.tableView.model().dataFrame().dtypes[index]
            self.updateDelegate(index, dtype)
        
        self.tableView.resizeColumnsToContents()
            
    def selectionModel(self):
        """return the table views selectionModel"""
        return self.view().selectionModel()
    
    def eventFilter(self, source, event):
        
        if (event.type() == QtCore.QEvent.KeyPress and
            event.matches(QtGui.QKeySequence.Copy)):
            
            self.copySelection()
            
            return True
        
        return super(DataTableWidget, self).eventFilter(source, event)
        
    def copySelection(self):
        
        selection = self.tableView.selectedIndexes()
        
        if selection:
            
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            
            for index in selection:
                
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data().toPyObject()
                
            stream = io.BytesIO()
            csv.writer(stream).writerows(table)
            QtGui.qApp.clipboard().setText(stream.getvalue())
            
        return
        
        
    @Slot(bool)
    def enableEditing(self, enabled):
        """Enable the editing buttons to add/remove rows/columns and to edit the data.

        This method is also a slot.
        In addition, the data of model will be made editable,
        if the `enabled` parameter is true.

        Args:
            enabled (bool): This flag indicates, if the buttons
                shall be activated.

        """
        
        model = self.tableView.model()

        if model is not None:
            model.enableEditing(enabled)
        
        if self.buttons is None: return 
        
        for button in self.buttons[1:]:
            button.setEnabled(enabled)
            if button.isChecked():
                button.setChecked(False)
                
        return

    @Slot()
    def uncheckButton(self):
        """Removes the checked stated of all buttons in this widget.

        This method is also a slot.

        """
    
        if self.buttons is None: return
        
        #for button in self.buttons[1:]:
        for button in self.buttons:
            # supress editButtons toggled event
            button.blockSignals(True)
            if button.isChecked():
                button.setChecked(False)
            button.blockSignals(False)
            
        return

    @Slot(str, object, object)
    def addColumn(self, columnName, dtype, defaultValue):
        """Adds a column with the given parameters to the underlying model

        This method is also a slot.
        If no model is set, nothing happens.

        Args:
            columnName (str): The name of the new column.
            dtype (numpy.dtype): The datatype of the new column.
            defaultValue (object): Fill the column with this value.

        """
        model = self.tableView.model()

        if model is not None:
            model.addDataFrameColumn(columnName, dtype, defaultValue)

        self.addColumnButton.setChecked(False)

    @Slot(bool)
    def showAddColumnDialog(self, triggered):
        """Display the dialog to add a column to the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the dialog will be created and shown.

        """
        if triggered:
            dialog = AddAttributesDialog(self)
            dialog.accepted.connect(self.addColumn)
            dialog.rejected.connect(self.uncheckButton)
            dialog.show()

    @Slot(bool)
    def addRow(self, triggered):
        """Adds a row to the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the row will be appended to the end.

        """
        if triggered:
            model = self.tableView.model()
            model.addDataFrameRows()
            self.sender().setChecked(False)

    @Slot(bool)
    def removeRow(self, triggered):
        """Removes a row to the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the selected row will be removed
                from the model.

        """
        if triggered:
            model = self.tableView.model()
            selection = self.tableView.selectedIndexes()

            rows = [index.row() for index in selection]
            model.removeDataFrameRows(set(rows))
            self.sender().setChecked(False)

    @Slot(list)
    def removeColumns(self, columnNames):
        """Removes one or multiple columns from the model.

        This method is also a slot.

        Args:
            columnNames (list): A list of columns, which shall
                be removed from the model.

        """
        model = self.tableView.model()

        if model is not None:
            sane_names = [(pos, str(name.toPyObject()))
                                                for pos, name in columnNames]
            model.removeDataFrameColumns(sane_names)

        self.removeColumnButton.setChecked(False)

    @Slot(bool)
    def showRemoveColumnDialog(self, triggered):
        """Display the dialog to remove column(s) from the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the dialog will be created and shown.

        """
        if triggered:
            model = self.tableView.model()
            if model is not None:
                columns = model.dataFrameColumns()
                dialog = RemoveAttributesDialog(columns, self)
                dialog.accepted.connect(self.removeColumns)
                dialog.rejected.connect(self.uncheckButton)
                dialog.show()

