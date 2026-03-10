import pytest

from dtocean_app.utils.display import is_high_dpi


@pytest.mark.parametrize("pixels, expected", [(99, False), (101, True)])
def test_is_high_dpi_false(mocker, pixels, expected):
    mocker.patch(
        "PySide6.QtGui.QScreen.logicalDotsPerInch",
        return_value=pixels,
    )
    assert is_high_dpi() is expected
