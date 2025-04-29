# -*- coding: utf-8 -*-

#    Copyright (C) 2018 Mathew Topper
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
Created on Sun Nov 25 16:49:55 2018

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

from PyQt4 import QtCore, QtGui


class ExtendedComboBox(QtGui.QComboBox):
    
    # https://stackoverflow.com/a/7693234/3215152
    
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditable(True)

        # Add a filter model to filter matching items
        self.pFilterModel = QtGui.QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # Add a completer, which uses the filter model
        self.completer = QtGui.QCompleter(self.pFilterModel, self)
        
        # Always show all (filtered) completions
        self.completer.setCompletionMode(
                                QtGui.QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # Connect signals
        self.lineEdit().textEdited[str].connect(
                                    self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)
        
        return

    # On selection of an item from the completer, select the corresponding item
    # from combobox 
    def on_completer_activated(self, text):
        
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            
        return

    # On model change, update the models of the filter and completer as well 
    def setModel(self, model):
        
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)
        
        return

    # On model column change, update the model column of the filter and
    # completer as well
    def setModelColumn(self, column):
        
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)
        
        return
