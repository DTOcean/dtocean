# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\boolselect.ui'
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

class Ui_BoolSelect(object):
    def setupUi(self, BoolSelect):
        BoolSelect.setObjectName(_fromUtf8("BoolSelect"))
        BoolSelect.resize(694, 200)
        self.verticalLayout = QtGui.QVBoxLayout(BoolSelect)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.staticLabel = QtGui.QLabel(BoolSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.staticLabel.sizePolicy().hasHeightForWidth())
        self.staticLabel.setSizePolicy(sizePolicy)
        self.staticLabel.setMinimumSize(QtCore.QSize(200, 0))
        self.staticLabel.setObjectName(_fromUtf8("staticLabel"))
        self.gridLayout.addWidget(self.staticLabel, 0, 0, 1, 1)
        self.valueLabel = QtGui.QLabel(BoolSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.valueLabel.sizePolicy().hasHeightForWidth())
        self.valueLabel.setSizePolicy(sizePolicy)
        self.valueLabel.setObjectName(_fromUtf8("valueLabel"))
        self.gridLayout.addWidget(self.valueLabel, 0, 1, 1, 2)
        self.questionLabel = QtGui.QLabel(BoolSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.questionLabel.sizePolicy().hasHeightForWidth())
        self.questionLabel.setSizePolicy(sizePolicy)
        self.questionLabel.setMinimumSize(QtCore.QSize(200, 0))
        self.questionLabel.setObjectName(_fromUtf8("questionLabel"))
        self.gridLayout.addWidget(self.questionLabel, 1, 0, 1, 1)
        self.checkBox = QtGui.QCheckBox(BoolSelect)
        self.checkBox.setText(_fromUtf8(""))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 86, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(BoolSelect)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(BoolSelect)
        QtCore.QMetaObject.connectSlotsByName(BoolSelect)

    def retranslateUi(self, BoolSelect):
        BoolSelect.setWindowTitle(_translate("BoolSelect", "Form", None))
        self.staticLabel.setText(_translate("BoolSelect", "Current value:", None))
        self.valueLabel.setText(_translate("BoolSelect", "None", None))
        self.questionLabel.setText(_translate("BoolSelect", "Select if True:", None))

