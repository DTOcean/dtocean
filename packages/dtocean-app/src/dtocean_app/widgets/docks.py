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
Created on Thu Apr 23 12:51:14 2015

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

from PyQt4 import QtCore, QtGui

from ..utils.display import is_high_dpi
from ..utils.qtlog import XStream

if is_high_dpi():

    from ..designer.high.listdock import Ui_ListDock
    from ..designer.high.pipelinedock import Ui_PipeLineDock
    from ..designer.high.treedock import Ui_TreeDock
    from ..designer.high.systemdock import Ui_SystemDock
    
else:
    
    from ..designer.low.listdock import Ui_ListDock
    from ..designer.low.pipelinedock import Ui_PipeLineDock
    from ..designer.low.treedock import Ui_TreeDock
    from ..designer.low.systemdock import Ui_SystemDock


class DockShowCloseFilter(QtCore.QObject):
    
    _show = QtCore.pyqtSignal()
    _close = QtCore.pyqtSignal()

    def eventFilter(self, source, event):

        if (event.type() == QtCore.QEvent.Show and
            isinstance(source, QtGui.QDockWidget)):

            self._show.emit()
        
        if (event.type() == QtCore.QEvent.Close and
            isinstance(source, QtGui.QDockWidget)):

            self._close.emit()

        return False


class PipeLineDock(QtGui.QDockWidget, Ui_PipeLineDock):

    def __init__(self, parent):
    
        QtGui.QDockWidget.__init__(self, "Dockable", parent)
        Ui_TreeDock.__init__(self)
        self.setupUi(self)
        self.treeView.setIconSize(QtCore.QSize(12,12))
        
        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)
        
        return


class TreeDock(QtGui.QDockWidget, Ui_TreeDock):

    def __init__(self, parent):
    
        QtGui.QDockWidget.__init__(self, "Dockable", parent)
        Ui_TreeDock.__init__(self)
        self.setupUi(self)
        self.treeWidget.setIconSize(QtCore.QSize(12,12))
        
        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)
        
        return


class ListDock(QtGui.QDockWidget, Ui_ListDock):

    def __init__(self, parent):
    
        QtGui.QDockWidget.__init__(self, "Dockable", parent)
        Ui_ListDock.__init__(self)
        self.setupUi(self)
        
        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)
        
        return
        
    def _get_list_values(self):
        
        items = []
        
        for index in xrange(self.listWidget.count()):
             items.append(self.listWidget.item(index))
             
        values = [str(i.text()) for i in items]
        
        return values


class LogDock(QtGui.QDockWidget, Ui_SystemDock):

    def __init__(self, parent=None, max_lines=1e5 - 1):
    
        QtGui.QDockWidget.__init__(self, "Dockable", parent)
        Ui_SystemDock.__init__(self)
        
        self._init_ui()
        self._set_max_lines(max_lines)
        
        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)
        
        return
        
    def _init_ui(self):
        
        self.setupUi(self)
        
        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(255, 255, 255)
        pal.setColor(QtGui.QPalette.Text, textc)
        
        self._console = QtGui.QPlainTextEdit(self)
        self._console.setPalette(pal)
        self._console.setReadOnly(True)

        self._layout = QtGui.QVBoxLayout()
        self._layout.setSpacing(2)
        self._layout.setMargin(2)
        self._layout.addWidget(self._console)
        self.verticalLayout.addLayout(self._layout)

        XStream.stdout().messageWritten.connect(self._add_text)
        XStream.stderr().messageWritten.connect(self._add_text)

        return
    
    def _set_max_lines(self, max_lines):
        
        self._console.setMaximumBlockCount(max_lines)
        
        return
    
    @QtCore.pyqtSlot(str)
    def _add_text(self, arg1):
        
        self._console.appendPlainText(arg1)
        self._console.moveCursor(QtGui.QTextCursor.End)
        
        return
