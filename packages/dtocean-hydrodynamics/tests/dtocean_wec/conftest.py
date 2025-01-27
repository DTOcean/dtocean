import os

import pytest

this_dir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def main_window(mocker, qtbot, tmp_path, install_lines):
    from dtocean_wec.main import QMessageBox

    exe_path = tmp_path / "python.exe"
    ini_file = tmp_path / "etc" / "dtocean-data" / "install.ini"
    ini_file.write(install_lines, ensure=True)

    mocker.patch("polite.paths.sys.executable", new=str(exe_path))
    mocker.patch("polite.paths.system", new="win32")
    mocker.patch(
        "dtocean_hydro.configure.SiteDataDirectory",
        return_value=tmp_path,
    )

    mocker.patch.object(
        QMessageBox, "question", return_value=QtGui.QMessageBox.Yes
    )

    window = MainWindow()
    window.show()
    qtbot.addWidget(window)

    return window


@pytest.fixture
def test_data_folder():
    return os.path.join(this_dir, "..", "test_data")
