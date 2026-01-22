import pickle
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from dtocean_hydro.output import WP2output

FILE = Path(__file__).resolve()


@pytest.fixture(scope="session")
def test_data_path():
    return FILE.parents[2] / "test_data"


@pytest.fixture(scope="session")
def inputs_wp2_tidal(test_data_path):
    yield _make_test_data(test_data_path, "inputs_wp2_tidal")
    _remove_test_data("inputs_wp2_tidal")


@pytest.fixture(scope="session")
def inputs_wp2_wave(test_data_path):
    yield _make_test_data(test_data_path, "inputs_wp2_wave")
    _remove_test_data("inputs_wp2_wave")


@pytest.fixture(scope="session")
def outputs_wp2_wave(test_data_path):
    dst_path_pkl = _make_test_data(test_data_path, "outputs_wp2_wave")
    with open(dst_path_pkl, "rb") as dataf:
        # Pickle dictionary using protocol 0.
        test_data: dict[str, Any] = pickle.load(dataf)

    yield {
        "wp2_outputs": WP2output(**test_data["wp2_outputs"]),
        "occurrence_matrix": test_data["occurrence_matrix"],
    }

    _remove_test_data("outputs_wp2_wave")


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
