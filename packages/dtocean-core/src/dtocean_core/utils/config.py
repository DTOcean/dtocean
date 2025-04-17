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

"""
.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import logging

from polite_config.paths import DirectoryMap, ModPath, UserDataPath

# Set up logging
module_logger = logging.getLogger(__name__)


def init_config(logging=False, database=False, overwrite=False):
    """Copy config files to user data directory"""

    if not any([logging, database]):
        return

    objdir = ModPath(__name__, "..", "config")
    datadir = UserDataPath("dtocean_core", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)

    if logging:
        dirmap.copy_file("logging.yaml", overwrite=overwrite)
    if database:
        dirmap.copy_file("database.yaml", overwrite=overwrite)

    return datadir
