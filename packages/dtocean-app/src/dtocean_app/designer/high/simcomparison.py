# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\high\simcomparison.ui'
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

class Ui_SimComparisonWidget(object):
    def setupUi(self, SimComparisonWidget):
        SimComparisonWidget.setObjectName(_fromUtf8("SimComparisonWidget"))
        SimComparisonWidget.resize(439, 189)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SimComparisonWidget.sizePolicy().hasHeightForWidth())
        SimComparisonWidget.setSizePolicy(sizePolicy)
        SimComparisonWidget.setMinimumSize(QtCore.QSize(320, 0))
        self.verticalLayout = QtGui.QVBoxLayout(SimComparisonWidget)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.headingLabel = QtGui.QLabel(SimComparisonWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.headingLabel.setFont(font)
        self.headingLabel.setTextFormat(QtCore.Qt.PlainText)
        self.headingLabel.setObjectName(_fromUtf8("headingLabel"))
        self.verticalLayout.addWidget(self.headingLabel)
        self.line = QtGui.QFrame(SimComparisonWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.topHorizontalLayout = QtGui.QHBoxLayout()
        self.topHorizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.topHorizontalLayout.setObjectName(_fromUtf8("topHorizontalLayout"))
        self.label_3 = QtGui.QLabel(SimComparisonWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(50, 0))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.topHorizontalLayout.addWidget(self.label_3)
        self.plotButton = QtGui.QRadioButton(SimComparisonWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotButton.sizePolicy().hasHeightForWidth())
        self.plotButton.setSizePolicy(sizePolicy)
        self.plotButton.setMinimumSize(QtCore.QSize(75, 0))
        self.plotButton.setChecked(True)
        self.plotButton.setObjectName(_fromUtf8("plotButton"))
        self.modeButtonGroup = QtGui.QButtonGroup(SimComparisonWidget)
        self.modeButtonGroup.setObjectName(_fromUtf8("modeButtonGroup"))
        self.modeButtonGroup.addButton(self.plotButton)
        self.topHorizontalLayout.addWidget(self.plotButton)
        self.dataButton = QtGui.QRadioButton(SimComparisonWidget)
        self.dataButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataButton.sizePolicy().hasHeightForWidth())
        self.dataButton.setSizePolicy(sizePolicy)
        self.dataButton.setMinimumSize(QtCore.QSize(75, 0))
        self.dataButton.setObjectName(_fromUtf8("dataButton"))
        self.modeButtonGroup.addButton(self.dataButton)
        self.topHorizontalLayout.addWidget(self.dataButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.topHorizontalLayout.addItem(spacerItem)
        self.strategyBox = QtGui.QCheckBox(SimComparisonWidget)
        self.strategyBox.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strategyBox.sizePolicy().hasHeightForWidth())
        self.strategyBox.setSizePolicy(sizePolicy)
        self.strategyBox.setMinimumSize(QtCore.QSize(150, 0))
        self.strategyBox.setMaximumSize(QtCore.QSize(150, 16777215))
        self.strategyBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.strategyBox.setChecked(True)
        self.strategyBox.setObjectName(_fromUtf8("strategyBox"))
        self.topHorizontalLayout.addWidget(self.strategyBox)
        self.verticalLayout.addLayout(self.topHorizontalLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 2, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.bottomHorizontalLayout = QtGui.QHBoxLayout()
        self.bottomHorizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.bottomHorizontalLayout.setObjectName(_fromUtf8("bottomHorizontalLayout"))
        self.label_2 = QtGui.QLabel(SimComparisonWidget)
        self.label_2.setMinimumSize(QtCore.QSize(65, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.bottomHorizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.bottomHorizontalLayout)
        self.middleHorizontalLayout = QtGui.QHBoxLayout()
        self.middleHorizontalLayout.setObjectName(_fromUtf8("middleHorizontalLayout"))
        self.label_4 = QtGui.QLabel(SimComparisonWidget)
        self.label_4.setMinimumSize(QtCore.QSize(65, 0))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.middleHorizontalLayout.addWidget(self.label_4)
        self.verticalLayout.addLayout(self.middleHorizontalLayout)
        spacerItem2 = QtGui.QSpacerItem(20, 80, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(SimComparisonWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.raise_()
        self.line.raise_()
        self.headingLabel.raise_()

        self.retranslateUi(SimComparisonWidget)
        QtCore.QMetaObject.connectSlotsByName(SimComparisonWidget)

    def retranslateUi(self, SimComparisonWidget):
        SimComparisonWidget.setWindowTitle(_translate("SimComparisonWidget", "Form", None))
        self.headingLabel.setText(_translate("SimComparisonWidget", "Simulation Comparison:", None))
        self.label_3.setText(_translate("SimComparisonWidget", "Mode:", None))
        self.plotButton.setText(_translate("SimComparisonWidget", "PLOT", None))
        self.dataButton.setText(_translate("SimComparisonWidget", "DATA", None))
        self.strategyBox.setText(_translate("SimComparisonWidget", "Ignore Strategy", None))
        self.label_2.setText(_translate("SimComparisonWidget", "Variable:", None))
        self.label_4.setText(_translate("SimComparisonWidget", "Module:", None))

