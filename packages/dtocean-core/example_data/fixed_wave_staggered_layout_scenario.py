# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os
import numpy as np
import pandas as pd

from datetime import datetime, timedelta

from dtocean_core.utils.moorings import get_moorings_tables

# Note that the electrical folder in the test_data directory should be
# placed in the same folder as this file
this_dir = os.path.dirname(os.path.realpath(__file__))
hydro_dir= os.path.join(this_dir, "rm3")
elec_dir = os.path.join(this_dir, "electrical")
moor_dir = os.path.join(this_dir, "moorings")
env_dir = os.path.join(this_dir, "environmental")


## CONSTANTS

gravity = 9.80665 #gravity
seaden = 1025.0 #sea water density
airden = 1.226 #air density

#cylinder drag coefficients
dragcoefcyl =  [[0.0, 0.0, 1e-5, 1e-2],
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
                [4e6, 0.67, 0.67, 1.08]]
                
#cylinder wake amplification factors
wakeampfactorcyl = [[0.0, 2.0, 2.0],
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
                    [60.0, 1.0, 1.0]]

#rectangular section wind drag coefficients
winddragcoefrect = [[4.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.6, 1.6],
                    [3.0, 1.1, 1.2, 1.25, 1.35, 1.4, 1.4, 1.4],
                    [2.0, 1.0, 1.05, 1.1, 1.15, 1.2, 1.2, 1.2],
                    [1.5, 0.95, 1.0, 1.05, 1.1, 1.15, 1.15, 1.15],
                    [1.0, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.4],
                    [0.6667, 0.8, 0.85, 0.9, 0.95, 1.0, 1.0, 1.0],
                    [0.5, 0.75, 0.75, 0.8, 0.85, 0.9, 0.9, 0.9],
                    [0.3333, 0.7, 0.75, 0.75, 0.75, 0.8, 0.8, 0.8],
                    [0.25, 0.7, 0.7, 0.75, 0.75, 0.75, 0.75, 0.75]]
                    
#rectangular section current drag coefficients
currentdragcoefrect =  [[10.0000, 1.88],
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
                        [0.2500, 1.15]]

#rectangular section wave drift coefficients
driftcoeffloatrect =   [[0.0, 0.0],
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
                        [1.5, 1.0]]

#rectangular section wave inertia coefficients
waveinertiacoefrect =  [[10.0, 2.23],
                        [5.0, 1.98],
                        [2.0, 1.7],
                        [1.0, 1.51],
                        [0.5, 1.36],
                        [0.2, 1.21],
                        [0.1, 1.14]]

## LEASE AREA
startx = 1000.
endx = 2000.
dx = 10.
numx = int(float(endx - startx) / dx) + 1

starty = 0.
endy = 2500.
dy = 10.
numy = int(float(endy - starty) / dy) + 1

x = np.linspace(startx, endx, numx)
y = np.linspace(starty, endy, numy)
nx = len(x)
ny = len(y)

# Bathymetry
X, Y = np.meshgrid(x,y)
Z = np.zeros(X.shape) - 80.
depths = Z.T[:, :, np.newaxis]

sediments = np.chararray((nx,ny,1), itemsize=20)
sediments[:] = "loose sand"
   
strata = {"values": {'depth': depths,
                     'sediment': sediments},
          "coords": [x, y, ["layer 1"]]}

# Soil characteristics
max_temp = 10.
max_soil_res = 10.
target_burial_depth = 10

# Polygons
lease_area = [(startx, starty),
              (endx, starty),
              (endx, endy),
              (startx, endy)]
              
#nogo_areas = [np.array([[50., 50.],[60., 50.],[60., 60.],[50., 60.]])]
nogo_areas = None

boundary_padding = 200.

# Wave time series
sample_size = 1000

dates = []
dt = datetime(2010, 12, 01)
step = timedelta(seconds=3600)
    
for _ in xrange(sample_size):
    dates.append(dt)
    dt += step
    
Te = np.random.rayleigh(6., size=sample_size)
Hm0 = np.random.rayleigh(4., size=sample_size)
direction = 360. * np.random.random(size=sample_size) - 180.

wave_series = {"DateTime": dates,
               "Te": Te,
               "Hm0": Hm0,
               "Dir": direction}
           
# SSH
point_SSH = 0.

# Tidal flow characteristics (moorings)
max_10year_current = 6.
max_10year_current_dir = 0.
current_profile = "1/7 Power Law" #current profile alternatives: "Uniform"
                                                               # "1/7 Power Law"
power_law_exponent = np.array([7.])

# Wave characterists
predominant_100year_wave_dir = 0.
max_100year_hs = 15.0
max_100year_tp = 25.0
max_100year_gamma = 1.

spectrum_type_farm = 'JONSWAP'
spectrum_gamma_farm = 3.3
spectrum_dir_spreading_farm = 0.

# Wind characteristics
mean_100_year_wind_speed = 2.0
mean_100_year_wind_dir = 0.0
max_100_year_gust_speed = 6.8
max_100_year_gust_dir = 0.0

# Water level characterists
max_50_year_water_level = 5.0 #water level maximum offset
min_50_year_water_level = 0.0 #water level minimum offset


## CABLE CORRIDOR

startx = 0.
endx = 1000.
dx = 10.
numx = int(float(endx - startx) / dx)

starty = 1000.
endy = 1500.
dy = 10.
numy = int(float(endy - starty) / dy) + 1

x = np.linspace(startx, endx, numx)
y = np.linspace(starty, endy, numy)
nx = len(x)
ny = len(y)

# Bathymetry
X, Y = np.meshgrid(x,y)
Z = np.zeros(X.shape) - 80.
depths = Z.T[:, :, np.newaxis]

sediments = np.chararray((nx,ny,1), itemsize=20)
sediments[:] = "loose sand"
   
export_strata = {"values": {'depth': depths,
                       'sediment': sediments},
                 "coords": [x, y, ["layer 1"]]}

# Soil characteristics                 
corridor_max_temp = 10.
corridor_max_soil_res = 10.
corridor_target_burial_depth = 20.

# Polygons
corridor_nogo_areas = None

# Tidal flow characteristics
corridor_10year_current = 6.
corridor_10year_current_dir = 0.

# Wave characterists
corridor_100year_wave_dir = 0.
                          

## SHORELINE
            
landing_point = (0., 1250.)
onshore_infrastructure_cost = 1000000.
            
# MACHINE

wave_data_directory = os.path.abspath(os.path.join(hydro_dir))


# Device characterists           
min_install = -np.inf
max_install = 0.
min_dist_x = 200.
min_dist_y = 200.
rated_power_device = 0.3
device_voltage= 10.
yaw_angle = 360.
connection = 'Wet-Mate'
footprint_radius = 20.
umbilical_connection = None
umbilical_safety = None

power_factor = 0.98
                
sys_prof = "Cylindrical"   #device profile options: "Cylindrical" "Rectangular"
sys_mass = 727.0 #device mass
sys_cog = [0.0, 0.0, 15.0] #device centre of gravity 
sys_vol = 1130. #device displaced volume
sys_height = 38.0 #device height
sys_width = 30.0 #device width
sys_length = 30.0 #device length
sys_draft = None #device draft
sys_dry_frontal = 0.0 #device dry frontal area
sys_dry_beam = 0.0 #device dry beam area
sys_wet_frontal = 240.0 #device wet frontal area
sys_wet_beam = 240.0 #device wet beam area
sys_rough = 0.9e-2 #device surface roughness

#predefined foundation type: Shallow, Gravity, Pile, Suction Caisson,
                           # Direct Embedment, Drag
prefound = None 

#foundation locations (from device origin)
found_loc = np.array([[-200.0,                0.0, 0.0],
                      [ 100.0,  100. * np.sqrt(3), 0.0],
                      [ 100.0, -100. * np.sqrt(3), 0.0]])
                      
# ARRAY LAYOUT

user_array_option = 'Staggered'

#pos = [(1250., 500.),
#       (1750., 500.),
#       (1500., 1250.),
#       (1250., 2000.),
#       (1750,  2000.)]
#       
#user_array_layout = np.array(pos)

main_direction = None
rated_array_power = 1.5


## ELECTRICAL NETWORK

# Farm
devices_per_string = 10
network_configuration = ["Radial"]
min_voltage = 15.
max_voltage = 30.
connector_type = "Wet-Mate"
collection_point_type = "Subsea"

# Corridor
corridor_voltage = 120.
number_of_export_cables = None

## FOUNDATIONS

found_safety = 1.5 #foundation safety factor
grout_safety  = 6.0 #grout safety factor
fab_cost = None # 1.0 #optional fabrication cost factor

## COMPONENT DATA

# Electrical
component_data_path = os.path.join(elec_dir, 'mock_db.xlsx')
xls_file = pd.ExcelFile(component_data_path, encoding = 'utf-8')
sheet_names = xls_file.sheet_names

static_cable = xls_file.parse(sheet_names[0])
dynamic_cable = xls_file.parse(sheet_names[1])
wet_mate_connectors = xls_file.parse(sheet_names[2])
dry_mate_connectors = xls_file.parse(sheet_names[3])
transformers = xls_file.parse(sheet_names[4])
collection_points = xls_file.parse(sheet_names[5])

collection_point_cog = {11: [0,0,0],
                        12: [0,0,0],
                        22: [0,0,0],
                        23: [0,0,0],
                        24: [0,0,0],
                        25: [0,0,0]
                        }
                        
collection_point_found = {11: [0,0,0],
                          12: [0,0,0],
                          22: [0,0,0],
                          23: [0,0,0],
                          24: [0,0,0],
                          25: [0,0,0]
                          }

compat_data_path = os.path.join(elec_dir,
                                'equipment_compatibility_matrix.xlsx')
xls_file = pd.ExcelFile(compat_data_path, encoding='utf-8')
sheet_names = xls_file.sheet_names

installation_soil_compatibility = xls_file.parse(sheet_names[0],
                                                 index_col=None)
installation_soil_compatibility.columns = ['Technique',
                                           'Loose Sand',
                                           'Medium Sand',
                                           'Dense Sand',
                                           'Very Soft Clay',
                                           'Soft Clay',
                                           'Firm Clay',
                                           'Stiff Clay',
                                           'Hard Glacial Till',
                                           'Cemented',
                                           'Soft Rock Coral',
                                           'Hard Rock',
                                           'Gravel Cobble']   
                                           
equipment_gradient_constraint = 14.

# Moorings and Foundations
compdict = eval(open(os.path.join(moor_dir, 'dummycompdb.txt')).read())
comp_tables = get_moorings_tables(compdict) #component database
                                             
cost_steel = 1.0 #steel cost
cost_grout = 0.1 #grout cost
cost_concrete = 0.11 #concrete cost
grout_strength = 125.0 #grout strength

## MATERIALS

# Foundations
steelden = 7750.0 #steel density
conden = 2400.0 #concrete density
groutden = 2450.0 #grout density

# Substrate
draincoh = 0.0 #drained soil cohesion
unsfang = 5.0 #undrained soil friction angle
dsfang = 35.0 #drained soil friction angle
soilweight = 9.4285e+03 #buoyant soil weight
relsoilden = 50.0 #relative soil density
undrained_soil_shear_strength_constant = 1.45e3
undrained_soil_shear_strength_dependent = 2e3 #undrained shear friction angle
soilsen = 3.0 #soil sensitivity
rockcomstr = 206843.0 #rock compressive strength

# default soil properties table
soilprops = pd.read_csv(os.path.join(moor_dir, 'soilprops.txt'),
                        sep='\t',
                        header=0,
                        index_col=False)

# buried line bearing capacity factors
line_bcf = [[20, 3],
            [25, 5], 
            [30, 8],
            [35, 12],
            [40, 22],
            [45, 36]]

#subgrade reaction coefficients
k1coeff = [[1, 100, 200],
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
           [20, 15, 16]]
           
#subgrade soil reaction coefficients cohesionless
subgradereaccoef = [[0.5, 4886048.0, 12893739.0, 24158795.0, 32573656.0],
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
                    [10.0, 678618.0, 2239439.0, 3868122.0, 5428943.0]]

#pile deflection coefficients
piledefcoef =  [[2.0, 4.65, 3.4],
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
                [5.0, 2.61, 1.7]]
                
#pile moment coefficients am
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
    [4.5, -0.076, 0.003, 0, 0, 0]
    ]
    
#pile moment coefficients bm
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
    [4.5, -0.102084, -0.001464, 0, 0, 0]
    ]

#pile limiting values non calcaeous soils
pilefricresnoncal = [[35, 30, 40, 95.761e3, 9576.051e3],
                     [30, 25, 20, 81.396e3, 4788.026e3],
                     [25, 20, 12, 67.032e3, 2872.815e3],
                     [20, 15, 8, 47.880e3, 1915.210e3]]
                     
#plate anchor holding capacity factors
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
    [13.0, 3.497500397, 5.991702643, 12.04338224, 24.34120734, 57.76787568]
    ]
    
# ENVIRONMENTAL INPUT


table_path = os.path.join(env_dir, "species_protected.csv")

protected_table = pd.read_csv(table_path, index_col=None)
name_map1 ={ "subclass or group" : "Subclass or Group",
                     "observed" : "Observed"}
protected_table = protected_table.rename(columns=name_map1)

table_path = os.path.join(env_dir, "species_receptors.csv")
receptors_table = pd.read_csv(table_path, index_col=None)
name_map2 ={ "subclass or group" : "Subclass or Group",
                     "observed" : "Observed",
                     "observed january" : "Observed January",
                     "observed february" : "Observed February",
                     "observed march" : "Observed March",
                     "observed april" : "Observed April",
                     "observed may" : "Observed May",
                     "observed june" : "Observed June",
                     "observed july" : "Observed July",
                     "observed august" : "Observed August",
                     "observed september" : "Observed September",
                     "observed october" : "Observed October",
                     "observed november" : "Observed November",
                     "observed december" : "Observed December"                     
                     }
                     
receptors_table = receptors_table.rename(columns=name_map2)

hydro_energy_modif_weight = "Gravel Cobble"

hydro_collision_risk_weight = "Sea Loch Entrance/ Devices In Parallel"

hydro_turbidity_risk_weight = None

hydro_underwater_noise_risk_weight = "Noise Device 100 - 150 dB re 1muPa"

hydro_reserve_effect_weight = "No Restriction"

hydro_reef_effect_weight = "Wave Design Vertical"

hydro_resting_place_weight = "Oscillating Bodies With Translation Part"

initial_turbidity =50 
hydro_measured_turbidity = 70

initial_noise =60 
hydro_measured_noise = 151
elec_measured_noise = 151
moor_measured_noise = 151

initial_elec_field = 60
elec_measured_elec_field  =1000
initial_magnetic_field =60
elec_measured_magnetic_field = 1000
initial_temeprature = 15
elec_measured_temperature = 18

fishery_restricted_area = 1000.


# SOLVER OPTIONS

op_threshold = 0.9


# LOAD VARIABLES

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
        "farm.collection_point_type": collection_point_type,
        "farm.connector_type": connector_type,
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
        "corridor.number_of_export_cables": number_of_export_cables,
        "project.export_voltage": corridor_voltage,
        "corridor.landing_point": landing_point,
        "corridor.nogo_areas": corridor_nogo_areas,
        "project.export_target_burial_depth": corridor_target_burial_depth,
        "device.wave_data_directory": wave_data_directory,
        "device.connector_type": connection,
        "device.installation_depth_max": max_install,
        "device.installation_depth_min": min_install,
        "device.minimum_distance_x": min_dist_x,
        "device.minimum_distance_y": min_dist_y,
        "device.constant_power_factor": power_factor,
        "device.power_rating": rated_power_device,
        "device.prescribed_footprint_radius": footprint_radius,
        "device.system_draft": sys_draft,
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
        "project.devices_per_string": devices_per_string,
        "farm.direction_of_max_surface_current":  max_10year_current_dir,
        "project.main_direction": main_direction,
        "farm.max_surface_current_10_year": max_10year_current,
        "project.network_configuration": network_configuration,
        "farm.nogo_areas": nogo_areas,
        "project.onshore_infrastructure_cost": onshore_infrastructure_cost,
#        "farm.point_sea_surface_height": point_SSH,
#        "farm.power_law_exponent": power_law_exponent,
        "project.rated_power": rated_array_power,
        "farm.spec_gamma": spectrum_gamma_farm,
        "farm.spec_spread": spectrum_dir_spreading_farm,
        "farm.spectrum_name": spectrum_type_farm,
        "project.target_burial_depth": target_burial_depth,
        "farm.wave_series": wave_series,
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
        "farm.wave_gamma_100_year": max_100year_gamma,
        
        "farm.protected_table" : protected_table,
        "farm.receptors_table" : receptors_table,
        "farm.hydro_energy_modif_weight" : hydro_energy_modif_weight,
        "farm.hydro_collision_risk_weight" : hydro_collision_risk_weight,
        "farm.hydro_turbidity_risk_weight" : hydro_turbidity_risk_weight,
        "device.hydro_underwater_noise_risk_weight" : hydro_underwater_noise_risk_weight,
        "farm.hydro_reserve_effect_weight" : hydro_reserve_effect_weight,
        "device.hydro_reef_effect_weight" : hydro_reef_effect_weight,
        "device.hydro_resting_place_weight" : hydro_resting_place_weight,
        "farm.initial_turbidity" : initial_turbidity,
        "project.hydro_measured_turbidity" : hydro_measured_turbidity,
        "farm.initial_noise" : initial_noise,
        "project.hydro_measured_noise" : hydro_measured_noise,
        "project.elec_measured_noise" : elec_measured_noise,
        "project.moor_measured_noise" : moor_measured_noise,
        "project.fishery_restricted_area" : fishery_restricted_area,     
        "farm.initial_elec_field" : initial_elec_field,
        "project.elec_measured_elec_field" : elec_measured_elec_field,
        "farm.initial_magnetic_field" : initial_magnetic_field,
        "project.elec_measured_magnetic_field" : elec_measured_magnetic_field,
        "farm.initial_temperature" : initial_temeprature,
        "project.elec_measured_temperature" : elec_measured_temperature,        
        
        "project.cost_of_concrete": cost_concrete,
        "project.cost_of_grout": cost_grout,
        "project.cost_of_steel": cost_steel,
        "options.optimisation_threshold": op_threshold,
        "options.boundary_padding" : boundary_padding,
#        "options.user_array_layout": user_array_layout,
        "options.user_array_option": user_array_option,
        "site.lease_boundary": lease_area,
        'component.foundations_anchor': comp_tables["drag anchor"],
        'component.foundations_pile': comp_tables["pile"],
        'component.foundations_anchor_sand': comp_tables["drag anchor sand"],
        'component.foundations_anchor_soft': comp_tables["drag anchor soft"]
        }
             
if __name__ == "__main__":
    
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)

