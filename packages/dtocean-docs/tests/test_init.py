from pathlib import Path

from dtocean_docs import get_index


def test_get_index():
    test = get_index()
    assert Path(test).is_file()
