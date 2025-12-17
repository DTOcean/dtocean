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

from importlib.metadata import PackageNotFoundError, distribution

from polite_config.paths import (
    DirectoryMap,
    ModPath,
    UserDataPath,
)


def get_docs_index():
    try:
        from dtocean_docs import (  # pyright: ignore[reportMissingImports]
            get_index,
        )
    except ImportError:
        return None

    return get_index()


def get_package_versions(*names: str) -> dict[str, str]:
    result = {}

    for name in names:
        try:
            dist = distribution(name)
            result[name] = dist.version
        except PackageNotFoundError:
            pass

    return result


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
