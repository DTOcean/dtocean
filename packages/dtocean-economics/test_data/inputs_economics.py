# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os

import pandas as pd

discount_rate = 0.1
electrical_network_efficiency = 0.99
capex_oandm = 100.0
externalities_capex = 1e6

zero_bom_dict = {
    "Key Identifier": [0, 1],
    "Quantity": [5, 10],
    "Cost": [100, 50],
    "Year": [0, 0],
}
zero_bom = pd.DataFrame(zero_bom_dict)

electrical_bom = zero_bom.copy()
moorings_bom = zero_bom.copy()

install_bom_dict = {
    "Key Identifier": [0, 1],
    "Quantity": [1, 1],
    "Cost": [1000, 2000],
    "Year": [1, 2],
}
install_bom = pd.DataFrame(install_bom_dict)

opex_bom_dict = {"Cost": [1000, 2000], "Year": [3, 4]}
opex_bom = pd.DataFrame(opex_bom_dict)

energy_record_dict = {"Energy": [10000, 20000], "Year": [3, 4]}
energy_record = pd.DataFrame(energy_record_dict)


test_data = {
    "project.discount_rate": discount_rate,
    "project.electrical_economics_data": electrical_bom,
    "project.moorings_foundations_economics_data": moorings_bom,
    "project.installation_economics_data": install_bom,
    "project.capex_oandm": capex_oandm,
    "project.opex_per_year": opex_bom,
    "project.energy_per_year": energy_record,
    "project.electrical_network_efficiency": electrical_network_efficiency,
    "project.externalities_capex": externalities_capex,
}

if __name__ == "__main__":
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)

    print("generate test data: {}".format(pkl_path))
