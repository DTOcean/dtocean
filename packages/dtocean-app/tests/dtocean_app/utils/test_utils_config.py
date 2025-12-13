from mdo_engine.boundary.interface import Box

from dtocean_app.utils.config import (
    get_software_version,
    init_config,
)


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
