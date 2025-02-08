from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QPoint, Qt

from dtocean_wec.tab2 import QFileDialog
from dtocean_wec.utils.Camera import Camera
from dtocean_wec.utils.mesh_plotter import PythonQtOpenGLMeshViewer

THIS_DIR = Path(__file__)


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
    assert mesh_plotter.isVisible()


def test_mesh_plotter_translate(
    mocker,
    qtbot,
    mesh_plotter: PythonQtOpenGLMeshViewer,
):
    translateSceneRightAndUp: MagicMock = mocker.spy(
        Camera,
        "translateSceneRightAndUp",
    )

    old_position = mesh_plotter.viewer3D.camera.position
    start = mesh_plotter.viewer3D.rect().center()
    end = QPoint(start.x() + 10, start.y())

    qtbot.mouseMove(mesh_plotter.viewer3D)
    qtbot.mousePress(mesh_plotter, Qt.MouseButton.LeftButton)
    qtbot.mouseMove(mesh_plotter.viewer3D, pos=end)
    qtbot.mouseRelease(mesh_plotter, Qt.MouseButton.LeftButton, pos=end)

    new_position = mesh_plotter.viewer3D.camera.position

    assert not old_position == new_position
    translateSceneRightAndUp.assert_called_once()


def test_mesh_plotter_rotate(
    mocker,
    qtbot,
    mesh_plotter: PythonQtOpenGLMeshViewer,
):
    orbit: MagicMock = mocker.spy(
        Camera,
        "orbit",
    )

    old_position = mesh_plotter.viewer3D.camera.position
    start = mesh_plotter.viewer3D.rect().center()
    end = QPoint(start.x() + 10, start.y())

    qtbot.mouseMove(mesh_plotter.viewer3D)
    qtbot.mousePress(mesh_plotter, Qt.MouseButton.RightButton)
    qtbot.mouseMove(mesh_plotter.viewer3D, pos=end)
    qtbot.mouseRelease(mesh_plotter, Qt.MouseButton.RightButton, pos=end)

    new_position = mesh_plotter.viewer3D.camera.position

    assert not old_position == new_position
    orbit.assert_called_once()


def test_mesh_plotter_zoom(
    mocker,
    qtbot,
    mesh_plotter: PythonQtOpenGLMeshViewer,
):
    dollyCameraForward: MagicMock = mocker.spy(
        Camera,
        "dollyCameraForward",
    )

    old_position = mesh_plotter.viewer3D.camera.position
    start = mesh_plotter.viewer3D.rect().center()
    end = QPoint(start.x(), start.y() + 10)

    qtbot.mouseMove(mesh_plotter.viewer3D)
    qtbot.mousePress(mesh_plotter, Qt.MouseButton.MiddleButton)
    qtbot.mouseMove(mesh_plotter.viewer3D, pos=end)
    qtbot.mouseRelease(mesh_plotter, Qt.MouseButton.MiddleButton, pos=end)

    new_position = mesh_plotter.viewer3D.camera.position

    assert not old_position == new_position
    dollyCameraForward.assert_called_once()


def test_mesh_plotter_zoom_wheel(
    mocker,
    qtbot,
    mesh_plotter: PythonQtOpenGLMeshViewer,
):
    mouse_zoom: MagicMock = mocker.spy(
        Camera,
        "mouse_zoom",
    )

    old_position = mesh_plotter.viewer3D.camera.position
    qtbot.mouseWheel(mesh_plotter.viewer3D)
    new_position = mesh_plotter.viewer3D.camera.position

    assert not old_position == new_position
    mouse_zoom.assert_called_once()
