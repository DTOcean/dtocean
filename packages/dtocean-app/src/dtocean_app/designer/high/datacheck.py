# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\datacheck.ui'
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

class Ui_DataCheckDialog(object):
    def setupUi(self, DataCheckDialog):
        DataCheckDialog.setObjectName(_fromUtf8("DataCheckDialog"))
        DataCheckDialog.resize(600, 398)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DataCheckDialog.sizePolicy().hasHeightForWidth())
        DataCheckDialog.setSizePolicy(sizePolicy)
        DataCheckDialog.setMinimumSize(QtCore.QSize(600, 300))
        DataCheckDialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        DataCheckDialog.setSizeGripEnabled(False)
        self.verticalLayout = QtGui.QVBoxLayout(DataCheckDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(DataCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.resultLabel = QtGui.QLabel(DataCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resultLabel.sizePolicy().hasHeightForWidth())
        self.resultLabel.setSizePolicy(sizePolicy)
        self.resultLabel.setMinimumSize(QtCore.QSize(100, 0))
        self.resultLabel.setText(_fromUtf8(""))
        self.resultLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.resultLabel.setObjectName(_fromUtf8("resultLabel"))
        self.horizontalLayout.addWidget(self.resultLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(DataCheckDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        spacerItem = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.provideLabel = QtGui.QLabel(DataCheckDialog)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.provideLabel.setFont(font)
        self.provideLabel.setObjectName(_fromUtf8("provideLabel"))
        self.verticalLayout.addWidget(self.provideLabel)
        self.tableWidget = QtGui.QTableWidget(DataCheckDialog)
        self.tableWidget.setEnabled(False)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(175)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(175)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tableWidget)
        spacerItem1 = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(DataCheckDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DataCheckDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DataCheckDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DataCheckDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DataCheckDialog)

    def retranslateUi(self, DataCheckDialog):
        DataCheckDialog.setWindowTitle(_translate("DataCheckDialog", "Dialog", None))
        self.label.setText(_translate("DataCheckDialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Checking data requirements...</span></p></body></html>", None))
        self.provideLabel.setText(_translate("DataCheckDialog", "<html><head/><body><p><span style=\" font-size:8pt; font-weight:600;\">The following data is required and must be provided:</span></p></body></html>", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("DataCheckDialog", "Section", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("DataCheckDialog", "Branch", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("DataCheckDialog", "Item", None))

