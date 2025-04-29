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

import sys
import argparse
import datetime

import importlib_metadata as metadata

from polite.configuration import ReadINI
from polite.paths import (DirectoryMap,
                          ObjDirectory,
                          SiteDataDirectory,
                          UserDataDirectory)

from . import SmartFormatter


def get_install_paths():
    
    """Pick the necessary paths to configure the external files for the 
    manuals."""
    
    install_config_name = "install.ini"
    
    user_data = UserDataDirectory("dtocean_doc", "DTOcean", "config")
    user_ini_reader = ReadINI(user_data, install_config_name)
    
    # Get the root path from the site data path.
    site_data = SiteDataDirectory("DTOcean Manuals", "DTOcean")
    site_ini_reader = ReadINI(site_data, install_config_name)
    
    if user_ini_reader.config_exists():
        config = user_ini_reader.get_config()
    elif site_ini_reader.config_exists():
        config = site_ini_reader.get_config()
    else:
        return None
                 
    path_dict = {"man_user_path": config["man"]["user_path"],
                 "man_technical_path": config["man"]["technical_path"]}
    
    return path_dict


def get_software_version():
    
    if 'dtocean' in get_distribution_names():
        package = 'dtocean'
    else:
        package = 'dtocean-app'
    
    version = metadata.version(package)
    
    if package == 'dtocean':
        values = [int(x) for x in version.split(".")]
        version = "{}.{:02d}".format(*values)
    
    return"{} {}".format(package, version)


def get_distribution_names():
    return [x.metadata['Name'] for x in metadata.distributions()]


def init_config(logging=False, files=False, install=False, overwrite=False):
    
    """Copy config files to user data directory"""
    
    if not any([logging, files, install]): return
    
    objdir = ObjDirectory(__name__, "..", "config")
    datadir = UserDataDirectory("dtocean_app", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)
    
    if logging: dirmap.copy_file("logging.yaml", overwrite=overwrite)
    if files: dirmap.copy_file("files.ini", overwrite=overwrite)
    if install: dirmap.copy_file("install.ini", overwrite=overwrite)
    
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
              "<UserName>\AppData\Roaming\DTOcean\dtocean-app\config")

    parser = argparse.ArgumentParser(description=desStr,
                                     epilog=epiStr,
                                     formatter_class=SmartFormatter)
    
    parser.add_argument("action",
                        choices=['logging', 'files', 'install'],
                        help="R|Select an action, where\n"
                             " logging = copy logging configuration\n"
                             " files = copy file location configuration\n"
                             " install = copy manuals installation path "
                                         "configuration")

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
              "files": False,
              "install": False,
              "overwrite": overwrite}
    
    kwargs[action] = True
    
    dir_path = init_config(**kwargs)
    
    if dir_path is not None:
        print "Copying configuration files to {}".format(dir_path)

    return
