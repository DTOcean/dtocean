from unittest.mock import MagicMock

import dtocean_wec.tab2 as tab2
from dtocean_wec.main import MainWindow
from dtocean_wec.tab2 import RunNemoh


def test_form_hyd_load(form_hyd: RunNemoh):
    assert form_hyd._data is not None


def test_add_body(form_hyd_filled: RunNemoh):
    assert form_hyd_filled.tab_body.rowCount() == 1


def test_submit_inputs(qtbot, form_hyd_filled: RunNemoh):
    form_hyd_filled.btn_submit_t2.click()
    qtbot.waitUntil(lambda: form_hyd_filled.btn_calculate_t2.isEnabled())
    assert form_hyd_filled.btn_calculate_t2.isEnabled()


def test_calculate(form_hyd_calculated: RunNemoh):
    assert form_hyd_calculated._data is not None
    assert "hyd" in form_hyd_calculated._data
    assert form_hyd_calculated._data["hyd"]


def test_calculate_again(
    mocker,
    monkeypatch,
    qtbot,
    form_hyd_calculated: RunNemoh,
    main_window: MainWindow,
):
    monkeypatch.setattr(RunNemoh, "_ask_existing", classmethod(lambda *args: 0))
    send_data_to_bem_interface: MagicMock = mocker.spy(
        tab2,
        "send_data_to_bem_interface",
    )

    form_hyd_calculated.btn_submit_t2.click()
    qtbot.waitUntil(lambda: form_hyd_calculated.btn_calculate_t2.isEnabled())

    form_hyd_calculated.btn_calculate_t2.click()

    def is_enabled():
        assert main_window.form_power is not None
        return main_window.form_power.isEnabled()

    qtbot.waitUntil(is_enabled)

    send_data_to_bem_interface.assert_called_once()
