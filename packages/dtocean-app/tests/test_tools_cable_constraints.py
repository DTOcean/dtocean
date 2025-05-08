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

pytest.importorskip("dtocean_electrical")

import matplotlib.pyplot as plt

from dtocean_app.tools.cable_constraints import GUICableConstraintsTool
from dtocean_app.widgets.display import MPLWidget


def test_GUICableConstraintsTool_init():
    tool = GUICableConstraintsTool()
    assert tool._fig is None


def test_GUICableConstraintsTool_get_widget_none():
    tool = GUICableConstraintsTool()
    assert tool.get_widget() is None


@pytest.fixture()
def constraints_tool(mocker, figure):
    mocker.patch(
        "dtocean_app.tools.cable_constraints.plot_devices",
        return_value=figure,
        autospec=True,
    )

    tool = GUICableConstraintsTool()
    tool._elec = mocker.MagicMock()
    tool._constrained_lines = mocker.MagicMock()

    return tool


def test_GUICableConstraintsTool_get_widget(qtbot, figure, constraints_tool):
    widget = constraints_tool.get_widget()
    assert isinstance(widget, MPLWidget)
    assert constraints_tool._fig is figure


def test_GUICableConstraintsTool_destroy_widget(qtbot, constraints_tool):
    n_figs = len(plt.get_fignums())

    constraints_tool.get_widget()
    constraints_tool.destroy_widget()

    assert len(plt.get_fignums()) == n_figs - 1
    assert constraints_tool._fig is None
