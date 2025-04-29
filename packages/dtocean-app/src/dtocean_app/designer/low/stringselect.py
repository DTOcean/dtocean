# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\stringselect.ui'
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

class Ui_StringSelect(object):
    def setupUi(self, StringSelect):
        StringSelect.setObjectName(_fromUtf8("StringSelect"))
        StringSelect.resize(750, 200)
        self.verticalLayout = QtGui.QVBoxLayout(StringSelect)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.staticLabel = QtGui.QLabel(StringSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.staticLabel.sizePolicy().hasHeightForWidth())
        self.staticLabel.setSizePolicy(sizePolicy)
        self.staticLabel.setMinimumSize(QtCore.QSize(200, 0))
        self.staticLabel.setObjectName(_fromUtf8("staticLabel"))
        self.gridLayout.addWidget(self.staticLabel, 0, 0, 1, 1)
        self.valueLabel = QtGui.QLabel(StringSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.valueLabel.sizePolicy().hasHeightForWidth())
        self.valueLabel.setSizePolicy(sizePolicy)
        self.valueLabel.setObjectName(_fromUtf8("valueLabel"))
        self.gridLayout.addWidget(self.valueLabel, 0, 1, 1, 2)
        self.questionLabel = QtGui.QLabel(StringSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.questionLabel.sizePolicy().hasHeightForWidth())
        self.questionLabel.setSizePolicy(sizePolicy)
        self.questionLabel.setMinimumSize(QtCore.QSize(200, 0))
        self.questionLabel.setObjectName(_fromUtf8("questionLabel"))
        self.gridLayout.addWidget(self.questionLabel, 1, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(StringSelect)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.unitsLabel = QtGui.QLabel(StringSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.unitsLabel.sizePolicy().hasHeightForWidth())
        self.unitsLabel.setSizePolicy(sizePolicy)
        self.unitsLabel.setObjectName(_fromUtf8("unitsLabel"))
        self.gridLayout.addWidget(self.unitsLabel, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 86, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(StringSelect)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(StringSelect)
        QtCore.QMetaObject.connectSlotsByName(StringSelect)

    def retranslateUi(self, StringSelect):
        StringSelect.setWindowTitle(_translate("StringSelect", "Form", None))
        self.staticLabel.setText(_translate("StringSelect", "Current value:", None))
        self.valueLabel.setText(_translate("StringSelect", "None", None))
        self.questionLabel.setText(_translate("StringSelect", "Please enter a string:", None))
        self.unitsLabel.setText(_translate("StringSelect", "(unit)", None))

