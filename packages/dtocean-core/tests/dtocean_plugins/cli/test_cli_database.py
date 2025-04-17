import sys

from dtocean_core.utils.cli import main


def test_setup_database(mocker):
    testargs = ["dtocean", "database", "dump", "-i", "local"]

    mocker.patch.object(sys, "argv", testargs)
    test = mocker.patch("dtocean_plugins.cli.database._database", autospec=True)

    main()
    args = test.call_args.args[0]

    assert args.action == "dump"
    assert args.identifier == "local"
