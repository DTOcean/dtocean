import logging
import logging.handlers
import shutil
from pathlib import Path

import pytest

from polite_config.configuration import Logger
from polite_config.paths import DirectoryMap, ModPath


@pytest.fixture(scope="module")
def src_dir():
    objdir = ModPath(__name__, "..", "examples", "config")
    return objdir


@pytest.fixture()
def target_dir(tmp_path):
    return tmp_path / "config"


@pytest.fixture
def logger(request):
    return request.getfixturevalue(request.param)


@pytest.fixture()
def plain_logger(target_dir: Path):
    return Logger(target_dir)


@pytest.fixture()
def map_logger(src_dir: Path, target_dir: Path):
    dirmap = DirectoryMap(target_dir, src_dir)
    return Logger(dirmap)


@pytest.mark.parametrize(
    "logger",
    ["plain_logger", "map_logger"],
    indirect=True,
)
def test_config_not_exists(logger: Logger, target_dir: Path):
    assert not (target_dir / logger.config_file_name).is_file()


@pytest.fixture
def plain_logger_copied(plain_logger: Logger, src_dir: Path, target_dir: Path):
    target_dir.mkdir()
    shutil.copy(src_dir / "logging.yaml", target_dir)
    return plain_logger


@pytest.fixture
def map_logger_copied(map_logger: Logger, target_dir: Path):
    target_dir.mkdir()
    map_logger.copy_config()
    return map_logger


def test_plain_logger_copy_config_error(plain_logger: Logger):
    with pytest.raises(ValueError):
        plain_logger.copy_config()


def test_map_logger_copy_config(map_logger_copied: Logger, target_dir: Path):
    files = list(target_dir.iterdir())
    assert len(files) == 1
    assert Path(files[0]).name == "logging.yaml"


@pytest.mark.parametrize(
    "logger",
    ["plain_logger_copied", "map_logger_copied"],
    indirect=True,
)
def test_configure_logger(logger: Logger):
    logger.configure_logger()
    assert "my_logger" in logging.Logger.manager.loggerDict


@pytest.mark.parametrize(
    "logger",
    ["plain_logger_copied", "map_logger_copied"],
    indirect=True,
)
def test_configure_logger_dict(logger: Logger):
    log_config_dict = logger.read()
    my_logger = log_config_dict["loggers"]["my_logger"]
    log_config_dict["loggers"] = {"my_logga": my_logger}

    logger.configure_logger(log_config_dict=log_config_dict)
    assert "my_logga" in logging.Logger.manager.loggerDict


@pytest.mark.parametrize(
    "logger",
    ["plain_logger_copied", "map_logger_copied"],
    indirect=True,
)
def test_configure_logger_prefix(logger: Logger, tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger.configure_logger(file_prefix=log_dir)

    assert "my_logger" in logging.Logger.manager.loggerDict
    my_logger = logging.Logger.manager.loggerDict["my_logger"]
    assert isinstance(my_logger, logging.Logger)

    assert len(my_logger.handlers) == 1
    assert isinstance(my_logger.handlers[0], logging.FileHandler)
    assert Path(my_logger.handlers[0].baseFilename).parent == log_dir


@pytest.mark.parametrize(
    "logger",
    ["plain_logger_copied", "map_logger_copied"],
    indirect=True,
)
def test_get_named_logger(logger: Logger):
    logger.configure_logger()
    my_logger = logger.get_named_logger("my_logger")

    assert isinstance(my_logger, logging.Logger)
    assert my_logger.name == "my_logger"
    assert my_logger.level == 10
    assert len(my_logger.handlers) == 1
    assert isinstance(my_logger.handlers[0], logging.FileHandler)


@pytest.mark.parametrize(
    "logger",
    ["plain_logger_copied", "map_logger_copied"],
    indirect=True,
)
def test_get_named_logger_level(logger: Logger):
    logger.configure_logger()
    my_logger = logger.get_named_logger("my_logger", "INFO")

    assert isinstance(my_logger, logging.Logger)
    assert my_logger.name == "my_logger"
    assert my_logger.level == 20


@pytest.mark.parametrize(
    "logger",
    ["plain_logger_copied", "map_logger_copied"],
    indirect=True,
)
def test_get_named_logger_message(logger: Logger, tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger.configure_logger(file_prefix=log_dir)
    logger.get_named_logger("my_logger", info_message="mock")

    log_files = list(log_dir.iterdir())
    assert len(log_files) == 1

    with open(log_files[0]) as f:
        first_line = f.readline()

    assert "mock" in first_line


@pytest.mark.parametrize(
    "logger",
    ["plain_logger_copied", "map_logger_copied"],
    indirect=True,
)
def test_call(logger: Logger, tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    my_logger = logger("my_logger", "INFO", "mock", log_dir)

    assert isinstance(my_logger, logging.Logger)
    assert my_logger.name == "my_logger"
    assert my_logger.level == 20
    assert len(my_logger.handlers) == 1
    assert isinstance(my_logger.handlers[0], logging.FileHandler)

    log_files = list(log_dir.iterdir())
    assert len(log_files) == 1

    with open(log_files[0]) as f:
        first_line = f.readline()

    assert "mock" in first_line
