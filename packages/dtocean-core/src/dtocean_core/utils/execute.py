# -*- coding: utf-8 -*-

#    Copyright (C) 2021 Mathew Topper
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

from .. import start_logging
from ..core import Core
from ..menu import ModuleMenu
from ..extensions import StrategyManager


def warn_with_traceback(message,
                        category,
                        filename,
                        lineno,
                        logfile=None,
                        line=None):
    
    log = logfile if hasattr(logfile, 'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(message,
                                     category,
                                     filename,
                                     lineno,
                                     line))
    
    return


def main(fpath,
         save=True,
         full=False,
         warn=False,
         log=False):
    
    if full:
        action_str = "all scheduled modules"
    else:
        action_str = "next scheduled module"
    
    msg_str = "\n>>> Executing {} in project '{}'".format(action_str, fpath)
    extra_string = ""
    
    if warn:
        extra_string += "warning tracebacks"
    
    if log:
        if extra_string:
            extra_string += " and "
        extra_string += "logging"
    
    if extra_string:
        msg_str = "{} with {}".format(msg_str, extra_string)
    
    msg_str += "\n"
    print msg_str
    
    if warn:
        warnings.showwarning = warn_with_traceback
    
    if log:
        start_logging()
    
    my_core = Core()
    my_project = my_core.load_project(fpath)
    
    if full:
    
        strategy_manager = StrategyManager()
        basic_strategy = strategy_manager.get_strategy("Basic")
        
        start_time = time.time()
        basic_strategy.execute(my_core, my_project)
    
    else:
        
        my_menu = ModuleMenu()
        
        start_time = time.time()
        my_menu.execute_current(my_core, my_project)
    
    msg_str = "\n>>> Execution time: {}s".format(time.time() - start_time)
    print msg_str
    
    if not save: return
    
    if save is True: 
        prepath, ext = os.path.splitext(fpath)
        save_path = "{}_complete{}".format(prepath, ext)
    else:
        save_path = save
    
    msg_str = "\n>>> Saving project to: {}".format(save_path)
    print msg_str
    
    my_core.dump_project(my_project, save_path)
    
    return


def main_interface():
    '''Command line interface for execute_dtocean_project.
    
    Example:
    
        To get help::
            
            $ python execute_dtocean_project -h
    
    '''
    
    desStr = ("Execute DTOcean .prj project files. By default, the next "
              "module scheduled is executed. All scheduled modules can also "
              "be run using the appropriate option. Completed simulations are "
              "saved to a new project file with '_complete' appended to the "
              "file path.")
    
    parser = argparse.ArgumentParser(description=desStr)
    
    parser.add_argument("fpath",
                        help=("path to DTOcean project file"),
                        type=str)
    
    parser.add_argument("-o", "--out",
                        help=("specify output path for results file"),
                        type=str,
                        default=None)
                        
    parser.add_argument("-f", "--full",
                        help=("execute all scheduled modules"),
                        action='store_true')
     
    parser.add_argument("-n", "--no-save",
                        help=("do not save the results"),
                        action='store_true')
                        
    parser.add_argument("-w", "--warnings",
                        help=("show tracebacks for all warnings"),
                        action='store_true')
    
    parser.add_argument("-l", "--logging",
                        help=("activate the DTOcean logging system"),
                        action='store_true')
    
    args = parser.parse_args()
    
    fpath = args.fpath
    rpath = args.out
    full = args.full
    warn = args.warnings
    no_save = args.no_save
    log = args.logging
    
    if no_save is True:
        save = False
    elif rpath is not None:
        save = rpath.strip()
    else:
        save = True
    
    main(fpath, save, full, warn, log)
    
    return
