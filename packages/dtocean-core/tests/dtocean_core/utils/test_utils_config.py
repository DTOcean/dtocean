import pytest

from dtocean_core.utils.config import (
    init_config,
    init_config_interface,
    init_config_parser,
)


def test_init_config(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.config.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    init_config(logging=True, database=True, files=True)

    assert len(config_tmpdir.listdir()) == 3


@pytest.mark.parametrize("test_input", ["logging", "database", "files"])
def test_init_config_parser(test_input):
    action, overwrite = init_config_parser([test_input])

    assert action == test_input
    assert not overwrite


@pytest.mark.parametrize("test_input", ["logging", "database", "files"])
def test_init_config_parser_overwrite(test_input):
    action, overwrite = init_config_parser([test_input, "--overwrite"])

    assert action == test_input
    assert overwrite


def test_init_config_interface(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.config.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )
    mocker.patch(
        "dtocean_core.utils.config.init_config_parser",
        return_value=("logging", False),
        autospec=True,
    )

    init_config_interface()

    assert len(config_tmpdir.listdir()) == 1
