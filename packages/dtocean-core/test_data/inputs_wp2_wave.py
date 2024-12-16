# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os
from datetime import datetime, timedelta

import numpy as np


dir_path = os.path.dirname(__file__)

# Setup
x = np.linspace(0.,1000.,20.)
y = np.linspace(0.,300.,20.) 
nx = len(x)
ny = len(y)

# Bathymetry?
X, Y = np.meshgrid(x,y)
Z = -X * 0.1 - 1
depths = Z.T[:, :, np.newaxis]

sediments = np.chararray((nx,ny,1), itemsize=20)
sediments[:] = "rock"
   
strata = {"values": {'depth': depths,
                     'sediment': sediments},
          "coords": [x, y, ["layer 1"]]}

sample_size = 1000

dates = []
dt = datetime(2010, 12, 01)
step = timedelta(seconds=3600)
    
for _ in range(sample_size):
    dates.append(dt)
    dt += step
    
Hm0 = 9. * np.random.random_sample(sample_size)
direction = 360. * np.random.random_sample(sample_size)
Te = 15. * np.random.random_sample(sample_size)

wave_series = {"DateTime": dates,
               "Te": Te,
               "Hm0": Hm0,
               "Dir": direction}

# Fixed array layout
pos = [(450., 100.),
       (550., 100.),
       (450., 150.),
       (550., 150.)]

FixedArrayLayout = np.array(pos)
               
#wave_xgrid = None
#B=  np.array([0.,270.])/180*np.pi
#H=  np.array([1.])
#T=  np.array([6.])
#p= 1.0/len(B)/len(H)/len(T)* np.ones((len(T),len(H),len(B)))
#               
#occurrence_matrix_coords = [T,H,B]
#wave_xgrid = {"values": p,
#              "coords": occurrence_matrix_coords}

lease_area = np.array([[50., 50.],[950., 50.],[950., 250.],[50., 250.]],dtype=float)
power_law_exponent = np.array([7.])
nogo_areas = {"a": np.array([[0, 0],[.1, 0],[.1, .1],[0, .1]])}
rated_array_power = 5.
main_direction = None
blockage_ratio = 1.
spectrum_type_farm = 'JONSWAP'
spectrum_gamma_farm = 3.3
spectrum_dir_spreading_farm = 0.
point_SSH = 0.
#user_array_option = 'rectangular'
#user_array_layout = None
user_array_option = 'User Defined Fixed'
user_array_layout = FixedArrayLayout
wave_data_directory = os.path.abspath(os.path.join(dir_path, "nemoh"))
float_flag = False
min_install = -np.inf
max_install = 0.
min_dist_x = 40.
min_dist_y = 40.
yaw_angle = 0.
rated_power_device = 1.
op_threshold = 0.

landing_point = (0.,0.)

test_data = {'bathymetry.layers': strata,
             'corridor.landing_point': landing_point,
             'device.installation_depth_max': max_install,
             'device.installation_depth_min': min_install,
             'device.minimum_distance_x': min_dist_x,
             'device.minimum_distance_y': min_dist_y,
             'options.optimisation_threshold': op_threshold,
             'device.power_rating': rated_power_device,
             'device.wave_data_directory': wave_data_directory,
             'device.yaw': yaw_angle,
             'farm.blockage_ratio': blockage_ratio,
             'site.lease_boundary': lease_area,
             'project.main_direction': main_direction,
             'farm.nogo_areas': nogo_areas,
#             'farm.point_sea_surface_height': point_SSH,
#             'farm.power_law_exponent': power_law_exponent,
             'project.rated_power': rated_array_power,
             'farm.spec_gamma': spectrum_gamma_farm,
             'farm.spec_spread': spectrum_dir_spreading_farm,
             'farm.spectrum_name': spectrum_type_farm,
#             'farm.wave_occurrence': wave_xgrid,
             'farm.wave_series': wave_series,
             'options.user_array_layout': user_array_layout,
             'options.user_array_option': user_array_option}
             
if __name__ == "__main__":
    
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)

