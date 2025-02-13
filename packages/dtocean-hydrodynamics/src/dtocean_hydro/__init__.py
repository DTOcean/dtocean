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
from logging import NullHandler

from polite_config.configuration import Logger
from polite_config.paths import DirectoryMap, ModPath, UserDataPath

logging.getLogger(__name__).addHandler(NullHandler())


def start_logging(level=None):
    """Start python logger"""

    objdir = ModPath(__name__, "config")
    datadir = UserDataPath("dtocean_hydro", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)

    log = Logger(dirmap)
    log(
        "dtocean_hydro",
        log_level=level,
        info_message="Begin logging for dtocean_hydro.",
    )
