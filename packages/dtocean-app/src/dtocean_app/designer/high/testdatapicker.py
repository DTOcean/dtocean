# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\high\testdatapicker.ui'
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

class Ui_TestDataPicker(object):
    def setupUi(self, TestDataPicker):
        TestDataPicker.setObjectName(_fromUtf8("TestDataPicker"))
        TestDataPicker.resize(565, 135)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TestDataPicker.sizePolicy().hasHeightForWidth())
        TestDataPicker.setSizePolicy(sizePolicy)
        TestDataPicker.setMinimumSize(QtCore.QSize(0, 135))
        TestDataPicker.setMaximumSize(QtCore.QSize(16777215, 135))
        self.verticalLayout = QtGui.QVBoxLayout(TestDataPicker)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(TestDataPicker)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setStyleSheet(_fromUtf8(""))
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.pathLineEdit = QtGui.QLineEdit(TestDataPicker)
        self.pathLineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pathLineEdit.setObjectName(_fromUtf8("pathLineEdit"))
        self.gridLayout.addWidget(self.pathLineEdit, 0, 1, 1, 1)
        self.overwriteBox = QtGui.QCheckBox(TestDataPicker)
        self.overwriteBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.overwriteBox.setObjectName(_fromUtf8("overwriteBox"))
        self.gridLayout.addWidget(self.overwriteBox, 1, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(10, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(TestDataPicker)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(TestDataPicker)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TestDataPicker.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TestDataPicker.reject)
        QtCore.QMetaObject.connectSlotsByName(TestDataPicker)

    def retranslateUi(self, TestDataPicker):
        TestDataPicker.setWindowTitle(_translate("TestDataPicker", "Load Test Data", None))
        self.label.setText(_translate("TestDataPicker", "Test data path: ", None))
        self.overwriteBox.setText(_translate("TestDataPicker", "Overwrite existing data:", None))

