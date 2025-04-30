# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer\shared\details.ui'
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


class Ui_DetailsWidget(object):
    def setupUi(self, DetailsWidget):
        DetailsWidget.setObjectName(_fromUtf8("DetailsWidget"))
        DetailsWidget.resize(518, 208)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            DetailsWidget.sizePolicy().hasHeightForWidth()
        )
        DetailsWidget.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DetailsWidget)
        self.verticalLayout_2.setSizeConstraint(
            QtGui.QLayout.SetDefaultConstraint
        )
        self.verticalLayout_2.setMargin(4)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.headingLabel = QtGui.QLabel(DetailsWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.headingLabel.sizePolicy().hasHeightForWidth()
        )
        self.headingLabel.setSizePolicy(sizePolicy)
        self.headingLabel.setTextFormat(QtCore.Qt.RichText)
        self.headingLabel.setObjectName(_fromUtf8("headingLabel"))
        self.verticalLayout_2.addWidget(self.headingLabel)
        self.line = QtGui.QFrame(DetailsWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_2.addWidget(self.line)
        self.scrollArea = QtGui.QScrollArea(DetailsWidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollArea.sizePolicy().hasHeightForWidth()
        )
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Raised)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        )
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 510, 168))
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setObjectName(
            _fromUtf8("scrollAreaWidgetContents")
        )
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setContentsMargins(2, 0, 0, 2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.staticLabel_1 = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.staticLabel_1.sizePolicy().hasHeightForWidth()
        )
        self.staticLabel_1.setSizePolicy(sizePolicy)
        self.staticLabel_1.setMinimumSize(QtCore.QSize(75, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.staticLabel_1.setFont(font)
        self.staticLabel_1.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        )
        self.staticLabel_1.setObjectName(_fromUtf8("staticLabel_1"))
        self.verticalLayout.addWidget(self.staticLabel_1)
        self.titleLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.titleLabel.sizePolicy().hasHeightForWidth()
        )
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.titleLabel.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        )
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setIndent(2)
        self.titleLabel.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse
        )
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.verticalLayout.addWidget(self.titleLabel)
        self.staticLabel_2 = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.staticLabel_2.sizePolicy().hasHeightForWidth()
        )
        self.staticLabel_2.setSizePolicy(sizePolicy)
        self.staticLabel_2.setMinimumSize(QtCore.QSize(110, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.staticLabel_2.setFont(font)
        self.staticLabel_2.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        )
        self.staticLabel_2.setObjectName(_fromUtf8("staticLabel_2"))
        self.verticalLayout.addWidget(self.staticLabel_2)
        self.descriptionLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.descriptionLabel.sizePolicy().hasHeightForWidth()
        )
        self.descriptionLabel.setSizePolicy(sizePolicy)
        self.descriptionLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.descriptionLabel.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        )
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setIndent(2)
        self.descriptionLabel.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse
        )
        self.descriptionLabel.setObjectName(_fromUtf8("descriptionLabel"))
        self.verticalLayout.addWidget(self.descriptionLabel)
        spacerItem = QtGui.QSpacerItem(
            20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)
        self.titleLabel.raise_()
        self.staticLabel_2.raise_()
        self.descriptionLabel.raise_()
        self.staticLabel_1.raise_()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)

        self.retranslateUi(DetailsWidget)
        QtCore.QMetaObject.connectSlotsByName(DetailsWidget)

    def retranslateUi(self, DetailsWidget):
        DetailsWidget.setWindowTitle(
            _translate("DetailsWidget", "Details", None)
        )
        self.headingLabel.setText(
            _translate(
                "DetailsWidget",
                '<html><head/><body><p><span style=" font-weight:600;">Variable Details:</span></p></body></html>',
                None,
            )
        )
        self.staticLabel_1.setText(_translate("DetailsWidget", "Title:", None))
        self.titleLabel.setText(_translate("DetailsWidget", "TextLabel", None))
        self.staticLabel_2.setText(
            _translate("DetailsWidget", "Description:", None)
        )
        self.descriptionLabel.setText(
            _translate("DetailsWidget", "TextLabel", None)
        )
