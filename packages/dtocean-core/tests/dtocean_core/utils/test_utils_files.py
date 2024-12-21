import os
import shutil
import sys
import zipfile
from stat import S_IREAD, S_IRGRP, S_IROTH

import pytest

from dtocean_core.utils.files import (
    init_dir,
    onerror,
    os_retry,
    remove_retry,
    rmtree_retry,
    unpack_archive,
)


def test_unpack_archive_zip(tmpdir):
    src_path = os.path.join(str(tmpdir), "zipfile_write.zip")
    dst_path = os.path.join(str(tmpdir), "test")

    readme = tmpdir.join("README.txt")
    readme.write("test")

    zf = zipfile.ZipFile(src_path, mode="w")

    try:
        zf.write(str(readme))
    finally:
        zf.close()

    unpack_archive(src_path, dst_path)

    assert len(os.listdir(dst_path)) == 1


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_onerror(tmpdir):
    config_tmpdir = tmpdir.mkdir("config")
    test_file = config_tmpdir.join("locked.file")
    test_file.write("a")

    os.chmod(str(test_file), S_IREAD | S_IRGRP | S_IROTH)

    assert len(os.listdir(str(tmpdir))) == 1

    with pytest.raises(Exception):
        shutil.rmtree(str(config_tmpdir))

    assert len(os.listdir(str(tmpdir))) == 1

    shutil.rmtree(str(config_tmpdir), onerror=onerror)

    assert len(os.listdir(str(tmpdir))) == 0


def test_os_retry_max_attempts():
    def always_fail(src_path):  # pylint: disable=unused-argument
        raise OSError

    test = os_retry(always_fail)

    with pytest.raises(OSError) as excinfo:
        test("mock", max_attempts=2)

    assert "failed for over 2 seconds" in str(excinfo.value)


def test_os_retry_max_attempts_silent():
    def always_fail(src_path):  # pylint: disable=unused-argument
        raise OSError

    test = os_retry(always_fail)
    test("mock", max_attempts=2, fail_silent=True)


def test_rmtree_retry(tmpdir):
    sub1 = tmpdir.mkdir("one")
    sub2 = sub1.mkdir("two")
    sub2.mkdir("three")

    rmtree_retry(str(sub1))

    assert len(os.listdir(str(tmpdir))) == 0


def test_remove_retry(tmpdir):
    readme = tmpdir.join("README.txt")
    readme.write("test")

    remove_retry(str(readme))

    assert len(os.listdir(str(tmpdir))) == 0


def test_init_dir(tmpdir):
    test_dir = os.path.join(str(tmpdir), "test")
    init_dir(test_dir)

    assert len(os.listdir(str(tmpdir))) == 1


def test_init_dir_existing(tmpdir):
    test_dir = os.path.join(str(tmpdir), "test")
    init_dir(test_dir)

    with pytest.raises(IOError) as excinfo:
        init_dir(test_dir)

    assert "Set clean_existing argument to True" in str(excinfo.value)


def test_init_dir_clean(tmpdir):
    sub_dir = tmpdir.mkdir("test")
    sub_dir.mkdir("another_dir")
    p = sub_dir.join("hello.txt")
    p.write("content")

    init_dir(str(sub_dir), clean_existing=True)

    assert len(os.listdir(str(tmpdir))) == 1
    assert not os.listdir(str(sub_dir))
    assert len(os.listdir(str(tmpdir))) == 1
    assert not os.listdir(str(sub_dir))
