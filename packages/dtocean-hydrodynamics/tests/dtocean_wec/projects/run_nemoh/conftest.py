from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog

from dtocean_wec.tab2 import RunNemoh

THIS_DIR = Path(__file__)


@pytest.fixture
def form_hyd(monkeypatch, qtbot, tmp_path, main_window):
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args: tmp_path,
    )

    main_window.entrance.btn_new.click()
    main_window.new_project.btn_prj.click()
    main_window.new_project.btn_t2.click()

    def check_form():
        assert main_window.form_hyd is not None

    qtbot.waitUntil(check_form)

    return main_window.form_hyd


@pytest.fixture
def form_hyd_filled(qtbot, monkeypatch, form_hyd: RunNemoh):
    form_hyd.ndof.setText("1")
    form_hyd.pto_dof.setText("1")
    form_hyd.moor_dof.setText("1")
    form_hyd.fre_def.setText("10, 0.1, 1.0")
    form_hyd.angles_def.setText("1")
    form_hyd.sb_water_depth.setValue(50.0)
    form_hyd.cb_gen_array_mat.setChecked(True)
    form_hyd.local_cs.setText("0, 0, 0")
    form_hyd.sh2.setChecked(True)

    mesh_path = THIS_DIR.parents[4] / "test_data" / "cube.GDF"
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args: (str(mesh_path.absolute()), None),
    )
    form_hyd.btn_mesh_f_t2.click()

    form_hyd.id_body.setText("0")
    form_hyd.cog_body.setText("0, 0, -1.5")
    form_hyd.cs_body.setText("0, 0, 0")
    form_hyd.parent_body.setText("-1")
    form_hyd.mass_body.setText("1000")
    form_hyd.inertia_body.setText("100,0,0; 0,100,0; 0,0,20")

    form_hyd.btn_add_body.click()
    qtbot.waitUntil(lambda: form_hyd.tab_body.rowCount() == 1)

    return form_hyd


@pytest.fixture
def form_hyd_calculated(qtbot, form_hyd_filled: RunNemoh, main_window):
    form_hyd_filled.btn_submit_t2.click()
    qtbot.waitUntil(lambda: form_hyd_filled.btn_calculate_t2.isEnabled())

    form_hyd_filled.btn_calculate_t2.click()
    qtbot.waitUntil(lambda: main_window.form_power.isEnabled())

    return form_hyd_filled
