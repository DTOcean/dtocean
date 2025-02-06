def test_form_hyd_load(form_hyd):
    form_hyd.btn_load_data_t1.click()
    assert "hyd" in form_hyd._data.keys()
