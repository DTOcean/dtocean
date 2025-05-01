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

from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets

from ..utils.display import is_high_dpi
from ..utils.qtlog import XStream

if is_high_dpi() or TYPE_CHECKING:
    from ..designer.high.listdock import Ui_ListDock
    from ..designer.high.pipelinedock import Ui_PipeLineDock
    from ..designer.high.systemdock import Ui_SystemDock
    from ..designer.high.treedock import Ui_TreeDock
else:
    from ..designer.low.listdock import Ui_ListDock
    from ..designer.low.pipelinedock import Ui_PipeLineDock
    from ..designer.low.systemdock import Ui_SystemDock
    from ..designer.low.treedock import Ui_TreeDock


class DockShowCloseFilter(QtCore.QObject):
    _show = QtCore.Signal()
    _close = QtCore.Signal()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Type.Show and isinstance(
            source, QtWidgets.QDockWidget
        ):
            self._show.emit()

        if event.type() == QtCore.QEvent.Type.Close and isinstance(
            source, QtWidgets.QDockWidget
        ):
            self._close.emit()

        return False


class PipeLineDock(QtWidgets.QDockWidget, Ui_PipeLineDock):
    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, "Dockable", parent)
        Ui_PipeLineDock.__init__(self)
        self.setupUi(self)
        self.treeView.setIconSize(QtCore.QSize(12, 12))

        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)


class TreeDock(QtWidgets.QDockWidget, Ui_TreeDock):
    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, "Dockable", parent)
        Ui_TreeDock.__init__(self)
        self.setupUi(self)
        self.treeWidget.setIconSize(QtCore.QSize(12, 12))

        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)


class ListDock(QtWidgets.QDockWidget, Ui_ListDock):
    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, "Dockable", parent)
        Ui_ListDock.__init__(self)
        self.setupUi(self)

        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)

    def _get_list_values(self):
        items = []

        for index in range(self.listWidget.count()):
            items.append(self.listWidget.item(index))

        values = [str(i.text()) for i in items]

        return values


class LogDock(QtWidgets.QDockWidget, Ui_SystemDock):
    def __init__(self, parent=None, max_lines=1e5 - 1):
        QtWidgets.QDockWidget.__init__(self, "Dockable", parent)
        Ui_SystemDock.__init__(self)

        self._init_ui()
        self._set_max_lines(max_lines)

        self._showclose_filter = DockShowCloseFilter(self)
        self.installEventFilter(self._showclose_filter)

    def _init_ui(self):
        self.setupUi(self)

        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.ColorRole.Base, bgc)
        textc = QtGui.QColor(255, 255, 255)
        pal.setColor(QtGui.QPalette.ColorRole.Text, textc)

        self._console = QtWidgets.QPlainTextEdit(self)
        self._console.setPalette(pal)
        self._console.setReadOnly(True)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.addWidget(self._console)
        self.verticalLayout.addLayout(self._layout)

        XStream.stdout().messageWritten.connect(self._add_text)
        XStream.stderr().messageWritten.connect(self._add_text)

    def _set_max_lines(self, max_lines):
        self._console.setMaximumBlockCount(max_lines)

    @QtCore.Slot(str)
    def _add_text(self, arg1):
        self._console.appendPlainText(arg1)
        self._console.moveCursor(QtGui.QTextCursor.MoveOperation.End)
