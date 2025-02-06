import pytest


@pytest.fixture
def form_plot(qtbot, form_hyd, main_window):
    form_hyd.btn_load_data_t1.click()

    def form_plot_enabled():
        assert main_window.form_plot.groupBox_11.isEnabled()

    qtbot.waitUntil(form_plot_enabled)

    return main_window.form_plot


def test_form_plot_update(qtbot, form_plot):
    old_canvas = form_plot.canvas
    form_plot.btn_plot_update.click()

    def canvas_changed():
        assert form_plot.canvas is not old_canvas

    qtbot.waitUntil(canvas_changed)
