import tarfile
import tempfile
from importlib.metadata import version
from pathlib import Path
from platform import system
from typing import Sequence
from urllib.request import urlopen
from zipfile import ZipFile

from polite_config.paths import UserDataPath

_ARCH = system().lower() if system().lower() != "windows" else "win64"
_DATA_URL_BASE = (
    "https://github.com/DTOcean/dtocean-data-next/releases/"
    "download/v2025.01.0/dtocean-data-v2025.01.0"
)
_NEMOH_URL_BASE = (
    "https://github.com/DTOcean/NEMOH/releases/download/v2024.12.2/"
    "nemoh-{}-v2024.12.2".format(_ARCH)
)
_VERSION = version("dtocean-data")
_USER_DIR = UserDataPath("dtocean_data", "DTOcean", _VERSION)


def install(options: Sequence[str]):
    def get_option(option: str):
        match option:
            case "data":
                return _DATA_URL_BASE
            case "nemoh":
                return _NEMOH_URL_BASE
            case _:
                raise ValueError("Unrecognised option")

    arch = system().lower()

    for option in options:
        url_base = get_option(option)

        match arch:
            case "linux":
                _extract_linux(url_base)
            case "windows":
                _extract_windows(url_base)
            case _:
                raise NotImplementedError("Unsupported architecture")


def _extract_linux(url_base: str):
    tg_url = url_base + ".tar.gz"

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_dir_path = Path(tmpdirname)
        tmp_tg_path = tmp_dir_path / "tempfile.tar.gz"
        _download_archive(tg_url, tmp_tg_path)

        _USER_DIR.mkdir(exist_ok=True)
        tar = tarfile.open(tmp_tg_path)
        tar.extractall(path=_USER_DIR, filter="tar")
        tar.close()


def _extract_windows(url_base: str):
    zip_url = url_base + ".zip"

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_dir_path = Path(tmpdirname)
        tmp_zip_path = tmp_dir_path / "tempfile.zip"
        _download_archive(zip_url, tmp_zip_path)

        _USER_DIR.mkdir(exist_ok=True)
        zf = ZipFile(tmp_zip_path)
        zf.extractall(path=_USER_DIR)
        zf.close()


def _download_archive(archive_url: str, archive_path: Path):
    archive_req = urlopen(archive_url)

    with open(archive_path, "wb") as archive:
        archive.write(archive_req.read())
