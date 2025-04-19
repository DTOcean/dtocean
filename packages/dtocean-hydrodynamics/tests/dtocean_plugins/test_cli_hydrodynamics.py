import sys
from unittest.mock import MagicMock

import pytest

from dtocean_plugins.cli.hydrodynamics import init

cli = pytest.importorskip("dtocean_core.utils.cli")


@pytest.mark.parametrize(
    "arg, expected",
    [
        (None, False),
        ("-f", True),
    ],
)
def test_setup_init(mocker, arg, expected):
    test: MagicMock = mocker.patch(
        "dtocean_plugins.cli.hydrodynamics.get_data",
        autospec=True,
    )

    def mock_init(name, *args):
        if name == "init":
            return [init]
        return []

    mocker.patch(
        "dtocean_core.utils.cli.get_plugin_function",
        side_effect=mock_init,
        autospec=True,
    )

    test_args = ["dtocean", "init"]
    if arg is not None:
        test_args.append(arg)

    mocker.patch.object(sys, "argv", test_args)

    cli.main()

    assert test.call_args.args[0] == expected


def test_setup_wec(mocker):
    testargs = ["dtocean", "hydrodynamics", "wec"]
    mocker.patch.object(sys, "argv", testargs)
    test: MagicMock = mocker.patch(
        "dtocean_plugins.cli.hydrodynamics.run",
        autospec=True,
    )
    cli.main()
    test.assert_called_once()
