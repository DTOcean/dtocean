import pytest


@pytest.fixture
def form_power(qtbot, form_hyd, main_window):
    form_hyd.btn_load_data_t1.click()

    def form_plot_enabled():
        assert main_window.form_power.btn_plot_pfit.isEnabled()

    qtbot.waitUntil(form_plot_enabled)

    return main_window.form_power


def test_form_power_plot(qtbot, form_power):
    old_canvas = form_power.canvas
    form_power.btn_plot_pfit.click()

    def canvas_changed():
        assert form_power.canvas is not old_canvas

    qtbot.waitUntil(canvas_changed)
