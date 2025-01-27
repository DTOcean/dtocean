from unittest.mock import MagicMock

from dtocean_hydro._cli import run


def test_init(mocker):
    mocker.patch("sys.argv", ["dtocean-hydro", "init"])
    get_data: MagicMock = mocker.patch("dtocean_hydro._cli.get_data")

    run()

    get_data.assert_called_once()


def test_init_force(mocker):
    mocker.patch("sys.argv", ["dtocean-hydro", "init", "-f"])
    get_data: MagicMock = mocker.patch("dtocean_hydro._cli.get_data")

    run()

    get_data.assert_called_once_with(True)
