# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\systemdock.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SystemDock(object):
    def setupUi(self, SystemDock):
        SystemDock.setObjectName(_fromUtf8("SystemDock"))
        SystemDock.resize(726, 268)
        SystemDock.setFeatures(QtGui.QDockWidget.DockWidgetClosable|QtGui.QDockWidget.DockWidgetMovable)
        SystemDock.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.dockWidgetContents = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setContentsMargins(0, 2, 2, 2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        SystemDock.setWidget(self.dockWidgetContents)

        self.retranslateUi(SystemDock)
        QtCore.QMetaObject.connectSlotsByName(SystemDock)

    def retranslateUi(self, SystemDock):
        SystemDock.setWindowTitle(_translate("SystemDock", "System", None))

