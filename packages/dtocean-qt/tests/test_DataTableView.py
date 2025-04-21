from dtocean_qt.compat import QtCore, QtGui, Qt

import time
import pytest
import pytestqt

import numpy
import pandas

from dtocean_qt.views.DataTableView import DataTableWidget
from dtocean_qt.models.DataFrameModel import DataFrameModel

@pytest.fixture()
def dataModel():
        df = pandas.DataFrame([10], columns=['A'])
        model = DataFrameModel(df)
        return model


@pytest.fixture()
def dataModel2():
    df = pandas.DataFrame([[1,2,3,4,5,6,7,8]],
                          columns=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
    model = DataFrameModel(df)
    return model
    
    
@pytest.fixture()
def dataModel3():
    df = pandas.DataFrame(numpy.arange(200), columns=['A'])
    model = DataFrameModel(df)
    return model


class TestTableViewWidget(object):

    def test_init(self, qtbot):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        assert widget.view().model() is None

        buttons = widget.findChildren(QtGui.QToolButton)

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

        buttons = widget.findChildren(QtGui.QToolButton)

        exclude_button = None
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                exclude_button = btn
                assert btn.isChecked()
                break

        for button in buttons:
            assert button.isEnabled()

        qtbot.mouseClick(btn, QtCore.Qt.LeftButton)

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

        buttons = widget.findChildren(QtGui.QToolButton)
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                assert widget.view().model().editable

                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                assert not widget.view().model().editable

                break

    def test_click_each_button(self, qtbot, dataModel):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel)

        buttons = widget.findChildren(QtGui.QToolButton)
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                break

        for btn in buttons:
            if btn.objectName() == 'editbutton':
                continue

            if btn.objectName() in ['addcolumnbutton', 'removecolumnbutton']:
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                dlg = widget.findChildren(QtGui.QDialog)[-1]

                dlg_buttons = dlg.findChildren(QtGui.QPushButton)

                for b in dlg_buttons:
                    if str(b.text()) == 'Cancel':
                        qtbot.mouseClick(b, QtCore.Qt.LeftButton)
                        break
            else:
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)


    def test_addColumn(self, qtbot, dataModel):
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel)

        buttons = widget.findChildren(QtGui.QToolButton)
        for btn in buttons:
            if btn.isEnabled:
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                break

        columns = []
        addButton = None
        for btn in buttons:
            if btn.objectName == 'addcolumnbutton':
                addbutton = btn
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                dlg = widget.findChildren(QtGui.QDialog)[-1]
                dlg_buttons = dlg.findChildren(QtGui.QPushButton)
                comboBox = dlg.findChildren(QtGui.QComboBox)[-1]

                for i in xrange(comboBox.count()):
                    columns.append(comboBox.itemText(i))

                for b in dlg_buttons:
                    if str(b.text()) == 'Cancel':
                        qtbot.mouseClick(b, QtCore.Qt.LeftButton)
                        break
                break

        columnCountBeforeInsert = widget.view().model().columnCount()
        for index, column in enumerate(columns):
            qtbot.mouseClick(addbutton, QtCore.Qt.LeftButton)
            dlg = widget.findChildren(QtGui.QDialog)[-1]

            textedits = dlg.findChildren(QtGui.QLineEdit)
            qtbot.keyClicks(textedits[0], column)

            comboBox = dlg.findChildren(QtGui.QComboBox)[-1]
            comboBox.setCurrentIndex(index)

            dlg_buttons = dlg.findChildren(QtGui.QPushButton)

            for b in dlg_buttons:
                if str(b.text()) == 'OK':
                    qtbot.mouseClick(b, QtCore.Qt.LeftButton)
                    break

            assert widget.view().model().columnCount() == \
                                        columnCountBeforeInsert + 1 + index

    def test_removeColumns(self, qtbot, dataModel2):
        
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel2)
        buttons = widget.findChildren(QtGui.QToolButton)
        
        for btn in buttons:
            if btn.isEnabled():
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)
                break

        for btn in buttons:
                        
            if str(btn.objectName()) == 'removecolumnbutton':
                                
                qtbot.mouseClick(btn, QtCore.Qt.LeftButton)                
                dlg = widget.findChildren(QtGui.QDialog)[-1]
                
                listview = dlg.findChildren(QtGui.QListView)[-1]
                listview.selectAll()
                
                dlg_buttons = dlg.findChildren(QtGui.QPushButton)

                for b in dlg_buttons:
                    if str(b.text()) == 'OK':
                        qtbot.mouseClick(b, QtCore.Qt.LeftButton)
                        break
                        
                break
                        
        assert widget.view().model().columnCount() == 0
        
    def test_paginate(self, qtbot, dataModel3):
        
        widget = DataTableWidget()
        qtbot.addWidget(widget)
        widget.show()

        widget.setViewModel(dataModel3)
        
        model = widget.tableView.model()
        scroll_bar = widget.tableView.verticalScrollBar()
                
        scroll_bar_value = scroll_bar.value()
        scroll_bar.setValue(scroll_bar_value + 110)
                
        assert model.rowsLoaded == 200
        
