
import pytest

from polite.paths import Directory
from dtocean_core.utils.config import (init_config,
                                       init_config_parser,
                                       init_config_interface)


def test_init_config(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.utils.config.UserDataDirectory',
                 return_value=mock_dir,
                 autospec=True)
                 
    init_config(logging=True, database=True, files=True)
        
    assert len(config_tmpdir.listdir()) == 3


@pytest.mark.parametrize("test_input", [
    'logging', 'database', 'files'])
def test_init_config_parser(test_input):
    
    action, overwrite = init_config_parser([test_input])
    
    assert action == test_input
    assert not overwrite

@pytest.mark.parametrize("test_input", [
    'logging', 'database', 'files'])
def test_init_config_parser_overwrite(test_input):
    
    action, overwrite = init_config_parser([test_input, "--overwrite"])
    
    assert action == test_input
    assert overwrite


def test_init_config_interface(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.utils.config.UserDataDirectory',
                 return_value=mock_dir,
                 autospec=True)
    mocker.patch('dtocean_core.utils.config.init_config_parser',
                 return_value=('logging', False),
                 autospec=True)
                 
    init_config_interface()
        
    assert len(config_tmpdir.listdir()) == 1
