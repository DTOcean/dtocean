import shutil
import subprocess
from pathlib import Path

import pytest

FILE = Path(__file__).resolve()


@pytest.fixture(scope="session")
def inputs_wp2_tidal():
    yield _make_test_data("inputs_wp2_tidal")
    _remove_test_data("inputs_wp2_tidal")


@pytest.fixture(scope="session")
def inputs_economics():
    yield _make_test_data("inputs_economics")
    _remove_test_data("inputs_economics")


def _make_test_data(name: str):
    # Pickle data files and move to test directory
    data_dir = FILE.parents[1] / "test_data"
    test_dir = FILE.parent

    src_path_py = (data_dir / name).with_suffix(".py")
    subprocess.run(["python", src_path_py], capture_output=True)

    src_path_pkl = (data_dir / name).with_suffix(".pkl")
    dst_path_pkl = (test_dir / name).with_suffix(".pkl")
    shutil.move(src_path_pkl, dst_path_pkl)

    return dst_path_pkl


def _remove_test_data(name: str):
    test_dir = FILE.parent
    (test_dir / name).with_suffix(".pkl").unlink()
