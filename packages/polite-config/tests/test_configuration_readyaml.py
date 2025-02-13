import shutil
from pathlib import Path

import pytest

from polite_config.configuration import ReadYAML
from polite_config.paths import DirectoryMap, ModPath


@pytest.fixture(scope="module")
def src_dir():
    objdir = ModPath(__name__, "..", "examples", "config")
    return objdir


@pytest.fixture()
def target_dir(tmp_path):
    return tmp_path / "config"


@pytest.fixture
def readyaml(request):
    return request.getfixturevalue(request.param)


@pytest.fixture()
def plain_readyaml(target_dir: Path):
    return ReadYAML(target_dir, "logging.yaml")


@pytest.fixture()
def map_readyaml(src_dir: Path, target_dir: Path):
    dirmap = DirectoryMap(target_dir, src_dir)
    return ReadYAML(dirmap, "logging.yaml")


@pytest.mark.parametrize(
    "readyaml",
    ["plain_readyaml", "map_readyaml"],
    indirect=True,
)
def test_config_not_exists(readyaml: ReadYAML, target_dir: Path):
    assert not (target_dir / readyaml.config_file_name).is_file()


@pytest.fixture
def plain_readyaml_copied(
    plain_readyaml: ReadYAML,
    src_dir: Path,
    target_dir: Path,
):
    target_dir.mkdir()
    shutil.copy(src_dir / "logging.yaml", target_dir)
    return plain_readyaml


@pytest.fixture
def map_readyaml_copied(map_readyaml: ReadYAML, target_dir: Path):
    target_dir.mkdir()
    map_readyaml.copy_config()
    return map_readyaml


def test_plain_logger_copy_config_error(plain_readyaml: ReadYAML):
    with pytest.raises(ValueError):
        plain_readyaml.copy_config()


def test_map_logger_copy_config(
    map_readyaml_copied: ReadYAML, target_dir: Path
):
    files = list(target_dir.iterdir())
    assert len(files) == 1
    assert Path(files[0]).name == "logging.yaml"


@pytest.mark.parametrize(
    "readyaml",
    ["plain_readyaml_copied", "map_readyaml_copied"],
    indirect=True,
)
def test_config_exists(readyaml: ReadYAML):
    assert readyaml.config_exists()


@pytest.mark.parametrize(
    "readyaml",
    ["plain_readyaml_copied", "map_readyaml_copied"],
    indirect=True,
)
def test_read_yaml(readyaml: ReadYAML):
    yaml_dict = readyaml.read()
    assert "loggers" in yaml_dict


@pytest.mark.parametrize(
    "readyaml",
    [
        "plain_readyaml",
        "map_readyaml",
        "plain_readyaml_copied",
        "map_readyaml_copied",
    ],
    indirect=True,
)
def test_write_yaml(readyaml: ReadYAML, target_dir):
    test_list = ["curly", "larry", "moe"]
    readyaml.write(test_list)

    yaml_files = list(target_dir.iterdir())
    assert len(yaml_files) == 1
    assert yaml_files[0].name == "logging.yaml"

    with open(yaml_files[0]) as f:
        first_line = f.readline()

    assert first_line == "- curly\n"
