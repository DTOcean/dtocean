# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os

test_data = {
    "project.discount_rate": 0.1,
    "project.lifetime": 20,
    "project.number_of_devices": 5,
    "device.system_cost": 1e6,
    "device.power_rating": 1.0,
    "project.electrical_cost_estimate": 1e5,
    "project.moorings_cost_estimate": 1e5,
    "project.installation_cost_estimate": 1e5,
    "project.opex_estimate": 1e4,
    "project.annual_repair_cost_estimate": 1e4,
    "project.annual_array_mttf_estimate": 10000.0,
    "project.electrical_network_efficiency": 0.95,
    "project.annual_energy": 10000.0,
    "project.estimate_energy_record": True,
}

if __name__ == "__main__":
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)

    print("generate test data: {}".format(pkl_path))
