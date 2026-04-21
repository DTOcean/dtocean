import doctest
from pathlib import Path

THIS_DIR = Path(__file__).parent


def test_README():
    readme_path = THIS_DIR.parent / "README.md"
    relative_readme_path = readme_path.relative_to(THIS_DIR, walk_up=True)
    doctest_results = doctest.testfile(str(relative_readme_path))
    assert doctest_results.failed == 0
