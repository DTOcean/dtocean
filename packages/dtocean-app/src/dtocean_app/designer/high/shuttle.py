# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\shuttle.ui'
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

class Ui_ShuttleDialog(object):
    def setupUi(self, ShuttleDialog):
        ShuttleDialog.setObjectName(_fromUtf8("ShuttleDialog"))
        ShuttleDialog.resize(648, 348)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ShuttleDialog.sizePolicy().hasHeightForWidth())
        ShuttleDialog.setSizePolicy(sizePolicy)
        ShuttleDialog.setMinimumSize(QtCore.QSize(560, 252))
        ShuttleDialog.setMaximumSize(QtCore.QSize(100000, 100000))
        self.verticalLayout_2 = QtGui.QVBoxLayout(ShuttleDialog)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.verticalLayout_2.setSpacing(9)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(14)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.leftLabel = QtGui.QLabel(ShuttleDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leftLabel.sizePolicy().hasHeightForWidth())
        self.leftLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI Semibold"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.leftLabel.setFont(font)
        self.leftLabel.setStyleSheet(_fromUtf8("font: 75 10pt \"Segoe UI Semibold\";"))
        self.leftLabel.setText(_fromUtf8(""))
        self.leftLabel.setTextFormat(QtCore.Qt.AutoText)
        self.leftLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.leftLabel.setObjectName(_fromUtf8("leftLabel"))
        self.gridLayout.addWidget(self.leftLabel, 0, 0, 1, 1)
        self.blankLabel = QtGui.QLabel(ShuttleDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.blankLabel.sizePolicy().hasHeightForWidth())
        self.blankLabel.setSizePolicy(sizePolicy)
        self.blankLabel.setText(_fromUtf8(""))
        self.blankLabel.setObjectName(_fromUtf8("blankLabel"))
        self.gridLayout.addWidget(self.blankLabel, 0, 1, 1, 1)
        self.rightLabel = QtGui.QLabel(ShuttleDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rightLabel.sizePolicy().hasHeightForWidth())
        self.rightLabel.setSizePolicy(sizePolicy)
        self.rightLabel.setStyleSheet(_fromUtf8("font: 75 10pt \"Segoe UI Semibold\";"))
        self.rightLabel.setText(_fromUtf8(""))
        self.rightLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.rightLabel.setObjectName(_fromUtf8("rightLabel"))
        self.gridLayout.addWidget(self.rightLabel, 0, 2, 1, 1)
        self.leftListView = QtGui.QListView(ShuttleDialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.leftListView.setFont(font)
        self.leftListView.setFrameShape(QtGui.QFrame.Box)
        self.leftListView.setFrameShadow(QtGui.QFrame.Plain)
        self.leftListView.setLineWidth(1)
        self.leftListView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.leftListView.setObjectName(_fromUtf8("leftListView"))
        self.gridLayout.addWidget(self.leftListView, 2, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.addButton = QtGui.QPushButton(ShuttleDialog)
        self.addButton.setObjectName(_fromUtf8("addButton"))
        self.verticalLayout.addWidget(self.addButton)
        self.removeButton = QtGui.QPushButton(ShuttleDialog)
        self.removeButton.setObjectName(_fromUtf8("removeButton"))
        self.verticalLayout.addWidget(self.removeButton)
        self.gridLayout.addLayout(self.verticalLayout, 2, 1, 1, 1)
        self.rightListView = QtGui.QListView(ShuttleDialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.rightListView.setFont(font)
        self.rightListView.setFrameShape(QtGui.QFrame.Box)
        self.rightListView.setFrameShadow(QtGui.QFrame.Plain)
        self.rightListView.setLineWidth(1)
        self.rightListView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.rightListView.setObjectName(_fromUtf8("rightListView"))
        self.gridLayout.addWidget(self.rightListView, 2, 2, 1, 1)
        self.line = QtGui.QFrame(ShuttleDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)
        self.line_2 = QtGui.QFrame(ShuttleDialog)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(ShuttleDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(ShuttleDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ShuttleDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ShuttleDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ShuttleDialog)

    def retranslateUi(self, ShuttleDialog):
        ShuttleDialog.setWindowTitle(_translate("ShuttleDialog", "Dialog", None))
        self.addButton.setText(_translate("ShuttleDialog", "Add", None))
        self.removeButton.setText(_translate("ShuttleDialog", "Remove", None))

