# -*- coding: utf-8 -*-
"""This module provides the command line interfaces for the
dtocean-package-template module.

It relies on the argparse module, which
only became part of the standard library as of python 2.7. For versions older
than 2.7, argparse must be installed separately.

.. module:: command
     :synopsis: Provides command line interface

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>

"""

# Import built-in modules
import argparse
import importlib.metadata
import logging
from logging import NullHandler
from pathlib import Path
from typing import cast

# Import DTOcean modules
from polite_config.configuration import Logger, ReadINI
from polite_config.paths import DirectoryMap, ModPath, UserDataPath

# Import local modules
from . import Spreadsheet

logging.getLogger(__name__).addHandler(NullHandler())


def start_logging(level=None):
    """Start python logger"""

    objdir = ModPath(__name__, "config")
    userdir = UserDataPath("dtocean_dummy", "DTOcean", "config")
    dirmap = DirectoryMap(userdir, objdir)
    
    appdir_path = userdir.parent
    logdir = Path(appdir_path, "logs")
    logdir.mkdir(exist_ok=True)

    log = Logger(dirmap)
    log(
        "dtocean_dummy",
        log_level=level,
        info_message="Begin logging for dtocean dummy module",
        file_prefix=logdir,
    )

    return log


def get_config(config_name="configuration.ini", valid_name="validation.ini"):
    """Pick the necessary paths to configure the external files for the wave
    and tidal packages."""

    source_dir = ModPath(__name__, "config")
    user_data = UserDataPath("dtocean_dummy", "DTOcean", "config")
    user_data_map = DirectoryMap(user_data, source_dir)

    user_ini_reader = ReadINI(user_data_map, config_name, valid_name)
    user_ini_reader.copy_config()

    # Collect the configuration data
    config = user_ini_reader.get_valid_config()

    return config


def module_interface():
    """Command line interface for the package.

    This function provides the command line interface for the example
    package.

    Example:

        This function should be available using a command line interface as
        dtocean-dummy. This is because this function is set as an "entry
        point" in the setup.py module for the package. To get the available
        options for the package, type the following in the command line::

            $ dtocean-dummy -h

    """

    # Bring up the logger
    start_logging()

    epiStr = """Mathew Topper, Tecnalia (c) 2014."""

    desStr = "Make a spreadsheet using Python Pandas"

    parser = argparse.ArgumentParser(description=desStr, epilog=epiStr)

    parser.add_argument(
        "rows",
        help=("number of random numbers in the spreadsheet"),
        type=int,
    )

    parser.add_argument(
        "-f",
        "--format",
        help=("format of the output file (csv or xls)"),
        type=str,
        default="csv",
    )

    parser.add_argument(
        "-o",
        "--out",
        help=("path to the output file"),
        type=str,
        default=None,
    )

    version = importlib.metadata.version("ProjectName")

    parser.add_argument(
        "-v",
        "--version",
        help=("show program's version number and exit"),
        action="version",
        version="{}: {}".format(__package__, version),
    )

    args = parser.parse_args()

    rows = args.rows
    out_fmt = args.format
    out_path = args.out

    # Collect the configuration data
    config = get_config()
    spreadsheet = cast(dict, config["Spreadsheet"])

    # Initiate and call the spreadsheet class
    sheet = Spreadsheet(**spreadsheet)
    sheet(rows, out_path, out_fmt)

    return
