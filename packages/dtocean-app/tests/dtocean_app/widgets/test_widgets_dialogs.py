# -*- coding: utf-8 -*-

#    Copyright (C) 2025 Mathew Topper
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


import pytest
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from dtocean_app.widgets.dialogs import (
    About,
    Help,
    TestDataPicker,
    _get_copyright_label,
    _get_software_label,
    _get_version_label,
)


@pytest.fixture
def picker_widget(qtbot):
    widget = TestDataPicker()
    widget.show()
    qtbot.addWidget(widget)

    return widget


def test_TestDataPicker_init(picker_widget):
    assert picker_widget.isVisible()


def test_TestDataPicker_write_path(mocker, qtbot, picker_widget):
    expected = "mock.pkl"
    mocker.patch.object(
        QtWidgets.QFileDialog,
        "getOpenFileName",
        return_value=(expected, None),
    )

    qtbot.mouseClick(picker_widget.browseButton, Qt.MouseButton.LeftButton)

    def has_path():
        assert str(picker_widget.pathLineEdit.text())

    qtbot.waitUntil(has_path)

    assert str(picker_widget.pathLineEdit.text()) == expected


def test_About_init(qtbot):
    widget = About()
    widget.show()
    qtbot.addWidget(widget)

    assert widget.isVisible()


def test_get_version_label_dtocean():
    test = _get_version_label()
    assert len(test.split()) >= 3


def test_get_version_label_dtocean_full():
    pytest.importorskip("dtocean")
    test = _get_version_label()
    assert len(test.split()) == 4


def test_get_copyright_label():
    test = _get_copyright_label()[-4:]
    assert test.isnumeric()


def test_get_software_label():
    test = _get_software_label()
    assert len(test.split()) == 6


def test_Help_init(qtbot):
    widget = Help()
    widget.show()
    qtbot.addWidget(widget)

    assert widget.isVisible()


def test_Help_docs(qtbot, mocker):
    expected = "dummy.html"

    mocker.patch(
        "dtocean_app.widgets.dialogs.get_docs_index",
        return_value=expected,
    )

    widget = Help()
    widget.show()
    qtbot.addWidget(widget)

    assert widget._url_widget is not None


def test_Help_no_docs(qtbot, mocker):
    mocker.patch(
        "dtocean_app.widgets.dialogs.get_docs_index",
        return_value=None,
    )

    widget = Help()
    widget.show()
    qtbot.addWidget(widget)

    assert widget._msg_widget is not None
    assert widget._msg_widget.text == "No manuals installated"
