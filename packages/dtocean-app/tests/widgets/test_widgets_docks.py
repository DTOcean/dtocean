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

# pylint: disable=redefined-outer-name,protected-access

import pytest

from dtocean_app.utils.qtlog import XStream
from dtocean_app.widgets.docks import LogDock


@pytest.fixture
def log_dock_widget(qtbot):
    widget = LogDock()
    widget.show()
    qtbot.addWidget(widget)

    return widget


def test_LogDock_init(log_dock_widget):
    assert log_dock_widget.isVisible()


def test_LogDock_stdout(log_dock_widget):
    expected = "mock"
    XStream.stdout().write(expected)
    assert str(log_dock_widget._console.toPlainText()) == expected


def test_LogDock_stderr(log_dock_widget):
    expected = "mock"
    XStream.stderr().write(expected)
    assert str(log_dock_widget._console.toPlainText()) == expected
