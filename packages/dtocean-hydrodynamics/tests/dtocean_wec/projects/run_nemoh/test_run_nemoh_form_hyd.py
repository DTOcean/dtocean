from pathlib import Path

THIS_DIR = Path(__file__)


def test_form_hyd_load(form_hyd):
    assert form_hyd._data is not None
