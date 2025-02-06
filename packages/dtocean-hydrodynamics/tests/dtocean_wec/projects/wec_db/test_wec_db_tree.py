import pytest
from PySide6.QtCore import QItemSelectionModel


@pytest.fixture
def closed_window(qtbot, form_hyd, main_window):
    form_hyd.btn_load_data_t1.click()
    assert "hyd" in form_hyd._data.keys()

    assert main_window.sub_hyd.close()
    assert main_window.sub_power.close()
    assert main_window.sub_plot.close()

    return main_window


def test_open_form_hyd(qtbot, closed_window):
    ix = closed_window.list_model.index(0, 0)
    closed_window.lw_area_selection_model.select(
        ix,
        QItemSelectionModel.SelectionFlag.Select,
    )

    def is_visible():
        assert closed_window.sub_hyd.isVisible()

    qtbot.waitUntil(is_visible)


def test_open_form_power(qtbot, closed_window):
    ix = closed_window.list_model.index(1, 0)
    closed_window.lw_area_selection_model.select(
        ix,
        QItemSelectionModel.SelectionFlag.Select,
    )

    def is_visible():
        assert closed_window.sub_power.isVisible()

    qtbot.waitUntil(is_visible)


def test_open_form_plot(qtbot, closed_window):
    ix = closed_window.list_model.index(2, 0)
    closed_window.lw_area_selection_model.select(
        ix,
        QItemSelectionModel.SelectionFlag.Select,
    )

    def is_visible():
        assert closed_window.sub_plot.isVisible()

    qtbot.waitUntil(is_visible)
