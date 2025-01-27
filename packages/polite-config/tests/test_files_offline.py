import tarfile
import zipfile
from pathlib import Path

import pytest

from polite_config.files import _resolve_src, extract_tar, extract_zip

PARENT_DIR = Path(__file__).parent


def _make_tar(tar_path: Path):
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(PARENT_DIR, arcname=PARENT_DIR.name)


def _make_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in PARENT_DIR.walk():
            for file in files:
                zipf.write(
                    root.joinpath(file),
                    root.joinpath(file).relative_to(PARENT_DIR.parent),
                )


@pytest.fixture
def tmp_tar(tmp_path):
    tar_path = tmp_path / "temp.tar.gz"
    _make_tar(tar_path)
    return tar_path


@pytest.fixture
def tmp_zip(tmp_path):
    zip_path = tmp_path / "temp.zip"
    _make_zip(zip_path)
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


def test_extract_tar_online_fake(mocker, tmp_path):
    def _download_archive(archive_url: str, archive_path: Path):
        _make_tar(archive_path)

    mocker.patch("polite_config.files._download_archive", _download_archive)

    mock_url = "https://example.com/mock.tar.gz"
    dst = tmp_path / "mock"
    extract_tar(mock_url, dst)

    test = [x.name for x in (dst / "tests").iterdir() if x.is_file()]
    expected = [x.name for x in PARENT_DIR.iterdir() if x.is_file()]

    assert test == expected


def test_extract_tar_src_error(tmp_path):
    src_path = tmp_path / "mock.tar"
    dst = tmp_path / "mock"

    with pytest.raises(ValueError) as excinfo:
        extract_tar(src_path, dst)

    assert "neither a file or a URL" in str(excinfo.value)
    assert not dst.is_dir()


def test_extract_zip(tmp_path, tmp_zip):
    dst = tmp_path / "mock"
    extract_zip(tmp_zip, dst)

    test = [x.name for x in (dst / "tests").iterdir() if x.is_file()]
    expected = [x.name for x in PARENT_DIR.iterdir() if x.is_file()]

    assert test == expected


def test_extract_zip_online_fake(mocker, tmp_path):
    def _download_archive(archive_url: str, archive_path: Path):
        _make_zip(archive_path)

    mocker.patch("polite_config.files._download_archive", _download_archive)

    mock_url = "https://example.com/mock.zip"
    dst = tmp_path / "mock"
    extract_zip(mock_url, dst)

    test = [x.name for x in (dst / "tests").iterdir() if x.is_file()]
    expected = [x.name for x in PARENT_DIR.iterdir() if x.is_file()]

    assert test == expected


def test_extract_zip_src_error(tmp_path):
    src_path = tmp_path / "mock.zip"
    dst = tmp_path / "mock"

    with pytest.raises(ValueError) as excinfo:
        extract_zip(src_path, dst)

    assert "neither a file or a URL" in str(excinfo.value)
    assert not dst.is_dir()
