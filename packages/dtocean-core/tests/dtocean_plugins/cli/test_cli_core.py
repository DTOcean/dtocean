import sys
from collections import namedtuple

import pytest

from dtocean_core.utils.cli import main
from dtocean_plugins.cli.core import _config


@pytest.mark.parametrize(
    "arg, expected", [("", True), ("-o out.prj", "out.prj"), ("-n", False)]
)
def test_setup_run(mocker, arg, expected):
    testargs = ["dtocean", "core", "run", "mock.prj", "-fwl"]
    if arg:
        testargs.append(arg)

    mocker.patch.object(sys, "argv", testargs)
    test = mocker.patch("dtocean_plugins.cli.core.main", autospec=True)

    main()

    assert test.call_args.args == ("mock.prj", expected, True, True, True)


@pytest.mark.parametrize("arg", ["logging", "database"])
def test_setup_config(mocker, arg):
    testargs = ["dtocean", "core", "config"]
    if arg:
        testargs.append(arg)

    mocker.patch.object(sys, "argv", testargs)
    test = mocker.patch("dtocean_plugins.cli.core._config", autospec=True)

    main()
    args = test.call_args.args[0]

    assert args.action == arg
    assert not args.overwrite


@pytest.mark.parametrize("arg", ["logging", "database"])
def test_setup_config_overwrite(mocker, arg):
    testargs = ["dtocean", "core", "config", "--overwrite"]
    if arg:
        testargs.append(arg)

    mocker.patch.object(sys, "argv", testargs)
    test = mocker.patch("dtocean_plugins.cli.core._config", autospec=True)

    main()
    args = test.call_args.args[0]

    assert args.action == arg
    assert args.overwrite


def test_config(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.config.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    Args = namedtuple("Args", ["action", "overwrite"])
    args = Args(action="logging", overwrite=False)

    _config(args)

    assert len(list(config_tmpdir.iterdir())) == 1
