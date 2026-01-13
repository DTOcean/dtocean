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

import os
import sys

import pytest
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from dtocean_plugins.strategy_guis.position import (
    AdvancedPositionWidget,
    GUIAdvancedPosition,
)


def test_GUIAdvancedPosition_allow_run_no_config():
    test = GUIAdvancedPosition()
    assert test.allow_run("mock", "mock") is False


def test_GUIAdvancedPosition_allow_run(mocker):
    mocker.patch(
        "dtocean_plugins.strategy_guis.position.AdvancedPosition.allow_run",
        return_value=True,
    )

    test = GUIAdvancedPosition()
    test._config = {"mock": "mock"}

    assert test.allow_run("mock", "mock") is True


def test_AdvancedPositionWidget_bad_status(qtbot, mock_shell):
    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)

    assert not window.tabWidget.isTabEnabled(1)
    assert not window.tabWidget.isTabEnabled(2)
    assert not window.tabWidget.isTabEnabled(3)
    assert not window.tabWidget.isTabEnabled(4)


def test_AdvancedPositionWidget_settings_open(qtbot, tmp_path, hydro_shell):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)


def test_AdvancedPositionWidget_with_config(mocker, qtbot, hydro_shell, config):
    max_cpu = 8
    mocker.patch(
        "dtocean_plugins.strategy_guis.position.multiprocessing.cpu_count",
        return_value=max_cpu,
        autospec=True,
    )

    window = AdvancedPositionWidget(None, hydro_shell, config)
    window.show()
    qtbot.addWidget(window)

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)
    assert float(window.penaltySpinBox.value()) == config["base_penalty"]
    assert not window.cleanDirCheckBox.isChecked()
    assert int(window.maxNoiseSpinBox.value()) == config["min_evals"]
    assert int(window.maxResamplesComboBox.currentIndex()) == 0
    assert (
        int(window.maxResamplesSpinBox.value()) == config["max_resample_factor"]
    )
    assert int(window.abortXSpinBox.value()) == config["max_simulations"]
    assert window.costVarCheckBox.isChecked() is config["maximise"]
    assert not window.minNoiseCheckBox.isChecked()
    assert int(window.minNoiseSpinBox.value()) == config["min_evals"]
    assert int(window.maxNoiseSpinBox.minimum()) == config["min_evals"]
    assert int(window.nThreadSpinBox.value()) == config["n_threads"]
    assert (
        str(window.costVarBox.currentText())
        == "Array Annual Energy Production (MWh)"
    )
    assert not window.populationCheckBox.isChecked()
    assert int(window.populationSpinBox.value()) == config["popsize"]
    assert int(window.abortTimeSpinBox.value()) == config["timeout"]
    assert float(window.toleranceSpinBox.value()) == config["tolfun"]
    assert str(window.workDirLineEdit.text()) == config["worker_dir"]


@pytest.fixture()
def config_alt():
    return {
        "base_penalty": 2.0,
        "clean_existing_dir": True,
        "max_evals": 3,
        "max_resample_factor": "auto2",
        "max_simulations": 1,
        "maximise": False,
        "min_evals": None,
        "n_threads": 9,
        "objective": "project.annual_energy",
        "parameters": {
            "delta_col": {"fixed": 1},
            "delta_row": {
                "range": {
                    "max_multiplier": 2.0,
                    "min_multiplier": 1.0,
                    "type": "multiplier",
                    "variable": "device.minimum_distance_x",
                }
            },
            "grid_orientation": {
                "range": {"max": 90.0, "min": -90.0, "type": "fixed"}
            },
            "n_nodes": {
                "range": {"max": 20, "min": 1, "type": "fixed"},
                "x0": 15,
            },
            "t1": {"range": {"max": 1.0, "min": 0.0, "type": "fixed"}},
            "t2": {"range": {"max": 1.0, "min": 0.0, "type": "fixed"}},
        },
        "popsize": None,
        "results_params": [
            "project.number_of_devices",
            "project.annual_energy",
            "project.q_factor",
            "project.capex_total",
            "project.capex_breakdown",
            "project.lifetime_opex_mean",
            "project.lifetime_cost_mean",
            "project.lifetime_energy_mean",
            "project.lcoe_mean",
        ],
        "root_project_path": None,
        "timeout": 1,
        "tolfun": 1,
        "worker_dir": "mock",
    }


def test_AdvancedPositionWidget_with_config_alt(
    mocker, qtbot, hydro_shell, config_alt
):
    max_cpu = 8
    mocker.patch(
        "dtocean_plugins.strategy_guis.position.multiprocessing.cpu_count",
        return_value=max_cpu,
        autospec=True,
    )

    window = AdvancedPositionWidget(None, hydro_shell, config_alt)
    window.show()
    qtbot.addWidget(window)

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)
    assert float(window.penaltySpinBox.value()) == config_alt["base_penalty"]
    assert not window.cleanDirCheckBox.isChecked()
    assert int(window.maxNoiseSpinBox.value()) == config_alt["max_evals"]
    assert int(window.maxResamplesComboBox.currentIndex()) == 1
    assert int(window.maxResamplesSpinBox.value()) == int(
        config_alt["max_resample_factor"][-1]
    )
    assert int(window.abortXSpinBox.value()) == config_alt["max_simulations"]
    assert window.costVarCheckBox.isChecked() is config_alt["maximise"]
    assert window.minNoiseCheckBox.isChecked()
    assert int(window.maxNoiseSpinBox.minimum()) == 1
    assert int(window.nThreadSpinBox.value()) == max_cpu
    assert (
        str(window.costVarBox.currentText())
        == "Array Annual Energy Production (MWh)"
    )
    assert window.populationCheckBox.isChecked()
    assert int(window.abortTimeSpinBox.value()) == config_alt["timeout"]
    assert float(window.toleranceSpinBox.value()) == config_alt["tolfun"]
    assert str(window.workDirLineEdit.text()) == config_alt["worker_dir"]


def test_AdvancedPositionWidget_import_config(
    mocker, qtbot, mock_shell, config
):
    from dtocean_plugins.strategy_guis.position import GUIAdvancedPosition

    mocker.patch.object(
        QtWidgets.QFileDialog, "getOpenFileName", return_value="mock"
    )
    mocker.patch.object(GUIAdvancedPosition, "load_yaml", return_value=config)

    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.cleanDirCheckBox.setChecked(True)
    qtbot.mouseClick(window.importConfigButton, Qt.MouseButton.LeftButton)

    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)


def test_AdvancedPositionWidget_export_config(
    mocker, qtbot, tmp_path, mock_shell, config
):
    f = tmp_path / "config.yaml"
    mocker.patch.object(
        QtWidgets.QFileDialog, "getSaveFileName", return_value=str(f)
    )

    window = AdvancedPositionWidget(None, mock_shell, config)
    window.show()
    qtbot.addWidget(window)

    qtbot.mouseClick(window.exportConfigButton, Qt.MouseButton.LeftButton)

    assert f.is_file()


def test_AdvancedPositionWidget_reset_worker_dir(qtbot, mock_shell, config):
    window = AdvancedPositionWidget(None, mock_shell, config)
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert("not_mock")
    window.workDirLineEdit.editingFinished.emit()

    assert str(window.workDirLineEdit.text()) == config["worker_dir"]


def test_AdvancedPositionWidget_reset_worker_dir_none(qtbot, mock_shell):
    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert("not_mock")
    window.workDirLineEdit.editingFinished.emit()

    assert str(window.workDirLineEdit.text()) == ""


def test_AdvancedPositionWidget_select_worker_dir(
    mocker, qtbot, mock_shell, config
):
    mock = mocker.patch.object(
        QtWidgets.QFileDialog,
        "getExistingDirectory",
        return_value="another_mock",
    )

    window = AdvancedPositionWidget(None, mock_shell, config)
    window.show()
    qtbot.addWidget(window)

    qtbot.mouseClick(window.workDirToolButton, Qt.MouseButton.LeftButton)

    assert mock.call_args.args[2] == config["worker_dir"]
    assert str(window.workDirLineEdit.text()) == "another_mock"


def test_AdvancedPositionWidget_select_worker_dir_none(
    mocker, qtbot, mock_shell
):
    mock = mocker.patch.object(
        QtWidgets.QFileDialog,
        "getExistingDirectory",
        return_value="another_mock",
    )

    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)

    qtbot.mouseClick(window.workDirToolButton, Qt.MouseButton.LeftButton)

    assert mock.call_args.args[2] == os.path.expanduser("~")
    assert str(window.workDirLineEdit.text()) == "another_mock"


@pytest.mark.parametrize("toggles, expected", [(1, True), (2, False)])
def test_AdvancedPositionWidget_update_clean_existing_dir(
    qtbot,
    hydro_shell,
    toggles,
    expected,
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    for _ in range(toggles):
        window.cleanDirCheckBox.toggle()

    assert window.get_configuration()["clean_existing_dir"] is expected


def test_AdvancedPositionWidget_update_objective(qtbot, tmp_path, hydro_shell):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    window.costVarBox.setCurrentIndex(1)

    assert str(window.penaltyUnitsLabel.text()) == "MWh"
    assert str(window.toleranceUnitsLabel.text()) == "MWh"

    window.costVarBox.setCurrentIndex(2)

    assert str(window.penaltyUnitsLabel.text()) == ""
    assert str(window.toleranceUnitsLabel.text()) == ""


@pytest.mark.parametrize("toggles, expected", [(1, True), (2, False)])
def test_AdvancedPositionWidget_update_maximise(
    qtbot, tmp_path, hydro_shell, toggles, expected
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    for _ in range(toggles):
        window.costVarCheckBox.toggle()
    assert window.get_configuration()["maximise"] is expected


def test_AdvancedPositionWidget_update_max_simulations(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    window.abortXSpinBox.setValue(1)
    assert window.get_configuration()["max_simulations"] == 1

    window.abortXSpinBox.setValue(0)
    assert window.get_configuration()["max_simulations"] is None


def test_AdvancedPositionWidget_update_max_time(qtbot, tmp_path, hydro_shell):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    window.abortTimeSpinBox.setValue(1)
    assert window.get_configuration()["timeout"] == 1

    window.abortTimeSpinBox.setValue(0)
    assert window.get_configuration()["timeout"] is None


def test_AdvancedPositionWidget_update_min_noise_auto(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    window.maxNoiseSpinBox.setMinimum(4)
    window.minNoiseCheckBox.setChecked(False)
    window.minNoiseCheckBox.toggle()

    assert window.get_configuration()["min_evals"] is None
    assert not window.minNoiseSpinBox.isEnabled()
    assert window.maxNoiseSpinBox.minimum() == 1

    window.minNoiseCheckBox.toggle()

    assert window.get_configuration()["min_evals"] == window._default_popsize
    assert window.minNoiseSpinBox.isEnabled()


def test_AdvancedPositionWidget_update_population_auto(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    window.populationCheckBox.setChecked(False)
    window.populationCheckBox.toggle()

    assert window.get_configuration()["popsize"] is None
    assert not window.populationSpinBox.isEnabled()

    window.populationCheckBox.toggle()

    assert window.get_configuration()["popsize"] == window._default_popsize
    assert window.populationSpinBox.isEnabled()


def test_AdvancedPositionWidget_update_max_resamples_algorithm(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    window.maxResamplesComboBox.setCurrentIndex(0)

    assert isinstance(window.get_configuration()["max_resample_factor"], int)

    window.maxResamplesComboBox.setCurrentIndex(1)

    assert "auto" in window.get_configuration()["max_resample_factor"]


def test_AdvancedPositionWidget_update_max_resamples(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    value = 5
    window.maxResamplesComboBox.setCurrentIndex(0)
    window.maxResamplesSpinBox.setValue(value)

    assert window.get_configuration()["max_resample_factor"] == value

    value = 6
    window.maxResamplesComboBox.setCurrentIndex(1)
    window.maxResamplesSpinBox.setValue(value)

    auto_value = "auto{}".format(value)
    assert window.get_configuration()["max_resample_factor"] == auto_value


def test_AdvancedPositionWidget_fixed_combo_slot_uncheck(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    delta_row = window._param_boxes["delta_row"]
    delta_row["fixed.check"].toggle()

    def range_group_disabled():
        assert not delta_row["range.group"].isEnabled()

    qtbot.waitUntil(range_group_disabled)

    assert window._config["parameters"]["delta_row"] == {"fixed": 0.0}


def test_AdvancedPositionWidget_fixed_combo_slot_check(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    delta_row = window._param_boxes["delta_row"]
    delta_row["fixed.check"].toggle()

    def range_group_disabled():
        assert not delta_row["range.group"].isEnabled()

    qtbot.waitUntil(range_group_disabled)

    delta_row["fixed.check"].toggle()

    def range_group_enabled():
        assert delta_row["range.group"].isEnabled()

    qtbot.waitUntil(range_group_enabled)

    assert list(window._config["parameters"]["delta_row"].keys()) == ["range"]


def test_AdvancedPositionWidget_fixed_value_slot(qtbot, tmp_path, hydro_shell):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    delta_row = window._param_boxes["delta_row"]
    delta_row["fixed.check"].toggle()

    def range_group_disabled():
        assert not delta_row["range.group"].isEnabled()

    qtbot.waitUntil(range_group_disabled)

    delta_row["fixed.box"].setValue(1)

    assert window._config["parameters"]["delta_row"] == {"fixed": 1.0}


def test_AdvancedPositionWidget_range_type_slot_multiplier(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    delta_row = window._param_boxes["delta_row"]
    delta_row["range.box.type"].setCurrentIndex(1)

    def range_box_var_enabled():
        assert delta_row["range.box.var"].isEnabled()

    qtbot.waitUntil(range_box_var_enabled)

    assert (
        window._config["parameters"]["delta_row"]["range"]["type"]
        == "multiplier"
    )


def test_AdvancedPositionWidget_range_type_slot_fixed(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    delta_row = window._param_boxes["delta_row"]

    def range_box_var_disabled():
        assert not delta_row["range.box.var"].isEnabled()

    qtbot.waitUntil(range_box_var_disabled)
    delta_row["range.box.type"].setCurrentIndex(1)

    def range_box_var_enabled():
        assert delta_row["range.box.var"].isEnabled()

    qtbot.waitUntil(range_box_var_enabled)
    delta_row["range.box.type"].setCurrentIndex(0)

    qtbot.waitUntil(range_box_var_disabled)

    assert window._config["parameters"]["delta_row"]["range"]["type"] == "fixed"


def test_AdvancedPositionWidget_generic_range_slot(
    qtbot, tmp_path, hydro_shell
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    delta_row = window._param_boxes["delta_row"]
    delta_row["range.box.max"].setValue(2)

    assert window._config["parameters"]["delta_row"]["range"]["max"] == 2


def test_AdvancedPositionWidget_import_yaml(mocker, qtbot, mock_shell):
    mocker.patch.object(
        QtWidgets.QFileDialog, "getOpenFileName", return_value="mock"
    )

    window = AdvancedPositionWidget(None, mock_shell, {})
    mock = window._shell.strategy = mocker.MagicMock()

    window.show()
    qtbot.addWidget(window)
    window.tabWidget.setCurrentIndex(5)
    qtbot.mouseClick(window.importYAMLButton, Qt.MouseButton.LeftButton)

    assert mock.import_simulation_file.call_args.args[-1] == "mock"


@pytest.mark.parametrize("article, etype", [("A", KeyError), ("An", IOError)])
def test_AdvancedPositionWidget_display_error(
    mocker, qtbot, mock_shell, article, etype
):
    mock = mocker.patch.object(QtWidgets.QMessageBox, "critical")

    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)

    evalue = etype("mock")
    _, _, etraceback = sys.exc_info()
    window._display_error(etype, evalue, etraceback)

    expected_msg = "{} {} occurred: {}".format(article, etype.__name__, evalue)
    assert mock.call_args.args[1] == "ERROR"
    assert mock.call_args.args[2] == expected_msg


def test_AdvancedPositionWidget_set_configuration(
    mocker, qtbot, hydro_shell, config
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)

    window.set_configuration(config)

    def settings_tab_enabled():
        assert window.tabWidget.isTabEnabled(1)

    qtbot.waitUntil(settings_tab_enabled)

    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)


def test_AdvancedPositionWidget_set_configuration_has_stored(
    mocker, qtbot, hydro_shell, config, config_alt
):
    window = AdvancedPositionWidget(None, hydro_shell, {})
    mock = window._shell.strategy = mocker.MagicMock()
    config["clean_existing_dir"] = None
    mock._config = config

    window.show()
    qtbot.addWidget(window)

    window.set_configuration(config_alt)

    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)
