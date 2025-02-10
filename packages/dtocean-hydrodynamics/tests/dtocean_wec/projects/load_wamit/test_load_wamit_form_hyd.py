from dtocean_wec.tab4 import ReadWamit


def test_form_hyd_load(form_hyd: ReadWamit):
    assert form_hyd._data is not None
