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
import shutil
from platform import system

from polite_config.files import extract_tar, extract_zip
from polite_config.paths import UserDataPath

module_logger = logging.getLogger(__name__)

_ARCH = system().lower() if system().lower() != "windows" else "win64"
_VERSION_DATA = "v2025.01.0"
_VERSION_NEMOH = "v2025.02.0"
_DIR_DATA = UserDataPath("dtocean_data", "DTOcean", _VERSION_DATA)
_DIR_NEMOH = UserDataPath("nemoh", "DTOcean", _VERSION_NEMOH)
_URL_BASE_DATA = (
    "https://github.com/DTOcean/dtocean-data-next/releases/"
    f"download/{_VERSION_DATA}/dtocean-data-{_VERSION_DATA}"
)
_URL_BASE_NEMOH = (
    f"https://github.com/DTOcean/NEMOH/releases/download/{_VERSION_NEMOH}/"
    f"nemoh-{_ARCH}-{_VERSION_NEMOH}"
)


def get_data(force: bool = False):
    arch = system().lower()

    for url_base, dst in zip(
        [_URL_BASE_DATA, _URL_BASE_NEMOH],
        [_DIR_DATA, _DIR_NEMOH],
    ):
        if dst.is_dir() and any(dst.iterdir()):
            if not force:
                module_logger.info(
                    f"Skipped creation of directory {dst}. Set 'force' "
                    "argument to True to overwrite"
                )
                continue

            shutil.rmtree(dst)

        match arch:
            case "linux":
                url = url_base + ".tar.gz"
                extract_tar(url, dst)
            case "windows":
                url = url_base + ".zip"
                extract_zip(url, dst)
            case _:
                raise NotImplementedError("Unsupported architecture")


def get_install_paths():
    """Pick the necessary paths to configure the external files for the wave
    and tidal packages."""

    tidal_share_path = _DIR_DATA / "share" / "dtocean_tidal"
    if not tidal_share_path.is_dir():
        raise RuntimeError(
            "Tidal shared data directory does not exist. Call dtocean-hydro "
            "init command."
        )

    wec_share_path = _DIR_DATA / "share" / "dtocean_wec"
    if not wec_share_path.is_dir():
        raise RuntimeError(
            "WEC shared data directory does not exist. Call dtocean-hydro "
            "init command."
        )

    arch = system().lower()

    match arch:
        case "linux":
            bin_path = _DIR_NEMOH / "bin"
        case "windows":
            bin_path = _DIR_NEMOH / "x64" / "Release"
        case _:
            raise NotImplementedError("Unsupported architecture")

    if not bin_path.is_dir():
        raise RuntimeError(
            "NEMOH executables directory does not exist. Has NEMOH been "
            "installed?"
        )

    return {
        "bin_path": bin_path,
        "tidal_share_path": tidal_share_path,
        "wec_share_path": wec_share_path,
    }
