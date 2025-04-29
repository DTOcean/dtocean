# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2022 Mathew Topper
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

# pylint: disable=redefined-outer-name,unused-argument

import os
import logging
import warnings

from polite.paths import Directory
from dtocean_app import (warn_with_traceback,
                         start_logging,
                         main_,
                         gui_interface)
from dtocean_app.utils.config import init_config


def test_warn_with_traceback():
    
    warnings.showwarning = warn_with_traceback
    warnings.warn("Test warning")
    
    assert True

def test_start_logging(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.UserDataDirectory',
                 return_value=mock_dir)

    start_logging()
    
    logdir = config_tmpdir.join("..", "logs")
    
    assert len(logdir.listdir()) == 1


def test_start_logging_twice(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.UserDataDirectory',
                 return_value=mock_dir)

    start_logging()
    logging.shutdown()
    start_logging()
    
    logdir = config_tmpdir.join("..", "logs")
    
    assert len(logdir.listdir()) == 2


def test_start_logging_debug(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.UserDataDirectory',
                 return_value=mock_dir)

    start_logging(debug=True)
    
    logdir = config_tmpdir.join("..", "logs")
    
    assert len(logdir.listdir()) == 1


def test_start_logging_user(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.utils.config.UserDataDirectory',
                 return_value=mock_dir)
    
    mocker.patch('dtocean_app.UserDataDirectory',
                 return_value=mock_dir)
                 
    init_config(logging=True, files=True)
    
    # This will raise if the logging file is not in the user directory
    mocker.patch('dtocean_app.ObjDirectory',
                 return_value=None)
    
    start_logging()
    
    logdir = config_tmpdir.join("..", "logs")
    
    assert len(logdir.listdir()) == 1


def test_main(mocker, qtbot):
    
    # The qtbot fixture must be requested along with mocking QApplication and
    # DTOceanWindow, or the teardown crashes test_main.py when it follows this 
    # test file.
    
    import sys
    import dtocean_app.main
    
    mocker.patch("dtocean_app.QtGui.QApplication", autospec=True)
    mocker.patch.object(dtocean_app.main, "DTOceanWindow", autospec=True)
    mocker.patch("dtocean_app.QtGui.QSplashScreen.finish")
    sys_exit = mocker.patch.object(sys, 'exit')
    
    main_()
    
    assert sys_exit.call_count == 1


def test_gui_interface(mocker):
    
    import sys
    
    testargs = ["dtocean-app", "--debug", "--trace-warnings", "--quit"]
    mocker.patch.object(sys, 'argv', testargs)
    main_ = mocker.patch('dtocean_app.main_')
    
    gui_interface()
    
    expected = {'debug': True, 'trace_warnings': True, 'force_quit': True}
    assert main_.call_args.kwargs == expected


def test_cli(capfd):
    
    exit_status = os.system('dtocean-app --help')
    
    assert exit_status == 0
    
    captured = capfd.readouterr()
    
    assert "Run the DTOcean graphical application." in captured.out
    assert "The DTOcean Developers (c) 2022." in captured.out
