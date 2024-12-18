# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os

import numpy as np
import pandas as pd

# from shapely.geometry import Polygon

this_dir = os.path.dirname(os.path.realpath(__file__))
elec_dir = os.path.join(this_dir, "electrical")

file_path = os.path.join(elec_dir, "lease_area.xlsx")
xls_file = pd.ExcelFile(file_path)
sheet_names = xls_file.sheet_names
lease_bathymetry = xls_file.parse(sheet_names[0])

layers = [1]

Z = np.array([lease_bathymetry["layer 1 start"]]).T

sediment = np.array([lease_bathymetry["layer 1 type"]]).T

x_max = lease_bathymetry.max()["x"]
y_max = lease_bathymetry.max()["y"]
x_min = lease_bathymetry.min()["x"]
y_min = lease_bathymetry.min()["y"]

num_x = (lease_bathymetry.max()["i"] - lease_bathymetry.min()["i"]) + 1
num_y = (lease_bathymetry.max()["j"] - lease_bathymetry.min()["j"]) + 1

x = np.linspace(x_min, x_max, num_x)
y = np.linspace(y_min, y_max, num_y)

depth_layers = []
sediment_layers = []

for z in layers:
    depths = []
    sediments = []

    for y_count in y:
        d = []
        s = []

        for x_count in x:
            point_df = lease_bathymetry[
                (lease_bathymetry["x"] == x_count)
                & (lease_bathymetry["y"] == y_count)
            ].index[0]

            if Z[point_df, z - 1] == "None":
                Z[point_df, z - 1] = np.nan

            d.append(Z[point_df, z - 1])
            s.append(sediment[point_df, z - 1])

        depths.append(d)
        sediments.append(s)

    depth_layers.append(depths)
    sediment_layers.append(sediments)

depth_array = np.swapaxes(np.array(depth_layers, dtype=float), 0, 2)

sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2)

layer_names = ["layer {}".format(x_layers) for x_layers in layers]

strata = {
    "values": {"depth": depth_array, "sediment": sediment_array},
    "coords": [x, y, layer_names],
}

nogo_areas = {"a": [(40.0, 40.0), (40.0, 110.0), (110.0, 110.0), (110.0, 40.0)]}

current_dir = 0.0
max_surf_current = 0.0
wave_dir = 0.0
power_rating = 1.0

layout = {
    "Device001": (1100.0, 600.0, 0.0),
    "Device002": (1250.0, 900.0, 0.0),
    "Device003": (1400.0, 1600.0, 0.0),
}

connection = "Wet-Mate"

number_devices = len(layout)
annual_power = 10.0

file_path = os.path.join(elec_dir, "mock_db.xlsx")
xls_file = pd.ExcelFile(file_path)
sheet_names = xls_file.sheet_names

static_cable = xls_file.parse(sheet_names[0])
dynamic_cable = xls_file.parse(sheet_names[1])
wet_mate_connectors = xls_file.parse(sheet_names[2])
dry_mate_connectors = xls_file.parse(sheet_names[3], parse_cols=21)
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
    11: [[0, 0, 0], [0, 0, 0]],
    12: [[0, 0, 0]],
    22: [[0, 0, 0], [0, 0, 0]],
    23: [[0, 0, 0], [0, 0, 0]],
    24: [[0, 0, 0], [0, 0, 0]],
    25: [[0, 0, 0], [0, 0, 0]],
}

max_temp = 10.0
max_soil_res = 10.0
voltage = 11000.0
mean_power_hist_per_device = {
    "Device001": ([0, 1.33, 1.33, 1.34], [0, 0.25, 0.5, 0.75, 1]),
    "Device002": ([0, 4, 0, 0], [0, 0.25, 0.5, 0.75, 1]),
    "Device003": ([0, 0.4, 2.4, 1.2], [0, 0.25, 0.5, 0.75, 1]),
}
network_configuration = "Radial"

target_burial_depth = 10.0
devices_per_string = 10
corridor_current_dir = 0.0
corridor_nogo_areas = {
    "a": [(40.0, 40.0), (40.0, 110.0), (110.0, 110.0), (110.0, 40.0)]
}

corridor_max_surf_current = 0.0
corridor_wave_dir = 0.0
corridor_target_burial_depth = 20.0
corridor_landing_point = [0, 0, 1]

file_path = os.path.join(elec_dir, "export_area.xlsx")
xls_file = pd.ExcelFile(file_path)
sheet_names = xls_file.sheet_names
corridor_depth = xls_file.parse(sheet_names[0])

export_layers = [1]

export_Z = np.array([corridor_depth["layer 1 start"]]).T
export_sediment = np.array([corridor_depth["layer 1 type"]]).T

x_max = corridor_depth.max()["x"]
y_max = corridor_depth.max()["y"]
x_min = corridor_depth.min()["x"]
y_min = corridor_depth.min()["y"]

num_x = (corridor_depth.max()["i"] - corridor_depth.min()["i"]) + 1
num_y = (corridor_depth.max()["j"] - corridor_depth.min()["j"]) + 1

x = np.linspace(x_min, x_max, num_x)
y = np.linspace(y_min, y_max, num_y)

export_depth_layers = []
export_sediment_layers = []

for z in export_layers:
    export_depths = []
    export_sediments = []

    for y_count in y:
        export_d = []
        export_s = []

        for x_count in x:
            point_df = corridor_depth[
                (corridor_depth["x"] == x_count)
                & (corridor_depth["y"] == y_count)
            ].index[0]

            if export_Z[point_df, z - 1] == "None":
                export_Z[point_df, z - 1] = np.nan

            export_d.append(export_Z[point_df, z - 1])
            export_s.append(export_sediment[point_df, z - 1])

        export_depths.append(export_d)
        export_sediments.append(export_s)

    export_depth_layers.append(export_depths)
    export_sediment_layers.append(export_sediments)

export_depth_array = np.swapaxes(
    np.array(export_depth_layers, dtype=float), 0, 2
)
export_sediment_array = np.swapaxes(np.array(export_sediment_layers), 0, 2)

export_layer_names = ["layer {}".format(x_layers) for x_layers in export_layers]

export_strata = {
    "values": {"depth": export_depth_array, "sediment": export_sediment_array},
    "coords": [x, y, export_layer_names],
}

corridor_max_temp = 10.0
corridor_max_soil_res = 10.0
corridor_voltage = 33000.0
min_voltage = 0.9
max_voltage = 1.0

power_factor = 0.98

equipment_gradient_constraint = 14.0

file_path = os.path.join(elec_dir, "equipment_compatibility_matrix.xlsx")
xls_file = pd.ExcelFile(file_path)
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

footprint_radius = 20.0
# footprint_coords = [(0.0,25.0,0.), (-25.0,-25.0,0.), (25.,-25.,0.)]
onshore_infrastructure_cost = 1000000.0

device_draft = 1.0
umbilical_connection = [0, 0, -0.5]
umbsf = 2.0
gravity = 9.80665  # gravity

test_data = {
    "bathymetry.layers": strata,
    "farm.nogo_areas": nogo_areas,
    "device.power_rating": power_rating,
    "project.layout": layout,
    "project.number_of_devices": number_devices,
    "project.annual_energy": annual_power,
    "component.static_cable": static_cable,
    "component.dynamic_cable": dynamic_cable,
    "component.wet_mate_connectors": wet_mate_connectors,
    "component.dry_mate_connectors": dry_mate_connectors,
    "component.transformers": transformers,
    "component.collection_points": collection_points,
    "component.collection_point_cog": collection_point_cog,
    "component.collection_point_foundations": collection_point_found,
    "device.voltage": voltage,
    "device.connector_type": connection,
    "project.network_configuration": network_configuration,
    "project.target_burial_depth": target_burial_depth,
    "project.devices_per_string": devices_per_string,
    "corridor.nogo_areas": corridor_nogo_areas,
    "project.export_target_burial_depth": corridor_target_burial_depth,
    "corridor.landing_point": corridor_landing_point,
    "corridor.layers": export_strata,
    "project.export_voltage": corridor_voltage,
    "project.equipment_gradient_constraint": equipment_gradient_constraint,
    "component.installation_soil_compatibility": installation_soil_compatibility,
    "device.constant_power_factor": power_factor,
    "device.prescribed_footprint_radius": footprint_radius,
    "project.onshore_infrastructure_cost": onshore_infrastructure_cost,
    "project.mean_power_hist_per_device": mean_power_hist_per_device,
    "device.system_draft": device_draft,
    "device.umbilical_connection_point": umbilical_connection,
    "project.umbilical_safety_factor": umbsf,
    "constants.gravity": gravity,
}

if __name__ == "__main__":
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)

    print("generate test data: {}".format(pkl_path))
