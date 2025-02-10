import pytest
from PySide6.QtWidgets import QFileDialog


@pytest.fixture
def form_hyd(monkeypatch, qtbot, tmp_path, main_window):
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args: tmp_path,
    )

    main_window.entrance.btn_new.click()
    main_window.new_project.btn_prj.click()
    main_window.new_project.btn_t4.click()

    def check_form():
        assert main_window.form_hyd is not None

    qtbot.waitUntil(check_form)

    return main_window.form_hyd
