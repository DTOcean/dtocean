from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog

from dtocean_wec.main import MainWindow
from dtocean_wec.tab2 import RunNemoh
from dtocean_wec.tab3 import ReadNemoh

THIS_DIR = Path(__file__)


@pytest.fixture
def nehom_path(mocker, monkeypatch, qtbot, tmp_path):
    from dtocean_wec.main import QMessageBox

    mocker.patch.object(
        QMessageBox,
        "question",
        return_value=QMessageBox.StandardButton.Yes,
    )

    main_window = MainWindow()
    main_window.show()
    qtbot.addWidget(main_window)

    run_nehom_path = tmp_path / "run_nehom"
    run_nehom_path.mkdir()
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args: run_nehom_path,
    )

    main_window.entrance.btn_new.click()
    main_window.new_project.btn_prj.click()
    main_window.new_project.btn_t2.click()

    def check_form():
        assert main_window.form_hyd is not None

    qtbot.waitUntil(check_form)

    form_hyd = main_window.form_hyd
    assert isinstance(form_hyd, RunNemoh)

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

    form_hyd.btn_submit_t2.click()
    qtbot.waitUntil(lambda: form_hyd.btn_calculate_t2.isEnabled())

    form_hyd.btn_calculate_t2.click()

    def is_enabled():
        assert main_window.form_power is not None
        assert main_window.form_power.isEnabled()

    qtbot.waitUntil(is_enabled)

    return run_nehom_path / "hydrodynamic"


@pytest.fixture
def form_hyd(monkeypatch, qtbot, tmp_path, main_window) -> ReadNemoh:
    load_nehom_path = tmp_path / "load_nehom"
    load_nehom_path.mkdir()
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args: load_nehom_path,
    )

    main_window.entrance.btn_new.click()
    main_window.new_project.btn_prj.click()
    main_window.new_project.btn_t3.click()

    def check_form():
        assert main_window.form_hyd is not None

    qtbot.waitUntil(check_form)

    return main_window.form_hyd


@pytest.fixture
def form_hyd_filled(qtbot, monkeypatch, form_hyd: ReadNemoh, nehom_path: Path):
    form_hyd.le_data_t3.setText(str(nehom_path))
    form_hyd.ndof_t3.setText("1")
    form_hyd.pto_dof_t3.setText("1")
    form_hyd.moor_dof_t3.setText("1")
    form_hyd.local_cs_t3.setText("0, 0, 0")
    form_hyd.sh2_t3.setChecked(True)

    mesh_path = THIS_DIR.parents[4] / "test_data" / "cube.GDF"
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args: (str(mesh_path.absolute()), None),
    )
    form_hyd.btn_mesh_f_t3.click()

    form_hyd.id_body_t3.setText("0")
    form_hyd.cog_body_t3.setText("0, 0, -1.5")
    form_hyd.cs_body_t3.setText("0, 0, 0")
    form_hyd.parent_body_t3.setText("-1")
    form_hyd.mass_body_t3.setText("1000")
    form_hyd.inertia_body_t3.setText("100,0,0; 0,100,0; 0,0,20")

    form_hyd.btn_add_body_t3.click()
    qtbot.waitUntil(lambda: form_hyd.tab_body_t3.rowCount() == 1)

    return form_hyd
