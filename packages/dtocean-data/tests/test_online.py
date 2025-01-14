import os
from urllib.error import URLError
from urllib.request import urlopen

import pytest

import dtocean_data
from dtocean_data import (
    _ARCH,
    _DATA_URL_BASE,
    _NEMOH_URL_BASE,
    _download_archive,
    _extract_linux,
    _extract_windows,
)


def is_online():
    try:
        urlopen("https://www.github.com")
        return True
    except URLError:
        return False


pytestmark = pytest.mark.skipif(not is_online(), reason="running offline")


def test_download_archive(tmp_path):
    if _ARCH == "linux":
        archive_url = _NEMOH_URL_BASE + ".tar.gz"
    else:
        archive_url = _NEMOH_URL_BASE + ".zip"

    print(archive_url)
    archive_path = tmp_path / "test.zip"
    _download_archive(archive_url, archive_path)

    assert archive_path.is_file()


def test_extract_data(mocker, tmp_path):
    mocker.patch.object(dtocean_data, "_USER_DIR", tmp_path)

    if _ARCH == "linux":
        _extract_linux(_DATA_URL_BASE)
    else:
        _extract_windows(_DATA_URL_BASE)

    file_names = [p.name for p in tmp_path.iterdir() if p.is_file()]
    dir_names = [p.name for p in tmp_path.iterdir() if p.is_dir()]

    assert len(file_names) == 0
    assert len(dir_names) == 1
    assert dir_names[0] == "share"


def test_extract_nemoh(mocker, tmp_path):
    mocker.patch.object(dtocean_data, "_USER_DIR", tmp_path)

    if _ARCH == "linux":
        _extract_linux(_NEMOH_URL_BASE)
    else:
        _extract_windows(_NEMOH_URL_BASE)

    file_names = [p.name for p in tmp_path.iterdir() if p.is_file()]
    dir_names = [p.name for p in tmp_path.iterdir() if p.is_dir()]

    assert len(file_names) == 0
    assert len(dir_names) == 1

    if _ARCH == "linux":
        assert dir_names[0] == "bin"
        bin_path = tmp_path / "bin"

        flags = [
            os.access(str(p), os.X_OK)
            for p in bin_path.iterdir()
            if p.is_file()
        ]
        assert len(flags) == 4
        assert all(flags)

    else:
        assert dir_names[0] == "x64"
        x64_path = tmp_path / "x64"

        file_names = [p.name for p in x64_path.iterdir() if p.is_file()]
        dir_names = [p.name for p in x64_path.iterdir() if p.is_dir()]

        assert len(file_names) == 0
        assert len(dir_names) == 1
        assert dir_names[0] == "Release"

        release_path = x64_path / "Release"

        exts = [p.suffix for p in release_path.iterdir() if p.is_file()]
        assert len(exts) == 4
        assert len(set(exts)) == 1
        assert list(set(exts))[0] == ".exe"
