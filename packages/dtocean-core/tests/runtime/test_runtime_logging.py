import logging

from dtocean_core import start_logging
from dtocean_core.utils.config import init_config


def test_start_logging(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    start_logging()

    logdir = config_tmpdir.parent / "logs"
    assert len(list(logdir.iterdir())) == 1


def test_start_logging_user(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.config.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    init_config(logging=True)

    mocker.patch(
        "dtocean_core.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    # This will raise is the files are not found in the user config directory
    mocker.patch("dtocean_core.ModPath", return_value=None, autospec=True)

    start_logging()

    logdir = config_tmpdir.parent / "logs"
    assert len(list(logdir.iterdir())) == 1


def test_start_logging_rollover(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    start_logging()

    logdir = config_tmpdir.parent / "logs"
    assert len(list(logdir.iterdir())) == 1

    logging.shutdown()
    start_logging()

    assert len(list(logdir.iterdir())) == 2
