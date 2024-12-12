# -*- coding: utf-8 -*-
"""py.test tests on main.py

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

# pylint: disable=W0621,C0103,C0111

import os
import shutil

import configobj
import pytest

from polite_config.configuration import Logger, ReadINI, ReadYAML
from polite_config.paths import ModPath


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def directory():
    """Share a ModPath object"""

    objdir = ModPath(__name__, "..", "examples", "config")

    return objdir


def test_user_config_exists(tmp_path):
    """Test if the user_config_exists function returns false"""

    # Make a local directory
    locd = tmp_path / "config"

    logger = Logger(locd)

    assert not (locd / logger.config_file_name).is_file()


def test_copy_logger_config(tmp_path):
    """Test if logger configuration is copied"""

    # Make a local directory
    locd = tmp_path / "config"
    logger = Logger(locd)

    with pytest.raises(ValueError):
        logger.copy_config()


def test_configure_logger(tmp_path, directory):
    """Test if logger configuration can be loaded"""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    locp = locd / "logging.yaml"

    logger = Logger(locd)

    # Copy the logging file
    src_file_path = directory / "logging.yaml"
    print(src_file_path)
    shutil.copy(src_file_path, str(locp))

    # Attempt to configure the logger
    log_config_dict = logger.read()
    print(log_config_dict)
    logger.configure_logger(log_config_dict)


def test_call_logger(tmp_path, directory):
    """Test if logger can be called"""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    locp = locd / "logging.yaml"

    logger = Logger(locd)

    # Copy the logging file
    src_file_path = directory / "logging.yaml"
    shutil.copy(src_file_path, str(locp))

    logger("my_logger")

    assert True


def test_call_logger_options(tmp_path, directory):
    """Test if logger can be called with options"""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    locp = locd / "logging.yaml"

    logger = Logger(locd)

    # Copy the logging file
    src_file_path = directory / "logging.yaml"
    shutil.copy(src_file_path, str(locp))

    logger("my_logger", level="CRITICAL", info_message="test")

    assert True


def test_copy_ini_config(tmp_path):
    """Test if the configuration file is correctly copied."""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    ini_reader = ReadINI(locd)

    with pytest.raises(ValueError):
        # Copy the logging file
        ini_reader.copy_config()


def test_config_exists(tmp_path, directory):
    """Test that the configuration file is read correctly"""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    locp = locd / "configuration.ini"

    # Create object
    ini_reader = ReadINI(locd)

    # Copy config and check for existance
    src_file_path = directory / "configuration.ini"
    shutil.copy(src_file_path, str(locp))

    test = ini_reader.config_exists()

    assert test


def test_get_config(tmp_path, directory):
    """Test that the configuration file is read correctly"""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    locp = locd / "configuration.ini"

    # Create object
    ini_reader = ReadINI(locd)

    # Copy the config file
    src_file_path = directory / "configuration.ini"
    shutil.copy(src_file_path, str(locp))

    # Read the config file
    config = ini_reader.get_config()

    assert isinstance(config, configobj.ConfigObj)
    assert set(config.keys()) == set(["Spreadsheet"])

    spreadsheet = config["Spreadsheet"]
    assert isinstance(spreadsheet, dict)
    assert set(spreadsheet.keys()) == set(["high", "low"])


def test_read_yaml(tmp_path, directory):
    """Test if the configuration file is correctly copied."""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    locp = locd / "logging.yaml"

    # Create Logger object
    yaml_reader = ReadYAML(locd, "logging.yaml")

    # Copy the config file
    src_file_path = directory / "logging.yaml"
    shutil.copy(src_file_path, str(locp))

    yaml_dict = yaml_reader.read()

    assert "loggers" in yaml_dict


def test_write_yaml(tmp_path):
    """Test if the configuration file is correctly copied."""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()

    yaml_reader = ReadYAML(locd, "logging.yaml")

    test_list = ["curly", "larry", "moe"]
    yaml_reader.write(test_list)

    assert os.path.basename(str(list(locd.iterdir())[0])) == "logging.yaml"


def test_write_yaml_nodir(tmp_path):
    """Test if the configuration file is correctly copied when directory is
    missing."""

    # Make a local directory
    locd = tmp_path / "config"
    locd.mkdir()
    nodir = locd / "nodir"

    yaml_reader = ReadYAML(nodir, "logging.yaml")

    test_list = ["curly", "larry", "moe"]
    yaml_reader.write(test_list)

    assert os.path.basename(str(list(nodir.iterdir())[0])) == "logging.yaml"
