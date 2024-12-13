# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os
import numpy as np
import pandas as pd


site_boundary = np.array([[0.0, 0.0],
                          [0.1, 0.0],
                          [0.1, 0.1],
                          [0.0, 0.1]])

lease_boundary = np.array([[  0.,   0.],
                           [100.,   0.],
                           [100., 200.],
                           [  0., 200.]])

cable_boundary = np.array([[  0.,   0.],
                           [100.,   0.],
                           [100., 100.],
                           [  0., 100.]])

test_proj = "+proj=utm +zone=31 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

site_boundaries = {"site one": np.copy(site_boundary),
                    "site_two": np.copy(site_boundary)}
lease_boundaries = {"site one": np.copy(lease_boundary),
                    "site_two": np.copy(lease_boundary)}
cable_boundaries = {"site one": np.copy(cable_boundary),
                    "site_two": np.copy(cable_boundary)}
landing_points = {"site one": (0, 0),
                  "site_two": (0, 0)}
entry_point = (100.,   0.)

sites_dict = {"id": [1, 2],
              "site_name": ["site one", "site_two"],
              "lease_area_proj4_string": [test_proj, test_proj]}
sites_df = pd.DataFrame(sites_dict)

selected_site = "site one"

test_data = {"hidden.available_sites": sites_df,
             "hidden.corridor_boundaries": cable_boundaries,
             "hidden.lease_boundaries": lease_boundaries,
             "hidden.landing_points": landing_points,
             "project.lease_area_entry_point": entry_point,
             "site.selected_name": selected_site,
             "hidden.site_boundaries": site_boundaries}
             
if __name__ == "__main__":
    
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)

