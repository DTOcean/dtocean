
import logging

from polite_config.paths import Directory
from dtocean_core import start_logging
from dtocean_core.utils.config import init_config


def test_start_logging(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.UserDataDirectory',
                 return_value=mock_dir,
                 autospec=True)

    start_logging()
    
    logdir = config_tmpdir.join("..", "logs")
    
    assert len(logdir.listdir()) == 1


def test_start_logging_user(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.utils.config.UserDataDirectory',
                 return_value=mock_dir,
                 autospec=True)
                 
    init_config(logging=True, files=True)
    
    mocker.patch('dtocean_core.UserDataDirectory',
                 return_value=mock_dir,
                 autospec=True)
    
    # This will raise is the files are not found in the user config directory
    mocker.patch('dtocean_core.ObjDirectory',
                 return_value=None,
                 autospec=True)
    
    start_logging()
    
    logdir = config_tmpdir.join("..", "logs")
    
    assert len(logdir.listdir()) == 1
              

def test_start_logging_rollover(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.UserDataDirectory',
                 return_value=mock_dir,
                 autospec=True)

    start_logging()
    
    logdir = config_tmpdir.join("..", "logs")
    
    assert len(logdir.listdir()) == 1
    
    logging.shutdown()
    start_logging()
    
    assert len(logdir.listdir()) == 2
