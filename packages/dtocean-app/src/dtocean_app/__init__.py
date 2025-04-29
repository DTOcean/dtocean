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

import os
import sys
import time
import argparse
import warnings
import traceback

from PyQt4 import QtGui, QtCore

from polite.configuration import ReadINI
from polite.paths import (Directory,
                          ObjDirectory,
                          UserDataDirectory)
from polite.configuration import Logger

from .utils.qtlog import QtHandler

module_path = os.path.realpath(__file__)


def warn_with_traceback(message,
                        category,
                        filename,
                        lineno,
                        file=None,
                        line=None):

    log = file if hasattr(file,'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(message,
                                     category,
                                     filename,
                                     lineno,
                                     line))
    
    return


def start_logging(debug=False):
    
    # Disable the logging QtHandler if the debug flag is set
    QtHandler.debug = debug
    
    # Pick up the configuration from the user directory if it exists
    userdir = UserDataDirectory("dtocean_app", "DTOcean", "config")
    
    # Look for logging.yaml
    if userdir.isfile("logging.yaml"):
        configdir = userdir
    else:
        configdir = ObjDirectory("dtocean_app", "config")
    
    # Get the logger configuration
    log = Logger(configdir)
    log_config_dict = log.read()
    
    # Get Directory to place logs
    log_dir = get_log_dir()
    
    # Update the file logger if present
    if "file" in log_config_dict["handlers"]:
        log_filename = log_config_dict["handlers"]["file"]["filename"]
        log_path = log_dir.get_path(log_filename)
        log_config_dict["handlers"]["file"]["filename"] = log_path
        log_dir.makedir()
    
    log.configure_logger(log_config_dict)
    logger = log.add_named_logger("dtocean_app")
    
    # Rotate any rotating file handlers
    for handler in logger.handlers:
        
        if handler.__class__.__name__ == 'RotatingFileHandler':
            
            try:
                handler.doRollover()
            except WindowsError:
                pass
    
    logger.info("Welcome to DTOcean")
    
    return


def get_log_dir():
    
    userdir = UserDataDirectory("dtocean_app", "DTOcean", "config")
    
    # Look for files.ini
    if userdir.isfile("files.ini"):
        configdir = userdir
    else:
        configdir = ObjDirectory("dtocean_app", "config")
    
    files_ini = ReadINI(configdir, "files.ini")
    files_config = files_ini.get_config()
    
    appdir_path = userdir.get_path("..")
    log_folder = files_config["logs"]["path"]
    log_path = os.path.join(appdir_path, log_folder)
    logdir = Directory(log_path)
    
    return logdir


#def main(debug=False, trace_warnings=False):
#    """An example of profiling"""
#    import cProfile 
#    cProfile.runctx("main_(debug, trace_warnings)",
#                    globals(),
#                    locals(),
#                    "profile.stat")


def main_(debug=False, trace_warnings=False, force_quit=False):

    """Run the DTOcean tool"""
    
    # Add traces to warnings
    if trace_warnings: warnings.showwarning = warn_with_traceback
    
    # Bring up the logger
    start_logging(debug)

    # Build the main app
    app = QtGui.QApplication(sys.argv)

    # Create and display the splash screen
    splash_path = os.path.join(module_path, '..', 'dtocean2plus_splash.png')
    splash_pix = QtGui.QPixmap(splash_path)
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash_font = QtGui.QFont()
    splash_font.setFamily("Verdana")
    splash_font.setPointSize(8)
    splash.setMask(splash_pix.mask())
    splash.setFont(splash_font)
    splash.show()
    app.processEvents()
    
    time.sleep(0.2)
    
    message_allignment = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom
    message_color = QtCore.Qt.white
    
    splash.showMessage("Loading matplotlib",
                       message_allignment,
                       message_color)
    
    import matplotlib
    import matplotlib.pyplot
    
    splash.showMessage("Loading pandas",
                       message_allignment,
                       message_color)
    
    import pandas
    
    splash.showMessage("Loading DTOcean core",
                       message_allignment,
                       message_color)
    
    import dtocean_core.core
    from .core import GUICore
    
    splash.showMessage("Loading DTOcean interface",
                       message_allignment,
                       message_color)
    
    from .main import DTOceanWindow, Shell

    splash.showMessage("Preparing data catalogue",
                       message_allignment,
                       message_color)
    
    core = GUICore()
    core._create_data_catalog()
    
    splash.showMessage("Preparing modules",
                       message_allignment,
                       message_color)
    
    core._create_control()

    splash.showMessage("Preparing IO",
                       message_allignment,
                       message_color)

    core._create_sockets()
    core._init_plots()
    
    splash.showMessage("Starting DTOcean application",
                       message_allignment,
                       message_color)
    
    time.sleep(0.2)
    
    shell = Shell(core)
    main_window = DTOceanWindow(shell, debug)
    main_window.show()
    
    splash.finish(main_window)
    
    if not force_quit:
        sys.exit(app.exec_())
    
    return


def gui_interface():
    
    '''Command line interface for dtocean-app.
    
    Example:
    
        For help::
        
            $ dtocean-app --help
        
    '''
    
    epiStr = ('''The DTOcean Developers (c) 2022.''')
    
    desStr = "Run the DTOcean graphical application."
    
    parser = argparse.ArgumentParser(description=desStr,
                                     epilog=epiStr)
    
    parser.add_argument("--debug",
                        help=("disable stream redirection"),
                        action='store_true')
    
    parser.add_argument("--trace-warnings",
                        help=("add stack trace to warnings"),
                        action='store_true')
    
    parser.add_argument("--quit",
                        help=("quit before interface opens"),
                        action='store_true')
    
    args = parser.parse_args()
    debug = args.debug
    trace_warnings = args.trace_warnings
    force_quit = args.quit
    
    main_(debug=debug, trace_warnings=trace_warnings, force_quit=force_quit)
    
    return
