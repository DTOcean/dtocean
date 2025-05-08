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


@pytest.fixture
def strategy_basic(mocker, qtbot, mock_shell):
    mocker.patch.object(
        GUIStrategyManager,
        "get_available",
        return_value=["Basic"],
        autospec=True,
    )

    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)

    if "Basic" not in window._plugin_names.keys():
        pytest.skip("Test requires Basic strategy")

    # Click on first strategy and apply
    item = window.listWidget.item(0)
    rect = window.listWidget.visualItemRect(item)
    qtbot.mouseClick(
        window.listWidget.viewport(), QtCore.Qt.LeftButton, pos=rect.center()
    )

    def apply_enabled():
        assert window.applyButton.isEnabled()

    qtbot.waitUntil(apply_enabled)

    qtbot.mouseClick(window.applyButton, QtCore.Qt.LeftButton)

    def strategy_set():
        assert str(window.topDynamicLabel.text()) == str(item.text())

    qtbot.waitUntil(strategy_set)

    return window


def test_strategy_basic_apply(strategy_basic):
    assert str(strategy_basic.topDynamicLabel.text()) == "Basic"


def test_strategy_basic_reset(qtbot, strategy_basic):
    # Reset the strategy
    qtbot.mouseClick(strategy_basic.resetButton, QtCore.Qt.LeftButton)

    assert str(strategy_basic.topDynamicLabel.text()) == "None"


@pytest.fixture
def strategy_sensitivity(mocker, qtbot, mock_shell):
    mocker.patch.object(
        GUIStrategyManager,
        "get_available",
        return_value=["Unit Sensitivity"],
        autospec=True,
    )

    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)

    if "Unit Sensitivity" not in window._plugin_names.keys():
        pytest.skip("Test requires Unit Sensitivity strategy")

    widget_id = id(window.mainWidget)

    # Click on first strategy and apply
    item = window.listWidget.item(0)
    rect = window.listWidget.visualItemRect(item)
    qtbot.mouseClick(
        window.listWidget.viewport(), QtCore.Qt.LeftButton, pos=rect.center()
    )

    def widget_changed():
        assert id(window.mainWidget) != widget_id

    qtbot.waitUntil(widget_changed)

    return window


def test_strategy_sensitivity_apply_null(strategy_sensitivity):
    assert not strategy_sensitivity.applyButton.isEnabled()


@pytest.fixture
def strategy_sensitivity_variable(qtbot, strategy_sensitivity):
    sensitivity = strategy_sensitivity.mainWidget

    # Select module
    idx = sensitivity.modBox.findText("Mock Module", QtCore.Qt.MatchFixedString)
    sensitivity.modBox.setCurrentIndex(idx)

    def varBox_not_empty():
        assert int(sensitivity.varBox.count()) > 0

    qtbot.waitUntil(varBox_not_empty)

    # Select variable
    idx = sensitivity.varBox.findText(
        "Tidal Turbine Cut-In Velocity (m/s)", QtCore.Qt.MatchFixedString
    )
    sensitivity.varBox.setCurrentIndex(idx)

    def lineEdit_enabled():
        assert sensitivity.lineEdit.isEnabled()

    qtbot.waitUntil(lineEdit_enabled)

    return strategy_sensitivity


def test_strategy_sensitivity_lineEdit_enabled(strategy_sensitivity_variable):
    assert strategy_sensitivity_variable.mainWidget.lineEdit.isEnabled()


def test_strategy_sensitivity_apply(strategy_sensitivity_variable):
    line = strategy_sensitivity_variable.mainWidget.lineEdit
    line.setText("1")

    assert strategy_sensitivity_variable.applyButton.isEnabled()


def test_strategy_sensitivity_apply_disable(strategy_sensitivity_variable):
    line = strategy_sensitivity_variable.mainWidget.lineEdit
    line.setText("1")

    assert strategy_sensitivity_variable.applyButton.isEnabled()

    line.setText("")

    assert not strategy_sensitivity_variable.applyButton.isEnabled()
