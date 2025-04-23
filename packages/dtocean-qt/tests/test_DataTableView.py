import numpy
import pandas
import pytest
from PySide6 import QtWidgets
from PySide6.QtCore import (
    Qt,
)

from dtocean_qt.pandas.models.DataFrameModel import DataFrameModel
from dtocean_qt.pandas.views.DataTableView import DataTableWidget


@pytest.fixture()
def dataModel():
    df = pandas.DataFrame([10], columns=["A"])
    model = DataFrameModel(df)
    return model


@pytest.fixture()
def dataModel2():
    df = pandas.DataFrame(
        [[1, 2, 3, 4, 5, 6, 7, 8]],
        columns=["a", "b", "c", "d", "e", "f", "g", "h"],
    )
    model = DataFrameModel(df)
    return model


@pytest.fixture()
def dataModel3():
    df = pandas.DataFrame(numpy.arange(200), columns=["A"])
    model = DataFrameModel(df)
    return model


class TestTableViewWidget(object):
    def test_init(self, qtbot):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        assert widget.view().model() is None

        buttons = widget.findChildren(QtWidgets.QToolButton)

        enabled_counter = 0
        for btn in buttons:
            assert not btn.isChecked()
            if btn.isEnabled():
                enabled_counter += 1

        assert enabled_counter == 1

    def test_enableToolBar(self, qtbot):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        assert widget.view().model() is None

        buttons = widget.findChildren(QtWidgets.QToolButton)

        exclude_button = None
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                exclude_button = btn
                assert btn.isChecked()
                break

        for button in buttons:
            assert button.isEnabled()

        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

        for button in buttons:
            if button == exclude_button:
                continue
            assert not button.isEnabled()
            assert not button.isChecked()

    def test_setModel(self, qtbot, dataModel):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel)

        assert widget.view().model() is not None
        assert widget.view().model() == dataModel

        buttons = widget.findChildren(QtWidgets.QToolButton)
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                model = widget.view().model()
                assert isinstance(model, DataFrameModel)
                assert model.editable

                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                model = widget.view().model()
                assert isinstance(model, DataFrameModel)
                assert not model.editable

                break

    def test_click_each_button(self, qtbot, dataModel):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel)

        buttons = widget.findChildren(QtWidgets.QToolButton)
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                break

        for btn in buttons:
            if btn.objectName() == "editbutton":
                continue

            if btn.objectName() in ["addcolumnbutton", "removecolumnbutton"]:
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                dlg = list(widget.findChildren(QtWidgets.QDialog))[-1]

                dlg_buttons = dlg.findChildren(QtWidgets.QPushButton)

                for b in dlg_buttons:
                    if str(b.text()) == "Cancel":
                        qtbot.mouseClick(b, Qt.MouseButton.LeftButton)
                        break
            else:
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_addColumn(self, qtbot, dataModel):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel)

        buttons = widget.findChildren(QtWidgets.QToolButton)
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                break

        columns = []
        for btn in buttons:
            if btn.objectName == "addcolumnbutton":
                addbutton = btn
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                dlg = list(widget.findChildren(QtWidgets.QDialog))[-1]
                dlg_buttons = dlg.findChildren(QtWidgets.QPushButton)
                comboBox = list(dlg.findChildren(QtWidgets.QComboBox))[-1]

                for i in range(comboBox.count()):
                    columns.append(comboBox.itemText(i))

                for b in dlg_buttons:
                    if str(b.text()) == "Cancel":
                        qtbot.mouseClick(b, Qt.MouseButton.LeftButton)
                        break
                break

        columnCountBeforeInsert = widget.view().model().columnCount()
        for index, column in enumerate(columns):
            qtbot.mouseClick(addbutton, Qt.MouseButton.LeftButton)
            dlg = list(widget.findChildren(QtWidgets.QDialog))[-1]

            textedits = list(dlg.findChildren(QtWidgets.QLineEdit))
            qtbot.keyClicks(textedits[0], column)

            comboBox = list(dlg.findChildren(QtWidgets.QComboBox))[-1]
            comboBox.setCurrentIndex(index)

            dlg_buttons = dlg.findChildren(QtWidgets.QPushButton)

            for b in dlg_buttons:
                if str(b.text()) == "OK":
                    qtbot.mouseClick(b, Qt.MouseButton.LeftButton)
                    break

            assert (
                widget.view().model().columnCount()
                == columnCountBeforeInsert + 1 + index
            )

    def test_removeColumns(self, qtbot, dataModel2):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel2)
        buttons = list(widget.findChildren(QtWidgets.QToolButton))

        for btn in buttons:
            if btn.isEnabled():
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                break

        for btn in buttons:
            if str(btn.objectName()) == "removecolumnbutton":
                qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                dlg = list(widget.findChildren(QtWidgets.QDialog))[-1]

                listview = list(dlg.findChildren(QtWidgets.QListView))[-1]
                listview.selectAll()

                dlg_buttons = dlg.findChildren(QtWidgets.QPushButton)

                for b in dlg_buttons:
                    if str(b.text()) == "OK":
                        qtbot.mouseClick(b, Qt.MouseButton.LeftButton)
                        break

                break

        assert widget.view().model().columnCount() == 0

    def test_paginate(self, qtbot, dataModel3):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel3)

        model = widget.tableView.model()
        assert isinstance(model, DataFrameModel)

        scroll_bar = widget.tableView.verticalScrollBar()
        scroll_bar_value = scroll_bar.value()
        scroll_bar.setValue(scroll_bar_value + 110)

        assert model.rowsLoaded == 200
