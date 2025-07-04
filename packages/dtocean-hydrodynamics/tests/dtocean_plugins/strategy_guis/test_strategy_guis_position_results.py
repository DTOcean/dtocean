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

import time
from copy import deepcopy

import pandas as pd
import pytest
from PIL import Image
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from dtocean_plugins.strategy_guis.position import AdvancedPositionWidget


@pytest.fixture
def results_df():
    data = {
        "project.annual_energy": {
            0: 28023.48059,
            1: 26643.27071,
            2: 26778.45299,
            3: 27814.33542,
            4: 26757.21522,
            5: 27764.08384,
            6: 26550.5673,
            7: 26514.06173,
            8: 26643.27087,
            9: 28023.47982,
            10: 27239.98945,
            11: 26806.925209999998,
            12: 27015.241060000004,
            13: 26902.301689999997,
            14: 27703.89522,
            15: 27592.686130000002,
            16: 27135.776339999997,
            17: 26920.497939999997,
            18: 26806.92582,
            19: 27239.98869,
        },
        "project.q_factor": {
            0: 0.643158496,
            1: 0.623552046,
            2: 0.619544776,
            3: 0.638151372,
            4: 0.627739436,
            5: 0.639574664,
            6: 0.621381745,
            7: 0.6219333429999999,
            8: 0.623552048,
            9: 0.643158482,
            10: 0.628048709,
            11: 0.621347485,
            12: 0.624239722,
            13: 0.624158242,
            14: 0.6397536,
            15: 0.635736073,
            16: 0.626756041,
            17: 0.624501289,
            18: 0.6213474929999999,
            19: 0.6280486999999999,
        },
        "delta_col": {
            0: 64.52022757,
            1: 76.45367283,
            2: 71.15118317,
            3: 59.4973027,
            4: 71.77538159,
            5: 20.852555300000002,
            6: 68.28236751,
            7: 68.20489517,
            8: 76.45367694,
            9: 64.52023109,
            10: 68.2075193,
            11: 74.75166956,
            12: 62.97270795,
            13: 67.20068782,
            14: 59.94350211,
            15: 65.31181504,
            16: 69.15202565,
            17: 72.23155823,
            18: 74.75166870000001,
            19: 68.20752592,
        },
        "grid_orientation": {
            0: 44.40745668,
            1: 33.37571009,
            2: 31.08369837,
            3: 44.20467039,
            4: 37.60163529,
            5: 314.2614026,
            6: 33.60661513,
            7: 35.39741359,
            8: 33.37571142,
            9: 44.40745683,
            10: 23.73700194,
            11: 27.35090955,
            12: 24.72097026,
            13: 37.02701777,
            14: 44.06050874,
            15: 43.03812177,
            16: 38.92446379,
            17: 35.23278284,
            18: 27.35090645,
            19: 23.73699979,
        },
        "n_nodes": {
            0: 1,
            1: 3,
            2: 3,
            3: 4,
            4: 5,
            5: 6,
            6: 7,
            7: 8,
            8: 9,
            9: 10,
            10: 11,
            11: 12,
            12: 13,
            13: 1,
            14: 2,
            15: 3,
            16: 4,
            17: 5,
            18: 6,
            19: 7,
        },
        "n_evals": {
            0: 1,
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 1,
            8: 1,
            9: 1,
            10: 1,
            11: 1,
            12: 1,
            13: 1,
            14: 1,
            15: 1,
            16: 1,
            17: 1,
            18: 1,
            19: 1,
        },
        "project.number_of_devices": {
            0: 13,
            1: 13,
            2: 13,
            3: 13,
            4: 13,
            5: 13,
            6: 13,
            7: 13,
            8: 13,
            9: 13,
            10: 13,
            11: 13,
            12: 13,
            13: 13,
            14: 13,
            15: 13,
            16: 13,
            17: 13,
            18: 13,
            19: 13,
        },
        "delta_row": {
            0: 22.92577303,
            1: 20.88411836,
            2: 20.69190282,
            3: 20.42196081,
            4: 20.18076208,
            5: 65.57126996,
            6: 20.17591929,
            7: 22.60274014,
            8: 20.88411952,
            9: 22.92576718,
            10: 20.30129026,
            11: 21.357913,
            12: 22.49606414,
            13: 22.13374607,
            14: 20.74594427,
            15: 22.47424913,
            16: 22.21391043,
            17: 20.21319696,
            18: 21.35790763,
            19: 20.301297299999998,
        },
        "sim_number": {
            0: 1,
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 8,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 18,
            14: 20,
            15: 21,
            16: 22,
            17: 23,
            18: 24,
            19: 25,
        },
        "t1": {
            0: 0.5825523539999999,
            1: 0.335333514,
            2: 0.649960257,
            3: 0.598152204,
            4: 0.358674858,
            5: 0.11531966099999999,
            6: 0.7516376490000001,
            7: 0.626618264,
            8: 0.335333535,
            9: 0.582552348,
            10: 0.639915098,
            11: 0.44859446299999994,
            12: 0.440489291,
            13: 0.68587213,
            14: 0.599689381,
            15: 0.685054472,
            16: 0.879525573,
            17: 0.521208095,
            18: 0.448594492,
            19: 0.639915119,
        },
        "t2": {
            0: 0.837202551,
            1: 0.852131616,
            2: 0.065172178,
            3: 0.201124935,
            4: 0.948168792,
            5: 0.23561065399999997,
            6: 0.222081996,
            7: 0.20230825100000002,
            8: 0.8521316290000001,
            9: 0.8372025470000001,
            10: 0.8775905009999999,
            11: 0.859587812,
            12: 0.778496615,
            13: 0.8157775970000001,
            14: 0.743709152,
            15: 0.79916979,
            16: 0.76798122,
            17: 0.843732638,
            18: 0.8595878240000001,
            19: 0.8775905190000001,
        },
    }
    table_cols = [
        "sim_number",
        "project.annual_energy",
        "grid_orientation",
        "delta_row",
        "delta_col",
        "n_nodes",
        "t1",
        "t2",
        "n_evals",
        "project.number_of_devices",
    ]

    return pd.DataFrame(data, columns=table_cols)


@pytest.fixture
def window_results(mocker, qtbot, tmp_path, hydro_shell, config, results_df):
    from dtocean_plugins.strategy_guis.position import GUIAdvancedPosition

    status_str = "Project ready"
    status_code = 1
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_project_status",
        return_value=(status_str, status_code),
    )

    status_str = "Configuration complete"
    status_code = 1
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_config_status",
        return_value=(status_str, status_code),
    )

    status_str = "Worker directory contains files"
    status_code = 0
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_worker_directory_status",
        return_value=(status_str, status_code),
    )

    status_str = "Optimisation complete"
    status_code = 1
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_optimiser_status",
        return_value=(status_str, status_code),
    )

    config["worker_dir"] = str(tmp_path)
    config["clean_existing_dir"] = True

    def copy_config(*args):
        return deepcopy(config)

    mocker.patch.object(
        GUIAdvancedPosition,
        "load_config",
        side_effect=copy_config,
    )

    mocker.patch.object(
        GUIAdvancedPosition, "get_all_results", return_value=results_df
    )

    window = AdvancedPositionWidget(None, hydro_shell, config)
    window.show()
    qtbot.addWidget(window)

    yield window

    def no_load_sims_thread():
        assert window._load_sims_thread is None

    qtbot.waitUntil(no_load_sims_thread)


def test_AdvancedPositionWidget_results_open(window_results):
    assert window_results.tabWidget.isTabEnabled(3)
    assert window_results.tabWidget.isTabEnabled(4)


def test_AdvancedPositionWidget_update_delete_sims(qtbot, window_results):
    qtbot.mouseClick(window_results.deleteSimsBox, Qt.MouseButton.LeftButton)

    assert not window_results._delete_sims
    assert not window_results.protectDefaultBox.isEnabled()

    qtbot.mouseClick(window_results.deleteSimsBox, Qt.MouseButton.LeftButton)

    assert window_results._delete_sims
    assert window_results.protectDefaultBox.isEnabled()


def test_AdvancedPositionWidget_update_protect_default(qtbot, window_results):
    qtbot.mouseClick(
        window_results.protectDefaultBox, Qt.MouseButton.LeftButton
    )

    assert not window_results._protect_default

    qtbot.mouseClick(
        window_results.protectDefaultBox, Qt.MouseButton.LeftButton
    )

    assert window_results._protect_default


@pytest.mark.parametrize(
    "button, expected",
    [
        ("bestSimButton", [1]),
        ("worstSimButton", [11]),
        ("top5SimButton", [1, 13, 4, 8, 20]),
        ("bottom5SimButton", [11, 10, 2, 12, 5]),
    ],
)
def test_AdvancedPositionWidget_select_sims_to_load(
    qtbot, window_results, button, expected
):
    window_results.tabWidget.setCurrentIndex(3)
    button = getattr(window_results, button)
    qtbot.mouseMove(button)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert window_results._sims_to_load == expected
    assert not window_results.simsLabel.isEnabled()
    assert not window_results.simSelectEdit.isEnabled()
    assert not window_results.simHelpLabel.isEnabled()
    assert window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_select_sims_to_load_custom(
    qtbot, window_results
):
    window_results.tabWidget.setCurrentIndex(3)
    button = getattr(window_results, "customSimButton")
    qtbot.mouseMove(button)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert window_results._sims_to_load is None
    assert window_results.simsLabel.isEnabled()
    assert window_results.simSelectEdit.isEnabled()
    assert window_results.simHelpLabel.isEnabled()
    assert not window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_update_custom_sims(qtbot, window_results):
    window_results.tabWidget.setCurrentIndex(3)

    button = getattr(window_results, "customSimButton")
    qtbot.mouseMove(button)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    expected = [1, 2, 3, 4]
    expected_str = ", ".join([str(x) for x in expected])
    window_results.simSelectEdit.insert(expected_str)
    window_results.simSelectEdit.returnPressed.emit()

    assert window_results._sims_to_load == expected
    assert window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_update_custom_sims_bad(qtbot, window_results):
    window_results.tabWidget.setCurrentIndex(3)

    button = getattr(window_results, "customSimButton")
    qtbot.mouseMove(button)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    window_results.simSelectEdit.insert("1, two, 3")
    window_results.simSelectEdit.returnPressed.emit()

    assert window_results._sims_to_load is None
    assert not window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_load_sims(qtbot, mocker, window_results):
    strategy = window_results._shell.strategy = mocker.MagicMock()
    strategy.load_simulation_ids.side_effect = lambda *args: time.sleep(0.5)

    # Need to assert that the progress bar was shown
    spy = mocker.spy(window_results, "_progress")

    window_results.tabWidget.setCurrentIndex(3)

    button = getattr(window_results, "bestSimButton")
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(window_results.simLoadButton, Qt.MouseButton.LeftButton)

    def progress_closed():
        assert spy.close.call_count == 1

    qtbot.waitUntil(progress_closed, timeout=1500)

    assert spy.show.call_count == 1
    assert spy.close.call_count == 1


def test_AdvancedPositionWidget_export_data_table(
    mocker, qtbot, tmp_path, window_results
):
    f = tmp_path / "mock.csv"
    mocker.patch.object(
        QtWidgets.QFileDialog, "getSaveFileName", return_value=str(f)
    )

    window_results.tabWidget.setCurrentIndex(3)
    qtbot.mouseClick(window_results.dataExportButton, Qt.MouseButton.LeftButton)

    assert f.is_file()


def test_AdvancedPositionWidget_set_plot(qtbot, window_results):
    window_results.tabWidget.setCurrentIndex(4)

    window_results.xAxisVarBox.setCurrentIndex(4)
    window_results.yAxisVarBox.setCurrentIndex(2)
    window_results.colorAxisVarBox.setCurrentIndex(6)
    window_results.filterVarBox.setCurrentIndex(5)

    window_results.xAxisMinBox.setChecked(True)
    window_results.xAxisMinSpinBox.setValue(20.5)
    window_results.xAxisMaxBox.setChecked(True)
    window_results.xAxisMaxSpinBox.setValue(22.5)

    window_results.yAxisMinBox.setChecked(True)
    window_results.yAxisMinSpinBox.setValue(26800)
    window_results.yAxisMaxBox.setChecked(True)
    window_results.yAxisMaxSpinBox.setValue(27600)

    min_value = 3
    max_value = 10
    window_results.colorAxisMinBox.setChecked(True)
    window_results.colorAxisMinSpinBox.setValue(min_value)
    window_results.colorAxisMaxBox.setChecked(True)
    window_results.colorAxisMaxSpinBox.setValue(max_value)

    window_results.filterVarMinBox.setChecked(True)
    window_results.filterVarMinSpinBox.setValue(65)
    window_results.filterVarMaxBox.setChecked(True)
    window_results.filterVarMaxSpinBox.setValue(70)

    qtbot.mouseMove(window_results.plotButton)
    qtbot.mouseClick(window_results.plotButton, Qt.MouseButton.LeftButton)

    assert window_results.plotExportButton.isEnabled()

    xlim = window_results.plotWidget.figure.axes[0].get_xlim()
    ylim = window_results.plotWidget.figure.axes[0].get_ylim()

    assert xlim == (20.5, 22.5)
    assert ylim == (26800.0, 27600.0)

    cb_yaxis = window_results.plotWidget.figure.axes[1].get_children()[10]
    cb_ticks = cb_yaxis.get_ticklabels()

    assert int(cb_ticks[0].get_text()) == min_value
    assert int(cb_ticks[-1].get_text()) == max_value

    window_results.colorAxisMinBox.setChecked(False)
    qtbot.mouseClick(window_results.plotButton, Qt.MouseButton.LeftButton)

    cb_yaxis = window_results.plotWidget.figure.axes[1].get_children()[9]
    cb_ticks = cb_yaxis.get_ticklabels()

    assert int(cb_ticks[0].get_text()) != min_value
    assert int(cb_ticks[-1].get_text()) == max_value

    window_results.colorAxisMinBox.setChecked(True)
    window_results.colorAxisMaxBox.setChecked(False)
    qtbot.mouseClick(window_results.plotButton, Qt.MouseButton.LeftButton)

    cb_yaxis = window_results.plotWidget.figure.axes[1].get_children()[9]
    cb_ticks = cb_yaxis.get_ticklabels()

    assert int(cb_ticks[0].get_text()) == min_value
    assert int(cb_ticks[-1].get_text()) != max_value

    window_results.colorAxisMinBox.setChecked(True)
    window_results.colorAxisMinSpinBox.setValue(5)
    window_results.colorAxisMaxBox.setChecked(True)
    window_results.colorAxisMaxSpinBox.setValue(5)

    qtbot.mouseClick(window_results.plotButton, Qt.MouseButton.LeftButton)

    assert len(window_results.plotWidget.figure.axes) == 1


def test_AdvancedPositionWidget_export_plot(
    mocker, qtbot, tmp_path, window_results
):
    f = tmp_path / "mock.png"
    mocker.patch.object(
        QtWidgets.QFileDialog, "getSaveFileName", return_value=str(f)
    )

    window_results.tabWidget.setCurrentIndex(4)

    window_results.xAxisVarBox.setCurrentIndex(4)
    window_results.yAxisVarBox.setCurrentIndex(2)
    window_results.colorAxisVarBox.setCurrentIndex(6)
    window_results.filterVarBox.setCurrentIndex(5)

    qtbot.mouseClick(window_results.plotButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(window_results.customSizeBox, Qt.MouseButton.LeftButton)

    window_results.customWidthSpinBox.setValue(6)
    window_results.customHeightSpinBox.setValue(3)

    f = tmp_path / "mock1.png"
    mocker.patch.object(
        QtWidgets.QFileDialog, "getSaveFileName", return_value=str(f)
    )

    qtbot.mouseClick(window_results.plotExportButton, Qt.MouseButton.LeftButton)

    assert f.is_file()

    im = Image.open(str(f))
    width, height = im.size

    expected_width = 1011
    expected_height = 539

    assert width == expected_width
    assert height == expected_height

    f = tmp_path / "mock2.png"
    mocker.patch.object(
        QtWidgets.QFileDialog, "getSaveFileName", return_value=str(f)
    )

    qtbot.mouseClick(window_results.customSizeBox, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(window_results.plotExportButton, Qt.MouseButton.LeftButton)

    assert f.is_file()

    im = Image.open(str(f))
    width, height = im.size

    assert width != expected_width
    assert height != expected_height


def test_AdvancedPositionWidget_optimiser_restart(
    mocker, qtbot, tmp_path, hydro_shell, config, results_df
):
    from dtocean_plugins.strategy_guis.position import GUIAdvancedPosition

    status_str = "Project ready"
    status_code = 1
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_project_status",
        return_value=(status_str, status_code),
    )

    status_str = "Configuration complete"
    status_code = 1
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_config_status",
        return_value=(status_str, status_code),
    )

    status_str = "Worker directory contains files"
    status_code = 0
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_worker_directory_status",
        return_value=(status_str, status_code),
    )

    status_str = "Optimisation incomplete (restart may be possible)"
    status_code = 2
    mocker.patch.object(
        GUIAdvancedPosition,
        "get_optimiser_status",
        return_value=(status_str, status_code),
    )

    config["worker_dir"] = str(tmp_path)
    config["clean_existing_dir"] = True
    mocker.patch.object(
        GUIAdvancedPosition,
        "load_config",
        side_effect=lambda *args: deepcopy(config),
    )

    mocker.patch.object(
        GUIAdvancedPosition, "get_all_results", return_value=results_df
    )

    window = AdvancedPositionWidget(None, hydro_shell, config)
    window.show()
    qtbot.addWidget(window)

    assert not window.tabWidget.isTabEnabled(3)
    assert not window.tabWidget.isTabEnabled(4)
