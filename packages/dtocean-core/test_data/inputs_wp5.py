# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 11:49:00 2016

@author: acollin
"""

import os
import datetime
from collections import Counter
from dateutil.parser import parse

import utm
import numpy as np
import pandas as pd
from shapely.geometry import Point

this_dir = os.path.dirname(os.path.realpath(__file__))
installation_dir = os.path.join(this_dir, "installation")
elec_dir = os.path.join(this_dir, "electrical")

### Equipment
file_path = os.path.join(installation_dir, 'logisticsDB_equipment_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
sheet_names = xls_file.sheet_names

equipment_rov = xls_file.parse("rov")
equipment_divers = xls_file.parse("divers")
equipment_cable_burial = xls_file.parse("cable_burial")
equipment_excavating = xls_file.parse("excavating")
equipment_mattress = xls_file.parse("mattress")
equipment_rock_filter_bags = xls_file.parse("rock_filter_bags")
equipment_split_pipe = xls_file.parse("split_pipe")
equipment_hammer = xls_file.parse("hammer")
equipment_drilling_rigs = xls_file.parse("drilling_rigs")
equipment_vibro_driver = xls_file.parse("vibro_driver")

# OLC updates

hs_olc_names = [
             "Vessel Positioning + Connection to cable pull-head + Cable float-out + Cable lay into pre-excavated trench",
             "Vessel positioning + Connection to cable pull-head + Cable float-out + Cable pull-in through HDD conduit",
             "Deploy of Cable Burial Tool",
             "Recover cable burial tool",
             "Cable lay and burial through cable route",
             "Cable lay through cable route",
             "Cable lay through open trench",
             "Cable lay with split pipes",
             "Cable lay with buoyancy modules",
             "Conduct dry-mate connection on deck",
             "Conduct splice connection on deck",
             "Connect to guide wire + Lower cable and connection equip + Perform wet-mate connect + Recover connection equip",
             "J-tube entrance inspection + Guide wire connection + Cable lay + Cable pull + Cable connection",
             "Lower cable-end to the seabed",
             "Lift cable-end from seabed",
             "Lower collection point to the seabed",
             "Lift top-side platform",
             "Connect top-side platform to the support structure",
             "Lift and overboard concrete mattress + Lower concrete mattress to seabed + Position and release concrete mattress + Recover installation frame",
             "Lift and overboard rock filter bag + Lower rock filter bag to seabed + Position and release concrete mattress"]
    
hs_olc_values = [0.75,
                 0.75,
                 1.75,
                 1.75,
                 1.75,
                 1.75,
                 1.75,
                 1.75,
                 1.75,
                 2.,
                 2.,
                 2.25,
                 2.,
                 2.,
                 1.5,
                 2.,
                 2.,
                 2.,
                 2.,
                 2.]

hs_olc_dict = {k: v for k, v in zip(hs_olc_names, hs_olc_values)}
    
tp_olc_dict = {"Seafloor & equipment preparation": 15.}
ws_olc_dict = {"Seafloor & equipment preparation": 15.}
cs_olc_dict = {"Seafloor & equipment preparation": 1.5}


### Ports
file_path = os.path.join(installation_dir, 'logisticsDB_ports_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
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

### Vessels
file_path = os.path.join(installation_dir, 'logisticsDB_vessel_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
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

### Export
file_path = os.path.join(installation_dir, 'export_area_30.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
sheet_names = xls_file.sheet_names
lease_bathymetry = xls_file.parse(sheet_names[0])

layers = [1]

Z = np.array([lease_bathymetry["layer 1 start"]]).T
            
sediment = np.array([lease_bathymetry["layer 1 type"]]).T

x_max = lease_bathymetry.max()["x"]
y_max = lease_bathymetry.max()["y"]
x_min = lease_bathymetry.min()["x"]
y_min = lease_bathymetry.min()["y"]

num_x = (lease_bathymetry.max()["i"]-lease_bathymetry.min()["i"])+1
num_y = (lease_bathymetry.max()["j"]-lease_bathymetry.min()["j"])+1

x= np.linspace(x_min , x_max , num_x)
y = np.linspace(y_min , y_max , num_y)

depth_layers = []
sediment_layers = []

for z in layers:
    
    depths = []
    sediments = []
    
    for y_count in y:
        
        d = []
        s = []
        
        for x_count in x:
            
            point_df = lease_bathymetry[(lease_bathymetry["x"] == x_count) &
                                        (lease_bathymetry["y"] == y_count)
                                        ].index[0]
            
            if Z[point_df,z-1] == "None":
                Z[point_df,z-1] = np.nan
                
            d.append(Z[point_df,z-1])
            s.append(sediment[point_df,z-1])
                
        depths.append(d)
        sediments.append(s)
        
    depth_layers.append(depths)
    sediment_layers.append(sediments)
    
depth_array = np.swapaxes(np.array(depth_layers, dtype=float), 0, 2)

sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2)

layer_names = ["layer {}".format(x_layers) for x_layers in layers]

export_strata = {"values": {"depth": depth_array,
                            'sediment': sediment_array},
                "coords": [x, y, layer_names]}


### Site
file_path = os.path.join(installation_dir, 'lease_area_30.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
sheet_names = xls_file.sheet_names
lease_bathymetry = xls_file.parse(sheet_names[0])

layers = [1]

Z = np.array([lease_bathymetry["layer 1 start"]]).T
            
sediment = np.array([lease_bathymetry["layer 1 type"]]).T

x_max = lease_bathymetry.max()["x"]
y_max = lease_bathymetry.max()["y"]
x_min = lease_bathymetry.min()["x"]
y_min = lease_bathymetry.min()["y"]

num_x = (lease_bathymetry.max()["i"]-lease_bathymetry.min()["i"])+1
num_y = (lease_bathymetry.max()["j"]-lease_bathymetry.min()["j"])+1

x= np.linspace(x_min , x_max , num_x)
y = np.linspace(y_min , y_max , num_y)

depth_layers = []
sediment_layers = []

for z in layers:
    
    depths = []
    sediments = []
    
    for y_count in y:
        
        d = []
        s = []
        
        for x_count in x:
            
            point_df = lease_bathymetry[(lease_bathymetry["x"] == x_count) &
                                        (lease_bathymetry["y"] == y_count)
                                        ].index[0]
            
            if Z[point_df,z-1] == "None":
                Z[point_df,z-1] = np.nan
                
            d.append(Z[point_df,z-1])
            s.append(sediment[point_df,z-1])
                
        depths.append(d)
        sediments.append(s)
        
    depth_layers.append(depths)
    sediment_layers.append(sediments)
    
depth_array = np.swapaxes(np.array(depth_layers, dtype=float), 0, 2)

sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2)

layer_names = ["layer {}".format(x_layers) for x_layers in layers]

strata = {"values": {"depth": depth_array,
                     'sediment': sediment_array},
          "coords": [x, y, layer_names]}

lease_utm_zone = \
    "+proj=utm +zone=30 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

### Metocean
file_path = os.path.join(installation_dir, 'inputs_user.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
metocean = xls_file.parse('metocean', index_col = 0)

date_index = metocean[['year',
                       'month',
                       'day',
                       'hour']].apply(lambda s: datetime.datetime(*s), axis=1)


wave_series = metocean.loc[:, ['Hs', 'Tp']]
wave_series['DateTime'] = date_index.copy()

tidal_series = metocean.loc[:, ['Cs']]
tidal_series['DateTime'] = date_index.copy()
tidal_series = tidal_series.set_index(["DateTime"])
tidal_series = tidal_series.to_records(convert_datetime64=True)
tidal_series = [(x, float(y)) for x, y in tidal_series]

wind_series = metocean.loc[:, ['Ws']]
wind_series['DateTime'] = date_index.copy()
wind_series = wind_series.set_index(["DateTime"])
wind_series = wind_series.to_records(convert_datetime64=True)
wind_series = [(x, float(y)) for x, y in wind_series]

### Device
device = xls_file.parse('device', index_col = 0)
device = device.apply(pd.to_numeric, errors='ignore')

system_type = device['type'].values.item()
system_length = float(device['length'].values.item())
system_width = float(device['width'].values.item())
system_height = float(device['height'].values.item())
system_mass = float(device['dry mass'].values.item())
assembly_duration = float(device['assembly duration'].values.item())
load_out_method = device['load out'].values.item()
transportation_method = device['transportation method'].values.item()
bollard_pull = float(device['bollard pull'].values.item())
connect_duration = float(device['connect duration'].values.item())
disconnect_duration = float(device['disconnect duration'].values.item())

start_date_str = device['Project start date'].values.item()
project_start_date = parse(start_date_str)
#sub_systems = device['sub system list'].values.item()

### Subdevice
sub_device = xls_file.parse('sub_device')

### Landfall
landfall = "Open Cut Trenching"

### Rates
file_path = os.path.join(installation_dir, 'equipment_perf_rates.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')

equipment_penetration_rates = xls_file.parse('penet')
installation_soil_compatibility = xls_file.parse('laying')
temp_other = xls_file.parse('other')

surface_laying_rate = temp_other[temp_other.index ==
    'Surface laying [m/h]'].values[0][0]
split_pipe_laying_rate = temp_other[temp_other.index ==
    'Installation of iron cast split pipes [m/h]'].values[0][0]
loading_rate = temp_other[temp_other.index ==
    'Loading rate [m/h]'].values[0][0]
grout_rate = temp_other[temp_other.index ==
    'Grout rate [m3/h]'].values[0][0]
fuel_cost_rate = temp_other[temp_other.index ==
    'Fuel cost rate [EUR/l]'].values[0][0]
port_percentage_cost = temp_other[temp_other.index ==
    'Port percentual cost [%]'].values[0][0]
comissioning_time = temp_other[temp_other.index ==
    'Comissioning time [weeks]'].values[0][0]
cost_contingency = temp_other[temp_other.index ==
    'Cost Contingency [%]'].values[0][0]

### Safety factors
port_sf_dict = {"Parameter": ["Terminal area [m^2]",
                              "Terminal load bearing [t/m^2]"],
                "Safety Factor": [0.2, 0.2]
                }
port_sf = pd.DataFrame(port_sf_dict)

vessel_sf_dict = {"Parameter":  ['Deck space [m^2]',
                                 'Deck loading [t/m^2]',
                                 'Max. cargo [t]',
                                 'Crane capacity [t]',
                                 'Bollard pull [t]',
                                 'Turntable loading [t]',
                                 'Turntable inner diameter [m]',
                                 'AH winch rated pull [t]',
                                 'AH drum capacity [m]',
                                 'JackUp max payload [t]',
                                 'JackUp max water depth [m]'],
                "Safety Factor": [0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.2,
                                  0.0,
                                  0.0,
                                  0.2,
                                  0.2]
                }
vessel_sf = pd.DataFrame(vessel_sf_dict)

rov_sf_dict = {"Parameter": ["Manipulator grip force [N]", "Depth rating [m]"],
               "Safety Factor": [0.2, 0.]}
rov_sf = pd.DataFrame(rov_sf_dict)

divers_sf_dict = {"Parameter": ["Max operating depth [m]"],
                  "Safety Factor": [0.]}
divers_sf = pd.DataFrame(divers_sf_dict)

hammer_sf_dict = {"Parameter": ["Max pile diameter [mm]"],
                  "Safety Factor": [0.2]}
hammer_sf = pd.DataFrame(hammer_sf_dict)

vibro_driver_sf_dict = {"Parameter": ['Max pile diameter [mm]',
                                      'Max pile weight [t]',
                                      'Depth rating [m]'],
                        "Safety Factor": [0.2, 0.2, 0.]}
vibro_driver_sf = pd.DataFrame(vibro_driver_sf_dict)

cable_burial_sf_dict = {"Parameter": ['Jetting trench depth [m]',
                                      'Ploughing trench depth [m]',
                                      'Cutting trench depth [m]',
                                      'Max cable diameter [mm]',
                                      'Min cable bending radius [m]',
                                      'Max operating depth [m]'],
                        "Safety Factor": [0, 0, 0, 0, 0, 0]}
cable_burial_sf = pd.DataFrame(cable_burial_sf_dict)

split_pipe_sf_dict = {"Parameter": ['Max cable size [mm]',
                                    'Min bending radius [m]'],
                      "Safety Factor": [0., 0.]}
split_pipe_sf = pd.DataFrame(split_pipe_sf_dict)


### Configuration options

# lease area entry point
file_path = os.path.join(installation_dir, 'inputs_user.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
entry_point = xls_file.parse('entry_point', index_col = 0)

x = entry_point.loc[:, 'x coord'].item()
y = entry_point.loc[:, 'y coord'].item()

entry_point_shapely = Point(x,y)

### Hydrodynamic
layout_dict = {'device001': [587850.,6650550.],
               'device002': [587850.,6650700.]}

#for _, device in layout.iterrows():
#
#    layout_dict[device['device']] = (device['x coord'], device['y coord'], 0)

### Electrical
tool = 'Jetting'

electrical_network = {
 'nodes': {'array': {'Export cable': {'marker': [[0, 1]],
                                      'quantity': Counter({"6": 1, "17": 1})},
                     'Substation': {'marker': [[2]],
                                    'quantity': Counter({"12": 1})}},
           'device001': {'marker': [[35, 8, 9, 32, 33]],
                         'quantity': Counter({"2": 1, "6": 3, 'id743': 1})},
           'device002': {'marker': [[36, 6, 7, 73, 34]],
                         'quantity': Counter({"2": 1, "6": 3, 'id743': 1})}},
 'topology': {'array': {'Export cable': [["17", "6"]],
                        'Substation': [["12"]],
                        'layout': [['device002',
                                    'device001']]},
              'device001': {'Elec sub-system': [["6", "2", "6", 'id743', "6"]]},
              'device002': {'Elec sub-system': [["6", "2", "6", 'id743', "6"]]}}}


electrical_components_dict = {   'Installation Type': {0: 'wet-mate',
                                                       2: 'wet-mate',
                                                       3: 'wet-mate',
                                                       6: 'export',
                                                       8: 'array',
                                                       9: 'array',
                                                       11: 'substation',
                                                       12: 'umbilical',
                                                       13: 'umbilical',
                                                       14: 'wet-mate',
                                                       15: 'wet-mate',
                                                       16: 'wet-mate',
                                                       17: 'wet-mate',},
                                 'Key Identifier': {0: 6,
                                                    2: 6,
                                                    3: 6,
                                                    6: 17,
                                                    8: 2,
                                                    9: 2,
                                                    11: 12,
                                                    12: 'id743',
                                                    13: 'id743',
                                                    14: 6,
                                                    15: 6,
                                                    16: 6,
                                                    17: 6},
                                 'Marker': {0: 1,
                                            2: 7,
                                            3: 9,
                                            6: 0,
                                            8: 6,
                                            9: 8,
                                            11: 2,
                                            12: 32,
                                            13: 73,
                                            14: 33,
                                            15: 34,
                                            16: 35,
                                            17: 36},
                                            
                                 'Quantity': {0: 1.0,
                                              2: 1.0,
                                              3: 1.0,
                                              6: 688.2842712474619,
                                              8: 150.0,
                                              9: 150.0,
                                              11: 1.0,
                                              12: 932.,
                                              13: 312.,
                                              14: 1.,
                                              15: 1.,
                                              16: 1.,
                                              17: 1.},
                                              
                                 'UTM X': {0: 587770.0,
                                           2: 587850.0,
                                           3: 587850.0,
                                           6: 'None',
                                           8: 'None',
                                           9: 'None',
                                           11: 587770.0,
                                           12: 'None',
                                           13: 'None',
                                           14: 587850.0,
                                           15: 587850.0,
                                           16: 587850.0,
                                           17: 587850.0,},
                                 'UTM Y': {0: 6650820.0,
                                           2: 6650700.0,
                                           3: 6650550.0,
                                           6: 'None',
                                           8: 'None',
                                           9: 'None',
                                           11: 6650820.0,
                                           12: 'None',
                                           13: 'None',
                                           14: 587850.0,
                                           15: 587850.0,
                                           16: 587850.0,
                                           17: 587850.0,}}

electrical_components = pd.DataFrame(electrical_components_dict)

cable_routes_dict = {'Burial Depth': {
                                      13: 1.0,
                                      14: 1.0,
                                      15: 1.0,
                                      16: 1.0,
                                      17: 1.0,
                                      18: 1.0,
                                      19: 1.0,
                                      20: 1.0,
                                      21: 1.0,
                                      22: 1.0,
                                      23: 1.0,
                                      24: 1.0,
                                      25: 1.0,
                                      26: 1.0,
                                      27: 1.0,
                                      28: 1.0,
                                      29: 1.0,
                                      30: 1.0,
                                      31: 1.0,
                                      32: 1.0,
                                      33: 1.0,
                                      34: 1.0,
                                      35: 1.0,
                                      36: 1.0,
                                      37: 1.0,
                                      38: 1.0,
                                      39: 1.0,
                                      40: 1.0,
                                      41: 1.0,
                                      42: 1.0,
                                      43: 1.0,
                                      44: 1.0,
                                      
                                      61: 2.0,
                                      62: 2.0,
                                      63: 2.0,
                                      64: 2.0,
                                      65: 2.0,
                                      66: 2.0,
                                      67: 2.0,
                                      68: 2.0,
                                      69: 2.0,
                                      70: 2.0,
                                      71: 2.0,
                                      72: 2.0,
                                      73: 2.0,
                                      74: 2.0,
                                      75: 2.0,
                                      76: 2.0,
                                      77: 2.0,
                                      78: 2.0,
                                      79: 2.0,
                                      80: 2.0,
                                      81: 2.0,
                                      82: 2.0,
                                      83: 2.0,
                                      84: 2.0,
                                      85: 2.0,
                                      86: 2.0,
                                      87: 2.0,
                                      88: 2.0,
                                      89: 2.0,
                                      90: 2.0,
                                      91: 2.0,
                                      92: 2.0,
                                      93: 2.0,
                                      94: 2.0,
                                      95: 2.0,
                                      96: 2.0,
                                      97: 2.0,
                                      98: 2.0,
                                      99: 2.0,
                                      100: 2.0,
                                      101: 2.0,
                                      102: 2.0,
                                      103: 2.0,
                                      104: 2.0,
                                      105: 2.0,
                                      106: 2.0,
                                      107: 2.0,
                                      108: 2.0,
                                      109: 2.0,
                                      110: 2.0,
                                      111: 2.0,
                                      112: 2.0,
                                      113: 2.0,
                                      114: 2.0,
                                      115: 2.0,
                                      116: 2.0,
                                      117: 2.0,
                                      118: 2.0,
                                      119: 2.0,
                                      120: 2.0,
                                      121: 2.0,
                                      122: 2.0,
                                      123: 2.0,
                                      124: 2.0,
                                      125: 2.0,
                                      126: 2.0,
                                      127: 2.0,
                                      128: 2.0,
                                      129: 2.0},
                     'Key Identifier': {
                                        13: 2,
                                        14: 2,
                                        15: 2,
                                        16: 2,
                                        17: 2,
                                        18: 2,
                                        19: 2,
                                        20: 2,
                                        21: 2,
                                        22: 2,
                                        23: 2,
                                        24: 2,
                                        25: 2,
                                        26: 2,
                                        27: 2,
                                        28: 2,
                                        29: 2,
                                        30: 2,
                                        31: 2,
                                        32: 2,
                                        33: 2,
                                        34: 2,
                                        35: 2,
                                        36: 2,
                                        37: 2,
                                        38: 2,
                                        39: 2,
                                        40: 2,
                                        41: 2,
                                        42: 2,
                                        43: 2,
                                        44: 2,
                                        
                                        61: 17,
                                        62: 17,
                                        63: 17,
                                        64: 17,
                                        65: 17,
                                        66: 17,
                                        67: 17,
                                        68: 17,
                                        69: 17,
                                        70: 17,
                                        71: 17,
                                        72: 17,
                                        73: 17,
                                        74: 17,
                                        75: 17,
                                        76: 17,
                                        77: 17,
                                        78: 17,
                                        79: 17,
                                        80: 17,
                                        81: 17,
                                        82: 17,
                                        83: 17,
                                        84: 17,
                                        85: 17,
                                        86: 17,
                                        87: 17,
                                        88: 17,
                                        89: 17,
                                        90: 17,
                                        91: 17,
                                        92: 17,
                                        93: 17,
                                        94: 17,
                                        95: 17,
                                        96: 17,
                                        97: 17,
                                        98: 17,
                                        99: 17,
                                        100: 17,
                                        101: 17,
                                        102: 17,
                                        103: 17,
                                        104: 17,
                                        105: 17,
                                        106: 17,
                                        107: 17,
                                        108: 17,
                                        109: 17,
                                        110: 17,
                                        111: 17,
                                        112: 17,
                                        113: 17,
                                        114: 17,
                                        115: 17,
                                        116: 17,
                                        117: 17,
                                        118: 17,
                                        119: 17,
                                        120: 17,
                                        121: 17,
                                        122: 17,
                                        123: 17,
                                        124: 17,
                                        125: 17,
                                        126: 17,
                                        127: 17,
                                        128: 17,
                                        129: 17},
                     'Marker': {
                                13: 6,
                                14: 6,
                                15: 6,
                                16: 6,
                                17: 6,
                                18: 6,
                                19: 6,
                                20: 6,
                                21: 6,
                                22: 6,
                                23: 6,
                                24: 6,
                                25: 6,
                                26: 6,
                                27: 6,
                                28: 6,
                                29: 8,
                                30: 8,
                                31: 8,
                                32: 8,
                                33: 8,
                                34: 8,
                                35: 8,
                                36: 8,
                                37: 8,
                                38: 8,
                                39: 8,
                                40: 8,
                                41: 8,
                                42: 8,
                                43: 8,
                                44: 8,
                                61: 0,
                                62: 0,
                                63: 0,
                                64: 0,
                                65: 0,
                                66: 0,
                                67: 0,
                                68: 0,
                                69: 0,
                                70: 0,
                                71: 0,
                                72: 0,
                                73: 0,
                                74: 0,
                                75: 0,
                                76: 0,
                                77: 0,
                                78: 0,
                                79: 0,
                                80: 0,
                                81: 0,
                                82: 0,
                                83: 0,
                                84: 0,
                                85: 0,
                                86: 0,
                                87: 0,
                                88: 0,
                                89: 0,
                                90: 0,
                                91: 0,
                                92: 0,
                                93: 0,
                                94: 0,
                                95: 0,
                                96: 0,
                                97: 0,
                                98: 0,
                                99: 0,
                                100: 0,
                                101: 0,
                                102: 0,
                                103: 0,
                                104: 0,
                                105: 0,
                                106: 0,
                                107: 0,
                                108: 0,
                                109: 0,
                                110: 0,
                                111: 0,
                                112: 0,
                                113: 0,
                                114: 0,
                                115: 0,
                                116: 0,
                                117: 0,
                                118: 0,
                                119: 0,
                                120: 0,
                                121: 0,
                                122: 0,
                                123: 0,
                                124: 0,
                                125: 0,
                                126: 0,
                                127: 0,
                                128: 0,
                                129: 0},
                     'Split Pipe': {
                                    13: False,
                                    14: False,
                                    15: False,
                                    16: False,
                                    17: False,
                                    18: False,
                                    19: False,
                                    20: False,
                                    21: False,
                                    22: False,
                                    23: False,
                                    24: False,
                                    25: False,
                                    26: False,
                                    27: False,
                                    28: False,
                                    29: False,
                                    30: False,
                                    31: False,
                                    32: False,
                                    33: False,
                                    34: False,
                                    35: False,
                                    36: False,
                                    37: False,
                                    38: False,
                                    39: False,
                                    40: False,
                                    41: False,
                                    42: False,
                                    43: False,
                                    44: False,
                                    
                                    61: False,
                                    62: False,
                                    63: False,
                                    64: False,
                                    65: False,
                                    66: False,
                                    67: False,
                                    68: False,
                                    69: False,
                                    70: False,
                                    71: False,
                                    72: False,
                                    73: False,
                                    74: False,
                                    75: False,
                                    76: False,
                                    77: False,
                                    78: False,
                                    79: False,
                                    80: False,
                                    81: False,
                                    82: False,
                                    83: False,
                                    84: False,
                                    85: False,
                                    86: False,
                                    87: False,
                                    88: False,
                                    89: False,
                                    90: False,
                                    91: False,
                                    92: False,
                                    93: False,
                                    94: False,
                                    95: False,
                                    96: False,
                                    97: False,
                                    98: False,
                                    99: False,
                                    100: False,
                                    101: False,
                                    102: False,
                                    103: False,
                                    104: False,
                                    105: False,
                                    106: False,
                                    107: False,
                                    108: False,
                                    109: False,
                                    110: False,
                                    111: False,
                                    112: False,
                                    113: False,
                                    114: False,
                                    115: False,
                                    116: False,
                                    117: False,
                                    118: False,
                                    119: False,
                                    120: False,
                                    121: False,
                                    122: False,
                                    123: False,
                                    124: False,
                                    125: False,
                                    126: False,
                                    127: False,
                                    128: False,
                                    129: False},
                     'UTM X': {
                               13: 587700,
                               14: 587710,
                               15: 587720,
                               16: 587730,
                               17: 587740,
                               18: 587750,
                               19: 587760,
                               20: 587770,
                               21: 587780,
                               22: 587790,
                               23: 587800,
                               24: 587810,
                               25: 587820,
                               26: 587830,
                               27: 587840,
                               28: 587850,
                               29: 587850,
                               30: 587850,
                               31: 587850,
                               32: 587850,
                               33: 587850,
                               34: 587850,
                               35: 587850,
                               36: 587850,
                               37: 587850,
                               38: 587850,
                               39: 587850,
                               40: 587850,
                               41: 587850,
                               42: 587850,
                               43: 587850,
                               44: 587850,
                               
                               61: 587750,
                               62: 587750,
                               63: 587750,
                               64: 587750,
                               65: 587750,
                               66: 587750,
                               67: 587750,
                               68: 587750,
                               69: 587750,
                               70: 587750,
                               71: 587750,
                               72: 587750,
                               73: 587750,
                               74: 587750,
                               75: 587750,
                               76: 587750,
                               77: 587750,
                               78: 587750,
                               79: 587750,
                               80: 587750,
                               81: 587750,
                               82: 587750,
                               83: 587750,
                               84: 587750,
                               85: 587750,
                               86: 587750,
                               87: 587750,
                               88: 587750,
                               89: 587750,
                               90: 587750,
                               91: 587750,
                               92: 587750,
                               93: 587750,
                               94: 587750,
                               95: 587750,
                               96: 587750,
                               97: 587750,
                               98: 587750,
                               99: 587750,
                               100: 587750,
                               101: 587750,
                               102: 587750,
                               103: 587750,
                               104: 587750,
                               105: 587750,
                               106: 587750,
                               107: 587750,
                               108: 587750,
                               109: 587750,
                               110: 587750,
                               111: 587750,
                               112: 587750,
                               113: 587750,
                               114: 587750,
                               115: 587750,
                               116: 587750,
                               117: 587750,
                               118: 587750,
                               119: 587750,
                               120: 587750,
                               121: 587750,
                               122: 587750,
                               123: 587750,
                               124: 587750,
                               125: 587750,
                               126: 587750,
                               127: 587750,
                               128: 587760,
                               129: 587770},
                     'UTM Y': {
                               13: 6650700,
                               14: 6650700,
                               15: 6650700,
                               16: 6650700,
                               17: 6650700,
                               18: 6650700,
                               19: 6650700,
                               20: 6650700,
                               21: 6650700,
                               22: 6650700,
                               23: 6650700,
                               24: 6650700,
                               25: 6650700,
                               26: 6650700,
                               27: 6650700,
                               28: 6650700,
                               29: 6650700,
                               30: 6650690,
                               31: 6650680,
                               32: 6650670,
                               33: 6650660,
                               34: 6650650,
                               35: 6650640,
                               36: 6650630,
                               37: 6650620,
                               38: 6650610,
                               39: 6650600,
                               40: 6650590,
                               41: 6650580,
                               42: 6650570,
                               43: 6650560,
                               44: 6650550,
                               
                               61: 6651500,
                               62: 6651490,
                               63: 6651480,
                               64: 6651470,
                               65: 6651460,
                               66: 6651450,
                               67: 6651440,
                               68: 6651430,
                               69: 6651420,
                               70: 6651410,
                               71: 6651400,
                               72: 6651390,
                               73: 6651380,
                               74: 6651370,
                               75: 6651360,
                               76: 6651350,
                               77: 6651340,
                               78: 6651330,
                               79: 6651320,
                               80: 6651310,
                               81: 6651300,
                               82: 6651290,
                               83: 6651280,
                               84: 6651270,
                               85: 6651260,
                               86: 6651250,
                               87: 6651240,
                               88: 6651230,
                               89: 6651220,
                               90: 6651210,
                               91: 6651200,
                               92: 6651190,
                               93: 6651180,
                               94: 6651170,
                               95: 6651160,
                               96: 6651150,
                               97: 6651140,
                               98: 6651130,
                               99: 6651120,
                               100: 6651110,
                               101: 6651100,
                               102: 6651090,
                               103: 6651080,
                               104: 6651070,
                               105: 6651060,
                               106: 6651050,
                               107: 6651040,
                               108: 6651030,
                               109: 6651020,
                               110: 6651010,
                               111: 6651000,
                               112: 6650990,
                               113: 6650980,
                               114: 6650970,
                               115: 6650960,
                               116: 6650950,
                               117: 6650940,
                               118: 6650930,
                               119: 6650920,
                               120: 6650910,
                               121: 6650900,
                               122: 6650890,
                               123: 6650880,
                               124: 6650870,
                               125: 6650860,
                               126: 6650850,
                               127: 6650840,
                               128: 6650830,
                               129: 6650820},
                       'Depth': {13: -30.0,
                                 14: -30.0,
                                 15: -30.0,
                                 16: -30.0,
                                 17: -30.0,
                                 18: -30.0,
                                 19: -30.0,
                                 20: -30.0,
                                 21: -30.0,
                                 22: -30.0,
                                 23: -30.0,
                                 24: -30.0,
                                 25: -30.0,
                                 26: -30.0,
                                 27: -30.0,
                                 28: -30.0,
                                 29: -30.0,
                                 30: -30.0,
                                 31: -30.0,
                                 32: -30.0,
                                 33: -30.0,
                                 34: -30.0,
                                 35: -30.0,
                                 36: -30.0,
                                 37: -30.0,
                                 38: -30.0,
                                 39: -30.0,
                                 40: -30.0,
                                 41: -30.0,
                                 42: -30.0,
                                 43: -30.0,
                                 44: -30.0,
                                 61: -30.0,
                                 62: -30.0,
                                 63: -30.0,
                                 64: -30.0,
                                 65: -30.0,
                                 66: -30.0,
                                 67: -30.0,
                                 68: -30.0,
                                 69: -30.0,
                                 70: -30.0,
                                 71: -30.0,
                                 72: -30.0,
                                 73: -30.0,
                                 74: -30.0,
                                 75: -30.0,
                                 76: -30.0,
                                 77: -30.0,
                                 78: -30.0,
                                 79: -30.0,
                                 80: -30.0,
                                 81: -30.0,
                                 82: -30.0,
                                 83: -30.0,
                                 84: -30.0,
                                 85: -30.0,
                                 86: -30.0,
                                 87: -30.0,
                                 88: -30.0,
                                 89: -30.0,
                                 90: -30.0,
                                 91: -30.0,
                                 92: -30.0,
                                 93: -30.0,
                                 94: -30.0,
                                 95: -30.0,
                                 96: -30.0,
                                 97: -30.0,
                                 98: -30.0,
                                 99: -30.0,
                                 100: -30.0,
                                 101: -30.0,
                                 102: -30.0,
                                 103: -30.0,
                                 104: -30.0,
                                 105: -30.0,
                                 106: -30.0,
                                 107: -30.0,
                                 108: -30.0,
                                 109: -30.0,
                                 110: -30.0,
                                 111: -30.0,
                                 112: -30.0,
                                 113: -30.0,
                                 114: -30.0,
                                 115: -30.0,
                                 116: -30.0,
                                 117: -30.0,
                                 118: -30.0,
                                 119: -30.0,
                                 120: -30.0,
                                 121: -30.0,
                                 122: -30.0,
                                 123: -30.0,
                                 124: -30.0,
                                 125: -30.0,
                                 126: -30.0,
                                 127: -30.0,
                                 128: -30.0,
                                 129: -30.0},
                            "Sediment": {13: 'soft clay',
                                         14: 'soft clay',
                                         15: 'soft clay',
                                         16: 'soft clay',
                                         17: 'soft clay',
                                         18: 'soft clay',
                                         19: 'soft clay',
                                         20: 'soft clay',
                                         21: 'soft clay',
                                         22: 'soft clay',
                                         23: 'soft clay',
                                         24: 'soft clay',
                                         25: 'soft clay',
                                         26: 'soft clay',
                                         27: 'soft clay',
                                         28: 'soft clay',
                                         29: 'soft clay',
                                         30: 'soft clay',
                                         31: 'soft clay',
                                         32: 'soft clay',
                                         33: 'soft clay',
                                         34: 'soft clay',
                                         35: 'soft clay',
                                         36: 'soft clay',
                                         37: 'soft clay',
                                         38: 'soft clay',
                                         39: 'soft clay',
                                         40: 'soft clay',
                                         41: 'soft clay',
                                         42: 'soft clay',
                                         43: 'soft clay',
                                         44: 'soft clay',
                                         61: 'soft clay',
                                         62: 'soft clay',
                                         63: 'soft clay',
                                         64: 'soft clay',
                                         65: 'soft clay',
                                         66: 'soft clay',
                                         67: 'soft clay',
                                         68: 'soft clay',
                                         69: 'soft clay',
                                         70: 'soft clay',
                                         71: 'soft clay',
                                         72: 'soft clay',
                                         73: 'soft clay',
                                         74: 'soft clay',
                                         75: 'soft clay',
                                         76: 'soft clay',
                                         77: 'soft clay',
                                         78: 'soft clay',
                                         79: 'soft clay',
                                         80: 'soft clay',
                                         81: 'soft clay',
                                         82: 'soft clay',
                                         83: 'soft clay',
                                         84: 'soft clay',
                                         85: 'soft clay',
                                         86: 'soft clay',
                                         87: 'soft clay',
                                         88: 'soft clay',
                                         89: 'soft clay',
                                         90: 'soft clay',
                                         91: 'soft clay',
                                         92: 'soft clay',
                                         93: 'soft clay',
                                         94: 'soft clay',
                                         95: 'soft clay',
                                         96: 'soft clay',
                                         97: 'soft clay',
                                         98: 'soft clay',
                                         99: 'soft clay',
                                         100: 'soft clay',
                                         101: 'soft clay',
                                         102: 'soft clay',
                                         103: 'soft clay',
                                         104: 'soft clay',
                                         105: 'soft clay',
                                         106: 'soft clay',
                                         107: 'soft clay',
                                         108: 'soft clay',
                                         109: 'soft clay',
                                         110: 'soft clay',
                                         111: 'soft clay',
                                         112: 'soft clay',
                                         113: 'soft clay',
                                         114: 'soft clay',
                                         115: 'soft clay',
                                         116: 'soft clay',
                                         117: 'soft clay',
                                         118: 'soft clay',
                                         119: 'soft clay',
                                         120: 'soft clay',
                                         121: 'soft clay',
                                         122: 'soft clay',
                                         123: 'soft clay',
                                         124: 'soft clay',
                                         125: 'soft clay',
                                         126: 'soft clay',
                                         127: 'soft clay',
                                         128: 'soft clay',
                                         129: 'soft clay'}}
           
cable_routes = pd.DataFrame(cable_routes_dict)

substations_dict = { 'Dry Beam Area': {0: 0},
                     'Dry Frontal Area': {0: 0},
                     'Height': {0: 10},
                     'Length': {0: 10},
                     'Marker': {0: 2},
                     'Mass': {0: 100},
                     'Orientation Angle': {0: 0},
                     'Profile': {0: 'rectangular'},
                     'Substation Identifier': {0: 'array'},
                     'Surface Roughness': {0: 9.9999999999999995e-07},
                     'Type': {0: u'subsea'},
                     'Volume': {0: 1000},
                     'Wet Beam Area': {0: 0},
                     'Wet Frontal Area': {0: 0},
                     'Width': {0: 10}}

substations = pd.DataFrame(substations_dict)

umbilical_data_dict = {
 'Dry Mass': {0: 10251.058909500687, 1: 3436.7119045633135},
 'Floatation Length': {0: 186.38288926364888, 1: 62.48567099206025},
 'Key Identifier': {0: 'id743', 1: 'id743'},
 'Length': {0: 931.91444631824436, 1: 312.42835496030125},
 'Marker': {0: 32, 1: 73},
 'Required Floatation': {0: 151.02240999999998, 1: 151.02240999999998}}

umbilicals = pd.DataFrame(umbilical_data_dict)

umbilical_terminations = {'device001': [587875.,6650550.],
                          'device002': [587875.,6650700.]}

# modify electrical solution to force installation solution
cable_routes.loc[:, 'Burial Depth'] = [0.5]*len(cable_routes)
electrical_components.loc[:, 'Quantity'] = [1]*len(electrical_components)

# elec db
file_name = 'mock_db.xlsx'
xls_file = pd.ExcelFile(os.path.join(elec_dir, file_name),
                        encoding = 'utf-8')
sheet_names = xls_file.sheet_names
static_cables = xls_file.parse(sheet_names[0])
dynamic_cables = xls_file.parse(sheet_names[1])
wet_mate = xls_file.parse(sheet_names[2])
dry_mate = xls_file.parse(sheet_names[3])
transformer = xls_file.parse(sheet_names[4])
collection_point = xls_file.parse(sheet_names[5])

### M & F

mf_network = {
 'nodes': {'array': {'Substation foundation': {'marker': [[82, 83]],
                                               'quantity': Counter({'id718': 1,
                                                                    'grout': 1})}},
           'device001': {'Foundation': {'marker': [[33, 34],
                                                   [35, 36],
                                                   [37, 38],
                                                   [39, 40]],
                                        'quantity': Counter({'grout': 4,
                                                             'id516': 3,
                                                             'id528': 1})},
                         'Mooring system': {'marker': [[0,
                                                        1,
                                                        2,
                                                        3,
                                                        4,
                                                        5,
                                                        6,
                                                        7],
                                                       [8,
                                                        9,
                                                        10,
                                                        11,
                                                        12,
                                                        13,
                                                        14,
                                                        15],
                                                       [16,
                                                        17,
                                                        18,
                                                        19,
                                                        20,
                                                        21,
                                                        22,
                                                        23],
                                                       [24,
                                                        25,
                                                        26,
                                                        27,
                                                        28,
                                                        29,
                                                        30,
                                                        31]],
                                            'quantity': Counter({'id316': 16,
                                                                 'id471': 4,
                                                                 'id422': 4,
                                                                 'id68': 4,
                                                                 'id338': 4})},
                         'Umbilical': {'marker': [[32]],
                                       'quantity': Counter({'id743': 1})}},
           'device002': {'Foundation': {'marker': [[74, 75],
                                                   [76, 77],
                                                   [78, 79],
                                                   [80, 81]],
                                        'quantity': Counter({'grout': 4,
                                                             'id516': 3,
                                                             'id528': 1})},
                         'Mooring system': {'marker': [[41,
                                                        42,
                                                        43,
                                                        44,
                                                        45,
                                                        46,
                                                        47,
                                                        48],
                                                       [49,
                                                        50,
                                                        51,
                                                        52,
                                                        53,
                                                        54,
                                                        55,
                                                        56],
                                                       [57,
                                                        58,
                                                        59,
                                                        60,
                                                        61,
                                                        62,
                                                        63,
                                                        64],
                                                       [65,
                                                        66,
                                                        67,
                                                        68,
                                                        69,
                                                        70,
                                                        71,
                                                        72]],
                                            'quantity': Counter({'id316': 16,
                                                                 'id471': 4,
                                                                 'id422': 4,
                                                                 'id68': 4,
                                                                 'id338': 4})},
                         'Umbilical': {'marker': [[73]],
                                       'quantity': Counter({'id743': 1})}}},
 'topology': {'array': {'Substation foundation': [['id718', 'grout']]},
              'device001': {'Foundation': [['id516', 'grout'],
                                           ['id516', 'grout'],
                                           ['id528', 'grout'],
                                           ['id516', 'grout']],
                            'Mooring system': [['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316'],
                                               ['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316'],
                                               ['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316'],
                                               ['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316']],
                            'Umbilical': [['id743']]},
              'device002': {'Foundation': [['id516', 'grout'],
                                           ['id516', 'grout'],
                                           ['id528', 'grout'],
                                           ['id516', 'grout']],
                            'Mooring system': [['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316'],
                                               ['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316'],
                                               ['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316'],
                                               ['id471',
                                                'id316',
                                                'id68',
                                                'id316',
                                                'id422',
                                                'id316',
                                                'id338',
                                                'id316']],
                            'Umbilical': [['id743']]}}}

foundations_data_dict = {'Depth': {0: -129.64764390798447,
                                   1: -131.06535602160358,
                                   2: -122.02807331534915,
                                   3: -114.17057764339403,
                                   4: -123.39040119401608,
                                   5: -116.04659899761107,
                                   6: -129.18197837246262,
                                   7: -121.65903920188651,
                                   8: -112.8361895661229},
                         'Dry Mass': {0: 157.55159536731895,
                                      1: 157.55159536731895,
                                      2: 6391.8893307176222,
                                      3: 861.87962454769695,
                                      4: 157.55159536731895,
                                      5: 157.55159536731895,
                                      6: 6391.8893307176222,
                                      7: 861.87962454769695,
                                      8: 90193.46400008176},
                         'Grout Type': {0: 'grout',
                                        1: 'grout',
                                        2: 'grout',
                                        3: 'grout',
                                        4: 'grout',
                                        5: 'grout',
                                        6: 'grout',
                                        7: 'grout',
                                        8: 'grout'},
                         'Grout Volume': {0: 0.016196675543330975,
                                          1: 0.016196675543330975,
                                          2: 0.477247220095879,
                                          3: 0.088603257895683671,
                                          4: 0.016196675543330975,
                                          5: 0.016196675543330975,
                                          6: 0.477247220095879,
                                          7: 0.088603257895683671,
                                          8: 7.9546039748529802},
                         'Height': {0: 0.91400000000000003,
                                    1: 0.91400000000000003,
                                    2: 18.0,
                                    3: 5.0,
                                    4: 0.91400000000000003,
                                    5: 0.91400000000000003,
                                    6: 18.0,
                                    7: 5.0,
                                    8: 15.0},
                         'Installation Depth': {0: 0.91400000000000003,
                                                1: 0.91400000000000003,
                                                2: 18.0,
                                                3: 5.0,
                                                4: 0.91400000000000003,
                                                5: 0.91400000000000003,
                                                6: 18.0,
                                                7: 5.0,
                                                8: 15.0},
                         'Length': {0: 0.45700000000000002,
                                    1: 0.45700000000000002,
                                    2: 0.55900000000000005,
                                    3: 0.45700000000000002,
                                    4: 0.45700000000000002,
                                    5: 0.45700000000000002,
                                    6: 0.55900000000000005,
                                    7: 0.45700000000000002,
                                    8: 2.5},
                         'Marker': {0: 33,
                                    1: 35,
                                    2: 37,
                                    3: 39,
                                    4: 74,
                                    5: 76,
                                    6: 78,
                                    7: 80,
                                    8: 82},
                         'Sub-Type': {0: 'pipe pile',
                                      1: 'pipe pile',
                                      2: 'pipe pile',
                                      3: 'pipe pile',
                                      4: 'pipe pile',
                                      5: 'pipe pile',
                                      6: 'pipe pile',
                                      7: 'pipe pile',
                                      8: 'pipe pile'},
                         'Type': {0: 'pile',
                                  1: 'pile',
                                  2: 'pile',
                                  3: 'pile',
                                  4: 'pile',
                                  5: 'pile',
                                  6: 'pile',
                                  7: 'pile',
                                  8: 'pile'},
                         'UTM X': {0: 587490.0,
                                   1: 587600.0,
                                   2: 587600.0,
                                   3: 587490.0,
                                   4: 587700.0,
                                   5: 587900.0,
                                   6: 587900.0,
                                   7: 587700.0,
                                   8: 587490.0},
                         'UTM Y': {0: 6650600.0,
                                   1: 6650600.0,
                                   2: 6650500.0,
                                   3: 6650500.0,
                                   4: 6650800.0,
                                   5: 6650800.0,
                                   6: 6650600.0,
                                   7: 6650600.0,
                                   8: 6651060.0},
                         'Width': {0: 0.45700000000000002,
                                   1: 0.45700000000000002,
                                   2: 0.55900000000000005,
                                   3: 0.45700000000000002,
                                   4: 0.45700000000000002,
                                   5: 0.45700000000000002,
                                   6: 0.55900000000000005,
                                   7: 0.45700000000000002,
                                   8: 2.5}}
                                   
foundations_data_df = pd.DataFrame(foundations_data_dict)

foundations_layers_dict = {  'Depth': {0: np.inf,
                                       1: np.inf,
                                       2: np.inf,
                                       3: np.inf,
                                       4: np.inf,
                                       5: np.inf,
                                       6: np.inf,
                                       7: np.inf,
                                       8: np.inf},
                             'Layer Number': {0: 0,
                                              1: 0,
                                              2: 0,
                                              3: 0,
                                              4: 0,
                                              5: 0,
                                              6: 0,
                                              7: 0,
                                              8: 0},
                             'Marker': {0: 33,
                                        1: 35,
                                        2: 37,
                                        3: 39,
                                        4: 74,
                                        5: 76,
                                        6: 78,
                                        7: 80,
                                        8: 82},
                             'Soil Type': {0: 'soft rock coral',
                                           1: 'soft rock coral',
                                           2: 'soft rock coral',
                                           3: 'soft rock coral',
                                           4: 'soft rock coral',
                                           5: 'soft rock coral',
                                           6: 'soft rock coral',
                                           7: 'soft rock coral',
                                           8: 'soft rock coral'}}

foundations_layers_df = pd.DataFrame(foundations_layers_dict)

moorings_data_dict= {'Line Identifier': {0: 'line000',
                                         1: 'line000',
                                         2: 'line000',
                                         3: 'line000',
                                         4: 'line000',
                                         5: 'line000',
                                         6: 'line000',
                                         7: 'line000',
                                         8: 'line000',
                                         9: 'line000',
                                         10: 'line000',
                                         11: 'line000',
                                         12: 'line000',
                                         13: 'line000',
                                         14: 'line000',
                                         15: 'line000',
                                         16: 'line000',
                                         17: 'line000',
                                         18: 'line000',
                                         19: 'line000',
                                         20: 'line000',
                                         21: 'line000',
                                         22: 'line000',
                                         23: 'line000',
                                         24: 'line000',
                                         25: 'line000',
                                         26: 'line000',
                                         27: 'line000',
                                         28: 'line000',
                                         29: 'line000',
                                         30: 'line000',
                                         31: 'line000',
                                         32: 'line001',
                                         33: 'line001',
                                         34: 'line001',
                                         35: 'line001',
                                         36: 'line001',
                                         37: 'line001',
                                         38: 'line001',
                                         39: 'line001',
                                         40: 'line001',
                                         41: 'line001',
                                         42: 'line001',
                                         43: 'line001',
                                         44: 'line001',
                                         45: 'line001',
                                         46: 'line001',
                                         47: 'line001',
                                         48: 'line001',
                                         49: 'line001',
                                         50: 'line001',
                                         51: 'line001',
                                         52: 'line001',
                                         53: 'line001',
                                         54: 'line001',
                                         55: 'line001',
                                         56: 'line001',
                                         57: 'line001',
                                         58: 'line001',
                                         59: 'line001',
                                         60: 'line001',
                                         61: 'line001',
                                         62: 'line001',
                                         63: 'line001'},
                     'Marker': {0: 0,
                                1: 1,
                                2: 2,
                                3: 3,
                                4: 4,
                                5: 5,
                                6: 6,
                                7: 7,
                                8: 8,
                                9: 9,
                                10: 10,
                                11: 11,
                                12: 12,
                                13: 13,
                                14: 14,
                                15: 15,
                                16: 16,
                                17: 17,
                                18: 18,
                                19: 19,
                                20: 20,
                                21: 21,
                                22: 22,
                                23: 23,
                                24: 24,
                                25: 25,
                                26: 26,
                                27: 27,
                                28: 28,
                                29: 29,
                                30: 30,
                                31: 31,
                                32: 41,
                                33: 42,
                                34: 43,
                                35: 44,
                                36: 45,
                                37: 46,
                                38: 47,
                                39: 48,
                                40: 49,
                                41: 50,
                                42: 51,
                                43: 52,
                                44: 53,
                                45: 54,
                                46: 55,
                                47: 56,
                                48: 57,
                                49: 58,
                                50: 59,
                                51: 60,
                                52: 61,
                                53: 62,
                                54: 63,
                                55: 64,
                                56: 65,
                                57: 66,
                                58: 67,
                                59: 68,
                                60: 69,
                                61: 70,
                                62: 71,
                                63: 72}}

moorings_data_df = pd.DataFrame(moorings_data_dict)

line_data_dict= {'Dry Mass': {0: 1430.591229948034,
                              1: 1415.9397801046453,
                              2: 1512.30941757388,
                              3: 1602.3805965050158,
                              4: 1486.827523054319,
                              5: 1569.8098504574803,
                              6: 1424.9535521548576,
                              7: 1505.9152289116521},
                 'Length': {0: 219.17430632967253,
                            1: 220.46777728340797,
                            2: 212.34089037366172,
                            3: 205.51854572965507,
                            4: 213.54752655309315,
                            5: 207.12551577682427,
                            6: 218.75091293642907,
                            7: 212.01520310580992},
                 'Line Identifier': {0: 'line000',
                                     1: 'line000',
                                     2: 'line000',
                                     3: 'line000',
                                     4: 'line001',
                                     5: 'line001',
                                     6: 'line001',
                                     7: 'line001'},
                 'Type': {0: 'catenary',
                          1: 'catenary',
                          2: 'catenary',
                          3: 'catenary',
                          4: 'catenary',
                          5: 'catenary',
                          6: 'catenary',
                          7: 'catenary'}}

line_data_df = pd.DataFrame(line_data_dict)

lines_id = ['line' + str(n).zfill(3) for n in range(len(line_data_df))]

line_data_df['Line Identifier'] = \
    pd.Series(lines_id, index = line_data_df.index)

line_markers = np.repeat(lines_id, 8)

moorings_data_df['Line Identifier'] = \
    pd.Series(line_markers, index = moorings_data_df.index)

## reset index as must be sequential
foundations_data_df.reset_index(drop=True, inplace=True)

# collect together
test_data = {"component.rov" : equipment_rov,
             "component.divers" : equipment_divers,
             "component.cable_burial" : equipment_cable_burial,
             "component.excavating" : equipment_excavating,
             "component.mattress_installation" : equipment_mattress,
             "component.rock_bags_installation" : equipment_rock_filter_bags,
             "component.split_pipes_installation" : equipment_split_pipe,
             "component.hammer" : equipment_hammer,
             "component.drilling_rigs" : equipment_drilling_rigs,
             "component.vibro_driver" : equipment_vibro_driver,
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
             "component.ports" : ports,
             "component.port_locations": port_locations,

             "project.electrical_network" : electrical_network,
             "project.electrical_component_data" : electrical_components,
             "project.cable_routes" : cable_routes,
             "project.substation_props" : substations,
             "project.umbilical_cable_data" : umbilicals,
             "project.umbilical_seabed_connection" : umbilical_terminations,

             "project.moorings_foundations_network" : mf_network,
             "project.foundations_component_data" : foundations_data_df,
             "project.foundations_soil_data" : foundations_layers_df,
             "project.moorings_component_data" : moorings_data_df,
             "project.moorings_line_data" : line_data_df,

             "component.equipment_penetration_rates" :
                 equipment_penetration_rates,
             "component.installation_soil_compatibility" :
                 installation_soil_compatibility,
             "project.surface_laying_rate" : surface_laying_rate,
             "project.split_pipe_laying_rate" : split_pipe_laying_rate,
             "project.loading_rate" : loading_rate,
             "project.grout_rate" : grout_rate,
             "project.fuel_cost_rate" : fuel_cost_rate,

             "project.port_percentage_cost" : port_percentage_cost,
             "project.commissioning_time" : comissioning_time,
             "project.cost_contingency" : cost_contingency,
             
             "project.port_safety_factors" : port_sf,
             "project.vessel_safety_factors" : vessel_sf,
             "project.rov_safety_factors": rov_sf,
             "project.divers_safety_factors": divers_sf,
             "project.hammer_safety_factors": hammer_sf,
             "project.vibro_driver_safety_factors": vibro_driver_sf,
             "project.cable_burial_safety_factors": cable_burial_sf,
             "project.split_pipe_safety_factors": split_pipe_sf,
             "project.lease_area_entry_point" : entry_point_shapely,
             "project.layout" : layout_dict,

             "device.system_type" : system_type,
             "device.system_length" : system_length,
             "device.system_width" : system_width,
             "device.system_height" : system_height,
             "device.system_mass": system_mass,
             "device.assembly_duration" : assembly_duration,
             "device.load_out_method" : load_out_method,
             "device.transportation_method" : transportation_method,
             "device.bollard_pull" : bollard_pull,
             "device.connect_duration" : connect_duration,
             "device.disconnect_duration" : disconnect_duration,
             "project.start_date" : project_start_date,
             
             "device.subsystem_installation" : sub_device,
             
             "farm.wave_series_installation" : wave_series,
             "farm.tidal_series_installation" : tidal_series,
             "farm.wind_series_installation" : wind_series,
             
             "bathymetry.layers" : strata,
             "corridor.layers" : export_strata,

             "project.landfall_contruction_technique" : landfall,
             
             "site.projection" : lease_utm_zone,
             
             "component.dry_mate_connectors" : dry_mate,
             "component.dynamic_cable" : dynamic_cables,
             "component.static_cable" : static_cables,
             "component.wet_mate_connectors" : wet_mate,    
             "component.collection_points" : collection_point,
             "component.transformers" : transformer,
             
             "component.operations_limit_hs": hs_olc_dict,
             "component.operations_limit_tp": tp_olc_dict,
             "component.operations_limit_ws": ws_olc_dict,
             "component.operations_limit_cs": cs_olc_dict,

             "project.selected_installation_tool": tool,
             "options.skip_phase": True

             }

if __name__ == "__main__":

    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)
