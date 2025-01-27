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
_VERSION_NEMOH = "v2024.12.2"
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
        if any(dst.iterdir()):
            if not force:
                raise RuntimeError(
                    f"Directory {dst} is not empty. Consider setting 'force' "
                    "argument to True"
                )

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

    # Look in the etc directory
    etc_data = EtcPath("dtocean-data")
    etc_ini_reader = ReadINI(etc_data, "install.ini")

    # Get the root path from the possible site data paths
    site_data = SiteDataPath("DTOcean Data", "DTOcean")
    site_ini_reader = ReadINI(site_data, "install.ini")

    if etc_ini_reader.config_exists():
        config = etc_ini_reader.get_config()
    elif site_ini_reader.config_exists():
        config = site_ini_reader.get_config()
    else:
        errStr = (
            "No suitable configuration file found at paths {} or {}"
        ).format(
            etc_ini_reader.get_config_path(), site_ini_reader.get_config_path()
        )
        raise RuntimeError(errStr)

    prefix = config["global"]["prefix"]
    bin_path = os.path.join(prefix, config["global"]["bin_path"])
    wec_share_path = os.path.join(prefix, config["dtocean_wec"]["share_path"])
    tidal_share_path = os.path.join(
        prefix, config["dtocean_tidal"]["share_path"]
    )

    return {
        "bin_path": bin_path,
        "wec_share_path": wec_share_path,
        "tidal_share_path": tidal_share_path,
    }
