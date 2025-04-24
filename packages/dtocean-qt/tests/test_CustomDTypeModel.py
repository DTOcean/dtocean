# -*- coding: utf-8 -*-

import numpy
import pandas
import pytest
from PySide6 import QtWidgets
from PySide6.QtCore import (
    QModelIndex,
    Qt,
)

from dtocean_qt.pandas.models.ColumnDtypeModel import (
    DTYPE_ROLE,
    ColumnDtypeModel,
)
from dtocean_qt.pandas.models.SupportedDtypes import SupportedDtypes
from dtocean_qt.pandas.views.CustomDelegates import DtypeComboDelegate


@pytest.fixture()
def dataframe():
    data = [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14]]
    columns = ["Foo", "Bar", "Spam", "Eggs", "Baz"]
    dataFrame = pandas.DataFrame(data, columns=columns)
    return dataFrame


@pytest.fixture()
def language_values():
    return SupportedDtypes._all


class TestColumnDType(object):
    def test_customDTypeModel_check_init(self):
        model = ColumnDtypeModel()

        assert model.dataFrame().empty
        assert not model.editable()

        model = ColumnDtypeModel(editable=True)
        assert model.editable()

    def test_headerData(self):
        model = ColumnDtypeModel()

        ret = model.headerData(0, Qt.Orientation.Horizontal)
        assert ret == "column"
        ret = model.headerData(1, Qt.Orientation.Horizontal)
        assert ret == "data type"
        ret = model.headerData(2, Qt.Orientation.Horizontal)
        assert ret is None
        ret = model.headerData(
            0, Qt.Orientation.Horizontal, Qt.ItemDataRole.EditRole
        )
        assert ret is None
        ret = model.headerData(0, Qt.Orientation.Vertical)
        assert ret is None

    def test_data(self, dataframe):
        model = ColumnDtypeModel(dataFrame=dataframe)
        index = model.index(0, 0)

        # get data for display role
        ret = index.data()
        assert ret == "Foo"

        # edit role does the same as display role
        ret = index.data(Qt.ItemDataRole.EditRole)
        assert ret == "Foo"

        # datatype only defined for column 1
        ret = index.data(DTYPE_ROLE)
        assert ret is None

        # datatype column
        index = index.sibling(0, 1)
        ret = index.data(DTYPE_ROLE)
        assert ret == numpy.dtype(numpy.int64)

        # check translation / display text
        assert (
            index.data()
            == "integer (64 bit)"
            == SupportedDtypes.description(ret)
        )

        # column not defined
        index = index.sibling(0, 2)
        assert index.data(DTYPE_ROLE) is None

        # invalid index
        index = QModelIndex()
        assert model.data(index) is None

        index = model.index(2, 0)

        # get data for display role
        ret = index.data()
        assert ret == "Spam"

    def test_setData(self, dataframe, language_values, qtbot):
        model = ColumnDtypeModel(dataFrame=dataframe)
        index = model.index(3, 1)
        model.setEditable(True)

        # change all values except datetime
        datetime = ()
        for expected_type, string in language_values:
            if expected_type == numpy.dtype("<M8[ns]"):
                datetime = (string, expected_type)
                continue
            else:
                model.setData(index, string)
                assert index.data(DTYPE_ROLE) == expected_type

        assert len(datetime) == 2
        assert not model.setData(index, "bool", Qt.ItemDataRole.DisplayRole)

        with pytest.raises(Exception) as err:
            model.setData(index, datetime[0])
        assert "Can't convert a boolean value into a datetime value" in str(
            err.value
        )

        # rewrite this with parameters
        for data in [
            ["2012-12-13"],
            ["2012-12-13 19:10"],
            ["2012-12-13 19:10:10"],
        ]:
            df = pandas.DataFrame(data, columns=["datetime"])
            model = ColumnDtypeModel(dataFrame=df)
            index = model.index(0, 0)
            model.setEditable(True)
            assert model.setData(index, "date and time")

        # convert datetime to anything else does not work and leave the
        # datatype unchanged. An error message is emitted.

        with pytest.raises(qtbot.TimeoutError):
            with qtbot.waitSignal(model.changeFailed):
                model.setData(index, "bool")

    def test_flags(self, dataframe):
        model = ColumnDtypeModel(dataFrame=dataframe)
        model.setEditable(True)

        index = model.index(0, 0)
        assert (
            model.flags(index)
            == Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        )
        index = index.sibling(0, 1)
        assert (
            model.flags(index)
            == Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

        index = index.sibling(15, 1)
        assert model.flags(index) == Qt.ItemFlag.NoItemFlags

    def test_columnCount(self):
        model = ColumnDtypeModel()
        assert model.columnCount() == 2

    def test_rowCount(self, dataframe):
        model = ColumnDtypeModel()
        assert model.rowCount() == 0

        model.setDataFrame(dataframe)
        assert model.rowCount() == 5

    def test_setDataFrame(self, dataframe):
        model = ColumnDtypeModel()

        model.setDataFrame(dataframe)
        assert model.rowCount() == 5

        with pytest.raises(TypeError) as err:
            model.setDataFrame(["some", "neat", "list", "entries"])
        assert "not of type pandas.DataFrame" in str(err.value)


class TestDtypeComboDelegate(object):
    def test_editing(self, dataframe, qtbot):
        model = ColumnDtypeModel(dataFrame=dataframe)

        model.setEditable(True)

        tableView = QtWidgets.QTableView()
        qtbot.addWidget(tableView)

        tableView.setModel(model)
        delegate = DtypeComboDelegate(tableView)
        tableView.setItemDelegateForColumn(1, delegate)
        tableView.show()

        index = model.index(0, 1)
        preedit_data = index.data(DTYPE_ROLE)

        tableView.edit(index)
        editor = list(tableView.findChildren(QtWidgets.QComboBox))[0]
        selectedIndex = editor.currentIndex()
        editor.setCurrentIndex(selectedIndex + 1)
        postedit_data = index.data(DTYPE_ROLE)

        assert preedit_data != postedit_data
