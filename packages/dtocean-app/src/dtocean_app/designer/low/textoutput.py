# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\textoutput.ui'
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

class Ui_TextOutput(object):
    def setupUi(self, TextOutput):
        TextOutput.setObjectName(_fromUtf8("TextOutput"))
        TextOutput.resize(750, 121)
        self.verticalLayout = QtGui.QVBoxLayout(TextOutput)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.textBrowser = QtGui.QTextBrowser(TextOutput)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)

        self.retranslateUi(TextOutput)
        QtCore.QMetaObject.connectSlotsByName(TextOutput)

    def retranslateUi(self, TextOutput):
        TextOutput.setWindowTitle(_translate("TextOutput", "Form", None))

