# -*- coding: utf-8 -*-

# pylint: disable=eval-used,redefined-outer-name

import os

import pytest
import pandas as pd

from dtocean_core.utils.reliability import (compdict_from_mock,
                                            get_reliability_tables)

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
MOOR_DIR = os.path.join(THIS_DIR, "..", "test_data", "moorings")
ELEC_DIR = os.path.join(THIS_DIR, "..", "test_data", "electrical")


@pytest.fixture(scope='module')
def compdict():
    
    compdict = eval(open(os.path.join(MOOR_DIR, 'dummycompdb.txt')).read())

    component_data_path = os.path.join(ELEC_DIR, 'mock_db.xlsx')
    xls_file = pd.ExcelFile(component_data_path, encoding='utf-8')
    elec_dict = compdict_from_mock(xls_file)
    
    compdict.update(elec_dict)
    
    return compdict


def test_get_reliability_tables(compdict):
    
    comp_tables = get_reliability_tables(compdict)
    
    assert set(comp_tables.keys()) == set(['shackle NCFR',
                                           'shackle CFR',
                                           'chain NCFR',
                                           'chain CFR',
                                           'forerunner NCFR',
                                           'forerunner CFR',
                                           'transformer NCFR',
                                           'transformer CFR',
                                           'swivel NCFR',
                                           'swivel CFR',
                                           'dry_mate NCFR',
                                           'dry_mate CFR',
                                           'pile NCFR',
                                           'pile CFR',
                                           'static_cable NCFR',
                                           'static_cable CFR',
                                           'dynamic_cable NCFR',
                                           'dynamic_cable CFR',
                                           'wet_mate NCFR',
                                           'wet_mate CFR',
                                           'anchor NCFR',
                                           'anchor CFR',
                                           'rope NCFR',
                                           'rope CFR',
                                           'collection_point NCFR',
                                           'collection_point CFR'])
    
    for table in comp_tables.values():
        assert set(table.columns) == set(["Key Identifier",
                                          "Lower Bound",
                                          "Mean",
                                          "Upper Bound"])
