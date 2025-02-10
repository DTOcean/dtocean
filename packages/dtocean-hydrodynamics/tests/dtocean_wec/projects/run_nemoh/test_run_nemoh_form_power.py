from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog

from dtocean_wec.main import MainWindow
from dtocean_wec.pfit_form import PowerPerformance


@pytest.fixture
def form_power(
    form_hyd_calculated,
    main_window: MainWindow,
) -> PowerPerformance:
    assert main_window.form_power is not None
    return main_window.form_power


@pytest.fixture
def form_power_loaded(
    monkeypatch,
    qtbot,
    form_power: PowerPerformance,
    main_window: MainWindow,
):
    heaving_cylinder_path = (
        main_window.wec_share_path / "wec_db" / "heaving_cylinder"
    )
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args: str(heaving_cylinder_path),
    )

    form_power.btn_browse_pfit.click()
    qtbot.waitUntil(lambda: form_power.btn_load_pfit.isEnabled())

    return form_power


def test_power_fit_load(
    form_power_loaded: PowerPerformance,
    main_window: MainWindow,
):
    heaving_cylinder_path = (
        main_window.wec_share_path / "wec_db" / "heaving_cylinder"
    )
    assert Path(form_power_loaded.le_pfit_data.text()) == heaving_cylinder_path
