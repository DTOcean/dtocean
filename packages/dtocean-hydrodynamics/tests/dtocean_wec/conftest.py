import os

import pytest
from PySide6 import QtWidgets

from dtocean_wec.main import MainWindow

this_dir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def main_window(mocker, qtbot):
    from dtocean_wec.main import QMessageBox

    mocker.patch.object(
        QMessageBox,
        "question",
        return_value=QtWidgets.QMessageBox.StandardButton.Yes,
    )

    window = MainWindow()
    window.show()
    qtbot.addWidget(window)

    return window


@pytest.fixture
def test_data_folder():
    return os.path.join(this_dir, "..", "..", "test_data")
