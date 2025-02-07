from pathlib import Path

import pytest
from PySide6.QtCore import QPoint, Qt

from dtocean_wec.tab2 import QFileDialog
from dtocean_wec.utils.mesh_plotter import PythonQtOpenGLMeshViewer

THIS_DIR = Path(__file__)


def test_form_hyd_load(form_hyd):
    assert form_hyd._data is not None


@pytest.fixture
def mesh_plotter(monkeypatch, form_hyd, main_window):
    mesh_path = THIS_DIR.parents[4] / "test_data" / "cube.GDF"
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args: (str(mesh_path.absolute()), None),
    )

    form_hyd.btn_mesh_f_t2.click()
    form_hyd.btn_view_mesh.click()

    return main_window.mesh_view


def test_open_mesh_plotter(mesh_plotter: PythonQtOpenGLMeshViewer):
    assert isinstance(mesh_plotter, PythonQtOpenGLMeshViewer)


def test_mesh_plotter_translate(qtbot, mesh_plotter: PythonQtOpenGLMeshViewer):
    print(mesh_plotter.viewer3D.camera.position)

    qtbot.mousePress(mesh_plotter, Qt.MouseButton.LeftButton)
    qtbot.mouseMove(mesh_plotter, pos=QPoint(50, 0))
    qtbot.mouseRelease(mesh_plotter, Qt.MouseButton.LeftButton)

    print(mesh_plotter.viewer3D.camera.position)

    assert False
