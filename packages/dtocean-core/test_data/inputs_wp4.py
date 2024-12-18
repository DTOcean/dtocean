# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os

import numpy as np
import pandas as pd

from dtocean_core.utils.moorings import get_moorings_tables

this_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(this_dir, "moorings")
elec_dir = os.path.join(this_dir, "electrical")

# fex = pickle.load(open(str(data_dir)+'\\fex_pelamiscuboid.pkl','rb'))

substparams = pd.read_csv(
    os.path.join(data_dir, "substparams_aegir.txt"),
    sep="\t",
    index_col=False,
    header=0,
)  # substation parameters

name_map = {
    "presubstfound": "Type",
    "subcog": "Centre of Gravity [x, y, z]",
    "subdryba": "Dry Beam Area",
    "subdryfa": "Dry Frontal Area",
    "subheight": "Height",
    "sublength": "Length",
    "submass": "Mass",
    "suborienang": "Orientation Angle",
    "suborig": "Origin [x, y, z]",
    "subprof": "Profile",
    "subrough": "Surface Roughness",
    "substloc": "Foundation Locations [x, y, z]",
    "subvol": "Volume",
    "subwetba": "Wet Beam Area",
    "subwetfa": "Wet Frontal Area",
    "subwidth": "Width",
    "substid": "Substation Identifier",
}

substparams = substparams.rename(columns=name_map)
substparams["Marker"] = range(len(substparams))

sub_ids = substparams["Substation Identifier"]
subcog = substparams.pop("Centre of Gravity [x, y, z]")
suborig = substparams.pop("Origin [x, y, z]")
substloc = substparams.pop("Foundation Locations [x, y, z]")

raw_origin_dict = {}
raw_cog_dict = {}
raw_found_dict = {}

for i, sub_id in enumerate(sub_ids):
    raw_origin_dict[sub_id] = eval(suborig.iloc[i])
    raw_cog_dict[sub_id] = eval(subcog.iloc[i])
    raw_found_dict[sub_id] = eval(substloc.iloc[i])

bathy_table = pd.read_csv(
    os.path.join(data_dir, "aegirbath2.txt"), delimiter="\t", header=None
)

soil_grid = pd.read_csv(
    os.path.join(data_dir, "aegirsoil2.txt"), delimiter="\t", header=None
)

soilprops = pd.read_csv(
    os.path.join(data_dir, "soilprops.txt"), sep="\t", header=0, index_col=False
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

layers = (1,)

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
sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2).astype(object)

layer_names = ["layer {}".format(x_layers) for x_layers in layers]

strata = {
    "values": {"depth": depth_array, "sediment": sediment_array},
    "coords": [x, y, layer_names],
}


turbine_hub_height = 20.0

gravity = 9.80665  # gravity
seaden = 1025.0  # sea water density
airden = 1.226  # air density
steelden = 7750.0  # steel density
conden = 2400.0  # concrete density
groutden = 2450.0  # grout density

compdict = eval(open(os.path.join(data_dir, "dummycompdb.txt")).read())
comp_tables = get_moorings_tables(compdict)  # component database

# Umbilical Cables
component_data_path = os.path.join(elec_dir, "mock_db.xlsx")
xls_file = pd.ExcelFile(component_data_path)
sheet_names = xls_file.sheet_names
dynamic_cable = xls_file.parse(sheet_names[1])

wlevmax = 5.0  # water level maximum offset
wlevmin = 0.0  # water level minimum offset
currentvel = 1.25  # current velocity
currentdir = 0.0  # current direction
currentprof = (
    "1/7 Power Law"  # current profile alternatives: "uniform" "1/7 power law"
)
wavedir = 0.0  # wave direction
hs = 0.5  # significant wave height. Leave the square bracket blank if there are no wave conditions to analyse
tp = 10.0  # peak wave period
gamma = 1.0  # jonswap gamma
windvel = 2.0  # wind velocity
winddir = 0.0  # wind direction
windgustvel = 6.0  # wind gust velocity
windgustdir = 0.0  # wind gust direction
draincoh = 0.0  # drained soil cohesion
unsfang = 5.0  # undrained soil friction angle
dsfang = 35.0  # drained soil friction angle
soilweight = 9.4285e03  # buoyant soil weight
relsoilden = 50.0  # relative soil density
undrained_soil_shear_strength_constant = 1.45e3
undrained_soil_shear_strength_dependent = 2e3  # undrained shear friction angle
soilsen = 3.0  # soil sensitivity

# buried line bearing capacity factors
linebcf = np.genfromtxt(os.path.join(data_dir, "linebcf.txt"), delimiter="\t")

# subgrade reaction coefficients
k1coef = pd.read_csv(
    os.path.join(data_dir, "subgradereactioncoefficientk1_cohesive.txt"),
    delimiter="\t",
    header=None,
    index_col=False,
    names=[
        "Allowable Deflection / Diameter",
        "Soft Clay Coefficient",
        "Stiff Clay Coefficient",
    ],
)

# subgrade cohesionless soil reaction coefficients
subgradereaccoef = pd.read_csv(
    os.path.join(data_dir, "subgradereactioncoefficient_cohesionless.txt"),
    delimiter="\t",
    header=None,
    index_col=False,
    names=[
        "Allowable Deflection / Diameter",
        "35% Relative Density Coefficient",
        "50% Relative Density Coefficient",
        "65% Relative Density Coefficient",
        "85% Relative Density Coefficient",
    ],
)

# pile deflection coefficients
piledefcoef = pd.read_csv(
    os.path.join(data_dir, "piledeflectioncoefficients.txt"),
    delimiter="\t",
    header=None,
    index_col=False,
    names=["Depth Coefficient", "Ay", "By"],
)

# pile moment coefficients am
pilemomcoefam = pd.read_csv(
    os.path.join(data_dir, "pilemomentcoefficientsam.txt"),
    delimiter="\t",
    header=None,
    index_col=False,
    names=[
        "Depth Coefficient",
        "Pile Length / Relative Soil-Pile Stiffness = 10",
        "Pile Length / Relative Soil-Pile Stiffness = 5",
        "Pile Length / Relative Soil-Pile Stiffness = 4",
        "Pile Length / Relative Soil-Pile Stiffness = 3",
        "Pile Length / Relative Soil-Pile Stiffness = 2",
    ],
)

# pile moment coefficients bm
pilemomcoefbm = pd.read_csv(
    os.path.join(data_dir, "pilemomentcoefficientsbm.txt"),
    delimiter="\t",
    header=None,
    index_col=False,
    names=[
        "Depth Coefficient",
        "Pile Length / Relative Soil-Pile Stiffness = 10",
        "Pile Length / Relative Soil-Pile Stiffness = 5",
        "Pile Length / Relative Soil-Pile Stiffness = 4",
        "Pile Length / Relative Soil-Pile Stiffness = 3",
        "Pile Length / Relative Soil-Pile Stiffness = 2",
    ],
)

# pile limiting values non calcaeous soils
pilefricresnoncal = pd.read_csv(
    os.path.join(data_dir, "pilelimitingvaluesnoncalcareous.txt"),
    delimiter="\t",
    header=None,
    index_col=False,
    names=[
        "Soil Friction Angle",
        "Friction Angle Sand-Pile",
        "Max Bearing Capacity Factor",
        "Max Unit Skin Friction",
        "Max End Bearing Capacity",
    ],
)

# plate anchor holding capacity factors
hcfdrsoil = pd.read_csv(
    os.path.join(data_dir, "holdingcapacityfactorsplateanchors.txt"),
    delimiter="\t",
    header=None,
    index_col=False,
    names=[
        "Relative Embedment Depth",
        "Drained Friction Angle = 20 degrees",
        "Drained Friction Angle = 25 degrees",
        "Drained Friction Angle = 30 degrees",
        "Drained Friction Angle = 35 degrees",
        "Drained Friction Angle = 40 degrees",
    ],
)

rockcomstr = 206843.0  # rock compressive strength

# cylinder drag coefficients
dragcoefcyl = np.loadtxt(
    os.path.join(data_dir, "dragcoefcyl.txt"), delimiter="\t"
)

# cylinder wake amplification factors
wakeampfactorcyl = np.loadtxt(
    os.path.join(data_dir, "wakeamplificationfactorcyl.txt"), delimiter="\t"
)

# rectangular wind drag coefficients
winddragcoefrect = np.loadtxt(
    os.path.join(data_dir, "winddragcoefrect.txt"), delimiter="\t"
)

# rectangular current drag coefficients
currentdragcoefrect = np.loadtxt(
    os.path.join(data_dir, "currentdragcoeffrect.txt"), delimiter="\t"
)

# rectangular wave drift coefficients
driftcoeffloatrect = np.loadtxt(
    os.path.join(data_dir, "driftcoefficientfloatrect.txt"), delimiter="\t"
)

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

depvar = False  # depth variation permitted
sysprof = "Rectangular"  # device profile options: "cylindrical" "rectangular"
sysmass = 4.5e5  # device mass
syscog = [0.0, 0.0, 0]  # device centre of gravity
sysvol = 440.0  # device displaced volume
sysheight = 6.0  # device height
syswidth = 15.0  # device width
syslength = 22.0  # device length
sysrough = 0.9e-2  # device surface roughness

layout = {"device001": [585500.0, 6650000.0, 0.0]}

fairloc = np.array(
    [
        [-15.0, 15.0, 0.0],
        [15.0, 15.0, 0.0],
        [15.0, -15.0, 0.0],
        [-15.0, -15.0, 0.0],
    ]
)  # fairlead locations (from device origin)

foundloc = np.array(
    [
        [-100, 100.0, 0.0],
        [100, 100.0, 0.0],
        [100.0, -100.0, 0.0],
        [-100.0, -100.0, 0.0],
    ]
)  # foundation locations (from device origin)

sysdryfa = 8.0  # device dry frontal area
sysdryba = 360.0  # device dry beam area


# Performance curves are matched to the same veloity abscissae
tidal_performance = {
    "Velocity": X,
    "Coefficient of Power": Cp,
    "Coefficient of Thrust": Ct,
}

rotor_diam = 23.0
turbine_interdist = 0.0
hubheight = -25.0  # hub height
sysorienang = 0.0  # device orientation angle
loadraos = np.loadtxt(
    os.path.join(data_dir, "loadraos.txt"), delimiter="\t"
)  # device load raos
addmass = np.loadtxt(
    os.path.join(data_dir, "addmass.txt"), delimiter="\t"
)  # device added mass
raddamp = np.loadtxt(
    os.path.join(data_dir, "raddamp.txt"), delimiter="\t"
)  # device radiation damping
hydrostiff = 66.394e3  # device hydrostatic stiffness
premoor = "Taut"  # predefined mooring system type options:, 'catenary', 'taut'
maxdisp = [
    75.0,
    75.0,
    10.0,
]  # device maximum displacements in surge, sway and heave
prefound = None  # predefined foundation type
coststeel = 1.0  # steel cost
costgrout = 0.1  # grout cost
costcon = 0.11  # concrete cost
groutstr = 125.0  # grout strength

preumb = "id743"  # predefined umbilical type
umbsf = 2.0  # umbilical safety factor
foundsf = 1.5  # foundation safety factor
prefootrad = None  # predefined footprint radius
seabed_connection = {"device001": [585146.00, 6650764.00, -121.0000]}

moorsfuls = 1.7  # mooring ultimate limit state safety factor
moorsfals = 1.1  # mooring accident limit state safety factor

groutsf = 6.0  # grout safety factor
syswetfa = 98.6  # device wet frontal area
syswetba = 132.5  # device wet beam area
sysdraft = 2.0  # device equilibrium draft without mooring system

waveinertiacoefrect = np.loadtxt(
    os.path.join(data_dir, "waveinertiacoefrect.txt"), delimiter="\t"
)

preline = []  # predefined mooring line component list e.g. ['shackle001','rope','shackle002']
fabcost = 1.0  # optional fabrication cost factor

umbilical_connection = [0, 0, -0.5]

use_max_thrust = True

test_data = {
    "constants.line_bearing_capacity_factor": linebcf,
    "constants.pile_Am_moment_coefficient": pilemomcoefam,
    "constants.pile_Bm_moment_coefficient": pilemomcoefbm,
    "constants.pile_deflection_coefficients": piledefcoef,
    "constants.pile_skin_friction_end_bearing_capacity": pilefricresnoncal,
    "constants.soilprops": soilprops,
    "constants.soil_cohesive_reaction_coefficient": k1coef,
    "constants.soil_cohesionless_reaction_coefficient": subgradereaccoef,
    "constants.soil_drained_holding_capacity_factor": hcfdrsoil,
    "farm.soil_sensitivity": soilsen,
    "constants.air_density": airden,
    "constants.concrete_density": conden,
    "constants.gravity": gravity,
    "constants.grout_compressive_strength": groutstr,
    "constants.grout_density": groutden,
    "constants.sea_water_density": seaden,
    "constants.steel_density": steelden,
    "device.turbine_hub_height": turbine_hub_height,
    "constants.cylinder_drag": dragcoefcyl,
    "constants.cylinder_wake_amplificiation": wakeampfactorcyl,
    "device.depth_variation_permitted": depvar,
    "device.dry_beam_area": sysdryba,
    "device.dry_frontal_area": sysdryfa,
    "device.fairlead_location": fairloc,
    "device.foundation_location": foundloc,
    "project.foundation_safety_factor": foundsf,
    "device.foundation_type": prefound,
    "device.maximum_displacement": maxdisp,
    "device.mooring_system_type": premoor,
    "project.main_direction": sysorienang,
    "device.prescribed_footprint_radius": prefootrad,
    "device.umbilical_connection_point": umbilical_connection,
    "constants.rectangular_current_drag": currentdragcoefrect,
    "constants.rectangular_drift": driftcoeffloatrect,
    "constants.rectangular_wind_drag": winddragcoefrect,
    "device.system_centre_of_gravity": syscog,
    "device.system_displaced_volume": sysvol,
    "device.system_draft": sysdraft,
    "device.system_height": sysheight,
    "device.system_length": syslength,
    "device.system_mass": sysmass,
    "device.system_profile": sysprof,
    "device.system_roughness": sysrough,
    "device.system_width": syswidth,
    "device.turbine_diameter": rotor_diam,
    "device.turbine_interdistance": turbine_interdist,
    "device.turbine_performance": tidal_performance,
    "project.umbilical_safety_factor": umbsf,
    "device.umbilical_type": preumb,
    "device.wet_beam_area": syswetba,
    "device.wet_frontal_area": syswetfa,
    "bathymetry.layers": strata,
    "farm.current_profile": currentprof,
    "farm.direction_of_max_surface_current": currentdir,
    "project.grout_strength_safety_factor": groutsf,
    "project.layout": layout,
    "farm.max_gust_wind_direction_100_year": windgustdir,
    "farm.max_gust_wind_speed_100_year": windgustvel,
    "farm.max_hs_100_year": hs,
    "farm.max_surface_current_10_year": currentvel,
    "farm.max_tp_100_year": tp,
    "farm.max_gamma_100_year": gamma,
    "farm.max_water_level_50_year": wlevmax,
    "farm.mean_wind_direction_100_year": winddir,
    "farm.mean_wind_speed_100_year": windvel,
    "farm.min_water_level_50_year": wlevmin,
    "project.mooring_ALS_safety_factor": moorsfals,
    "project.mooring_ULS_safety_factor": moorsfuls,
    "farm.wave_direction_100_year": wavedir,
    "farm.spec_gamma": gamma,
    "project.cost_of_concrete": costcon,
    "project.cost_of_grout": costgrout,
    "project.cost_of_steel": coststeel,
    "constants.rectangular_wave_inertia": waveinertiacoefrect,
    "project.predefined_mooring_list": preline,
    "project.fabrication_cost": fabcost,
    #             "farm.fex" : fex,
    "project.substation_props": substparams,
    "project.substation_layout": raw_origin_dict,
    "project.substation_cog": raw_cog_dict,
    "project.substation_foundation_location": raw_found_dict,
    "project.umbilical_seabed_connection": seabed_connection,
    "component.foundations_anchor": comp_tables["drag anchor"],
    "component.foundations_pile": comp_tables["pile"],
    "component.moorings_chain": comp_tables["chain"],
    "component.moorings_forerunner": comp_tables["forerunner assembly"],
    "component.moorings_rope": comp_tables["rope"],
    "component.moorings_rope_stiffness": comp_tables["rope axial stiffness"],
    "component.moorings_shackle": comp_tables["shackle"],
    "component.moorings_swivel": comp_tables["swivel"],
    "component.dynamic_cable": dynamic_cable,
    "component.foundations_anchor_sand": comp_tables["drag anchor sand"],
    "component.foundations_anchor_soft": comp_tables["drag anchor soft"],
    "options.use_max_thrust": use_max_thrust,
}


if __name__ == "__main__":
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)

    print("generate test data: {}".format(pkl_path))
