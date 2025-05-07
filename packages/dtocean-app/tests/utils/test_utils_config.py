
import pytest

from polite.paths import Directory
from dtocean_app.utils.config import (get_install_paths,
                                      get_distribution_names,
                                      get_software_version,
                                      init_config,
                                      init_config_parser,
                                      init_config_interface)


def test_get_install_paths(mocker, tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.utils.config.UserDataDirectory',
                 return_value=mock_dir)
                 
    init_config(install=True)
    test_dict = get_install_paths()
    
    assert "man_user_path" in test_dict


def test_get_distribution_names():
    assert 'dtocean-app' in get_distribution_names()


@pytest.mark.parametrize("names, version, expected", [
                            (['dtocean-app'], '2.1.0', 'dtocean-app 2.1.0'),
                            (['dtocean-app', 'dtocean'],
                             '2022.7',
                             'dtocean 2022.07'),
                            (['dtocean-app', 'dtocean'],
                             '2022.11',
                             'dtocean 2022.11')])
def test_get_software_version(mocker, names, version, expected):
    
    mocker.patch('dtocean_app.utils.config.get_distribution_names',
                 return_value=names)
    mocker.patch('dtocean_app.utils.config.metadata.version',
                 return_value=version)
    
    assert get_software_version() == expected


def test_init_config(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.utils.config.UserDataDirectory',
                 return_value=mock_dir)
                 
    init_config(logging=True, files=True)
        
    assert len(config_tmpdir.listdir()) == 2
              
    init_config(logging=True, files=True)
    
    assert len(config_tmpdir.listdir()) == 4


def test_init_config_overwrite(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.utils.config.UserDataDirectory',
                 return_value=mock_dir)
                 
    init_config(logging=True, files=True)
        
    assert len(config_tmpdir.listdir()) == 2
              
    init_config(logging=True, files=True, overwrite=True)
    
    assert len(config_tmpdir.listdir()) == 2


def test_init_config_install(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.utils.config.UserDataDirectory',
                 return_value=mock_dir)
                 
    init_config(logging=True, files=True, install=True)
        
    assert len(config_tmpdir.listdir()) == 3


@pytest.mark.parametrize("test_input", [
    'logging', 'files', 'install'])
def test_init_config_parser(test_input):
    
    action, overwrite = init_config_parser([test_input])
    
    assert action == test_input
    assert not overwrite


@pytest.mark.parametrize("test_input", [
    'logging', 'files', 'install'])
def test_init_config_parser_overwrite(test_input):
    
    action, overwrite = init_config_parser([test_input, "--overwrite"])
    
    assert action == test_input
    assert overwrite


def test_init_config_interface(mocker, tmpdir):

    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_app.utils.config.UserDataDirectory',
                 return_value=mock_dir)
    mocker.patch('dtocean_app.utils.config.init_config_parser',
                 return_value=('logging', False),
                 autospec=True)
                 
    init_config_interface()
        
    assert len(config_tmpdir.listdir()) == 1
