# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os
from collections import Counter

import pandas as pd

from dtocean_core.utils.reliability import (get_reliability_tables,
                                            compdict_from_mock)

this_dir = os.path.dirname(os.path.realpath(__file__))
moor_dir = os.path.join(this_dir, "moorings")
elec_dir = os.path.join(this_dir, "electrical")
reli_dir = os.path.join(this_dir, "reliability")

compdict = eval(open(os.path.join(moor_dir, 'dummycompdb.txt')).read())

component_data_path = os.path.join(elec_dir, 'mock_db.xlsx')
xls_file = pd.ExcelFile(component_data_path, encoding = 'utf-8')
elec_dict = compdict_from_mock(xls_file)

compdict.update(elec_dict)

comp_tables = get_reliability_tables(compdict) #component database

moor_found_network = {"topology": eval(open(os.path.join(reli_dir ,
                                              'dummymoorhier.txt')).read()),
                      "nodes": eval(open(os.path.join(reli_dir ,
                                               'dummymoorbom.txt')).read())}

electrical_network = {"topology": eval(open(os.path.join(reli_dir ,
                                              'dummyelechier.txt')).read()),
                      "nodes": eval(open(os.path.join(reli_dir ,
                                               'dummyelecbom.txt')).read())}

test_data = {"project.moorings_foundations_network": moor_found_network,
             "project.electrical_network": electrical_network,
             "component.moorings_chain_NCFR": comp_tables["chain NCFR"],
             "component.moorings_chain_CFR": comp_tables["chain CFR"],
             "component.moorings_forerunner_NCFR":comp_tables["forerunner NCFR"],
             "component.moorings_forerunner_CFR": comp_tables["forerunner CFR"],
             "component.moorings_shackle_NCFR":comp_tables["shackle NCFR"],
             "component.moorings_shackle_CFR": comp_tables["shackle CFR"],
             "component.moorings_swivel_NCFR":comp_tables["swivel NCFR"],
             "component.moorings_swivel_CFR": comp_tables["swivel CFR"],
             "component.foundations_anchor_NCFR":comp_tables["anchor NCFR"],
             "component.foundations_anchor_CFR": comp_tables["anchor CFR"],
             "component.foundations_pile_NCFR":comp_tables["pile NCFR"],
             "component.foundations_pile_CFR": comp_tables["pile CFR"],
             "component.moorings_rope_NCFR":comp_tables["rope NCFR"],
             "component.moorings_rope_CFR": comp_tables["rope CFR"],
             "component.static_cable_NCFR":comp_tables["static_cable NCFR"],
             "component.static_cable_CFR": comp_tables["static_cable CFR"],
             "component.dynamic_cable_NCFR":comp_tables["dynamic_cable NCFR"],
             "component.dynamic_cable_CFR": comp_tables["dynamic_cable CFR"],
             "component.wet_mate_connectors_NCFR":comp_tables["wet_mate NCFR"],
             "component.wet_mate_connectors_CFR": comp_tables["wet_mate CFR"],
             "component.dry_mate_connectors_NCFR":comp_tables["dry_mate NCFR"],
             "component.dry_mate_connectors_CFR": comp_tables["dry_mate CFR"],
             "component.transformers_NCFR":comp_tables["transformer NCFR"],
             "component.transformers_CFR": comp_tables["transformer CFR"],
             "component.collection_points_NCFR":comp_tables["collection_point NCFR"],
             "component.collection_points_CFR": comp_tables["collection_point CFR"],
             }


if __name__ == "__main__":
    
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)


