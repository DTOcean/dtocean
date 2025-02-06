# -*- coding: utf-8 -*-

#    Copyright (C) 2025 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QFileDialog

from dtocean_wec.main import NewProject


def test_new_project(main_window):
    main_window.entrance.btn_new.click()
    assert isinstance(main_window.new_project, NewProject)


def test_new_project_folder_non_empty(monkeypatch, tmp_path, main_window):
    touch = tmp_path / "mock.txt"
    touch.write_text("mock")
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args: tmp_path,
    )

    def handle_dialog():
        while main_window._test_dialog is None:
            QApplication.processEvents()

        button = main_window._test_dialog.buttons()[2]
        assert button.text() == "Clear"
        button.click()

    QTimer.singleShot(0, handle_dialog)
    main_window.entrance.btn_new.click()
    main_window.new_project.btn_prj.click()

    assert not touch.is_file()
