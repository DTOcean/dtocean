import sys
from unittest.mock import MagicMock

import pytest

cli = pytest.importorskip("dtocean_core.utils.cli")


def test_setup_docs(mocker):
    testargs = ["dtocean", "docs"]
    mocker.patch.object(sys, "argv", testargs)
    test: MagicMock = mocker.patch(
        "dtocean_plugins.cli.docs.open_docs",
        autospec=True,
    )
    cli.main()
    test.assert_called_once()
