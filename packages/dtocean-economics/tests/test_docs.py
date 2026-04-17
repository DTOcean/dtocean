import doctest
from pathlib import Path

PACKAGE_DIR = Path(__file__).parents[1]


def test_README():
    readme_path = PACKAGE_DIR / "README.md"
    doctest_results = doctest.testfile(str(readme_path))
    assert doctest_results.failed == 0
