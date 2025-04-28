import re

import numpy
from pandas import Timestamp, isnull
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
)

from ..models.SupportedDtypes import SupportedDtypes


class DefaultValueValidator(QtGui.QValidator):
    def __init__(self, parent=None):
        super(DefaultValueValidator, self).__init__(parent)
        self.dtype = None

        self.intPattern = re.compile(r"[-+]?\d+")
        self.uintPattern = re.compile(r"\d+")
        self.floatPattern = re.compile(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)")
        self.boolPattern = re.compile("(1|t|0|f){1}$")

    @Slot(numpy.dtype)  # type: ignore
    def validateType(self, dtype):
        self.dtype = dtype

    def fixup(self, string):
        pass

    def validate(self, s, pos):
        if not s:
            # s is emtpy
            return (QtGui.QValidator.State.Acceptable, pos)

        if self.dtype in SupportedDtypes.strTypes():
            return (QtGui.QValidator.State.Acceptable, pos)

        elif self.dtype in SupportedDtypes.boolTypes():
            match = re.match(self.boolPattern, s)
            if match:
                return (QtGui.QValidator.State.Acceptable, pos)
            else:
                return (QtGui.QValidator.State.Invalid, pos)

        elif self.dtype in SupportedDtypes.datetimeTypes():
            try:
                Timestamp(s)
            except ValueError:
                return (QtGui.QValidator.State.Intermediate, pos)
            return (QtGui.QValidator.State.Acceptable, pos)

        else:
            dtypeInfo = None
            if self.dtype in SupportedDtypes.intTypes():
                match = re.search(self.intPattern, s)
                if match:
                    try:
                        value = int(match.string)
                    except ValueError:
                        return (QtGui.QValidator.State.Invalid, pos)

                    dtypeInfo = numpy.iinfo(self.dtype)  # type: ignore

            elif self.dtype in SupportedDtypes.uintTypes():
                match = re.search(self.uintPattern, s)
                if match:
                    try:
                        value = int(match.string)
                    except ValueError:
                        return (QtGui.QValidator.State.Invalid, pos)

                    dtypeInfo = numpy.iinfo(self.dtype)  # type: ignore

            elif self.dtype in SupportedDtypes.floatTypes():
                match = re.search(self.floatPattern, s)
                if match:
                    try:
                        value = float(match.string)
                    except ValueError:
                        return (QtGui.QValidator.State.Invalid, pos)

                    dtypeInfo = numpy.finfo(self.dtype)  # type: ignore

            if dtypeInfo is not None:
                if value >= dtypeInfo.min and value <= dtypeInfo.max:
                    return (QtGui.QValidator.State.Acceptable, pos)
                else:
                    return (QtGui.QValidator.State.Invalid, pos)
            else:
                return (QtGui.QValidator.State.Invalid, pos)

        return (QtGui.QValidator.State.Invalid, pos)


class AddAttributesDialog(QtWidgets.QDialog):
    accepted = Signal(str, object, object)

    def __init__(self, parent=None):
        super(AddAttributesDialog, self).__init__(parent)

        self.initUi()

    def initUi(self):
        self.setModal(True)
        self.resize(303, 168)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.setSizePolicy(sizePolicy)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        self.dialogHeading = QtWidgets.QLabel(
            self.tr("Add a new attribute column"), self
        )

        self.gridLayout = QtWidgets.QGridLayout()

        self.columnNameLineEdit = QtWidgets.QLineEdit(self)
        self.columnNameLabel = QtWidgets.QLabel(self.tr("Name"), self)
        self.dataTypeComboBox = QtWidgets.QComboBox(self)

        self.dataTypeComboBox.addItems(SupportedDtypes.names())

        self.columnTypeLabel = QtWidgets.QLabel(self.tr("Type"), self)
        self.defaultValueLineEdit = QtWidgets.QLineEdit(self)
        self.lineEditValidator = DefaultValueValidator(self)
        self.defaultValueLineEdit.setValidator(self.lineEditValidator)
        self.defaultValueLabel = QtWidgets.QLabel(
            self.tr("Inital Value(s)"), self
        )

        self.gridLayout.addWidget(self.columnNameLabel, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.columnNameLineEdit, 0, 1, 1, 1)

        self.gridLayout.addWidget(self.columnTypeLabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.dataTypeComboBox, 1, 1, 1, 1)

        self.gridLayout.addWidget(self.defaultValueLabel, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.defaultValueLineEdit, 2, 1, 1, 1)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )

        self.verticalLayout.addWidget(self.dialogHeading)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.dataTypeComboBox.currentIndexChanged.connect(
            self.updateValidatorDtype
        )
        self.updateValidatorDtype(self.dataTypeComboBox.currentIndex())

    def accept(self):
        super(AddAttributesDialog, self).accept()

        newColumn = self.columnNameLineEdit.text()
        dtype = SupportedDtypes.dtype(self.dataTypeComboBox.currentText())
        assert dtype is not None

        defaultValue = self.defaultValueLineEdit.text()

        try:
            if dtype in (
                SupportedDtypes.intTypes() + SupportedDtypes.uintTypes()
            ):
                defaultValue = int(defaultValue)
            elif dtype in SupportedDtypes.floatTypes():
                defaultValue = float(defaultValue)
            elif dtype in SupportedDtypes.boolTypes():
                defaultValue = defaultValue.lower() in ["t", "1"]
            elif dtype in SupportedDtypes.datetimeTypes():
                defaultValue = Timestamp(defaultValue)
                if isnull(defaultValue):
                    defaultValue = Timestamp("")
            else:
                defaultValue = dtype.type()
        except ValueError:
            defaultValue = dtype.type()

        self.accepted.emit(newColumn, dtype, defaultValue)

    @Slot(int)  # type: ignore
    def updateValidatorDtype(self, index):
        (dtype, name) = SupportedDtypes.tupleAt(index)  # type: ignore
        self.defaultValueLineEdit.clear()
        self.lineEditValidator.validateType(dtype)


class RemoveAttributesDialog(QtWidgets.QDialog):
    accepted = Signal(list)

    def __init__(self, columns, parent=None):
        super(RemoveAttributesDialog, self).__init__(parent)
        self.columns = columns
        self.initUi()

    def initUi(self):
        self.setWindowTitle(self.tr("Remove Attributes"))
        self.setModal(True)
        self.resize(366, 274)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.setSizePolicy(sizePolicy)

        self.gridLayout = QtWidgets.QGridLayout(self)

        self.dialogHeading = QtWidgets.QLabel(
            self.tr("Select the attribute column(s) which shall be removed"),
            self,
        )

        self.listView = QtWidgets.QListView(self)

        model = QtGui.QStandardItemModel()
        for column in self.columns:
            item = QtGui.QStandardItem(column)
            model.appendRow(item)

        self.listView.setModel(model)
        self.listView.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )

        self.gridLayout.addWidget(self.dialogHeading, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.listView, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def accept(self):
        selection = self.listView.selectedIndexes()
        names = []
        for index in selection:
            position = index.row()
            names.append((position, index.data(Qt.ItemDataRole.DisplayRole)))

        super(RemoveAttributesDialog, self).accept()
        self.accepted.emit(names)
