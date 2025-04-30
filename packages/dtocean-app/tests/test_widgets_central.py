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

# pylint: disable=redefined-outer-name,protected-access

import pytest
from PySide6 import QtCore, QtGui

from dtocean_app.widgets.central import FileManagerWidget, PlotManagerWidget


@pytest.fixture
def fm_widget(qtbot):
    widget = FileManagerWidget()
    widget.show()
    qtbot.addWidget(widget)

    return widget


def test_FileManagerWidget_load(fm_widget):
    load_ext_dict = {".in": "mock"}
    save_ext_dict = None

    fm_widget._set_files("mock", load_ext_dict, save_ext_dict)

    assert fm_widget.loadButton.isEnabled()
    assert not fm_widget.saveButton.isEnabled()


def test_FileManagerWidget_save(fm_widget):
    load_ext_dict = None
    save_ext_dict = {".out": "mock"}

    fm_widget._set_files("mock", load_ext_dict, save_ext_dict)

    assert not fm_widget.loadButton.isEnabled()
    assert fm_widget.saveButton.isEnabled()


@pytest.fixture
def fm_widget_both(fm_widget):
    load_ext_dict = {".in": "mock"}
    save_ext_dict = {".out": "mock"}

    fm_widget._set_files("mock", load_ext_dict, save_ext_dict)

    return fm_widget


def test_FileManagerWidget_both(fm_widget_both):
    assert fm_widget_both.loadButton.isEnabled()
    assert fm_widget_both.saveButton.isEnabled()


def test_FileManagerWidget_set_path_load(qtbot, mocker, fm_widget_both):
    file_name = "mock.in"
    mocker.patch(
        "dtocean_app.widgets.central.QtGui.QFileDialog.exec_", autospec=True
    )
    mocker.patch(
        "dtocean_app.widgets.central.QtGui.QFileDialog.selectedFiles",
        return_value=[file_name],
    )

    qtbot.mouseClick(fm_widget_both.getPathButton, QtCore.Qt.LeftButton)

    def has_file_name():
        assert str(fm_widget_both.pathEdit.text())

    qtbot.waitUntil(has_file_name)

    assert str(fm_widget_both.pathEdit.text()) == file_name
    assert fm_widget_both.buttonBox.button(
        QtGui.QDialogButtonBox.Ok
    ).isEnabled()


def test_FileManagerWidget_set_path_save(qtbot, mocker, fm_widget_both):
    file_name = "mock.out"
    mocker.patch(
        "dtocean_app.widgets.central.QtGui.QFileDialog.exec_", autospec=True
    )
    mocker.patch(
        "dtocean_app.widgets.central.QtGui.QFileDialog.selectedFiles",
        return_value=[file_name],
    )

    qtbot.mouseClick(fm_widget_both.saveButton, QtCore.Qt.LeftButton)

    def load_not_checked():
        assert not fm_widget_both.loadButton.isChecked()

    qtbot.waitUntil(load_not_checked)

    qtbot.mouseClick(fm_widget_both.getPathButton, QtCore.Qt.LeftButton)

    def has_file_name():
        assert str(fm_widget_both.pathEdit.text())

    qtbot.waitUntil(has_file_name)

    assert str(fm_widget_both.pathEdit.text()) == file_name
    assert fm_widget_both.buttonBox.button(
        QtGui.QDialogButtonBox.Ok
    ).isEnabled()


@pytest.fixture
def pm_widget(qtbot):
    widget = PlotManagerWidget()
    widget.show()
    qtbot.addWidget(widget)

    return widget


def test_PlotManagerWidget_disabled(pm_widget):
    pm_widget._set_plots(None)
    assert not pm_widget.isEnabled()


def test_PlotManagerWidget_plot_list(mocker, pm_widget):
    mocker.patch(
        "dtocean_app.widgets.central.get_current_filetypes",
        return_value={"bmp": "bitmap"},
        autospec=True,
    )

    pm_widget._set_plots("mock", plot_list=["mock"])

    assert pm_widget.plotBox.isEnabled()
    assert pm_widget.pathEdit.isEnabled()
    assert pm_widget.plotButton.isEnabled()


@pytest.fixture
def pm_widget_auto(mocker, pm_widget):
    mocker.patch(
        "dtocean_app.widgets.central.get_current_filetypes",
        return_value={"bmp": "bitmap"},
        autospec=True,
    )

    pm_widget._set_plots("mock", plot_auto=True)

    return pm_widget


def test_PlotManagerWidget_auto(pm_widget_auto):
    assert pm_widget_auto.defaultButton.isEnabled()
    assert pm_widget_auto.pathEdit.isEnabled()
    assert not pm_widget_auto.plotButton.isEnabled()


def test_PlotManagerWidget_set_path(mocker, qtbot, pm_widget_auto):
    file_name = "mock.bmp"
    mocker.patch(
        "dtocean_app.widgets.central.QtGui.QFileDialog.exec_", autospec=True
    )
    mocker.patch(
        "dtocean_app.widgets.central.QtGui.QFileDialog.selectedFiles",
        return_value=[file_name],
    )

    qtbot.mouseClick(pm_widget_auto.getPathButton, QtCore.Qt.LeftButton)

    def has_file_name():
        assert str(pm_widget_auto.pathEdit.text())

    qtbot.waitUntil(has_file_name)

    assert str(pm_widget_auto.pathEdit.text()) == file_name
    assert pm_widget_auto.saveButton.isEnabled()
