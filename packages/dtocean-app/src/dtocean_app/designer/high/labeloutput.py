# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\labeloutput.ui'
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

class Ui_LabelOutput(object):
    def setupUi(self, LabelOutput):
        LabelOutput.setObjectName(_fromUtf8("LabelOutput"))
        LabelOutput.resize(750, 121)
        self.verticalLayout = QtGui.QVBoxLayout(LabelOutput)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.staticLabel = QtGui.QLabel(LabelOutput)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.staticLabel.sizePolicy().hasHeightForWidth())
        self.staticLabel.setSizePolicy(sizePolicy)
        self.staticLabel.setMinimumSize(QtCore.QSize(200, 0))
        self.staticLabel.setObjectName(_fromUtf8("staticLabel"))
        self.horizontalLayout.addWidget(self.staticLabel)
        self.valueLabel = QtGui.QLabel(LabelOutput)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.valueLabel.sizePolicy().hasHeightForWidth())
        self.valueLabel.setSizePolicy(sizePolicy)
        self.valueLabel.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.valueLabel.setObjectName(_fromUtf8("valueLabel"))
        self.horizontalLayout.addWidget(self.valueLabel)
        self.unitsLabel = QtGui.QLabel(LabelOutput)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.unitsLabel.sizePolicy().hasHeightForWidth())
        self.unitsLabel.setSizePolicy(sizePolicy)
        self.unitsLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.unitsLabel.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.unitsLabel.setObjectName(_fromUtf8("unitsLabel"))
        self.horizontalLayout.addWidget(self.unitsLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(20, 86, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(LabelOutput)
        QtCore.QMetaObject.connectSlotsByName(LabelOutput)

    def retranslateUi(self, LabelOutput):
        LabelOutput.setWindowTitle(_translate("LabelOutput", "Form", None))
        self.staticLabel.setText(_translate("LabelOutput", "Current value:", None))
        self.valueLabel.setText(_translate("LabelOutput", "None", None))
        self.unitsLabel.setText(_translate("LabelOutput", "(unit)", None))

