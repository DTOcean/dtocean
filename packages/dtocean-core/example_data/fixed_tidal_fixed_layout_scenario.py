# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os

import numpy as np
import pandas as pd
import utm
from scipy.stats import multivariate_normal, norm
from shapely.geometry import Point

from dtocean_core.utils.moorings import get_moorings_tables
from dtocean_core.utils.reliability import (
    compdict_from_mock,
    get_reliability_tables,
)

# Note that the electrical folder in the test_data directory should be
# placed in the same folder as this file
this_dir = os.path.dirname(os.path.realpath(__file__))
elec_dir = os.path.join(this_dir, "electrical")
moor_dir = os.path.join(this_dir, "moorings")
inst_dir = os.path.join(this_dir, "installation")
op_dir = os.path.join(this_dir, "operations")


### CONSTANTS

gravity = 9.80665  # gravity
seaden = 1025.0  # sea water density
airden = 1.226  # air density

# cylinder drag coefficients
dragcoefcyl = [
    [0.0, 0.0, 1e-5, 1e-2],
    [1e4, 1.2, 1.2, 1.15],
    [2e4, 1.2, 1.2, 1.05],
    [3e4, 1.2, 1.2, 0.87],
    [4e4, 1.2, 1.15, 0.82],
    [5e4, 1.2, 1.0, 0.8],
    [6e4, 1.2, 0.9, 0.8],
    [7e4, 1.2, 0.85, 0.83],
    [8e4, 1.2, 0.7, 0.9],
    [9e4, 1.2, 0.65, 0.94],
    [1e5, 1.2, 0.6, 0.95],
    [2e5, 1.2, 0.35, 1.02],
    [3e5, 1.15, 0.3, 1.03],
    [4e5, 0.95, 0.33, 1.05],
    [5e5, 0.6, 0.35, 1.06],
    [6e5, 0.35, 0.38, 1.07],
    [7e5, 0.29, 0.4, 1.07],
    [8e5, 0.31, 0.43, 1.08],
    [9e5, 0.33, 0.45, 1.08],
    [1e6, 0.35, 0.47, 1.08],
    [2e6, 0.54, 0.53, 1.08],
    [3e6, 0.62, 0.62, 1.08],
    [4e6, 0.67, 0.67, 1.08],
]

# cylinder wake amplification factors
wakeampfactorcyl = [
    [0.0, 2.0, 2.0],
    [5.0, 0.4, 0.8],
    [10.0, 0.78, 1.3],
    [15.0, 1.07, 1.4],
    [20.0, 1.25, 1.25],
    [25.0, 1.2, 1.2],
    [30.0, 1.18, 1.18],
    [35.0, 1.12, 1.12],
    [40.0, 1.1, 1.1],
    [45.0, 1.06, 1.06],
    [50.0, 1.03, 1.03],
    [55.0, 1.01, 1.01],
    [60.0, 1.0, 1.0],
]

# rectangular section wind drag coefficients
winddragcoefrect = [
    [4.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.6, 1.6],
    [3.0, 1.1, 1.2, 1.25, 1.35, 1.4, 1.4, 1.4],
    [2.0, 1.0, 1.05, 1.1, 1.15, 1.2, 1.2, 1.2],
    [1.5, 0.95, 1.0, 1.05, 1.1, 1.15, 1.15, 1.15],
    [1.0, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.4],
    [0.6667, 0.8, 0.85, 0.9, 0.95, 1.0, 1.0, 1.0],
    [0.5, 0.75, 0.75, 0.8, 0.85, 0.9, 0.9, 0.9],
    [0.3333, 0.7, 0.75, 0.75, 0.75, 0.8, 0.8, 0.8],
    [0.25, 0.7, 0.7, 0.75, 0.75, 0.75, 0.75, 0.75],
]

# rectangular section current drag coefficients
currentdragcoefrect = [
    [10.0000, 1.88],
    [5.0000, 1.95],
    [3.3333, 2.06],
    [2.5000, 2.24],
    [2.0000, 2.39],
    [1.6667, 2.6],
    [1.4286, 2.73],
    [1.2500, 2.5],
    [1.1111, 2.31],
    [1.0000, 2.19],
    [0.9091, 2.06],
    [0.8333, 1.95],
    [0.7692, 1.87],
    [0.7143, 1.8],
    [0.6667, 1.73],
    [0.6250, 1.67],
    [0.5882, 1.63],
    [0.5556, 1.58],
    [0.5263, 1.52],
    [0.5000, 1.49],
    [0.4762, 1.46],
    [0.4545, 1.44],
    [0.4348, 1.41],
    [0.4167, 1.37],
    [0.4000, 1.35],
    [0.3846, 1.32],
    [0.3704, 1.29],
    [0.3571, 1.26],
    [0.3448, 1.25],
    [0.3333, 1.23],
    [0.3226, 1.21],
    [0.3125, 1.2],
    [0.3030, 1.19],
    [0.2941, 1.18],
    [0.2857, 1.16],
    [0.2778, 1.15],
    [0.2703, 1.15],
    [0.2632, 1.15],
    [0.2564, 1.15],
    [0.2500, 1.15],
]

# rectangular section wave drift coefficients
driftcoeffloatrect = [
    [0.0, 0.0],
    [0.1, 0.02],
    [0.2, 0.06],
    [0.3, 0.15],
    [0.4, 0.28],
    [0.5, 0.44],
    [0.6, 0.60],
    [0.7, 0.74],
    [0.8, 0.84],
    [0.9, 0.91],
    [1.0, 0.94],
    [1.1, 0.97],
    [1.2, 0.98],
    [1.3, 0.99],
    [1.4, 1.0],
    [1.5, 1.0],
]

# rectangular section wave inertia coefficients
waveinertiacoefrect = [
    [10.0, 2.23],
    [5.0, 1.98],
    [2.0, 1.7],
    [1.0, 1.51],
    [0.5, 1.36],
    [0.2, 1.21],
    [0.1, 1.14],
]

### LEASE AREA

# Projection and extent
lease_utm_zone = (
    "+proj=utm +zone=30 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
)

startx = 101000.0
endx = 102000.0
dx = 10.0
numx = int(float(endx - startx) / dx) + 1

starty = 0.0
endy = 2500.0
dy = 10.0
numy = int(float(endy - starty) / dy) + 1

x = np.linspace(startx, endx, numx)
y = np.linspace(starty, endy, numy)
nx = len(x)
ny = len(y)

# Bathymetry
X, Y = np.meshgrid(x, y)
Z = np.zeros(X.shape) - 50.0
depths = Z.T[:, :, np.newaxis]

sediments = np.chararray((nx, ny, 1), itemsize=20)
sediments[:] = "loose sand"

strata = {
    "values": {"depth": depths, "sediment": sediments},
    "coords": [x, y, ["layer 1"]],
}

# Soil characteristics
max_temp = 10.0
max_soil_res = 10.0
target_burial_depth = 10

# Polygons
lease_area = [(startx, starty), (endx, starty), (endx, endy), (startx, endy)]

# nogo_areas = [np.array([[50., 50.],[60., 50.],[60., 60.],[50., 60.]])]
nogo_areas = None

# Tidal time series
n_bins = 6
time_points = 48
t = np.linspace(0, 1, time_points)

rv = norm()
time_sin = np.sin(np.linspace(0, 4 * np.pi, time_points))
time_scaled = time_sin * (1.0 / np.amax(time_sin))

xgrid, ygrid = np.meshgrid(x, y)
pos = np.dstack((xgrid, ygrid))

rv = multivariate_normal(
    [500.0, 150.0], [[max(x) * 5.0, max(y) * 2.0], [max(y) * 2.0, max(x) * 5.0]]
)

u_max = 0.0
v_max = 6.0
ssh_max = 1.0
TI = 0.1

grid_pdf = rv.pdf(pos).T

# u_scaled = grid_pdf * (u_max / np.amax(grid_pdf))
u_scaled = np.ones((nx, ny)) * u_max
v_scaled = np.ones((nx, ny)) * v_max
ssh_scaled = np.ones((nx, ny)) * ssh_max
# ssh_scaled = grid_pdf * (ssh_max / np.amax(grid_pdf))

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

# Tidal flow characteristics (hydro)
power_law_exponent = np.array([7.0])
blockage_ratio = 1.0

# Tidal flow characteristics (moorings)
max_10year_current = 6.0
max_10year_current_dir = 0.0
current_profile = "1/7 Power Law"  # current profile alternatives: "Uniform"
# "1/7 Power Law"

# Wave characterists
predominant_100year_wave_dir = 0.0
max_100year_hs = 0.5
max_100year_tp = 10.0
spectrum_gamma_farm = 3.3

# Wind characteristics
mean_100_year_wind_speed = 2.0
mean_100_year_wind_dir = 0.0
max_100_year_gust_speed = 6.8
max_100_year_gust_dir = 0.0

# Water level characterists
max_50_year_water_level = 5.0  # water level maximum offset
min_50_year_water_level = 0.0  # water level minimum offset

# Logistics
entry_point = (102000.0, 1250.0)

# Long Term Metocean Data
file_path = os.path.join(inst_dir, "inputs_user.xlsx")
xls_file = pd.ExcelFile(file_path)
metocean = xls_file.parse("metocean", index_col=0)

fmtStr = "%Y-%m-%d %H:%M:%S.%f"
datetime_index_dict = {
    "year": metocean["year"],
    "month": metocean["month"],
    "day": metocean["day"],
    "hour": metocean["hour"],
}

wave_series = metocean.loc[:, ["Hs", "Tp"]]
wave_series["DateTime"] = pd.to_datetime(datetime_index_dict, format=fmtStr)
# wave_series = wave_series.set_index(["DateTime"])

tidal_series = metocean.loc[:, ["Cs"]]
tidal_series["DateTime"] = pd.to_datetime(datetime_index_dict, format=fmtStr)
tidal_series = tidal_series.set_index(["DateTime"])
tidal_series = tidal_series.to_records(convert_datetime64=True)

wind_series = metocean.loc[:, ["Ws"]]
wind_series["DateTime"] = pd.to_datetime(datetime_index_dict, format=fmtStr)
wind_series = wind_series.set_index(["DateTime"])
wind_series = wind_series.to_records(convert_datetime64=True)

### CABLE CORRIDOR

startx = 100000.0
endx = 101000.0
dx = 10.0
numx = int(float(endx - startx) / dx)

starty = 1000.0
endy = 1500.0
dy = 10.0
numy = int(float(endy - starty) / dy) + 1

x = np.linspace(startx, endx, numx)
y = np.linspace(starty, endy, numy)
nx = len(x)
ny = len(y)

# Bathymetry
X, Y = np.meshgrid(x, y)
Z = np.zeros(X.shape) - 50.0
depths = Z.T[:, :, np.newaxis]

sediments = np.chararray((nx, ny, 1), itemsize=20)
sediments[:] = "loose sand"

export_strata = {
    "values": {"depth": depths, "sediment": sediments},
    "coords": [x, y, ["layer 1"]],
}

# Soil characteristics
corridor_max_temp = 10.0
corridor_max_soil_res = 10.0
corridor_target_burial_depth = 20.0

# Polygons
corridor_nogo_areas = None

# Tidal flow characteristics
corridor_10year_current = 6.0
corridor_10year_current_dir = 0.0

# Wave characterists
corridor_100year_wave_dir = 0.0

# Logistics
landfall_contruction_technique = "Open Cut Trenching"


### SHORELINE

landing_point = (100000.0, 1250.0)
onshore_infrastructure_cost = 1000000.0


### MACHINE

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

# Performance curves are matched to the same veloity abscissae
tidal_performance = {
    "Velocity": X,
    "Coefficient of Power": Cp,
    "Coefficient of Thrust": Ct,
}

# Device characterists
turbine_hub_height = 20.0
rotor_diam = 18.0
turbine_interdist = None
min_install = -np.inf
max_install = -40.0
min_dist_x = 40.0
min_dist_y = 40.0
bidirection = True
rated_power_device = 1.25
device_voltage = 11000.0
yaw_angle = 0.0
cut_in = 1.0
cut_out = 4.0
connection = "Wet-Mate"
footprint_radius = 20.0
device_draft = None
umbilical_connection = None
umbilical_safety = None

power_factor = 0.98

sys_prof = "Cylindrical"  # device profile options: "Cylindrical" "Rectangular"
sys_mass = 300.0e3  # device mass
sys_cog = [0.0, 0.0, 15.0]  # device centre of gravity
sys_vol = 148.44  # device displaced volume
sys_height = 21.0  # device height
sys_width = 3.0  # device width
sys_length = 3.0  # device length
sys_dry_frontal = 0.0  # device dry frontal area
sys_dry_beam = 0.0  # device dry beam area
sys_wet_frontal = 63.0  # device wet frontal area
sys_wet_beam = 63.0  # device wet beam area
sys_rough = 0.9e-2  # device surface roughness

# predefined foundation type: Shallow, Gravity, Pile, Suction Caisson,
# Direct Embedment, Drag
prefound = None

# foundation locations (from device origin)
found_loc = np.array(
    [
        [-10.0, -10.0, 0.0],
        [-10.0, 10.0, 0.0],
        [10.0, 10.0, 0.0],
        [10.0, -10.0, 0.0],
    ]
)

# Installation details
assembly_duration = 12
load_out_method = "Lift Away"
transportation_method = "Deck"
bollard_pull = None
connect_duration = 1
disconnect_duration = 1

installation_limit_Hs = 1.5
installation_limit_Tp = 10.0
installation_limit_Ws = 20.0
installation_limit_Cs = 1.0

device_failure_rates = {
    "Prime Mover": 0.5,
    "PTO": 0.25,
    "Control": 0.1,
    "Support Structure": 0.05,
}

book_path = os.path.join(op_dir, "device_requirements.xlsx")
device_onsite_requirements = pd.read_excel(book_path, sheet_name="On-Site")
device_replacement_requirements = pd.read_excel(
    book_path, sheet_name="Replacement"
)
device_inspections_requirements = pd.read_excel(
    book_path, sheet_name="Inspections"
)

book_path = os.path.join(op_dir, "device_parts.xlsx")
device_onsite_parts = pd.read_excel(book_path, sheet_name="On-Site")
device_replacement_parts = pd.read_excel(book_path, sheet_name="Replacement")

device_lead_times = {
    "Prime Mover": 120.0,
    "PTO": 96.0,
    "Control": 48.0,
    "Support Structure": 48.0,
}

device_costs = {
    "Prime Mover": 200000.0,
    "PTO": 150000.0,
    "Control": 10000.0,
    "Support Structure": 30000.0,
}


### SUB-SYSTEMS
file_path = os.path.join(inst_dir, "inputs_user.xlsx")
xls_file = pd.ExcelFile(file_path)
sub_device = xls_file.parse("sub_device")

### ARRAY LAYOUT

user_array_option = "User Defined Fixed"

pos = [
    (101250.0, 500.0),
    (101750.0, 500.0),
    (101500.0, 1250.0),
    (101250.0, 2000.0),
    (101750, 2000.0),
]

user_array_layout = np.array(pos)

main_direction = None
rated_array_power = 6.25


### ELECTRICAL NETWORK

# Farm
devices_per_string = 10
network_configuration = "Star"
min_voltage = 0.9
max_voltage = 1.0

book_path = os.path.join(op_dir, "electrical_requirements.xlsx")
electrical_onsite_requirements = pd.read_excel(book_path, sheet_name="On-Site")
electrical_inspections_requirements = pd.read_excel(
    book_path, sheet_name="Inspections"
)

book_path = os.path.join(op_dir, "electrical_parts.xlsx")
electrical_onsite_parts = pd.read_excel(book_path, sheet_name="On-Site")

electrical_lead_times = {
    "Inter-Array Cables": 48.0,
    "Substations": 120.0,
    "Export Cable": 240.0,
}

# Corridor
corridor_voltage = 33000.0


### FOUNDATIONS

found_safety = 1.5  # foundation safety factor
grout_safety = 6.0  # grout safety factor
fab_cost = None  # 1.0 #optional fabrication cost factor

book_path = os.path.join(op_dir, "moorings_requirements.xlsx")
moorings_onsite_requirements = pd.read_excel(book_path, sheet_name="On-Site")
moorings_inspections_requirements = pd.read_excel(
    book_path, sheet_name="Inspections"
)

book_path = os.path.join(op_dir, "moorings_parts.xlsx")
moorings_onsite_parts = pd.read_excel(book_path, sheet_name="On-Site")

moorings_lead_times = {"Foundations": 48.0}


### LOGISTICS

# Equipment
file_path = os.path.join(inst_dir, "logisticsDB_equipment_python.xlsx")
xls_file = pd.ExcelFile(file_path)
sheet_names = xls_file.sheet_names

equipment_rov = xls_file.parse(sheet_names[0])
equipment_divers = xls_file.parse(sheet_names[1])
equipment_cable_burial = xls_file.parse(sheet_names[2])
equipment_excavating = xls_file.parse(sheet_names[3])
equipment_mattress = xls_file.parse(sheet_names[4])
equipment_rock_filter_bags = xls_file.parse(sheet_names[5])
equipment_split_pipe = xls_file.parse(sheet_names[6])
equipment_hammer = xls_file.parse(sheet_names[7])
equipment_drilling_rigs = xls_file.parse(sheet_names[8])
equipment_vibro_driver = xls_file.parse(sheet_names[9])

# Ports
file_path = os.path.join(inst_dir, "logisticsDB_ports_python.xlsx")
xls_file = pd.ExcelFile(file_path)
ports = xls_file.parse()

port_names = ports["Name"]
port_x = ports.pop("UTM x")
port_y = ports.pop("UTM y")
port_utm = ports.pop("UTM zone")

port_points = []

for x, y, zone_str in zip(port_x, port_y, port_utm):
    zone_number_str, zone_letter = zone_str.split()
    lat, lon = utm.to_latlon(x, y, int(zone_number_str), zone_letter)
    point = Point(lon, lat)
    port_points.append(point)

port_locations = {name: point for name, point in zip(port_names, port_points)}

### VESSELS

file_path = os.path.join(inst_dir, "logisticsDB_vessel_python.xlsx")
xls_file = pd.ExcelFile(file_path)
helicopter_df = xls_file.parse(sheet_name="Helicopter")
ahts_df = xls_file.parse(sheet_name="AHTS")
multicat_df = xls_file.parse(sheet_name="Multicat")
barge_df = xls_file.parse(sheet_name="Barge")
crane_barge_df = xls_file.parse(sheet_name="Crane Barge")
crane_vessel_df = xls_file.parse(sheet_name="Crane Vessel")
csv_df = xls_file.parse(sheet_name="CSV")
ctv_df = xls_file.parse(sheet_name="CTV")
clb_df = xls_file.parse(sheet_name="CLB")
clv_df = xls_file.parse(sheet_name="CLV")
jackup_barge_df = xls_file.parse(sheet_name="Jackup Barge")
jackup_vssel_df = xls_file.parse(sheet_name="Jackup Vessel")
tugboat_df = xls_file.parse(sheet_name="Tugboat")

# Project data
comissioning_time = 6
cost_contingency = 10
port_percentage_cost = 10
project_start_date = pd.to_datetime("01:01:1992 12:30:00")
project_start_date = project_start_date.to_datetime()


# MAINTENANCE TYPE SELECTIONS

calendar_based_maintenance = True
condition_based_maintenance = False

calendar_maintenance_interval = {
    "Prime Mover": 5.0,
    "PTO": 1.0,
    "Control": 5.0,
    "Support Structure": 10.0,
    "Umbilical Cable": 10.0,
    "Inter-Array Cables": np.nan,
    "Substations": 10.0,
    "Export Cable": 10.0,
    "Foundations": 10.0,
    "Mooring Lines": 10.0,
}

condition_maintenance_soh = {
    "Prime Mover": 50.0,
    "PTO": 50.0,
    "Control": 50.0,
    "Support Structure": np.nan,
    "Umbilical Cable": 50.0,
    "Inter-Array Cables": np.nan,
    "Substations": 50.0,
    "Export Cable": 50.0,
    "Foundations": 50.0,
    "Mooring Lines": 50.0,
}

condition_maintenance_cost = {
    "Prime Mover": 30000.0,
    "PTO": 20000.0,
    "Control": 0.0,
    "Support Structure": 15000.0,
    "Umbilical Cable": np.nan,
    "Inter-Array Cables": 0.0,
    "Substations": 0.0,
    "Export Cable": 0.0,
    "Foundations": 15000.0,
    "Mooring Lines": np.nan,
}


### OPERATION TYPE SELECTIONS

operations_onsite_maintenance = {
    "Prime Mover": True,
    "PTO": True,
    "Control": True,
    "Support Structure": True,
    "Umbilical Cable": True,
    "Inter-Array Cables": True,
    "Substations": True,
    "Export Cable": True,
    "Foundations": True,
    "Mooring Lines": True,
}

operations_replacements = {
    "Prime Mover": True,
    "PTO": True,
    "Control": True,
    "Support Structure": True,
    "Umbilical Cable": True,
    "Mooring Lines": True,
}

operations_inspections = {
    "Prime Mover": True,
    "PTO": True,
    "Control": True,
    "Support Structure": True,
    "Umbilical Cable": True,
    "Inter-Array Cables": True,
    "Substations": True,
    "Export Cable": True,
    "Foundations": True,
    "Mooring Lines": True,
}

### OPERATION WEIGHTINGS

full_weightings = {"On-Site Maintenance": 4, "Replacement": 4, "Inspections": 2}

site_weightings = {"On-Site Maintenance": 4, "Inspections": 2}


### OPERATION COSTS

transit_cost_multiplier = 0.03
loading_cost_multiplier = 0.01

### PROJECT DATES

annual_maintenance_start = "April"
annual_maintenance_end = "October"
lifetime = 7.0  # 'project.lifetime',


### CREW SPECIFICATION

duration_shift = 8.0
helideck = False
number_crews_available = 8
number_crews_per_shift = 4
number_shifts_per_day = 3
wage_specialist_day = 200.0
wage_specialist_night = 300.0
wage_technician_day = 100.0
wage_technician_night = 150.0
workdays_summer = 7
workdays_winter = 7


### COMPONENT DATA

# Electrical
component_data_path = os.path.join(elec_dir, "mock_db.xlsx")
xls_file = pd.ExcelFile(component_data_path)
sheet_names = xls_file.sheet_names

static_cable = xls_file.parse(sheet_names[0])
dynamic_cable = xls_file.parse(sheet_names[1])
wet_mate_connectors = xls_file.parse(sheet_names[2])
dry_mate_connectors = xls_file.parse(sheet_names[3])
transformers = xls_file.parse(sheet_names[4])
collection_points = xls_file.parse(sheet_names[5])

collection_point_cog = {
    11: [0, 0, 0],
    12: [0, 0, 0],
    22: [0, 0, 0],
    23: [0, 0, 0],
    24: [0, 0, 0],
    25: [0, 0, 0],
}

collection_point_found = {
    11: [[0, 0, 0]],
    12: [[0, 0, 0]],
    22: [[0, 0, 0]],
    23: [[0, 0, 0]],
    24: [[0, 0, 0]],
    25: [[0, 0, 0]],
}

compat_data_path = os.path.join(elec_dir, "equipment_compatibility_matrix.xlsx")
xls_file = pd.ExcelFile(compat_data_path)
sheet_names = xls_file.sheet_names

installation_soil_compatibility = xls_file.parse(sheet_names[0], index_col=None)
installation_soil_compatibility.columns = [
    "Technique",
    "Loose Sand",
    "Medium Sand",
    "Dense Sand",
    "Very Soft Clay",
    "Soft Clay",
    "Firm Clay",
    "Stiff Clay",
    "Hard Glacial Till",
    "Cemented",
    "Soft Rock Coral",
    "Hard Rock",
    "Gravel Cobble",
]

equipment_gradient_constraint = 14.0

# Moorings and Foundations
compdict = eval(open(os.path.join(moor_dir, "dummycompdb.txt")).read())
comp_tables = get_moorings_tables(compdict)  # component database

cost_steel = 1.0  # steel cost
cost_grout = 0.1  # grout cost
cost_concrete = 0.11  # concrete cost
grout_strength = 125.0  # grout strength


### SAFETY FACTORS

port_sf_dict = {
    "Parameter": ["Terminal area [m^2]", "Terminal load bearing [t/m^2]"],
    "Safety Factor": [0.2, 0.2],
}
port_sf = pd.DataFrame(port_sf_dict)

vessel_sf_dict = {
    "Parameter": [
        "Deck space [m^2]",
        "Deck loading [t/m^2]",
        "Max. cargo [t]",
        "Crane capacity [t]",
        "Bollard pull [t]",
        "Turntable loading [t]",
        "Turntable inner diameter [m]",
        "AH winch rated pull [t]",
        "AH drum capacity [m]",
        "JackUp max payload [t]",
        "JackUp max water depth [m]",
    ],
    "Safety Factor": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0, 0.2, 0.2],
}
vessel_sf = pd.DataFrame(vessel_sf_dict)

rov_sf_dict = {
    "Parameter": ["Manipulator grip force [N]", "Depth rating [m]"],
    "Safety Factor": [0.2, 0.0],
}
rov_sf = pd.DataFrame(rov_sf_dict)

divers_sf_dict = {
    "Parameter": ["Max operating depth [m]"],
    "Safety Factor": [0.0],
}
divers_sf = pd.DataFrame(divers_sf_dict)

hammer_sf_dict = {
    "Parameter": ["Max pile diameter [mm]"],
    "Safety Factor": [0.2],
}
hammer_sf = pd.DataFrame(hammer_sf_dict)

vibro_driver_sf_dict = {
    "Parameter": [
        "Max pile diameter [mm]",
        "Max pile weight [t]",
        "Depth rating [m]",
    ],
    "Safety Factor": [0.2, 0.2, 0.0],
}
vibro_driver_sf = pd.DataFrame(vibro_driver_sf_dict)

cable_burial_sf_dict = {
    "Parameter": [
        "Jetting trench depth [m]",
        "Ploughing trench depth [m]",
        "Cutting trench depth [m]",
        "Max cable diameter [mm]",
        "Min cable bending radius [m]",
        "Max operating depth [m]",
    ],
    "Safety Factor": [0, 0, 0, 0, 0, 0],
}
cable_burial_sf = pd.DataFrame(cable_burial_sf_dict)

split_pipe_sf_dict = {
    "Parameter": ["Max cable size [mm]", "Min bending radius [m]"],
    "Safety Factor": [0.0, 0.0],
}
split_pipe_sf = pd.DataFrame(split_pipe_sf_dict)


#### RELIABILITY DATA

compdict = eval(open(os.path.join(moor_dir, "dummycompdb.txt")).read())

component_data_path = os.path.join(elec_dir, "mock_db.xlsx")
xls_file = pd.ExcelFile(component_data_path)
elec_dict = compdict_from_mock(xls_file)

compdict.update(elec_dict)

comp_tables_rel = get_reliability_tables(compdict)


### RATES

file_path = os.path.join(inst_dir, "equipment_perf_rates.xlsx")
xls_file = pd.ExcelFile(file_path)
equipment_penetration_rates = xls_file.parse("penet")

surface_laying_rate = 1000.0
split_pipe_laying_rate = 300.0
loading_rate = 450
grout_rate = 20
fuel_cost_rate = 1.5


### MATERIALS

# Foundations
steelden = 7750.0  # steel density
conden = 2400.0  # concrete density
groutden = 2450.0  # grout density

# Substrate
draincoh = 0.0  # drained soil cohesion
unsfang = 5.0  # undrained soil friction angle
dsfang = 35.0  # drained soil friction angle
soilweight = 9.4285e03  # buoyant soil weight
relsoilden = 50.0  # relative soil density
undrained_soil_shear_strength_constant = 1.45e3
undrained_soil_shear_strength_dependent = 2e3  # undrained shear friction angle
soilsen = 3.0  # soil sensitivity
rockcomstr = 206843.0  # rock compressive strength

# default soil properties table
soilprops = pd.read_csv(
    os.path.join(moor_dir, "soilprops.txt"), sep="\t", header=0, index_col=False
)

# buried line bearing capacity factors
line_bcf = [[20, 3], [25, 5], [30, 8], [35, 12], [40, 22], [45, 36]]

# subgrade reaction coefficients
k1coeff = [
    [1, 100, 200],
    [2, 57, 119],
    [3, 45.75, 94],
    [4, 34.5, 69],
    [5, 30.75, 56],
    [6, 27, 43],
    [7, 25.25, 38],
    [8, 23.5, 33],
    [9, 22.25, 29],
    [10, 21, 25],
    [11, 19.75, 22.5],
    [12, 18.5, 20],
    [13, 17.75, 19],
    [14, 17, 18],
    [15, 16.5, 17.5],
    [16, 16, 17],
    [17, 15.75, 16.75],
    [18, 15.5, 16.5],
    [19, 15.25, 16.25],
    [20, 15, 16],
]

# subgrade soil reaction coefficients cohesionless
subgradereaccoef = [
    [0.5, 4886048.0, 12893739.0, 24158795.0, 32573656.0],
    [1.0, 3800260.0, 10043544.0, 17644064.0, 24430242.0],
    [1.5, 3257366.0, 7464796.0, 14115251.0, 19272747.0],
    [2.0, 2850195.0, 6107561.0, 11672227.0, 16286828.0],
    [2.5, 2443024.0, 5428943.0, 10179268.0, 14658145.0],
    [3.0, 2171577.0, 5021772.0, 9229203.0, 13300910.0],
    [3.5, 2035854.0, 4750325.0, 8414861.0, 11943674.0],
    [4.0, 1764406.0, 4411016.0, 7736243.0, 10857885.0],
    [4.5, 1628683.0, 4139569.0, 7193349.0, 10043544.0],
    [5.0, 1560821.0, 3935983.0, 6650455.0, 9229203.0],
    [5.5, 1425097.0, 3732398.0, 6107561.0, 8686308.0],
    [6.0, 1357236.0, 3596675.0, 5768252.0, 8143414.0],
    [6.5, 1289374.0, 3393089.0, 5361081.0, 7736243.0],
    [7.0, 1221512.0, 3257366.0, 5021772.0, 7261211.0],
    [7.5, 1153650.0, 3053780.0, 4818187.0, 6854040.0],
    [8.0, 1085789.0, 2850195.0, 4614601.0, 6514731.0],
    [8.5, 1017927.0, 2646610.0, 4411016.0, 6243284.0],
    [9.0, 950065.0, 2443024.0, 4207431.0, 5971837.0],
    [9.5, 814341.0, 2307301.0, 4003845.0, 5700390.0],
    [10.0, 678618.0, 2239439.0, 3868122.0, 5428943.0],
]

# pile deflection coefficients
piledefcoef = [
    [2.0, 4.65, 3.4],
    [2.25, 3.51, 2.4],
    [2.5, 2.95, 2.05],
    [2.75, 2.77, 1.85],
    [3.0, 2.75, 1.8],
    [3.25, 2.73, 1.77],
    [3.5, 2.7, 1.75],
    [3.75, 2.67, 1.72],
    [4.0, 2.65, 1.7],
    [4.25, 2.637, 1.7],
    [4.5, 2.63, 1.7],
    [4.75, 2.62, 1.7],
    [5.0, 2.61, 1.7],
]

# pile moment coefficients am
pilemomcoefam = [
    [0, 0, 0, 0, 0, 0],
    [0.25, 0.255751417, 0.255752104, 0.25576445, 0.243605698, 0.227417941],
    [0.5, 0.475, 0.475, 0.475, 0.475, 0.422],
    [0.75, 0.642998583, 0.642997896, 0.64298555, 0.655144302, 0.534082059],
    [1, 0.745, 0.745, 0.745, 0.745, 0.514],
    [1.25, 0.773629251, 0.773631312, 0.773668349, 0.722567095, 0.345628822],
    [1.5, 0.751, 0.751, 0.751, 0.634, 0.147],
    [1.75, 0.700609413, 0.700601855, 0.700466055, 0.52883732, 0.036527654],
    [2, 0.622, 0.622, 0.622, 0.402, 0],
    [2.25, 0.513558099, 0.513586268, 0.51409243, 0.246333627, 0],
    [2.5, 0.393, 0.393, 0.393, 0.101, 0],
    [2.75, 0.280908193, 0.280803075, 0.277539226, 0.007453173, 0],
    [3, 0.19, 0.19, 0.179, -0.03, 0],
    [3.25, 0.126559129, 0.127576434, 0.104750666, 0, 0],
    [3.5, 0.079, 0.084, 0.054, 0, 0],
    [3.75, 0.03435529, 0.048391189, 0.023458111, 0, 0],
    [4, -0.008, 0.021, 0.008, 0, 0],
    [4.25, -0.04560529, 0.004858811, 0, 0, 0],
    [4.5, -0.076, 0.003, 0, 0, 0],
]

# pile moment coefficients bm
pilemomcoefbm = [
    [0, 1, 1, 1, 1, 1],
    [0.25, 0.987315551, 0.987332937, 0.98122151, 0.992090215, 0.969472347],
    [0.5, 0.970278, 0.970278, 0.970278, 0.970278, 0.938576],
    [0.75, 0.935494699, 0.935477313, 0.94555149, 0.925895035, 0.865467403],
    [1, 0.869573, 0.869573, 0.885424, 0.850273, 0.708303],
    [1.25, 0.764931527, 0.764983686, 0.777489904, 0.738243769, 0.452696415],
    [1.5, 0.637234, 0.637234, 0.646193, 0.59864, 0.19409],
    [1.75, 0.505730443, 0.505539192, 0.519353392, 0.44529864, 0.031270686],
    [2, 0.380771, 0.380771, 0.401447, 0.298073, -0.033425],
    [2.25, 0.269349077, 0.270061921, 0.292410027, 0.175437797, 0],
    [2.5, 0.173931, 0.173931, 0.197364, 0.084337, 0],
    [2.75, 0.094848998, 0.092188875, 0.121739999, 0, 0],
    [3, 0.028426, 0.028426, 0.067022, 0, 0],
    [3.25, -0.028406943, -0.014258045, 0.032568228, 0, 0],
    [3.5, -0.072277, -0.038507, 0.013181, 0, 0],
    [3.75, -0.099507477, -0.047911693, 0.003155466, 0, 0],
    [4, -0.111648, -0.044108, -0.000686, 0, 0],
    [4.25, -0.111554773, -0.028243057, 0, 0, 0],
    [4.5, -0.102084, -0.001464, 0, 0, 0],
]

# pile limiting values non calcaeous soils
pilefricresnoncal = [
    [35, 30, 40, 95.761e3, 9576.051e3],
    [30, 25, 20, 81.396e3, 4788.026e3],
    [25, 20, 12, 67.032e3, 2872.815e3],
    [20, 15, 8, 47.880e3, 1915.210e3],
]

# plate anchor holding capacity factors
hcfdrsoil = [
    [1.0, 1.638945315, 1.994698838, 2.307140604, 2.784, 3.396946397],
    [2.0, 2.250880594, 3.062312263, 3.879752818, 5.05497647, 6.628796215],
    [3.0, 2.707479408, 4.280253728, 5.806261102, 8.04851414, 11.22159355],
    [4.0, 3.042979832, 4.987799672, 7.670616585, 11.18864898, 17.28173317],
    [5.0, 3.093482117, 5.183423044, 9.04172475, 13.93390939, 23.58377747],
    [6.0, 3.143984402, 5.284457994, 10.04028578, 16.67916981, 30.0924043],
    [7.0, 3.194486687, 5.385492944, 10.32644242, 19.42443022, 37.24428049],
    [8.0, 3.244988972, 5.486527894, 10.61259905, 20.35658647, 42.81468093],
    [9.0, 3.295491257, 5.587562844, 10.89875569, 21.15351064, 47.52531117],
    [10.0, 3.345993542, 5.688597794, 11.18491233, 21.95043482, 50.76899705],
    [11.0, 3.396495827, 5.789632743, 11.47106897, 22.74735899, 53.1019566],
    [12.0, 3.446998112, 5.890667693, 11.75722561, 23.54428317, 55.43491614],
    [13.0, 3.497500397, 5.991702643, 12.04338224, 24.34120734, 57.76787568],
]


### SOLVER OPTIONS

op_threshold = 0.0
power_bin_width = 0.05
skip_phase = True


### LOAD VARIABLES

test_data = {
    "bathymetry.layers": strata,
    "constants.line_bearing_capacity_factor": line_bcf,
    "constants.pile_Am_moment_coefficient": pilemomcoefam,
    "constants.pile_Bm_moment_coefficient": pilemomcoefbm,
    "constants.pile_deflection_coefficients": piledefcoef,
    "constants.pile_skin_friction_end_bearing_capacity": pilefricresnoncal,
    "constants.soil_cohesionless_reaction_coefficient": subgradereaccoef,
    "constants.soil_cohesive_reaction_coefficient": k1coeff,
    "constants.soil_drained_holding_capacity_factor": hcfdrsoil,
    "farm.soil_sensitivity": soilsen,
    "constants.soilprops": soilprops,
    "constants.gravity": gravity,
    "constants.sea_water_density": seaden,
    "constants.air_density": airden,
    "constants.steel_density": steelden,
    "constants.concrete_density": conden,
    "constants.grout_density": groutden,
    "constants.grout_compressive_strength": grout_strength,
    "constants.cylinder_drag": dragcoefcyl,
    "constants.cylinder_wake_amplificiation": wakeampfactorcyl,
    "constants.rectangular_wind_drag": winddragcoefrect,
    "constants.rectangular_current_drag": currentdragcoefrect,
    "constants.rectangular_drift": driftcoeffloatrect,
    "constants.rectangular_wave_inertia": waveinertiacoefrect,
    "corridor.layers": export_strata,
    "component.collection_points": collection_points,
    "component.collection_point_cog": collection_point_cog,
    "component.collection_point_foundations": collection_point_found,
    "component.dry_mate_connectors": dry_mate_connectors,
    "component.dynamic_cable": dynamic_cable,
    "project.equipment_gradient_constraint": equipment_gradient_constraint,
    "component.installation_soil_compatibility": installation_soil_compatibility,
    "component.static_cable": static_cable,
    "component.transformers": transformers,
    "component.wet_mate_connectors": wet_mate_connectors,
    "project.fabrication_cost": fab_cost,
    "project.export_voltage": corridor_voltage,
    "corridor.landing_point": landing_point,
    "corridor.nogo_areas": corridor_nogo_areas,
    "project.export_target_burial_depth": corridor_target_burial_depth,
    "device.bidirection": bidirection,
    "device.connector_type": connection,
    "device.turbine_hub_height": turbine_hub_height,
    "device.cut_in_velocity": cut_in,
    "device.cut_out_velocity": cut_out,
    "device.installation_depth_max": max_install,
    "device.installation_depth_min": min_install,
    "device.minimum_distance_x": min_dist_x,
    "device.minimum_distance_y": min_dist_y,
    "device.constant_power_factor": power_factor,
    "device.power_rating": rated_power_device,
    "device.prescribed_footprint_radius": footprint_radius,
    "device.system_draft": device_draft,
    "device.turbine_diameter": rotor_diam,
    "device.turbine_interdistance": turbine_interdist,
    "device.turbine_performance": tidal_performance,
    "device.umbilical_connection_point": umbilical_connection,
    "project.umbilical_safety_factor": umbilical_safety,
    "device.voltage": device_voltage,
    "device.yaw": yaw_angle,
    "device.dry_beam_area": sys_dry_beam,
    "device.dry_frontal_area": sys_dry_frontal,
    "device.foundation_location": found_loc,
    "project.foundation_safety_factor": found_safety,
    "device.foundation_type": prefound,
    "device.system_centre_of_gravity": sys_cog,
    "device.system_displaced_volume": sys_vol,
    "device.system_height": sys_height,
    "device.system_length": sys_length,
    "device.system_mass": sys_mass,
    "device.system_profile": sys_prof,
    "device.system_roughness": sys_rough,
    "device.system_width": sys_width,
    "device.wet_beam_area": sys_wet_beam,
    "device.wet_frontal_area": sys_wet_frontal,
    "farm.blockage_ratio": blockage_ratio,
    "project.devices_per_string": devices_per_string,
    "farm.direction_of_max_surface_current": max_10year_current_dir,
    "project.main_direction": main_direction,
    "farm.max_surface_current_10_year": max_10year_current,
    "project.network_configuration": network_configuration,
    "farm.nogo_areas": nogo_areas,
    "project.onshore_infrastructure_cost": onshore_infrastructure_cost,
    #        "farm.power_law_exponent": power_law_exponent,
    "project.rated_power": rated_array_power,
    "farm.spec_gamma": spectrum_gamma_farm,
    "project.target_burial_depth": target_burial_depth,
    "project.tidal_occurrence_nbins": n_bins,
    "farm.tidal_occurrence_point": tidal_point,
    "farm.tidal_series": tidal_series_raw,
    "farm.wave_direction_100_year": predominant_100year_wave_dir,
    "farm.current_profile": current_profile,
    "project.grout_strength_safety_factor": grout_safety,
    "farm.max_gust_wind_direction_100_year": max_100_year_gust_dir,
    "farm.max_gust_wind_speed_100_year": max_100_year_gust_speed,
    "farm.max_hs_100_year": max_100year_hs,
    "farm.max_tp_100_year": max_100year_tp,
    "farm.max_water_level_50_year": max_50_year_water_level,
    "farm.mean_wind_direction_100_year": mean_100_year_wind_dir,
    "farm.mean_wind_speed_100_year": mean_100_year_wind_speed,
    "farm.min_water_level_50_year": min_50_year_water_level,
    "project.cost_of_concrete": cost_concrete,
    "project.cost_of_grout": cost_grout,
    "project.cost_of_steel": cost_steel,
    "options.optimisation_threshold": op_threshold,
    "options.user_array_layout": user_array_layout,
    "options.user_array_option": user_array_option,
    "site.lease_boundary": lease_area,
    "component.foundations_anchor": comp_tables["drag anchor"],
    "component.foundations_pile": comp_tables["pile"],
    "component.foundations_anchor_sand": comp_tables["drag anchor sand"],
    "component.foundations_anchor_soft": comp_tables["drag anchor soft"],
    "options.power_bin_width": power_bin_width,
    "component.rov": equipment_rov,
    "component.divers": equipment_divers,
    "component.cable_burial": equipment_cable_burial,
    "component.excavating": equipment_excavating,
    "component.mattress_installation": equipment_mattress,
    "component.rock_bags_installation": equipment_rock_filter_bags,
    "component.split_pipes_installation": equipment_split_pipe,
    "component.hammer": equipment_hammer,
    "component.drilling_rigs": equipment_drilling_rigs,
    "component.vibro_driver": equipment_vibro_driver,
    "component.vehicle_helicopter": helicopter_df,
    "component.vehicle_vessel_ahts": ahts_df,
    "component.vehicle_vessel_multicat": multicat_df,
    "component.vehicle_vessel_crane_barge": crane_barge_df,
    "component.vehicle_vessel_barge": barge_df,
    "component.vehicle_vessel_crane_vessel": crane_vessel_df,
    "component.vehicle_vessel_csv": csv_df,
    "component.vehicle_vessel_ctv": ctv_df,
    "component.vehicle_vessel_clb": clb_df,
    "component.vehicle_vessel_clv": clv_df,
    "component.vehicle_vessel_jackup_barge": jackup_barge_df,
    "component.vehicle_vessel_jackup_vessel": jackup_vssel_df,
    "component.vehicle_vessel_tugboat": tugboat_df,
    "component.ports": ports,
    "component.port_locations": port_locations,
    "project.port_safety_factors": port_sf,
    "project.vessel_safety_factors": vessel_sf,
    "project.rov_safety_factors": rov_sf,
    "project.divers_safety_factors": divers_sf,
    "project.hammer_safety_factors": hammer_sf,
    "project.vibro_driver_safety_factors": vibro_driver_sf,
    "project.cable_burial_safety_factors": cable_burial_sf,
    "project.split_pipe_safety_factors": split_pipe_sf,
    "component.equipment_penetration_rates": equipment_penetration_rates,
    "project.surface_laying_rate": surface_laying_rate,
    "project.split_pipe_laying_rate": split_pipe_laying_rate,
    "project.loading_rate": loading_rate,
    "project.grout_rate": grout_rate,
    "project.fuel_cost_rate": fuel_cost_rate,
    "project.landfall_contruction_technique": landfall_contruction_technique,
    "device.assembly_duration": assembly_duration,
    "device.bollard_pull": bollard_pull,
    "device.connect_duration": connect_duration,
    "device.disconnect_duration": disconnect_duration,
    "device.installation_limit_Cs": installation_limit_Cs,
    "device.installation_limit_Hs": installation_limit_Hs,
    "device.installation_limit_Tp": installation_limit_Tp,
    "device.installation_limit_Ws": installation_limit_Ws,
    "device.load_out_method": load_out_method,
    "device.transportation_method": transportation_method,
    "device.subsystem_installation": sub_device,
    "project.port_percentage_cost": port_percentage_cost,
    "project.commissioning_time": comissioning_time,
    "project.cost_contingency": cost_contingency,
    "project.start_date": project_start_date,
    "project.lease_area_entry_point": entry_point,
    "farm.wave_series_installation": wave_series,
    "farm.tidal_series_installation": tidal_series,
    "farm.wind_series_installation": wind_series,
    "site.projection": lease_utm_zone,
    "options.skip_phase": skip_phase,
    "project.calendar_based_maintenance": calendar_based_maintenance,
    "project.condition_based_maintenance": condition_based_maintenance,
    "project.duration_shift": duration_shift,
    "farm.helideck": helideck,
    "project.number_crews_available": number_crews_available,
    "project.number_crews_per_shift": number_crews_per_shift,
    "project.number_shifts_per_day": number_shifts_per_day,
    "project.wage_specialist_day": wage_specialist_day,
    "project.wage_specialist_night": wage_specialist_night,
    "project.wage_technician_day": wage_technician_day,
    "project.wage_technician_night": wage_technician_night,
    "project.workdays_summer": workdays_summer,
    "project.workdays_winter": workdays_winter,
    "project.energy_selling_price": 0.2,
    "options.annual_maintenance_start": annual_maintenance_start,
    "options.annual_maintenance_end": annual_maintenance_end,
    "project.lifetime": lifetime,
    "options.operations_onsite_maintenance": operations_onsite_maintenance,
    "options.operations_replacements": operations_replacements,
    "options.operations_inspections": operations_inspections,
    "device.prime_mover_operations_weighting": full_weightings,
    "device.pto_operations_weighting": full_weightings,
    "device.control_operations_weighting": full_weightings,
    "device.support_operations_weighting": full_weightings,
    "project.umbilical_operations_weighting": full_weightings,
    "project.array_cables_operations_weighting": site_weightings,
    "project.substations_operations_weighting": site_weightings,
    "project.export_cable_operations_weighting": site_weightings,
    "project.foundations_operations_weighting": site_weightings,
    "project.moorings_operations_weighting": full_weightings,
    "device.subsystem_failure_rates": device_failure_rates,
    "options.condition_maintenance_soh": condition_maintenance_soh,
    "options.calendar_maintenance_interval": calendar_maintenance_interval,
    "device.onsite_maintenance_requirements": device_onsite_requirements,
    "project.electrical_onsite_maintenance_requirements": electrical_onsite_requirements,
    "project.moorings_onsite_maintenance_requirements": moorings_onsite_requirements,
    "device.replacement_requirements": device_replacement_requirements,
    "project.electrical_replacement_requirements": None,
    "project.moorings_replacement_requirements": None,
    "device.inspections_requirements": device_inspections_requirements,
    "project.electrical_inspections_requirements": electrical_inspections_requirements,
    "project.moorings_inspections_requirements": moorings_inspections_requirements,
    "device.onsite_maintenance_parts": device_onsite_parts,
    "project.electrical_onsite_maintenance_parts": electrical_onsite_parts,
    "project.moorings_onsite_maintenance_parts": moorings_onsite_parts,
    "device.replacement_parts": device_replacement_parts,
    "project.electrical_replacement_parts": None,
    "project.moorings_replacement_parts": None,
    "device.subsystem_lead_times": device_lead_times,
    "project.electrical_subsystem_lead_times": electrical_lead_times,
    "project.moorings_subsystem_lead_times": moorings_lead_times,
    "device.subsystem_costs": device_costs,
    "options.subsystem_monitering_costs": condition_maintenance_cost,
    "options.transit_cost_multiplier": transit_cost_multiplier,
    "options.loading_cost_multiplier": loading_cost_multiplier,
    "component.moorings_chain_NCFR": comp_tables_rel["chain NCFR"],
    "component.moorings_chain_CFR": comp_tables_rel["chain CFR"],
    "component.moorings_forerunner_NCFR": comp_tables_rel["forerunner NCFR"],
    "component.moorings_forerunner_CFR": comp_tables_rel["forerunner CFR"],
    "component.moorings_shackle_NCFR": comp_tables_rel["shackle NCFR"],
    "component.moorings_shackle_CFR": comp_tables_rel["shackle CFR"],
    "component.moorings_swivel_NCFR": comp_tables_rel["swivel NCFR"],
    "component.moorings_swivel_CFR": comp_tables_rel["swivel CFR"],
    "component.foundations_anchor_NCFR": comp_tables_rel["anchor NCFR"],
    "component.foundations_anchor_CFR": comp_tables_rel["anchor CFR"],
    "component.foundations_pile_NCFR": comp_tables_rel["pile NCFR"],
    "component.foundations_pile_CFR": comp_tables_rel["pile CFR"],
    "component.moorings_rope_NCFR": comp_tables_rel["rope NCFR"],
    "component.moorings_rope_CFR": comp_tables_rel["rope CFR"],
    "component.static_cable_NCFR": comp_tables_rel["static_cable NCFR"],
    "component.static_cable_CFR": comp_tables_rel["static_cable CFR"],
    "component.dynamic_cable_NCFR": comp_tables_rel["dynamic_cable NCFR"],
    "component.dynamic_cable_CFR": comp_tables_rel["dynamic_cable CFR"],
    "component.wet_mate_connectors_NCFR": comp_tables_rel["wet_mate NCFR"],
    "component.wet_mate_connectors_CFR": comp_tables_rel["wet_mate CFR"],
    "component.dry_mate_connectors_NCFR": comp_tables_rel["dry_mate NCFR"],
    "component.dry_mate_connectors_CFR": comp_tables_rel["dry_mate CFR"],
    "component.transformers_NCFR": comp_tables_rel["transformer NCFR"],
    "component.transformers_CFR": comp_tables_rel["transformer CFR"],
    "component.collection_points_NCFR": comp_tables_rel[
        "collection_point NCFR"
    ],
    "component.collection_points_CFR": comp_tables_rel["collection_point CFR"],
}

if __name__ == "__main__":
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)

    print("generate test data: {}".format(pkl_path))

    print("generate test data: {}".format(pkl_path))
