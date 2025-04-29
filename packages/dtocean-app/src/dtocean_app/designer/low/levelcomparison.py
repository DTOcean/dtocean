# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\low\levelcomparison.ui'
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

class Ui_LevelComparisonWidget(object):
    def setupUi(self, LevelComparisonWidget):
        LevelComparisonWidget.setObjectName(_fromUtf8("LevelComparisonWidget"))
        LevelComparisonWidget.resize(320, 192)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LevelComparisonWidget.sizePolicy().hasHeightForWidth())
        LevelComparisonWidget.setSizePolicy(sizePolicy)
        LevelComparisonWidget.setMinimumSize(QtCore.QSize(320, 0))
        self.verticalLayout = QtGui.QVBoxLayout(LevelComparisonWidget)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.headingLabel = QtGui.QLabel(LevelComparisonWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.headingLabel.setFont(font)
        self.headingLabel.setTextFormat(QtCore.Qt.PlainText)
        self.headingLabel.setObjectName(_fromUtf8("headingLabel"))
        self.verticalLayout.addWidget(self.headingLabel)
        self.line = QtGui.QFrame(LevelComparisonWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.topHorizontalLayout = QtGui.QHBoxLayout()
        self.topHorizontalLayout.setObjectName(_fromUtf8("topHorizontalLayout"))
        self.label_3 = QtGui.QLabel(LevelComparisonWidget)
        self.label_3.setMinimumSize(QtCore.QSize(40, 0))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.topHorizontalLayout.addWidget(self.label_3)
        self.plotButton = QtGui.QRadioButton(LevelComparisonWidget)
        self.plotButton.setMinimumSize(QtCore.QSize(55, 0))
        self.plotButton.setChecked(True)
        self.plotButton.setObjectName(_fromUtf8("plotButton"))
        self.modeButtonGroup = QtGui.QButtonGroup(LevelComparisonWidget)
        self.modeButtonGroup.setObjectName(_fromUtf8("modeButtonGroup"))
        self.modeButtonGroup.addButton(self.plotButton)
        self.topHorizontalLayout.addWidget(self.plotButton)
        self.dataButton = QtGui.QRadioButton(LevelComparisonWidget)
        self.dataButton.setEnabled(True)
        self.dataButton.setMinimumSize(QtCore.QSize(55, 0))
        self.dataButton.setObjectName(_fromUtf8("dataButton"))
        self.modeButtonGroup.addButton(self.dataButton)
        self.topHorizontalLayout.addWidget(self.dataButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.topHorizontalLayout.addItem(spacerItem)
        self.strategyBox = QtGui.QCheckBox(LevelComparisonWidget)
        self.strategyBox.setEnabled(False)
        self.strategyBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.strategyBox.setChecked(True)
        self.strategyBox.setObjectName(_fromUtf8("strategyBox"))
        self.topHorizontalLayout.addWidget(self.strategyBox)
        self.verticalLayout.addLayout(self.topHorizontalLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 2, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.bottomHorizontalLayout = QtGui.QHBoxLayout()
        self.bottomHorizontalLayout.setObjectName(_fromUtf8("bottomHorizontalLayout"))
        self.label_2 = QtGui.QLabel(LevelComparisonWidget)
        self.label_2.setMinimumSize(QtCore.QSize(65, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.bottomHorizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.bottomHorizontalLayout)
        spacerItem2 = QtGui.QSpacerItem(20, 80, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(LevelComparisonWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.raise_()
        self.line.raise_()
        self.headingLabel.raise_()

        self.retranslateUi(LevelComparisonWidget)
        QtCore.QMetaObject.connectSlotsByName(LevelComparisonWidget)

    def retranslateUi(self, LevelComparisonWidget):
        LevelComparisonWidget.setWindowTitle(_translate("LevelComparisonWidget", "Form", None))
        self.headingLabel.setText(_translate("LevelComparisonWidget", "Module Comparison:", None))
        self.label_3.setText(_translate("LevelComparisonWidget", "Mode:", None))
        self.plotButton.setText(_translate("LevelComparisonWidget", "PLOT", None))
        self.dataButton.setText(_translate("LevelComparisonWidget", "DATA", None))
        self.strategyBox.setText(_translate("LevelComparisonWidget", "Ignore Strategy", None))
        self.label_2.setText(_translate("LevelComparisonWidget", "Variable:", None))

