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
