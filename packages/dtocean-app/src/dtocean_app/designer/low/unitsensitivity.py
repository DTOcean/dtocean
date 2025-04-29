# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\unitsensitivity.ui'
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

class Ui_UnitSensitivityWidget(object):
    def setupUi(self, UnitSensitivityWidget):
        UnitSensitivityWidget.setObjectName(_fromUtf8("UnitSensitivityWidget"))
        UnitSensitivityWidget.resize(600, 450)
        self.horizontalLayout = QtGui.QHBoxLayout(UnitSensitivityWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.frame = QtGui.QFrame(UnitSensitivityWidget)
        self.frame.setMaximumSize(QtCore.QSize(600, 16777215))
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        spacerItem = QtGui.QSpacerItem(17, 13, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.frame)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 277, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout.addWidget(self.frame)
        spacerItem2 = QtGui.QSpacerItem(1, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.horizontalLayout.setStretch(0, 1)

        self.retranslateUi(UnitSensitivityWidget)
        QtCore.QMetaObject.connectSlotsByName(UnitSensitivityWidget)

    def retranslateUi(self, UnitSensitivityWidget):
        UnitSensitivityWidget.setWindowTitle(_translate("UnitSensitivityWidget", "Form", None))
        self.label_2.setText(_translate("UnitSensitivityWidget", "<html><head/><body><p>Select a variable from a module to vary. The range of values must be supplied using commas to separate them.</p><p>Note that the project may contain only one existing simulation.</p></body></html>", None))
        self.label.setText(_translate("UnitSensitivityWidget", "Module: ", None))
        self.label_3.setText(_translate("UnitSensitivityWidget", "Variable: ", None))
        self.label_4.setText(_translate("UnitSensitivityWidget", "Values: ", None))

