import sys

import pytest

from dtocean_core.utils.cli import main


@pytest.mark.parametrize(
    "arg, expected",
    [
        (None, False),
        ("-f", True),
    ],
)
def test_setup_init(mocker, arg, expected):
    result_args = None

    def mock_init(args):
        nonlocal result_args
        result_args = args

    mocker.patch(
        "dtocean_core.utils.cli.get_plugin_function",
        return_value=[mock_init],
        autospec=True,
    )

    test_args = ["dtocean", "init"]
    if arg is not None:
        test_args.append(arg)

    mocker.patch.object(sys, "argv", test_args)

    main()

    assert result_args is not None
    assert result_args.force == expected
