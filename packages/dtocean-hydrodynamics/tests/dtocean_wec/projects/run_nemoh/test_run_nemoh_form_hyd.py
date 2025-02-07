from pathlib import Path

import pytest

from dtocean_wec.tab2 import QFileDialog
from dtocean_wec.utils.mesh_plotter import PythonQtOpenGLMeshViewer

THIS_DIR = Path(__file__)


def test_form_hyd_load(form_hyd):
    assert form_hyd._data is not None


@pytest.fixture
def mesh_plotter(monkeypatch, form_hyd):
    mesh_path = THIS_DIR.parents[4] / "test_data" / "cube.GDF"
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args: (str(mesh_path.absolute()), None),
    )

    form_hyd.btn_view_mesh.click()


def test_open_mesh_plotter(mesh_plotter, main_window):
    assert isinstance(main_window.mesh_view, PythonQtOpenGLMeshViewer)
