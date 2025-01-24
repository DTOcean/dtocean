from urllib.error import URLError
from urllib.request import urlopen

import pytest

from polite_config.files import (
    _download_archive,
    _resolve_src,
    extract_tar,
    extract_zip,
)


def is_online():
    try:
        urlopen("https://www.github.com")
        return True
    except URLError:
        return False


pytest.mark.skipif(not is_online(), reason="running offline")

NEMOH_URL_BASE = (
    "https://github.com/DTOcean/NEMOH/releases/download/v2024.12.2/"
    "nemoh-{}-v2024.12.2"
)


def test_download_archive(tmp_path):
    archive_url = NEMOH_URL_BASE.format("win64") + ".zip"
    archive_path = tmp_path / "test.zip"
    _download_archive(archive_url, archive_path)

    assert archive_path.is_file()


def test_resolve_src(mocker):
    _download_archive = mocker.patch("polite_config.files._download_archive")

    archive_url = NEMOH_URL_BASE.format("win64") + ".zip"
    with _resolve_src(archive_url) as archive_path:
        assert archive_path != archive_url

    assert _download_archive.call_count == 1


def test_extract_tar(mocker, tmp_path):
    archive_url = NEMOH_URL_BASE.format("linux") + ".tar.gz"
    extract_tar(archive_url, tmp_path)

    file_names = [p.name for p in tmp_path.iterdir() if p.is_file()]
    dir_names = [p.name for p in tmp_path.iterdir() if p.is_dir()]

    assert len(file_names) == 0
    assert len(dir_names) == 1
    assert dir_names[0] == "bin"


def test_extract_zip(mocker, tmp_path):
    archive_url = NEMOH_URL_BASE.format("win64") + ".zip"
    extract_zip(archive_url, tmp_path)

    file_names = [p.name for p in tmp_path.iterdir() if p.is_file()]
    dir_names = [p.name for p in tmp_path.iterdir() if p.is_dir()]

    assert len(file_names) == 0
    assert len(dir_names) == 1
    assert dir_names[0] == "x64"
