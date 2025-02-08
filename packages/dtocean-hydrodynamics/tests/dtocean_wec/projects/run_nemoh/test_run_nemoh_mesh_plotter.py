from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QPoint, Qt

from dtocean_wec.tab2 import QFileDialog
from dtocean_wec.utils.Camera import Camera
from dtocean_wec.utils.mesh_plotter import (
    PythonQtOpenGLMeshViewer,
    Viewer3DWidget,
)

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


def test_mesh_plotter_structure_off(mocker, mesh_plotter):
    drawMesh: MagicMock = mocker.spy(
        Viewer3DWidget,
        "drawMesh",
    )
    mesh_plotter.button1.click()

    assert not mesh_plotter.viewer3D.drawMesh_cond
    drawMesh.assert_not_called()


def test_mesh_plotter_structure_on(qtbot, mocker, mesh_plotter):
    drawMesh: MagicMock = mocker.spy(
        Viewer3DWidget,
        "drawMesh",
    )
    mesh_plotter.button1.click()
    mesh_plotter.button1.click()
    qtbot.waitUntil(lambda: drawMesh.assert_called())

    args, _ = drawMesh.call_args
    assert mesh_plotter.viewer3D.drawMesh_cond
    assert len(args) == 1


def test_mesh_plotter_wireframe_on(qtbot, mocker, mesh_plotter):
    drawMesh: MagicMock = mocker.spy(
        Viewer3DWidget,
        "drawMesh",
    )
    mesh_plotter.button3.click()
    qtbot.waitUntil(lambda: drawMesh.assert_called())

    assert not mesh_plotter.viewer3D.drawMesh_cond
    assert mesh_plotter.viewer3D.drawWire_cond

    _, kwargs = drawMesh.call_args
    assert len(kwargs) == 1
    assert "wireframe" in kwargs
    assert kwargs["wireframe"]


def test_mesh_plotter_wireframe_off(qtbot, mocker, mesh_plotter):
    bounding_box: MagicMock = mocker.spy(
        Viewer3DWidget,
        "bounding_box",
    )
    drawMesh: MagicMock = mocker.spy(
        Viewer3DWidget,
        "drawMesh",
    )
    mesh_plotter.button3.click()
    qtbot.waitUntil(lambda: drawMesh.assert_called())

    bounding_box.reset_mock()
    drawMesh.reset_mock()
    mesh_plotter.button3.click()
    qtbot.waitUntil(lambda: bounding_box.assert_called())

    assert not mesh_plotter.viewer3D.drawMesh_cond
    assert not mesh_plotter.viewer3D.drawWire_cond
    assert not drawMesh.called


def test_mesh_plotter_norms_on(qtbot, mocker, mesh_plotter):
    drawNorms: MagicMock = mocker.spy(
        Viewer3DWidget,
        "drawNorms",
    )
    mesh_plotter.button2.click()
    qtbot.waitUntil(lambda: drawNorms.assert_called())

    assert mesh_plotter.viewer3D.drawNorms_cond


def test_mesh_plotter_norms_off(qtbot, mocker, mesh_plotter):
    bounding_box: MagicMock = mocker.spy(
        Viewer3DWidget,
        "bounding_box",
    )
    drawNorms: MagicMock = mocker.spy(
        Viewer3DWidget,
        "drawNorms",
    )
    mesh_plotter.button2.click()
    qtbot.waitUntil(lambda: drawNorms.assert_called())

    bounding_box.reset_mock()
    drawNorms.reset_mock()
    mesh_plotter.button2.click()
    qtbot.waitUntil(lambda: bounding_box.assert_called())

    assert not mesh_plotter.viewer3D.drawNorms_cond
    assert not drawNorms.called
