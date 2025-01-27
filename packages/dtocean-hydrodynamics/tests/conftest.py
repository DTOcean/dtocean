import pytest


@pytest.fixture
def install_lines():
    lines = [
        "[dtocean_tidal]",
        "share_path=dtocean_tidal_mock",
        "",
        "[dtocean_wec]",
        "share_path=dtocean_wec_mock",
        "",
        "[global]",
        "prefix=mock",
        "bin_path=bin_mock",
    ]

    return "\n".join(lines)
