# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os

import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal, norm

# Setup
x = np.linspace(0.0, 1100.0, 100)
y = np.linspace(0.0, 300.0, 30)
nx = len(x)
ny = len(y)

# Bathymetry?
X, Y = np.meshgrid(x, y)
Z = -X * 0.1 - 1
depths = Z.T[:, :, np.newaxis]
sediments = np.full((nx, ny, 1), "rock")

strata = {
    "values": {"depth": depths, "sediment": sediments},
    "coords": [x, y, ["layer 1"]],
}

# Machine data
X = np.array(
    [
        0.0,
        0.1010101,
        0.2020202,
        0.3030303,
        0.4040404,
        0.50505051,
        0.60606061,
        0.70707071,
        0.80808081,
        0.90909091,
        1.01010101,
        1.11111111,
        1.21212121,
        1.31313131,
        1.41414141,
        1.51515152,
        1.61616162,
        1.71717172,
        1.81818182,
        1.91919192,
        2.02020202,
        2.12121212,
        2.22222222,
        2.32323232,
        2.42424242,
        2.52525253,
        2.62626263,
        2.72727273,
        2.82828283,
        2.92929293,
        3.03030303,
        3.13131313,
        3.23232323,
        3.33333333,
        3.43434343,
        3.53535354,
        3.63636364,
        3.73737374,
        3.83838384,
        3.93939394,
        4.04040404,
        4.14141414,
        4.24242424,
        4.34343434,
        4.44444444,
        4.54545455,
        4.64646465,
        4.74747475,
        4.84848485,
        4.94949495,
        5.05050505,
        5.15151515,
        5.25252525,
        5.35353535,
        5.45454545,
        5.55555556,
        5.65656566,
        5.75757576,
        5.85858586,
        5.95959596,
        6.06060606,
        6.16161616,
        6.26262626,
        6.36363636,
        6.46464646,
        6.56565657,
        6.66666667,
        6.76767677,
        6.86868687,
        6.96969697,
        7.07070707,
        7.17171717,
        7.27272727,
        7.37373737,
        7.47474747,
        7.57575758,
        7.67676768,
        7.77777778,
        7.87878788,
        7.97979798,
        8.08080808,
        8.18181818,
        8.28282828,
        8.38383838,
        8.48484848,
        8.58585859,
        8.68686869,
        8.78787879,
        8.88888889,
        8.98989899,
        9.09090909,
        9.19191919,
        9.29292929,
        9.39393939,
        9.49494949,
        9.5959596,
        9.6969697,
        9.7979798,
        9.8989899,
        10.0,
    ]
)

Cp = np.array(
    [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.00248182,
        0.0273,
        0.05211818,
        0.07693636,
        0.10175455,
        0.12657273,
        0.15139091,
        0.17620909,
        0.20102727,
        0.22584545,
        0.25066364,
        0.27548182,
        0.3003,
        0.32511818,
        0.34993636,
        0.37475455,
        0.39957273,
        0.42439091,
        0.44920909,
        0.47402727,
        0.49884545,
        0.52366364,
        0.54848182,
        0.5733,
        0.59811818,
        0.62293636,
        0.64775455,
        0.67257273,
        0.69739091,
        0.72220909,
        0.74702727,
        0.77184545,
        0.79666364,
        0.82148182,
        0.8463,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
        0.86,
    ]
)

Ct = 0.4 * np.ones((100))

# p = np.array([1.])
# N = len(p)
# V = 1.*np.ones((ny,nx,N))
# U = 2.*np.ones((ny,nx,N))
# SSH = 3.0*np.ones((N))
# tide_matrix = {'V':V,'U':U,'p':p,'TI':TI,'x':x,'y':y,'SSH':SSH}

# Performance curves are matched to the same veloity abscissae
tidal_performance = {
    "Velocity": X,
    "Coefficient of Power": Cp,
    "Coefficient of Thrust": Ct,
}

# Tidal time series
n_bins = 6
time_points = 48
t = pd.date_range("1/1/2011", periods=time_points, freq="h")

rv = norm()
time_sin = np.sin(np.linspace(0, 4 * np.pi, time_points))
time_scaled = time_sin * (1.0 / np.amax(time_sin))

xgrid, ygrid = np.meshgrid(x, y)
pos = np.dstack((xgrid, ygrid))

rv = multivariate_normal(
    [500.0, 150.0],
    [[max(x) * 5.0, max(y) * 2.0], [max(y) * 2.0, max(x) * 5.0]],  # type: ignore
)

u_max = 0.0
v_max = 6.0
ssh_max = 1.0
TI = 0.1

grid_pdf = rv.pdf(pos).T

# u_scaled = grid_pdf * (u_max / np.amax(grid_pdf))
u_scaled = np.ones((nx, ny)) * u_max
v_scaled = np.ones((nx, ny)) * v_max
ssh_scaled = grid_pdf * (ssh_max / np.amax(grid_pdf))

u_arrays = []
v_arrays = []
ssh_arrays = []

for multiplier in time_scaled:
    u_arrays.append(np.abs(u_scaled * multiplier))
    v_arrays.append(np.abs(v_scaled * multiplier))
    ssh_arrays.append(ssh_scaled * multiplier)

U = np.dstack(u_arrays)
V = np.dstack(v_arrays)
SSH = np.dstack(ssh_arrays)
TI = np.ones(SSH.shape) * TI

tidal_series_raw = {
    "values": {"U": U, "V": V, "SSH": SSH, "TI": TI},
    "coords": [x, y, t],
}

xc = x[int(nx / 2)]
yc = y[int(ny / 2)]
tidal_point = (xc, yc)

# Fixed array layout
pos = [(450.0, 100.0), (550.0, 100.0), (450.0, 150.0), (550.0, 150.0)]

FixedArrayLayout = np.array(pos)

# Lease area is extended beyond bathymetry limits.
lease_area = np.array(
    [[50.0, 50.0], [1050.0, 50.0], [1050.0, 250.0], [50.0, 250.0]], dtype=float
)
power_law_exponent = np.array([7.0])
nogo_areas = {
    "a": np.array([[50.0, 50.0], [60.0, 50.0], [60.0, 60.0], [50.0, 60.0]])
}
rated_array_power = 10.0
main_direction = None
blockage_ratio = 1.0
turbine_hub_height = 20.0
user_array_option = "User Defined Fixed"
user_array_layout = FixedArrayLayout
rotor_diam = 8.0
turbine_interdist = 20.0
min_install = -np.inf
max_install = 0.0
min_dist_x = 40.0
min_dist_y = 40.0
bidirection = True
rated_power_device = 1.0
yaw_angle = 0.0
cut_in = 1.0
cut_out = 5.0
op_threshold = 0.0

landing_point = (0.0, 0.0)

test_data = {
    "bathymetry.layers": strata,
    "corridor.landing_point": landing_point,
    "device.bidirection": bidirection,
    "device.turbine_hub_height": turbine_hub_height,
    "device.cut_in_velocity": cut_in,
    "device.cut_out_velocity": cut_out,
    "device.installation_depth_max": max_install,
    "device.installation_depth_min": min_install,
    "device.minimum_distance_x": min_dist_x,
    "device.minimum_distance_y": min_dist_y,
    "options.optimisation_threshold": op_threshold,
    "device.power_rating": rated_power_device,
    "device.turbine_diameter": rotor_diam,
    "device.turbine_interdistance": turbine_interdist,
    "device.turbine_performance": tidal_performance,
    "device.yaw": yaw_angle,
    "farm.blockage_ratio": blockage_ratio,
    "site.lease_boundary": lease_area,
    "project.main_direction": main_direction,
    "farm.nogo_areas": nogo_areas,
    "project.rated_power": rated_array_power,
    "farm.tidal_series": tidal_series_raw,
    "project.tidal_occurrence_nbins": n_bins,
    "farm.tidal_occurrence_point": tidal_point,
    "options.user_array_layout": user_array_layout,
    "options.user_array_option": user_array_option,
}

if __name__ == "__main__":
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)

    print("generate test data: {}".format(pkl_path))
