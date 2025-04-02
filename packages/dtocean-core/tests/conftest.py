import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FILE = Path(__file__).resolve()


def pytest_addoption(parser):
    parser.addoption(
        "--postgresql-path",
        dest="postgresql_path",
        help="path to postgresql database setup files",
    )


@pytest.fixture(scope="session")
def test_data_path():
    return FILE.parents[1] / "test_data"


@pytest.fixture(scope="session")
def inputs_boundary(test_data_path):
    yield _make_test_data(test_data_path, "inputs_boundary")
    _remove_test_data("inputs_boundary")


@pytest.fixture(scope="session")
def inputs_economics(test_data_path):
    yield _make_test_data(test_data_path, "inputs_economics")
    _remove_test_data("inputs_economics")


@pytest.fixture(scope="session")
def inputs_wp2_tidal(test_data_path):
    yield _make_test_data(test_data_path, "inputs_wp2_tidal")
    _remove_test_data("inputs_wp2_tidal")


@pytest.fixture(scope="session")
def inputs_wp2_wave(test_data_path):
    yield _make_test_data(test_data_path, "inputs_wp2_wave")
    _remove_test_data("inputs_wp2_wave")


@pytest.fixture(scope="session")
def inputs_wp3(test_data_path):
    yield _make_test_data(test_data_path, "inputs_wp3")
    _remove_test_data("inputs_wp3")


def _make_test_data(data_dir: Path, name: str):
    # Pickle data files and move to test directory
    test_dir = FILE.parent

    src_path_py = (data_dir / name).with_suffix(".py")
    result = subprocess.run(
        [sys.executable, src_path_py],
        capture_output=True,
        text=True,
    )

    if result.returncode:
        raise ChildProcessError(result.stderr)

    src_path_pkl = (data_dir / name).with_suffix(".pkl")
    dst_path_pkl = (test_dir / name).with_suffix(".pkl")
    shutil.move(src_path_pkl, dst_path_pkl)

    return dst_path_pkl


def _remove_test_data(name: str):
    test_dir = FILE.parent
    (test_dir / name).with_suffix(".pkl").unlink()
