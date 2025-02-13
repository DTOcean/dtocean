import shutil
from pathlib import Path

import pytest

from polite_config.configuration import Config
from polite_config.paths import DirectoryMap, ModPath


@pytest.fixture(scope="module")
def src_dir():
    objdir = ModPath(__name__, "..", "examples", "config")
    return objdir


@pytest.fixture()
def target_dir(tmp_path):
    return tmp_path / "config"


@pytest.fixture
def config(request):
    return request.getfixturevalue(request.param)


@pytest.fixture()
def plain_config(target_dir: Path):
    return Config(target_dir, "configuration.ini")


@pytest.fixture()
def map_config(src_dir: Path, target_dir: Path):
    dirmap = DirectoryMap(target_dir, src_dir)
    return Config(dirmap, "configuration.ini")


@pytest.mark.parametrize(
    "config",
    ["plain_config", "map_config"],
    indirect=True,
)
def test_config_not_exists(config: Config, target_dir: Path):
    assert not (target_dir / config.config_file_name).is_file()


@pytest.fixture
def plain_config_copied(
    plain_config: Config,
    src_dir: Path,
    target_dir: Path,
):
    target_dir.mkdir()
    shutil.copy(src_dir / "configuration.ini", target_dir)
    return plain_config


@pytest.fixture
def map_config_copied(map_config: Config, target_dir: Path):
    target_dir.mkdir()
    map_config.copy_config()
    return map_config


def test_plain_logger_copy_config_error(plain_config: Config):
    with pytest.raises(ValueError):
        plain_config.copy_config()


def test_map_logger_copy_config(map_config_copied: Config, target_dir: Path):
    files = list(target_dir.iterdir())
    assert len(files) == 1
    assert Path(files[0]).name == "configuration.ini"


@pytest.mark.parametrize(
    "config",
    ["plain_config_copied", "map_config_copied"],
    indirect=True,
)
def test_config_exists(config: Config):
    assert config.config_exists()


def test_make_head_foot_bar():
    head_foot_length = 50
    head_title = "This is a TEST!"

    header, footer = Config.make_head_foot_bar(head_title, head_foot_length)

    assert len(header) == head_foot_length
    assert len(footer) == head_foot_length
