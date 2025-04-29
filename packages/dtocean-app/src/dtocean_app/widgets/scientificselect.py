# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2022 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Thu Apr 23 12:51:14 2015

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import re

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QValidator, QDoubleSpinBox

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
    
# Fork of jdreaver/scientificspin.py
# https://gist.github.com/jdreaver/0be2e44981159d0854f5

_float_re = re.compile(r'(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)')


class ScientificDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, *args, **kwargs):
        super(QDoubleSpinBox, self).__init__(*args, **kwargs)
        self.setMinimum(-1.e+18)
        self.setMaximum(1.e+18)
        self.setDecimals(323)

    def validate(self, text, position):
        
        string = str(text)

        if valid_float_string(string):
            return (QValidator.Acceptable, position)
        if string == "" or string[position - 1] in 'e.-+':
            return (QValidator.Intermediate, position)

        return (QValidator.Invalid, position)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        return format_float(value)

    def stepBy(self, steps):
        text = self.cleanText()
        groups = _float_re.search(text).groups()
        decimal = float(groups[1])
        decimal += steps
        new_string = "{:g}".format(decimal) + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)


class Ui_ScientificSelect(object):
    def setupUi(self, FloatSelect):
        FloatSelect.setObjectName(_fromUtf8("FloatSelect"))
        FloatSelect.resize(750, 200)
        self.verticalLayout = QtGui.QVBoxLayout(FloatSelect)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.staticLabel = QtGui.QLabel(FloatSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                self.staticLabel.sizePolicy().hasHeightForWidth())
        self.staticLabel.setSizePolicy(sizePolicy)
        self.staticLabel.setMinimumSize(QtCore.QSize(200, 0))
        self.staticLabel.setObjectName(_fromUtf8("staticLabel"))
        self.gridLayout.addWidget(self.staticLabel, 0, 0, 1, 1)
        self.valueLabel = QtGui.QLabel(FloatSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                self.valueLabel.sizePolicy().hasHeightForWidth())
        self.valueLabel.setSizePolicy(sizePolicy)
        self.valueLabel.setObjectName(_fromUtf8("valueLabel"))
        self.gridLayout.addWidget(self.valueLabel, 0, 1, 1, 2)
        self.questionLabel = QtGui.QLabel(FloatSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                self.questionLabel.sizePolicy().hasHeightForWidth())
        self.questionLabel.setSizePolicy(sizePolicy)
        self.questionLabel.setMinimumSize(QtCore.QSize(200, 0))
        self.questionLabel.setObjectName(_fromUtf8("questionLabel"))
        self.gridLayout.addWidget(self.questionLabel, 1, 0, 1, 1)
        self.unitsLabel = QtGui.QLabel(FloatSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                self.unitsLabel.sizePolicy().hasHeightForWidth())
        self.unitsLabel.setSizePolicy(sizePolicy)
        self.unitsLabel.setObjectName(_fromUtf8("unitsLabel"))
        self.gridLayout.addWidget(self.unitsLabel, 1, 2, 1, 1)
        self.doubleSpinBox = ScientificDoubleSpinBox(FloatSelect)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                self.doubleSpinBox.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox.setSizePolicy(sizePolicy)
        self.doubleSpinBox.setMinimumSize(QtCore.QSize(0, 0))
        self.doubleSpinBox.setKeyboardTracking(False)
        self.doubleSpinBox.setObjectName(_fromUtf8("doubleSpinBox"))
        self.gridLayout.addWidget(self.doubleSpinBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20,
                                       86,
                                       QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(FloatSelect)
        self.buttonBox.setStandardButtons(
                QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(FloatSelect)
        QtCore.QMetaObject.connectSlotsByName(FloatSelect)

    def retranslateUi(self, FloatSelect):
        FloatSelect.setWindowTitle(_translate("FloatSelect", "Form", None))
        self.staticLabel.setText(_translate("FloatSelect",
                                            "Current value:",
                                            None))
        self.valueLabel.setText(_translate("FloatSelect", "None", None))
        self.questionLabel.setText(_translate("FloatSelect",
                                              "Please enter a number:",
                                              None))
        self.unitsLabel.setText(_translate("FloatSelect", "(unit)", None))


def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


def format_float(value):
    """Modified form of the 'g' format specifier."""
    string = "{:g}".format(value).replace("e+", "e")
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string
