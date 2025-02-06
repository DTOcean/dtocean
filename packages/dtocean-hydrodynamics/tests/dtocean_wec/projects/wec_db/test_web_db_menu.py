from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QMessageBox

import dtocean_wave.utils.hdf5_interface as h5i
from dtocean_wec.main import MainWindow


@pytest.fixture
def loaded_window(form_hyd, main_window):
    form_hyd.btn_load_data_t1.click()
    assert "hyd" in form_hyd._data.keys()
    return main_window


@pytest.fixture
def closed_window(loaded_window):
    assert loaded_window.sub_hyd.close()
    assert loaded_window.sub_power.close()
    assert loaded_window.sub_plot.close()
    return loaded_window


def test_save_project_no_data(mocker, form_hyd, main_window):
    save_dict_to_hdf5: MagicMock = mocker.spy(h5i, "save_dict_to_hdf5")
    main_window.actionSave_Project.trigger()

    assert "inputs_hydrodynamic" in main_window._data
    assert "hyd" not in main_window._data
    save_dict_to_hdf5.assert_called_once()


def test_save_project_loaded(mocker, loaded_window):
    save_dict_to_hdf5: MagicMock = mocker.spy(h5i, "save_dict_to_hdf5")
    loaded_window.actionSave_Project.trigger()

    assert "inputs_hydrodynamic" in loaded_window._data
    assert "hyd" in loaded_window._data
    save_dict_to_hdf5.assert_called_once()


def test_load_project(mocker, monkeypatch, loaded_window):
    populate_project: MagicMock = mocker.spy(MainWindow, "populate_project")
    monkeypatch.setattr(
        MainWindow,
        "save_choice",
        lambda *args: QMessageBox.StandardButton.Save,
    )

    loaded_window.actionLoad_Project.trigger()
    populate_project.assert_called_once()


def test_save_dtocean_format(loaded_window):
    loaded_window.actionGenerate_array_hydrodynamic.trigger()


def test_open_form_hyd(qtbot, closed_window):
    closed_window.actionHydrodynamic.trigger()

    def is_visible():
        assert closed_window.sub_hyd.isVisible()

    qtbot.waitUntil(is_visible)


def test_open_form_power(qtbot, closed_window):
    closed_window.actionPerformance_Fit.trigger()

    def is_visible():
        assert closed_window.sub_power.isVisible()

    qtbot.waitUntil(is_visible)


def test_open_form_plot(qtbot, closed_window):
    closed_window.actionData_Visualisation.trigger()

    def is_visible():
        assert closed_window.sub_plot.isVisible()

    qtbot.waitUntil(is_visible)
    qtbot.waitUntil(is_visible)
    qtbot.waitUntil(is_visible)
