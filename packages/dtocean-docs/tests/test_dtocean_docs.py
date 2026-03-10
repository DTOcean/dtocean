from pathlib import Path
from unittest.mock import MagicMock

from dtocean_docs import get_index, open_docs
from dtocean_docs._cli import run


def test_get_index():
    test = get_index()
    assert Path(test).is_file()


def test_open(mocker):
    test: MagicMock = mocker.patch(
        "dtocean_docs.webbrowser.open_new_tab",
        autospec=True,
    )
    open_docs()
    test.assert_called_once()

    index_url: str = test.call_args[0][0]
    index_path = index_url.replace("file:///", "")
    assert Path(index_path).is_file()


def test_cli_run(mocker):
    mocker.patch("sys.argv", ["dtocean-docs"])
    open_docs: MagicMock = mocker.patch("dtocean_docs._cli.open_docs")

    run()
    open_docs.assert_called_once()
