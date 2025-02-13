import shutil
from pathlib import Path

import configobj
import pytest
from configobj.validate import ValidateError

from polite_config.configuration import ReadINI
from polite_config.paths import DirectoryMap, ModPath


@pytest.fixture(scope="module")
def src_dir():
    objdir = ModPath(__name__, "..", "examples", "config")
    return objdir


@pytest.fixture()
def target_dir(tmp_path):
    return tmp_path / "config"


@pytest.fixture
def readini(request):
    return request.getfixturevalue(request.param)


@pytest.fixture()
def plain_readini(target_dir: Path):
    return ReadINI(target_dir, "configuration.ini")


@pytest.fixture()
def map_readini(src_dir: Path, target_dir: Path):
    dirmap = DirectoryMap(target_dir, src_dir)
    return ReadINI(dirmap, "configuration.ini")


@pytest.mark.parametrize(
    "readini",
    ["plain_readini", "map_readini"],
    indirect=True,
)
def test_config_not_exists(readini: ReadINI, target_dir: Path):
    assert not (target_dir / readini.config_file_name).is_file()


@pytest.fixture
def plain_readini_copied(
    plain_readini: ReadINI,
    src_dir: Path,
    target_dir: Path,
):
    target_dir.mkdir()
    shutil.copy(src_dir / "configuration.ini", target_dir)
    return plain_readini


@pytest.fixture
def map_readini_copied(map_readini: ReadINI, target_dir: Path):
    target_dir.mkdir()
    map_readini.copy_config()
    return map_readini


def test_plain_logger_copy_config_error(plain_readini: ReadINI):
    with pytest.raises(ValueError):
        plain_readini.copy_config()


def test_map_logger_copy_config(map_readini_copied: ReadINI, target_dir: Path):
    files = list(target_dir.iterdir())
    assert len(files) == 1
    assert Path(files[0]).name == "configuration.ini"


@pytest.mark.parametrize(
    "readini",
    ["plain_readini_copied", "map_readini_copied"],
    indirect=True,
)
def test_config_exists(readini: ReadINI):
    assert readini.config_exists()


@pytest.mark.parametrize(
    "readini",
    ["plain_readini_copied", "map_readini_copied"],
    indirect=True,
)
def test_get_config(readini: ReadINI):
    config = readini.get_config()

    assert isinstance(config, configobj.ConfigObj)
    assert set(config.keys()) == set(["Spreadsheet"])

    spreadsheet = config["Spreadsheet"]
    assert isinstance(spreadsheet, dict)
    assert set(spreadsheet.keys()) == set(["high", "low"])


@pytest.fixture()
def plain_readini_valid(src_dir: Path, target_dir: Path):
    target_dir.mkdir()
    shutil.copy(src_dir / "configuration.ini", target_dir)
    shutil.copy(src_dir / "validation.ini", target_dir)

    return ReadINI(
        target_dir,
        "configuration.ini",
        validation_file_name="validation.ini",
    )


@pytest.fixture()
def map_readini_valid(src_dir: Path, target_dir: Path):
    dirmap = DirectoryMap(target_dir, src_dir)
    readini = ReadINI(
        dirmap,
        "configuration.ini",
        validation_file_name="validation.ini",
    )
    readini.copy_config()

    return readini


@pytest.mark.parametrize(
    "readini",
    ["plain_readini_valid", "map_readini_valid"],
    indirect=True,
)
def test_get_valid_config(readini: ReadINI):
    config = readini.get_valid_config()

    assert isinstance(config, configobj.ConfigObj)
    assert set(config.keys()) == set(["Spreadsheet"])

    spreadsheet = config["Spreadsheet"]
    assert isinstance(spreadsheet, dict)
    assert set(spreadsheet.keys()) == set(["high", "low"])


@pytest.fixture()
def plain_readini_invalid(src_dir: Path, target_dir: Path):
    target_dir.mkdir()
    shutil.copy(src_dir / "bad_configuration.ini", target_dir)
    shutil.copy(src_dir / "validation.ini", target_dir)

    return ReadINI(
        target_dir,
        "bad_configuration.ini",
        validation_file_name="validation.ini",
    )


@pytest.fixture()
def map_readini_invalid(src_dir: Path, target_dir: Path):
    dirmap = DirectoryMap(target_dir, src_dir)
    readini = ReadINI(
        dirmap,
        "bad_configuration.ini",
        validation_file_name="validation.ini",
    )
    readini.copy_config()

    return readini


@pytest.mark.parametrize(
    "readini",
    ["plain_readini_invalid", "map_readini_invalid"],
    indirect=True,
)
def test_not_valid_config(readini: ReadINI):
    with pytest.raises(ValidateError):
        readini.get_valid_config()
