# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2024 Mathew Topper
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

"""The core component of the dtocean project.

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import logging
from logging import NullHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import cast

from polite_config.configuration import Logger, ReadINI
from polite_config.paths import ModPath, UserDataPath

logging.getLogger(__name__).addHandler(NullHandler())


def start_logging():
    """Start python logger"""

    # Pick up the configuration from the user directory if it exists
    userdir = UserDataPath("dtocean_core", "DTOcean", "config")

    # Look for files.ini
    if (userdir / "files.ini").is_file():
        configdir = userdir
    else:
        configdir = ModPath("dtocean_core", "config")

    files_ini = ReadINI(configdir, "files.ini")
    files_config = cast(dict, files_ini.get_config())

    appdir_path = userdir.parent
    log_folder = files_config["logs"]["path"]
    logdir = Path(appdir_path, log_folder)

    # Look for logging.yaml
    if (userdir / "logging.yaml").is_file():
        configdir = userdir
    else:
        configdir = ModPath("dtocean_core", "config")

    log = Logger(configdir)
    log_config_dict = log.read()

    # Update the file logger if present
    if "file" in log_config_dict["handlers"]:
        log_filename = log_config_dict["handlers"]["file"]["filename"]
        log_path = logdir / log_filename
        log_config_dict["handlers"]["file"]["filename"] = log_path
        logdir.mkdir()

    log.configure_logger(log_config_dict)
    logger = log.add_named_logger("dtocean_core")

    # Rotate any rotating file handlers
    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()

    logger.info("Begin logging for dtocean_core")

    return
