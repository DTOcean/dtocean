# -*- coding: utf-8 -*-
"""py.test tests on main.py

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

#pylint: disable=W0621,C0103,C0111

import os
import configobj
from validate import ValidateError

import pytest

from polite.paths import Directory, ObjDirectory, DirectoryMap
from polite.configuration import Config, Logger, ReadINI, ReadYAML

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def directory():
    '''Share a ObjDirectory object'''

    objdir = ObjDirectory(__name__, "..", "examples", "config")

    return objdir

def test_user_config_exists(tmpdir, directory):

    '''Test if the user_config_exists function returns false'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    logger = Logger(dirmap)

    assert not configdir.isfile(logger.config_file_name)

def test_copy_logger_config(tmpdir, directory):

    '''Test if logger configuration is copied'''

    # Make a local directory
    locd = tmpdir.mkdir("config")
    locp = locd.join("logging.yaml")

    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    logger = Logger(dirmap)

    # Copy the logging file
    logger.copy_config()

    assert dirmap.last_copy_path == str(locp)
    assert len(locd.listdir()) == 1
    assert os.path.basename(str(locd.listdir()[0])) == "logging.yaml"


def test_configure_logger(tmpdir, directory):

    '''Test if logger configuration can be loaded'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    logger = Logger(dirmap)

    # Copy the logging file
    logger.copy_config()

    # Attempt to configure the logger
    log_config_dict = logger.read()
    logger.configure_logger(log_config_dict)


def test_call_logger(tmpdir, directory):

    '''Test if logger can be called'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    logger = Logger(dirmap)
    logger('my_logger')

    assert True


def test_call_logger_options(tmpdir, directory):

    '''Test if logger can be called'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    logger = Logger(dirmap)
    logger('my_logger', level="CRITICAL", info_message="test")

    assert True


def test_copy_ini_config(tmpdir, directory):

    '''Test if the configuration file is correctly copied.'''

    # Make a local directory
    locd = tmpdir.mkdir("config")
    locp = locd.join("configuration.ini")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    ini_reader = ReadINI(dirmap)

    # Copy the logging file
    ini_reader.copy_config()

    assert dirmap.last_copy_path == str(locp)
    assert len(locd.listdir()) == 1
    assert os.path.basename(str(locd.listdir()[0])) == "configuration.ini"

def test_config_exists(tmpdir, directory):

    '''Test that the configuration file is read correctly'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    # Copy config and check for existance
    ini_reader = ReadINI(dirmap)
    ini_reader.copy_config()
    test = ini_reader.config_exists()

    assert test

def test_get_config(tmpdir, directory):

    '''Test that the configuration file is read correctly'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    ini_reader = ReadINI(dirmap)

    # Copy the logging file
    ini_reader.copy_config()

    # Read the config file
    config = ini_reader.get_config()

    assert isinstance(config, configobj.ConfigObj)
    assert set(config.keys()) == set(['Spreadsheet'])
    assert set(config['Spreadsheet'].keys()) == set(['high', 'low'])

def test_get_valid_config(tmpdir, directory):

    '''Test that the configuration file is read correctly'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    ini_reader = ReadINI(dirmap,
                         validation_file_name="validation.ini")

    # Copy the logging file
    ini_reader.copy_config()

    # Read the config file
    config = ini_reader.get_valid_config()

    assert isinstance(config, configobj.ConfigObj)
    assert set(config.keys()) == set(['Spreadsheet'])
    assert set(config['Spreadsheet'].keys()) == set(['high', 'low'])

def test_not_valid_config(tmpdir, directory):

    '''Test that the configuration file is read correctly'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    ini_reader = ReadINI(dirmap,
                         config_file_name="bad_configuration.ini",
                         validation_file_name="validation.ini")

    # Copy the logging file
    ini_reader.copy_config()

    with pytest.raises(ValidateError):
        # Read the config file
        ini_reader.get_valid_config()


def test_make_head_foot_bar():

    '''Test the length of the character strings matches input'''

    head_foot_length = 50
    head_title = 'This is a TEST!'

    header, footer = Config.make_head_foot_bar(head_title, head_foot_length)

    assert len(header) == head_foot_length
    assert len(footer) == head_foot_length

def test_read_yaml(tmpdir, directory):

    '''Test if the configuration file is correctly copied.'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    yaml_reader = ReadYAML(dirmap, "logging.yaml")
    yaml_reader.copy_config()

    yaml_dict = yaml_reader.read()

    assert "loggers" in yaml_dict

def test_write_yaml(tmpdir, directory):

    '''Test if the configuration file is correctly copied.'''

    # Make a local directory
    locd = tmpdir.mkdir("config")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(str(locd))
    dirmap = DirectoryMap(configdir, directory)

    yaml_reader = ReadYAML(dirmap, "logging.yaml")

    test_list = ["curly", "larry", "moe"]
    yaml_reader.write(test_list)

    assert os.path.basename(str(locd.listdir()[0])) == "logging.yaml"


def test_write_yaml_nodir(tmpdir, directory):

    '''Test if the configuration file is correctly copied when directory is
    missing.'''

    # Make a local directory
    locd = tmpdir.mkdir("config")
    nodir = os.path.join(str(locd), "nodir")

    # Create Logger object and change path to user data dir to tmp
    configdir = Directory(nodir)
    dirmap = DirectoryMap(configdir, directory)

    yaml_reader = ReadYAML(dirmap, "logging.yaml")

    test_list = ["curly", "larry", "moe"]
    yaml_reader.write(test_list)

    testdir = locd.join("nodir")
    
    assert os.path.basename(str(testdir.listdir()[0])) == "logging.yaml"
