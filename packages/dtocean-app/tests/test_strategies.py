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

from dtocean_app.strategies import StrategyWidget
from dtocean_app.strategies.multi import GUIMultiSensitivity
from dtocean_app.strategies.position import GUIAdvancedPosition
from dtocean_app.strategies.sensitivity import GUIUnitSensitivity


@pytest.mark.parametrize(
    "project, expected", [(["a"], True), (["a", "b"], False)]
)
def test_GUIUnitSensitivity_allow_run(project, expected):
    test = GUIUnitSensitivity()
    assert test.allow_run("mock", project) is expected


@pytest.mark.parametrize(
    "project, expected", [(["a"], True), (["a", "b"], False)]
)
def test_GUIMultiSensitivity_allow_run(project, expected):
    test = GUIMultiSensitivity()
    assert test.allow_run("mock", project) is expected


def test_GUIAdvancedPosition_allow_run_no_config():
    test = GUIAdvancedPosition()
    assert test.allow_run("mock", "mock") is False


def test_GUIAdvancedPosition_allow_run(mocker):
    mocker.patch(
        "dtocean_app.strategies.position.AdvancedPosition.allow_run",
        return_value=True,
    )

    test = GUIAdvancedPosition()
    test._config = "mock"

    assert test.allow_run("mock", "mock") is True


@pytest.mark.parametrize(
    "raw_string_input, expected",
    [
        ("None", [None]),
        ("True, False", [True, False]),
        ("1, 1.", [1, 1.0]),
        ("one, 2, 3.", ["one", 2, 3.0]),
    ],
)
def test_StrategyWidget_string2types(raw_string_input, expected):
    results = StrategyWidget.string2types(raw_string_input)
    assert results == expected
