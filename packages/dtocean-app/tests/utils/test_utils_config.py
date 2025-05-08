import pytest
from mdo_engine.boundary.interface import Box

from dtocean_app.utils.config import (
    get_install_paths,
    get_software_version,
    init_config,
    init_config_interface,
    init_config_parser,
)


def test_get_install_paths(mocker, tmp_path):
    # Make a source directory with some files
    mock_dir = tmp_path / "config"
    mock_dir.mkdir()

    mocker.patch(
        "dtocean_app.utils.config.UserDataPath",
        return_value=mock_dir,
    )

    init_config(install=True)
    test_dict = get_install_paths()

    assert test_dict is not None
    assert "man_user_path" in test_dict


def test_get_software_version(mocker):
    dist = Box({"version": "mock"})
    mocker.patch("dtocean_app.utils.config.distribution", return_value=dist)

    assert get_software_version() == "dtocean-app mock"


def test_init_config(mocker, tmp_path):
    # Make a source directory with some files
    mock_dir = tmp_path / "config"
    mock_dir.mkdir()

    mocker.patch("dtocean_app.utils.config.UserDataPath", return_value=mock_dir)

    init_config(logging=True)
    assert len(list(mock_dir.iterdir())) == 1

    init_config(logging=True)
    assert len(list(mock_dir.iterdir())) == 2


def test_init_config_overwrite(mocker, tmp_path):
    # Make a source directory with some files
    mock_dir = tmp_path / "config"
    mock_dir.mkdir()

    mocker.patch("dtocean_app.utils.config.UserDataPath", return_value=mock_dir)

    init_config(logging=True)
    assert len(list(mock_dir.iterdir())) == 1

    init_config(logging=True, overwrite=True)
    assert len(list(mock_dir.iterdir())) == 1


def test_init_config_install(mocker, tmp_path):
    # Make a source directory with some files
    mock_dir = tmp_path / "config"
    mock_dir.mkdir()

    mocker.patch("dtocean_app.utils.config.UserDataPath", return_value=mock_dir)

    init_config(logging=True, install=True)
    assert len(list(mock_dir.iterdir())) == 2


@pytest.mark.parametrize("test_input", ["logging", "install"])
def test_init_config_parser(test_input):
    action, overwrite = init_config_parser([test_input])
    assert action == test_input
    assert not overwrite


@pytest.mark.parametrize("test_input", ["logging", "install"])
def test_init_config_parser_overwrite(test_input):
    action, overwrite = init_config_parser([test_input, "--overwrite"])

    assert action == test_input
    assert overwrite


def test_init_config_interface(mocker, tmp_path):
    # Make a source directory with some files
    mock_dir = tmp_path / "config"
    mock_dir.mkdir()

    mocker.patch("dtocean_app.utils.config.UserDataPath", return_value=mock_dir)
    mocker.patch(
        "dtocean_app.utils.config.init_config_parser",
        return_value=("logging", False),
        autospec=True,
    )

    init_config_interface()

    assert len(list(mock_dir.iterdir())) == 1
