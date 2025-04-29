# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\plotmanager.ui'
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

class Ui_PlotManagerWidget(object):
    def setupUi(self, PlotManagerWidget):
        PlotManagerWidget.setObjectName(_fromUtf8("PlotManagerWidget"))
        PlotManagerWidget.resize(679, 216)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlotManagerWidget.sizePolicy().hasHeightForWidth())
        PlotManagerWidget.setSizePolicy(sizePolicy)
        PlotManagerWidget.setMinimumSize(QtCore.QSize(350, 0))
        self.verticalLayout = QtGui.QVBoxLayout(PlotManagerWidget)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.headingLabel = QtGui.QLabel(PlotManagerWidget)
        self.headingLabel.setTextFormat(QtCore.Qt.RichText)
        self.headingLabel.setObjectName(_fromUtf8("headingLabel"))
        self.verticalLayout.addWidget(self.headingLabel)
        self.line = QtGui.QFrame(PlotManagerWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(PlotManagerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(65, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.plotBox = QtGui.QComboBox(PlotManagerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotBox.sizePolicy().hasHeightForWidth())
        self.plotBox.setSizePolicy(sizePolicy)
        self.plotBox.setMinimumSize(QtCore.QSize(75, 0))
        self.plotBox.setObjectName(_fromUtf8("plotBox"))
        self.horizontalLayout.addWidget(self.plotBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(PlotManagerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(65, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.pathEdit = QtGui.QLineEdit(PlotManagerWidget)
        self.pathEdit.setObjectName(_fromUtf8("pathEdit"))
        self.horizontalLayout_2.addWidget(self.pathEdit)
        self.getPathButton = QtGui.QToolButton(PlotManagerWidget)
        self.getPathButton.setObjectName(_fromUtf8("getPathButton"))
        self.horizontalLayout_2.addWidget(self.getPathButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_5 = QtGui.QLabel(PlotManagerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QtCore.QSize(0, 0))
        self.label_5.setText(_fromUtf8(""))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_3.addWidget(self.label_5)
        self.checkBox = QtGui.QCheckBox(PlotManagerWidget)
        self.checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.horizontalLayout_3.addWidget(self.checkBox)
        self.label_3 = QtGui.QLabel(PlotManagerWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.widthSpinBox = QtGui.QDoubleSpinBox(PlotManagerWidget)
        self.widthSpinBox.setEnabled(False)
        self.widthSpinBox.setObjectName(_fromUtf8("widthSpinBox"))
        self.horizontalLayout_3.addWidget(self.widthSpinBox)
        self.label_4 = QtGui.QLabel(PlotManagerWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_3.addWidget(self.label_4)
        self.heightSpinBox = QtGui.QDoubleSpinBox(PlotManagerWidget)
        self.heightSpinBox.setEnabled(False)
        self.heightSpinBox.setObjectName(_fromUtf8("heightSpinBox"))
        self.horizontalLayout_3.addWidget(self.heightSpinBox)
        self.label_6 = QtGui.QLabel(PlotManagerWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_3.addWidget(self.label_6)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem = QtGui.QSpacerItem(20, 80, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(PlotManagerWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.raise_()
        self.line.raise_()
        self.headingLabel.raise_()

        self.retranslateUi(PlotManagerWidget)
        QtCore.QMetaObject.connectSlotsByName(PlotManagerWidget)

    def retranslateUi(self, PlotManagerWidget):
        PlotManagerWidget.setWindowTitle(_translate("PlotManagerWidget", "Form", None))
        self.headingLabel.setText(_translate("PlotManagerWidget", "<html><head/><body><p><span style=\" font-weight:600;\">Plot Manager:</span></p></body></html>", None))
        self.label.setText(_translate("PlotManagerWidget", "Plot name: ", None))
        self.label_2.setText(_translate("PlotManagerWidget", "File path: ", None))
        self.getPathButton.setText(_translate("PlotManagerWidget", "...", None))
        self.checkBox.setText(_translate("PlotManagerWidget", "Custom size", None))
        self.label_3.setText(_translate("PlotManagerWidget", "Width", None))
        self.label_4.setText(_translate("PlotManagerWidget", "Height", None))
        self.label_6.setText(_translate("PlotManagerWidget", "(inches)", None))

