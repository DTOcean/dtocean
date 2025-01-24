import tarfile
import zipfile
from pathlib import Path

import pytest

from polite_config.files import _resolve_src, extract_tar, extract_zip

PARENT_DIR = Path(__file__).parent


@pytest.fixture
def tmp_tar(tmp_path):
    tar_path = tmp_path / "temp.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(PARENT_DIR, arcname=PARENT_DIR.name)
    return tar_path


@pytest.fixture
def tmp_zip(tmp_path):
    zip_path = tmp_path / "temp.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in PARENT_DIR.walk():
            for file in files:
                zipf.write(
                    root.joinpath(file),
                    root.joinpath(file).relative_to(PARENT_DIR.parent),
                )
    return zip_path


def test_resolve_src(mocker, tmp_path):
    _download_archive = mocker.patch("polite_config.files._download_archive")
    p = tmp_path / "hello.zip"
    p.write_text("mock")

    with _resolve_src(p) as test:
        assert p == test

    assert _download_archive.call_count == 0


def test_resolve_src_error(tmp_path):
    p = tmp_path / "mock"

    with pytest.raises(ValueError) as excinfo:
        with _resolve_src(p):
            pass

    assert "neither a file or a URL" in str(excinfo.value)


def test_extract_tar(tmp_path, tmp_tar):
    dst = tmp_path / "mock"
    extract_tar(tmp_tar, dst)

    test = [x.name for x in (dst / "tests").iterdir() if x.is_file()]
    expected = [x.name for x in PARENT_DIR.iterdir() if x.is_file()]

    assert test == expected


def test_extract_zip(tmp_path, tmp_zip):
    dst = tmp_path / "mock"
    extract_zip(tmp_zip, dst)

    test = [x.name for x in (dst / "tests").iterdir() if x.is_file()]
    expected = [x.name for x in PARENT_DIR.iterdir() if x.is_file()]

    assert test == expected
