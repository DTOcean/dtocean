from dtocean_wec.main import MainWindow
from dtocean_wec.tab3 import ReadNemoh


def test_form_hyd_load(form_hyd: ReadNemoh):
    assert form_hyd._data is not None


def test_add_body(form_hyd_filled: ReadNemoh):
    assert form_hyd_filled.tab_body_t3.rowCount() == 1


def test_submit_inputs(qtbot, form_hyd_filled: ReadNemoh):
    form_hyd_filled.btn_submit_t3.click()
    qtbot.waitUntil(lambda: form_hyd_filled.btn_load_data_t3.isEnabled())
    assert form_hyd_filled.btn_load_data_t3.isEnabled()


def test_load_data(qtbot, form_hyd_filled: ReadNemoh, main_window: MainWindow):
    form_hyd_filled.btn_submit_t3.click()
    qtbot.waitUntil(lambda: form_hyd_filled.btn_load_data_t3.isEnabled())

    form_hyd_filled.btn_load_data_t3.click()

    def is_enabled():
        assert main_window.form_power is not None
        assert main_window.form_power.isEnabled()

    qtbot.waitUntil(is_enabled)

    assert form_hyd_filled._data is not None
    assert "hyd" in form_hyd_filled._data
    assert form_hyd_filled._data["hyd"]
