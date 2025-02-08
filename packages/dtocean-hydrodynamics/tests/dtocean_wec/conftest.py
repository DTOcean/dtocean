import os

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QWheelEvent

from dtocean_wec.main import MainWindow

this_dir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def main_window(mocker, qtbot):
    from dtocean_wec.main import QMessageBox

    mocker.patch.object(
        QMessageBox,
        "question",
        return_value=QMessageBox.StandardButton.Yes,
    )

    window = MainWindow()
    window.show()
    qtbot.addWidget(window)

    return window


@pytest.fixture
def test_data_folder():
    return os.path.join(this_dir, "..", "..", "test_data")


@pytest.fixture
def qtbot(qapp, qtbot):
    def mouseWheel(
        widget,
        pos=QPoint(),
        delta=QPoint(10, 10),
        inverted=False,
        source=Qt.MouseEventSource.MouseEventNotSynthesized,
    ):
        event = QWheelEvent(
            pos,
            widget.mapToGlobal(pos),
            delta,
            delta,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            inverted,
            source,
        )
        qapp.sendEvent(widget, event)

    qtbot.mouseWheel = mouseWheel

    return qtbot
