# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2019 Mathew Topper
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

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import sys
import logging
import argparse
import datetime

from polite.paths import (ObjDirectory,
                          UserDataDirectory,
                          DirectoryMap)

from . import SmartFormatter

# Set up logging
module_logger = logging.getLogger(__name__)


def init_config(logging=False, database=False, files=False, overwrite=False):
    
    """Copy config files to user data directory"""
    
    if not any([logging, database, files]): return
    
    objdir = ObjDirectory(__name__, "..", "config")
    datadir = UserDataDirectory("dtocean_core", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)
    
    if logging: dirmap.copy_file("logging.yaml", overwrite=overwrite)
    if database: dirmap.copy_file("database.yaml", overwrite=overwrite)
    if files: dirmap.copy_file("files.ini", overwrite=overwrite)
            
    return datadir.get_path()


def init_config_parser(args):
    
    '''Command line parser for init_config.
    
    Example:
    
        To get help::
        
            $ dtocean-core-config -h
            
    '''
       

    now = datetime.datetime.now()
    epiStr = 'The DTOcean Developers (c) {}.'.format(now.year)
              
    desStr = ("Copy user modifiable configuration files to "
              "<UserName>\AppData\Roaming\DTOcean\dtocean-core\config")

    parser = argparse.ArgumentParser(description=desStr,
                                     epilog=epiStr,
                                     formatter_class=SmartFormatter)
    
    parser.add_argument("action",
                        choices=['logging', 'database', 'files'],
                        help="R|Select an action, where\n"
                             " logging = copy logging configuration\n"
                             " database = copy database configuration\n"
                             " files = copy file location configuration")

    parser.add_argument("--overwrite",
                        help=("overwrite any existing configuration files"),
                        action="store_true")
    
    args = parser.parse_args(args)
                        
    action = args.action
    overwrite = args.overwrite
    
    return action, overwrite


def init_config_interface():
    
    '''Command line interface for init_config.'''
    
    action, overwrite = init_config_parser(sys.argv[1:])
    
    kwargs = {"logging": False,
              "database": False,
              "files": False,
              "overwrite": overwrite}
    
    kwargs[action] = True
    
    dir_path = init_config(**kwargs)
    
    if dir_path is not None:
        print "Copying configuration files to {}".format(dir_path)

    return
