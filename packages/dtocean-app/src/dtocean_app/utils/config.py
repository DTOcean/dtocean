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

from importlib.metadata import distribution

from polite_config.configuration import ReadINI
from polite_config.paths import (
    DirectoryMap,
    ModPath,
    SiteDataPath,
    UserDataPath,
)


def get_install_paths():
    """Pick the necessary paths to configure the external files for the
    manuals."""

    install_config_name = "install.ini"

    user_data = UserDataPath("dtocean_doc", "DTOcean", "config")
    user_ini_reader = ReadINI(user_data, install_config_name)

    # Get the root path from the site data path.
    site_data = SiteDataPath("DTOcean Manuals", "DTOcean")
    site_ini_reader = ReadINI(site_data, install_config_name)

    if user_ini_reader.config_exists():
        config = user_ini_reader.get_config()
    elif site_ini_reader.config_exists():
        config = site_ini_reader.get_config()
    else:
        return None

    man = config["man"]
    assert isinstance(man, dict)

    path_dict: dict[str, str] = {
        "man_user_path": man["user_path"],
        "man_technical_path": man["technical_path"],
    }

    return path_dict


def get_software_version():
    package = "dtocean-app"
    dist = distribution(package)
    version = dist.version
    return "{} {}".format(package, version)


def init_config(logging=False, overwrite=False):
    """Copy config files to user data directory"""

    if not any([logging]):
        return

    objdir = ModPath(__name__, "..", "config")
    datadir = UserDataPath("dtocean_app", "DTOcean", "config")
    dirmap = DirectoryMap(datadir, objdir)

    if logging:
        dirmap.copy_file("logging.yaml", overwrite=overwrite)

    return datadir
