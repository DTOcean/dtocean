import sys
from collections import namedtuple
from unittest.mock import MagicMock

import pytest
from dtocean_core.utils.cli import main

from dtocean_plugins.cli.app import _config


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("", (False, False, False)),
        ("--debug", (True, False, False)),
        ("--trace-warnings", (False, True, False)),
        ("--quit", (False, False, True)),
    ],
)
def test_setup_app(mocker, arg, expected):
    testargs = ["dtocean", "app"]
    if arg:
        testargs.append(arg)

    mocker.patch.object(sys, "argv", testargs)
    test: MagicMock = mocker.patch(
        "dtocean_plugins.cli.app.main_",
        autospec=True,
    )

    main()

    assert tuple(test.call_args.kwargs.values()) == expected


def test_setup_config(mocker):
    testargs = ["dtocean", "app", "config", "logging"]
    mocker.patch.object(sys, "argv", testargs)
    test = mocker.patch("dtocean_plugins.cli.app._config", autospec=True)

    main()
    args = test.call_args.args[0]

    assert args.action == "logging"
    assert not args.overwrite


def test_setup_config_overwrite(mocker):
    testargs = ["dtocean", "app", "config", "logging", "--overwrite"]
    mocker.patch.object(sys, "argv", testargs)
    test = mocker.patch("dtocean_plugins.cli.app._config", autospec=True)

    main()
    args = test.call_args.args[0]

    assert args.action == "logging"
    assert args.overwrite


def test_config(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_app.utils.config.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    Args = namedtuple("Args", ["action", "overwrite"])
    args = Args(action="logging", overwrite=False)

    _config(args)

    assert len(list(config_tmpdir.iterdir())) == 1
