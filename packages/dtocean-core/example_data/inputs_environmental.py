# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os

import numpy as np
import pandas as pd

# test_data_dir = os.path.dirname(os.path.realpath(__file__))
# data_dir = os.path.join(test_data_dir, "environmental")
#
# table_path = os.path.join(data_dir, "species_protected.csv")
#
#
#
# protected_table = pd.read_csv(table_path, index_col=None)
#
# name_map1 ={ "subclass or group": "Subclass or Group",
#                     "observed": "Observed"}
#
#
# protected_table = protected_table.rename(columns=name_map1)

#
#
#
# table_path = os.path.join(data_dir, "species_receptors.csv")
# receptors_table = pd.read_csv(table_path, index_col=None)
#
#
# name_map2 ={ "subclass or group": "Subclass or Group",
#                     "observed": "Observed",
#                     "observed january": "Observed January",
#                     "observed february": "Observed February",
#                     "observed march": "Observed March",
#                     "observed april": "Observed April",
#                     "observed may": "Observed May",
#                     "observed june": "Observed June",
#                     "observed july": "Observed July",
#                     "observed august": "Observed August",
#                     "observed september": "Observed September",
#                     "observed october": "Observed October",
#                     "observed november": "Observed November",
#                     "observed december": "Observed December"
#                     }
#
# receptors_table = receptors_table.rename(columns=name_map2)
##


protected_species = None
receptor_species = None

# receptors_fishes = receptors_fishes_df1.set_index("Subclass or Group")


hydro_energy_modif_weight = "Gravel Cobble"

hydro_collision_risk_weight = "Sea Loch Entrance/ Devices In Parallel"

hydro_turbidity_risk_weight = None

hydro_underwater_noise_risk_weight = "Noise Device 100 - 150 dB re 1muPa"

hydro_reserve_effect_weight = "No Restriction"

hydro_reef_effect_weight = "Tidal Design Horizontal"

hydro_resting_place_weight = "Blades"

resource_reduction = 0.9

layout = {
    "Device001": (100.0, 900.0, 0.0),
    #              'Device002': (300.,900.,0.),
    #              'Device003': (400.,600.,0.)
}

initial_turbidity = 50.0
measured_turbidity = 0.1

initial_noise = 60.0
measured_noise = 75.0

number_of_devices = 2

device_draft = 20.0

device_width = 10.0

device_length = 10.0

device_height = 20.0

current_direction = 45.0

dry_frontal_area = 10.0

wet_frontal_area = 20.0

fishery_restricted_area = 1159.0

# fishery_restricted_area = None

lease_boundary = lease_area = np.array(
    [[50.0, 50.0], [950.0, 50.0], [950.0, 250.0], [50.0, 250.0]], dtype=float
)

## Setup
# x = np.linspace(0.,1000.,100)
# y = np.linspace(0.,1000.,100)
# nx = len(x)
# ny = len(y)
#
## Bathymetry?
# X, Y = np.meshgrid(x,y)
# Z = -X * 0.1 - 50
# xyz = np.vstack((X.ravel(),Y.ravel(),Z.ravel())).T
# depth = xyz

this_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(this_dir, "moorings")

bathy_table = pd.read_csv(
    os.path.join(data_dir, "aegirbath2.txt"), delimiter="\t", header=None
)

soil_grid = pd.read_csv(
    os.path.join(data_dir, "aegirsoil2.txt"), delimiter="\t", header=None
)

Z1 = bathy_table[2]
dZ = soil_grid[3]

Z = np.array([Z1.values, (Z1 - dZ).values]).T
sediment = np.array([soil_grid[2].values, soil_grid[4].values]).T
x_max = bathy_table.max()[0]
y_max = bathy_table.max()[1]
x_min = bathy_table.min()[0]
y_min = bathy_table.min()[1]

nx = 144
ny = 176

dx = (x_max - x_min) / (nx - 1)
dy = (y_max - y_min) / (ny - 1)

x = np.linspace(x_min, x_max, nx)
y = np.linspace(y_min, y_max, ny)
[X, Y] = np.meshgrid(x, y)


bathy_table[0] = np.ravel(X)
bathy_table[1] = np.ravel(Y)


layers = (0, 1)


depth_layers = []
sediment_layers = []
for z in layers:
    depths = []
    sediments = []
    for y_count in y:
        d = []
        s = []
        for x_count in x:
            point_df = bathy_table[
                (bathy_table[0] == x_count) & (bathy_table[1] == y_count)
            ].index[0]

            d.append(Z[point_df, z])
            s.append(sediment[point_df, z])

        depths.append(d)
        sediments.append(s)

    depth_layers.append(depths)
    sediment_layers.append(sediments)

depth_array = np.swapaxes(np.array(depth_layers, dtype=float), 0, 2)
sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2)

layer_names = ["layer {}".format(x_layers) for x_layers in layers]

strata = strata = {
    "values": {"depth": depth_array, "sediment": sediment_array},
    "coords": [x, y, layer_names],
}

test_data = {
    #             "farm.protected_table": protected_table,
    #             "farm.receptors_table": receptors_table,
    "farm.hydro_energy_modif_weight": hydro_energy_modif_weight,
    "project.hydro_collision_risk_weight": hydro_collision_risk_weight,
    "farm.hydro_turbidity_risk_weight": hydro_turbidity_risk_weight,
    "device.hydro_underwater_noise_risk_weight": hydro_underwater_noise_risk_weight,
    "farm.hydro_reserve_effect_weight": hydro_reserve_effect_weight,
    "device.hydro_reef_effect_weight": hydro_reef_effect_weight,
    "device.hydro_resting_place_weight": hydro_resting_place_weight,
    #             "project.resource_reduction": resource_reduction,
    "project.layout": layout,
    "farm.initial_turbidity": initial_turbidity,
    "project.hydro_measured_turbidity": measured_turbidity,
    "farm.initial_noise": initial_turbidity,
    "project.hydro_measured_noise": measured_noise,
    "project.number_of_devices": number_of_devices,
    #             "device.system_draft": device_draft,
    #             "device.system_width": device_width,
    #             "device.system_length": device_length,
    #             "device.system_height": device_height,
    #             "farm.direction_of_max_surface_current": current_direction,
    #             "project.fishery_restricted_area": fishery_restricted_area,
    "site.lease_boundary": lease_boundary,
    "bathymetry.layers": strata,
    "farm.protected_species": protected_species,
    "farm.receptor_species": receptor_species,
    #             "farm.receptors_soft_habitat": receptors_soft_habitat,
    #             "farm.receptors_particular_habitat": receptors_particular_habitat,
    #             "farm.receptors_shallow_diving_birds": receptors_shallow_diving_birds,
    #             "farm.receptors_medium_diving_birds": receptors_medium_diving_birds,
    #             "farm.receptors_deep_diving_birds": receptors_deep_diving_birds,
    #             "farm.receptors_fishes": receptors_fishes,
    #             "farm.receptors_elasmobranchs": receptors_elasmobranchs,
    #             "farm.receptors_mysticete": receptors_mysticete,
    #             "farm.receptors_odontocete": receptors_odontocete,
    #             "farm.receptors_seals": receptors_seals,
    #             "farm.receptors_magnetosensitive_species": receptors_magnetosensitive_species,
    #             "farm.receptors_electrosensitive_species": receptors_electrosensitive_species,
    #             'bathymetry.mooring_buried_line_bearing_capacity_factor': linebcf
}


if __name__ == "__main__":
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)

    print("generate test data: {}".format(pkl_path))
