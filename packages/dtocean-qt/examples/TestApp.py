# -*- coding: utf-8 -*-
import sys

import pandas
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import (
    QAbstractItemModel,
    QMimeData,
    Signal,
    Slot,
)
from util import getCsvData, getRandomData

from dtocean_qt.pandas.excepthook import excepthook
from dtocean_qt.pandas.models.DataFrameModel import DataFrameModel
from dtocean_qt.pandas.models.DataSearch import DataSearch
from dtocean_qt.pandas.models.mime import PandasCellMimeType, PandasCellPayload
from dtocean_qt.pandas.views._ui import icons_rc  # noqa: F401
from dtocean_qt.pandas.views.CSVDialogs import CSVExportDialog, CSVImportDialog
from dtocean_qt.pandas.views.CustomDelegates import DtypeComboDelegate
from dtocean_qt.pandas.views.DataTableView import DataTableWidget

sys.excepthook = excepthook


class DropLineEdit(QtWidgets.QLineEdit):
    def __init__(self, text, parent=None):
        super(DropLineEdit, self).__init__(text, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """recieve a drag event and check if we want to accept or reject

        Args:
            event (QDragEnterEvent)
        """
        if event.mimeData().hasFormat(PandasCellMimeType):
            if event.mimeData().data().isValid():
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """process the dragged data

        Args:
            event (QDragEnterEvent)
        """
        super(DropLineEdit, self).dropEvent(event)
        mimeDataPayload = event.mimeData().data()
        self.setText("dropped column: {0}".format(mimeDataPayload.column))


class ComplexDropWidget(QtWidgets.QLineEdit):
    dropRecieved = Signal(QMimeData)

    def __init__(self, parent=None):
        super(ComplexDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """recieve a drag event and check if we want to accept or reject

        Args:
            event (QDragEnterEvent)
        """
        if event.mimeData().hasFormat(PandasCellMimeType):
            if event.mimeData().data().isValid():
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """process the dragged data

        Args:
            event (QDragEnterEvent)
        """
        self.dropRecieved.emit(event.mimeData())


class TestWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)
        self.resize(1680, 756)
        self.move(0, 0)

        self.df = pandas.DataFrame()
        self.dataModel = None

        #  init the data view's
        self.dataTableView = DataTableWidget(self)
        # self.dataTableView.setSortingEnabled(True)
        # self.dataTableView.setAlternatingRowColors(True)

        self.dataListView = QtWidgets.QListView(self)
        self.dataListView.setAlternatingRowColors(True)

        self.dataComboBox = QtWidgets.QComboBox(self)

        # make combobox to choose the model column for dataComboBox and dataListView
        self.chooseColumnComboBox = QtWidgets.QComboBox(self)

        self.buttonCsvData = QtWidgets.QPushButton("load csv data")
        self.buttonRandomData = QtWidgets.QPushButton("load random data")
        importDialog = CSVImportDialog(self)
        importDialog.load.connect(self.updateModel)
        self.buttonCsvData.clicked.connect(lambda: importDialog.show())
        self.buttonRandomData.clicked.connect(
            lambda: self.setDataFrame(getRandomData(rows=100, columns=100))
        )

        self.exportDialog = CSVExportDialog(self)

        self.buttonCSVExport = QtWidgets.QPushButton("export to csv")
        self.buttonCSVExport.clicked.connect(self._exportModel)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.buttonCsvData)
        self.buttonLayout.addWidget(self.buttonCSVExport)
        self.buttonLayout.addWidget(self.buttonRandomData)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.buttonLayout)

        self.mainLayout.addWidget(self.dataTableView)

        self.spinbox = QtWidgets.QSpinBox()
        self.mainLayout.addWidget(self.spinbox)
        self.spinbox.setMaximum(999999999)
        self.spinbox.setValue(999999999)

        self.rightLayout = QtWidgets.QVBoxLayout()
        self.chooseColumLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.rightLayout)
        self.rightLayout.addLayout(self.chooseColumLayout)
        self.chooseColumLayout.addWidget(QtWidgets.QLabel("Choose column:"))
        self.chooseColumLayout.addWidget(self.chooseColumnComboBox)
        self.rightLayout.addWidget(self.dataListView)
        self.rightLayout.addWidget(self.dataComboBox)

        self.tableViewColumnDtypes = QtWidgets.QTableView(self)
        self.rightLayout.addWidget(QtWidgets.QLabel("dtypes"))
        self.rightLayout.addWidget(self.tableViewColumnDtypes)
        self.buttonGoToColumn = QtWidgets.QPushButton("go to column")
        self.rightLayout.addWidget(self.buttonGoToColumn)
        self.buttonGoToColumn.clicked.connect(self.goToColumn)

        self.buttonSetFilter = QtWidgets.QPushButton("set filter")
        self.rightLayout.addWidget(self.buttonSetFilter)
        self.buttonSetFilter.clicked.connect(self.setFilter)
        self.buttonClearFilter = QtWidgets.QPushButton("clear filter")
        self.rightLayout.addWidget(self.buttonClearFilter)
        self.buttonClearFilter.clicked.connect(self.clearFilter)
        self.lineEditFilterCondition = QtWidgets.QLineEdit("freeSearch('am')")
        self.rightLayout.addWidget(self.lineEditFilterCondition)

        self.chooseColumnComboBox.currentIndexChanged.connect(
            self.setModelColumn
        )

        self.dataListView.mouseReleaseEvent = self.mouseReleaseEvent

        self.dropLineEdit = DropLineEdit("drop data from table here", self)
        self.rightLayout.addWidget(self.dropLineEdit)

        self.dropWidget = ComplexDropWidget(self)
        self.dropWidget.dropRecieved.connect(self.processDataDrops)
        self.rightLayout.addWidget(self.dropWidget)

    @Slot(QMimeData)
    def processDataDrops(self, mimeData):
        """if you have more complicated stuff to do and you want to match some models, might be possible like that"""
        mimeDataPayload = mimeData.data()
        if isinstance(mimeDataPayload, PandasCellPayload):
            if self.dataModel is not None:
                if hex(id(self.dataModel)) == mimeDataPayload.parentId:
                    self.dropWidget.setText(
                        "complex stuff done after drop event. {0}".format(
                            mimeDataPayload.column
                        )
                    )

    def setDataFrame(self, dataFrame):
        self.df = dataFrame
        dataModel = DataFrameModel()
        dataModel.setDataFrame(self.df)

        self.dataModel = dataModel

        self.dataListView.setModel(dataModel)
        self.dataTableView.setViewModel(dataModel)
        self.dataComboBox.setModel(dataModel)

        # self.dataTableView.resizeColumnsToContents()

        # create a simple item model for our choosing combobox
        columnModel = QtGui.QStandardItemModel()
        for column in self.df.columns:
            columnModel.appendRow(QtGui.QStandardItem(column))
        self.chooseColumnComboBox.setModel(columnModel)

        self.tableViewColumnDtypes.setModel(dataModel.columnDtypeModel())
        self.tableViewColumnDtypes.horizontalHeader().setDefaultSectionSize(200)
        self.tableViewColumnDtypes.setItemDelegateForColumn(
            1, DtypeComboDelegate(self.tableViewColumnDtypes)
        )
        dataModel.changingDtypeFailed.connect(self.changeColumnValue)

    @Slot()
    def _exportModel(self):
        model = self.dataTableView.view().model()
        self.exportDialog.setExportModel(model)
        self.exportDialog.show()

    @Slot(QAbstractItemModel)
    def updateModel(self, model):
        self.dataModel = model
        self.dataListView.setModel(model)
        self.dataTableView.setViewModel(model)
        self.dataComboBox.setModel(model)

        self.tableViewColumnDtypes.setModel(model.columnDtypeModel())

    def setModelColumn(self, index):
        self.dataListView.setModelColumn(index)
        self.dataComboBox.setModelColumn(index)

    def goToColumn(self):
        print("go to column 7")
        index = self.dataTableView.view().model().index(7, 0)
        self.dataTableView.view().setCurrentIndex(index)

    def changeColumnValue(self, columnName, index, dtype):
        print("failed to change", columnName, "to", dtype)
        print(index.data(), index.isValid())
        self.dataTableView.view().setCurrentIndex(index)

    def setFilter(self):
        # filterIndex = eval(self.lineEditFilterCondition.text())
        search = DataSearch("Test", self.lineEditFilterCondition.text())
        model = self.dataTableView.view().model()
        assert isinstance(model, DataFrameModel)
        model.setFilter(search)
        # raise NotImplementedError

    def clearFilter(self):
        model = self.dataTableView.view().model()
        assert isinstance(model, DataFrameModel)
        model.clearFilter()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = TestWidget()
    widget.show()

    widget.setDataFrame(getCsvData())

    # widget.setDataFrame( getRandomData(2, 2) )

    app.exec()
