# -*- coding: utf-8 -*-
"""This module provides the command line interfaces for the
dtocean-package-template module.

It relies on the argparse module, which
only became part of the standard library as of python 2.7. For versions older
than 2.7, argparse must be installed separately.

.. module:: command
   :platform: Windows
   :synopsis: Provides command line interface
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>

"""

# Import built-in modules
import argparse
import logging

# Import DTOcean modules
from polite.paths import ObjDirectory, UserDataDirectory, DirectoryMap
from polite.configuration import Logger, ReadINI

# Import local modules
from . import Spreadsheet, __version__

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

def start_logging(level=None):

    """Start python logger"""

    objdir = ObjDirectory(__name__, "config")
    datadir = UserDataDirectory("dtocean_dummy", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)

    log = Logger(dirmap)
    log("dtocean_dummy",
        level=level,
        info_message="Begin logging for dtocean dummy module")
        
    return log
    
def get_config(config_name="configuration.ini",
               valid_name="validation.ini"):
    
    """Pick the necessary paths to configure the external files for the wave
    and tidal packages."""
    
    source_dir = ObjDirectory(__name__, "config")
    user_data = UserDataDirectory("dtocean_dummy", "DTOcean", "config")
    user_data_map = DirectoryMap(user_data, source_dir)

    user_ini_reader = ReadINI(user_data_map, config_name, valid_name)
    user_ini_reader.copy_config()
    
    # Collect the configuration data
    config = user_ini_reader.get_valid_config()
    
    return config

def module_interface():
    '''Command line interface for the package.
    
    This function provides the command line interface for the example
    package.
    
    Example:
    
        This function should be available using a command line interface as
        dtocean-dummy. This is because this function is set as an "entry
        point" in the setup.py module for the package. To get the available
        options for the package, type the following in the command line::
        
            $ dtocean-dummy -h
            
    '''
    
    # Bring up the logger
    start_logging()
    
    epiStr = ('''Mathew Topper, Tecnalia (c) 2014.''')
              
    desStr = "Make a spreadsheet using Python Pandas"

    parser = argparse.ArgumentParser(description=desStr,
                                     epilog=epiStr)
    
    parser.add_argument("rows",
                        help=("number of random numbers in the spreadsheet"),
                        type=int)
                        
    parser.add_argument("-f", "--format",
                        help=("format of the output file (csv or xls)"),
                        type=str,
                        default='csv')
                        
    parser.add_argument("-o", "--out",
                        help=("path to the output file"),
                        type=str,
                        default=None)
                        
    parser.add_argument("-v", "--version",
                        help=("show program's version number and exit"),
                        action='version',
                        version='{}: {}'.format(__package__, __version__))
                                     
    args = parser.parse_args()
    
    rows        = args.rows
    out_fmt     = args.format
    out_path    = args.out 
        
    # Collect the configuration data
    config = get_config()
        
    # Initiate and call the spreadsheet class
    sheet = Spreadsheet(**config['Spreadsheet'])
    sheet(rows, out_path, out_fmt)

    return

