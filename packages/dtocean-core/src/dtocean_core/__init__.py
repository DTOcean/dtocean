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

"""The core component of the dtocean project.

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

from logging.handlers import RotatingFileHandler
from pathlib import Path

from polite_config.configuration import Logger
from polite_config.paths import ModPath, UserDataPath


def start_logging():
    """Start python logger"""

    # Pick up the configuration from the user directory if it exists
    userdir = UserDataPath("dtocean_core", "DTOcean", "config")

    appdir_path = userdir.parent
    logdir = Path(appdir_path, "logs")

    # Look for logging.yaml
    if (userdir / "logging.yaml").is_file():
        configdir = userdir
    else:
        configdir = ModPath("dtocean_core", "config")

    log = Logger(configdir)
    logger = log("dtocean_core", file_prefix=logdir)

    # Rotate any rotating file handlers
    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()

    logger.info("Begin logging for dtocean_core")
