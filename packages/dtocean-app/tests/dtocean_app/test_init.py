# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2025 Mathew Topper
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


import logging
import warnings

from dtocean_app import main_, start_logging, warn_with_traceback
from dtocean_app.utils.config import init_config


def test_warn_with_traceback():
    warnings.showwarning = warn_with_traceback
    warnings.warn("Test warning")

    assert True


def test_start_logging(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch("dtocean_app.UserDataPath", return_value=tmp_path)

    start_logging()

    logdir = config_tmpdir / ".." / "logs"
    assert len(list(logdir.iterdir())) == 1


def test_start_logging_twice(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch("dtocean_app.UserDataPath", return_value=tmp_path)

    start_logging()
    logging.shutdown()
    start_logging()

    logdir = config_tmpdir / ".." / "logs"
    assert len(list(logdir.iterdir())) == 2


def test_start_logging_debug(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch("dtocean_app.UserDataPath", return_value=tmp_path)

    start_logging(debug=True)

    logdir = config_tmpdir / ".." / "logs"
    assert len(list(logdir.iterdir())) == 1


def test_start_logging_user(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_app.utils.config.UserDataPath",
        return_value=tmp_path,
    )

    mocker.patch("dtocean_app.UserDataPath", return_value=tmp_path)

    init_config(logging=True)

    # This will raise if the logging file is not in the user directory
    mocker.patch("dtocean_app.ModPath", return_value=None)

    start_logging()

    logdir = config_tmpdir / ".." / "logs"
    assert len(list(logdir.iterdir())) == 1


def test_main(mocker, qtbot, tmp_path):
    # The qtbot fixture must be requested along with mocking QApplication and
    # DTOceanWindow, or the teardown crashes test_main.py when it follows this
    # test file.

    import sys

    import dtocean_app.window

    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch("dtocean_app.UserDataPath", return_value=tmp_path)
    mocker.patch("dtocean_app.QtWidgets.QApplication", autospec=True)
    mocker.patch.object(dtocean_app.window, "DTOceanWindow", autospec=True)
    mocker.patch("dtocean_app.QtWidgets.QSplashScreen.finish")
    sys_exit = mocker.patch.object(sys, "exit")

    main_()

    assert sys_exit.call_count == 1
