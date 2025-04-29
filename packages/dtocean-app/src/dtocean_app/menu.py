# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2022 Mathew Topper
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
Created on Mon Jun 13 12:11:53 2016

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os

import pandas as pd
from PyQt4 import QtGui, QtCore

from .widgets.dialogs import ListTableEditor

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

# User home directory
HOME = os.path.expanduser("~")


class DBSelector(ListTableEditor):
    
    database_deselected = QtCore.pyqtSignal()
    database_dump = QtCore.pyqtSignal(str, str, dict)
    database_load = QtCore.pyqtSignal(str, str, dict)
    database_selected = QtCore.pyqtSignal(str, dict)
    
    def __init__(self, parent, data_menu):
        
        super(DBSelector, self).__init__(parent)
        self._data_menu = data_menu
        self._selected = None
        self._unsaved = False
        self._valid_cred_keys = ['host', 'dbname', 'user', 'pwd']
        
        self._init_ui()
                
        return
        
    def _init_ui(self):
        
        self.setWindowTitle("Select database...")
        self.topStaticLabel.setText("Current database:")
        self.listLabel.setText("Available:")
        self.tableLabel.setText("Credentials:")
        self._update_current("None")
        
        # Add warning about passwords
        label_str = ("NOTE: Passwords are saved as PLAIN TEXT. Do not save "
                     "your password if you have any security concerns, "
                     "instead fill the 'pwd' field in this dialogue, before "
                     "pressing apply.")
        self.extraLabel.setText(label_str)
        
        # Tool tips for standard buttons
        tip_msg = 'Add stored credentials'
        self.addButton.setToolTip(tip_msg)
        
        tip_msg = 'Delete stored credentials'
        self.deleteButton.setToolTip(tip_msg)
        
        tip_msg = 'Store updated credentials'
        self.saveButton.setToolTip(tip_msg)
        
        # Add new buttons
        self.loadButton = self._make_button()
        self.loadButton.setObjectName(_fromUtf8("loadButton"))
        self.loadButton.setText("Load...")
        self.loadButton.setDisabled(True)
        self.verticalLayout.addWidget(self.loadButton)
        
        tip_msg = 'Load database from structured files'
        self.loadButton.setToolTip(tip_msg)
        
        self.dumpButton = self._make_button()
        self.dumpButton.setObjectName(_fromUtf8("dumpButton"))
        self.dumpButton.setText("Dump...")
        self.dumpButton.setDisabled(True)
        self.verticalLayout.addWidget(self.dumpButton)
        
        tip_msg = 'Dump database to structured files'
        self.dumpButton.setToolTip(tip_msg)
        
        # Add label and combo box
        self.sectionLabel = self._make_label()
        self.sectionLabel.setObjectName(_fromUtf8("sectionLabel"))
        self.sectionLabel.setText("Select section:")
        self.sectionLabel.setEnabled(True)
        self.verticalLayout.addWidget(self.sectionLabel)
        
        tip_msg = 'Dump or load a partial section of the database'
        self.sectionLabel.setToolTip(tip_msg)
        
        self.sectionCombo = self._make_combo()
        self.sectionCombo.setMinimumSize(QtCore.QSize(75, 0))
        self.sectionCombo.setObjectName(_fromUtf8("sectionCombo"))
        self.sectionCombo.setDisabled(True)
        self.verticalLayout.addWidget(self.sectionCombo)
        
        combo_list = ["All", "Device", "Site", "Other"]
        
        for item in combo_list:
            self.sectionCombo.addItem(item)
        
        self.listWidget.itemClicked.connect(self._update_table)
        self.listWidget.itemDelegate().closeEditor.connect(
                                                        self._rename_database)
        
        self.tableWidget.cellChanged.connect(self._unsaved_data)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        self.buttonBox.button(
            QtGui.QDialogButtonBox.Apply).clicked.connect(self._set_database)
        self.buttonBox.button(
            QtGui.QDialogButtonBox.Reset).clicked.connect(self._reset_database)
        self.addButton.clicked.connect(self._add_database)
        self.saveButton.clicked.connect(self._update_database)
        self.deleteButton.clicked.connect(self._delete_database)
        self.dumpButton.clicked.connect(self._dump_database)
        self.loadButton.clicked.connect(self._load_database)
        
        self.addButton.setEnabled(True)
        self.deleteButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        
        # Populate the database list
        self._update_list()

        return
    
    def _make_button(self):
        
        button = QtGui.QPushButton(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy)
        
        return button
    
    def _make_label(self):
        
        label = QtGui.QLabel(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
        label.setSizePolicy(sizePolicy)
        
        return label
    
    def _make_combo(self):
        
        combo = QtGui.QComboBox(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(combo.sizePolicy().hasHeightForWidth())
        combo.setSizePolicy(sizePolicy)
        
        return combo
        
    def _update_list(self):
        
        db_names = self._data_menu.get_available_databases()
        super(DBSelector, self)._update_list(db_names)
        
        # Make them editable
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            
        if self.listWidget.count() > 0:
            self.deleteButton.setEnabled(True)
        
        return
    
    def _get_db_dict(self):
        
        tabledf = self._read_table()
        keys = tabledf["Key"]
        values = tabledf["Value"]
        
        db_dict = {k: v for k, v in zip(keys, values)
                                            if k in self._valid_cred_keys}
        
        return db_dict
    
    @QtCore.pyqtSlot()
    def _convert_enabled(self):
        
        # Switch on dump/load functions
        self.loadButton.setEnabled(True)
        self.dumpButton.setEnabled(True)
        self.sectionCombo.setEnabled(True)
        
        return
    
    @QtCore.pyqtSlot()
    def _convert_disabled(self):
        
        # Switch on dump/load functions
        self.loadButton.setDisabled(True)
        self.dumpButton.setDisabled(True)
        self.sectionCombo.setDisabled(True)
        
        return
        
    @QtCore.pyqtSlot(str)
    def _update_current(self, current_db):
        
        self.topDynamicLabel.setText(current_db)
        
        # Set button default
        if current_db == "None":
            self.buttonBox.button(
                    QtGui.QDialogButtonBox.Apply).setDefault(True)
        else:
            self.buttonBox.button(
                    QtGui.QDialogButtonBox.Close).setDefault(True)
        
        return
    
    @QtCore.pyqtSlot(object)
    def _update_table(self, item, template=False):
        
        selected = str(item.text())
        value_order = []
        
        if template:
            db_dict = {}
        else:
            db_dict = self._data_menu.get_database_dict(selected)

        for key in self._valid_cred_keys:
            if key in db_dict:
                value = db_dict[key]
            else:
                value = ""
            value_order.append(value)
    
        frame_dict = {"Key": self._valid_cred_keys,
                      "Value": value_order}
        df = pd.DataFrame(frame_dict)
                
        super(DBSelector, self)._update_table(df, ["Key"])
        
        # Record the selected database
        self._selected = selected
        
        # Set data as saved
        if not template:
            self.tableLabel.setText("Credentials:")
            self.saveButton.setEnabled(False)
            self._unsaved = False
        
        return
        
    @QtCore.pyqtSlot(int, int)
    def _unsaved_data(self, *args):
        
        self.tableLabel.setText("Credentials (unsaved):")
        self.saveButton.setEnabled(True)
        self._unsaved = True
        
        return
        
    @QtCore.pyqtSlot()
    def _set_database(self):
        
        if self._selected is None: return
        
        name = self._selected
        if self._unsaved: name += " (modified)"
        db_dict = self._get_db_dict()

        self.database_selected.emit(name, db_dict)
        
        # Switch on dump/load functions
        self._convert_enabled()
        
        return
        
    @QtCore.pyqtSlot()
    def _reset_database(self):
        
        self.database_deselected.emit()
        
        # Set apply button as default
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        
        # Switch off dump/load functions
        self._convert_disabled()
        
        return
    
    @QtCore.pyqtSlot(object, object)
    def _rename_database(self, editor, hint):
       
        new_name = str(editor.text())
                
        if new_name == self._selected: return
                
        # If the name is already used then reject it
        if new_name in self._data_menu.get_available_databases():
            
            item = self.listWidget.currentItem()
            item.setText(self._selected)
            
            return
        
        db_dict = self._get_db_dict()

        self._data_menu.delete_database(self._selected)
        self._data_menu.update_database(new_name,
                                        db_dict,
                                        True)
        
        self._selected = new_name
        
        return
    
    @QtCore.pyqtSlot()
    def _add_database(self):
        
        # Ensure name is unique
        base_name = "unnamed"
        new_name = base_name
        add_number = 1
        
        while True:
                        
            if new_name in self._data_menu.get_available_databases():
                new_name = "{}-{}".format(base_name, add_number)
                add_number += 1
            else:
                break
        
        new_item = self._add_item(new_name)
        new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsEditable)
        self._update_table(new_item, template=True)
        self._unsaved = True
        self._update_database()
        
        self.deleteButton.setEnabled(True)
        
        return

    @QtCore.pyqtSlot()
    def _update_database(self):
        
        if not self._unsaved: return
        
        db_dict = self._get_db_dict()
        
        self._data_menu.update_database(self._selected,
                                        db_dict,
                                        True)
                                        
        # Set data as saved
        self.tableLabel.setText("Credentials:")
        self.saveButton.setEnabled(False)
        self._unsaved = False
                                        
        return
    
    @QtCore.pyqtSlot()
    def _delete_database(self):
        
        # Check again
        qm = QtGui.QMessageBox
        ret = qm.question(self,
                          "Delete '{}'?".format(self._selected),
                          "Are you sure you wish to remove these credentials?",
                          qm.Yes | qm.No)

        if ret == qm.No: return
        
        self._data_menu.delete_database(self._selected)
        self._delete_selected()
        
        if self.listWidget.count() == 0:
            
            self.deleteButton.setDisabled(True)
            self.tableWidget.clear()
            self.tableWidget.setColumnCount(0)
        
        else:
            
            item = self.listWidget.item(self.listWidget.currentRow())
            self._update_table(item)
        
        return
    
    @QtCore.pyqtSlot()
    def _dump_database(self):
    
        title_str = 'Select Directory for File Dump'
        
        root_path = QtGui.QFileDialog.getExistingDirectory(
                                                self,
                                                title_str,
                                                HOME,
                                                QtGui.QFileDialog.ShowDirsOnly)
        
        section = self.sectionCombo.currentText()
        
        if not root_path: return
        
        qstr = "Existing files will be overwritten. Continue?"
        
        reply = QtGui.QMessageBox.warning(
                            self,
                            'Database dump',
                            qstr,
                            QtGui.QMessageBox.Yes,
                            QtGui.QMessageBox.No | QtGui.QMessageBox.Default)
        
        if reply == QtGui.QMessageBox.Yes:
            db_dict = self._get_db_dict()
            self.database_dump.emit(root_path, section, db_dict)

        return
    
    @QtCore.pyqtSlot()
    def _load_database(self):
    
        title_str = 'Select Directory to Load'
        
        root_path = QtGui.QFileDialog.getExistingDirectory(
                                                self,
                                                title_str,
                                                HOME,
                                                QtGui.QFileDialog.ShowDirsOnly)
        
        section = self.sectionCombo.currentText()
        
        if not root_path: return
        
        qstr = "Existing data will be overwritten. Continue?"
        
        reply = QtGui.QMessageBox.warning(
                            self,
                            'Database load',
                            qstr,
                            QtGui.QMessageBox.Yes,
                            QtGui.QMessageBox.No | QtGui.QMessageBox.Default)
        
        if reply == QtGui.QMessageBox.Yes:
            db_dict = self._get_db_dict()
            self.database_load.emit(root_path, section, db_dict)

        return
