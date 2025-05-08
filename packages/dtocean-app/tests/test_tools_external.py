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

pytest.importorskip("dtocean_hydro")

from dtocean_app.tools.external import GUIWECSimulatorTool


def test_GUIWECSimulatorTool_init():
    GUIWECSimulatorTool()
    assert True


def test_GUIWECSimulatorTool_get_weight():
    test = GUIWECSimulatorTool()
    assert test.get_weight() == 1


def test_GUIWECSimulatorTool_has_widget():
    test = GUIWECSimulatorTool()
    assert test.has_widget() is False
