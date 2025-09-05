# -*- coding: utf-8 -*-

#    Copyright (C) 2022-2025 Mathew Topper
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

from dtocean_plugins.strategy_guis.multi import GUIMultiSensitivity
from dtocean_plugins.strategy_guis.sensitivity import GUIUnitSensitivity


@pytest.mark.parametrize(
    "project, expected",
    [(["a"], True), (["a", "b"], False)],
)
def test_GUIUnitSensitivity_allow_run(project, expected):
    test = GUIUnitSensitivity()
    assert test.allow_run("mock", project) is expected


@pytest.mark.parametrize(
    "project, expected",
    [(["a"], True), (["a", "b"], False)],
)
def test_GUIMultiSensitivity_allow_run(project, expected):
    test = GUIMultiSensitivity()
    assert test.allow_run("mock", project) is expected
