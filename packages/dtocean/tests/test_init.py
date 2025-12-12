import tomllib
from pathlib import Path

from dtocean import get_version


def get_expected_version(short: bool = False) -> str:
    top_dir = Path(__file__).resolve().parents[3]
    project = top_dir / "pyproject.toml"

    with open(project, "rb") as f:
        data = tomllib.load(f)

    release = data["tool"]["poetry"]["version"]

    if not short:
        return release

    parts = release.split(".")
    return ".".join(parts[:2])


def test_get_version():
    test = get_version()
    expected = get_expected_version()

    assert test == expected
