# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 10:39:38 2015

@author: 108630
"""

import os
import datetime as dt
from collections import Counter

import numpy as np
import pandas as pd

from dtocean_core.utils.reliability import (get_reliability_tables,
                                            compdict_from_mock)

from inputs_wp4 import comp_tables
from inputs_wp5 import (equipment_cable_burial,
                        cable_burial_sf,
                        collection_point,
                        equipment_divers,
                        divers_sf,
                        equipment_drilling_rigs,
                        dry_mate,
                        dynamic_cables,
                        equipment_penetration_rates,
                        equipment_excavating,
                        fuel_cost_rate,
                        grout_rate,
                        equipment_hammer,
                        hammer_sf,
                        installation_soil_compatibility,
                        loading_rate,
                        equipment_mattress,
                        port_locations,
                        port_sf,
                        ports,
                        equipment_rock_filter_bags,
                        equipment_rov,
                        rov_sf,
                        split_pipe_laying_rate,
                        split_pipe_sf,
                        equipment_split_pipe,
                        static_cables,
                        surface_laying_rate,
                        transformer,
                        vessel_sf,
                        helicopter_df,
                        ahts_df,
                        multicat_df,
                        crane_barge_df,
                        barge_df,
                        crane_vessel_df,
                        csv_df,
                        ctv_df,
                        clb_df,
                        clv_df,
                        jackup_barge_df,
                        jackup_vssel_df,
                        tugboat_df,
                        equipment_vibro_driver,
                        vibro_driver_sf,
                        wet_mate,
                        landfall,
                        export_strata,
                        assembly_duration,
                        bollard_pull,
                        connect_duration,
                        disconnect_duration,
                        load_out_method,
                        sub_device,
                        system_height,
                        system_length,
                        system_mass,
                        system_width,
                        transportation_method,
                        cable_routes,
                        electrical_components,
                        entry_point_shapely,
                        foundations_data_df,
                        foundations_layers_df,
                        line_data_df,
                        moorings_data_df,
                        tool,
                        substations,
                        tidal_series,
                        umbilicals,
                        umbilical_terminations,
                        wave_series,
                        wind_series,
                        comissioning_time,
                        cost_contingency,
                        port_percentage_cost,
                        project_start_date,
                        lease_utm_zone,
                        electrical_network,
                        mf_network,
                        strata)

this_dir = os.path.dirname(os.path.realpath(__file__))
elec_dir = os.path.join(this_dir, "electrical")
moor_dir = os.path.join(this_dir, "moorings")
op_dir = os.path.join(this_dir, "operations")

### ARRAY LAYOUT

array_layout = {'device001': [587850.,6650550.],
                'device002': [587850.,6650700.]}

### MACHINE
device_failure_rates = {'Prime Mover': 0.5,
                        'PTO': 0.25,
                        'Support Structure': 0.05}

control_failure_rates = {'Control': 0.1}

book_path = os.path.join(op_dir, "device_access.xlsx")
device_access = pd.read_excel(book_path, sheet_name="Access")

book_path = os.path.join(op_dir, "device_requirements.xlsx")
device_onsite_requirements = pd.read_excel(book_path, sheet_name="On-Site")
device_replacement_requirements = pd.read_excel(book_path,
                                                sheet_name="Replacement")
device_inspections_requirements = pd.read_excel(book_path,
                                                sheet_name="Inspections")

book_path = os.path.join(op_dir, "device_parts.xlsx")
device_onsite_parts = pd.read_excel(book_path, sheet_name="On-Site")

book_path = os.path.join(op_dir, "control_access.xlsx")
control_access = pd.read_excel(book_path, sheet_name="Access")

book_path = os.path.join(op_dir, "control_requirements.xlsx")
control_onsite_requirements = pd.read_excel(book_path, sheet_name="On-Site")
control_replacement_requirements = pd.read_excel(book_path,
                                                 sheet_name="Replacement")
control_inspections_requirements = pd.read_excel(book_path,
                                                 sheet_name="Inspections")

book_path = os.path.join(op_dir, "control_parts.xlsx")
control_onsite_parts = pd.read_excel(book_path, sheet_name="On-Site")

device_lead_times = {'Prime Mover': 120.,
                     'PTO': 96.,
                     'Control': 48.,
                     'Support Structure': 48.}
                     
device_costs = {'Prime Mover': 200000.,
                'PTO': 150000.,
                'Support Structure': 30000.}

control_costs = {'Control': 10000.}

device_weightings_dict = {'Sub-System': ['Prime Mover',
                                         'PTO',
                                         'Support Structure'],
                          'On-Site Maintenance': [4, 4, 4],
                          'Replacement': [4, 4, 4],
                          'Inspections': [2, 2, 2]}
                
device_weightings = pd.DataFrame(device_weightings_dict)

control_weightings_dict = {'Sub-System': ['Control'],
                           'On-Site Maintenance': [4],
                           'Replacement': [4],
                           'Inspections': [2]}
                
control_weightings = pd.DataFrame(control_weightings_dict)
                
### ELECTRICAL NETWORK

network_configuration = "Radial"

elec_bom =  {'Cost': {0: 800.0,
                      1: 700.0,
                      2: 150000.0,
                      3: 200000.0,
                      4: 800.0,
                      5: 1000000.0},
             'Key Identifier': {0: 17,
                                1: 2,
                                2: 12,
                                3: 6,
                                4: u'id742',
                                5: None},
             'Quantity': {0: 1240.0,
                          1: 1330.0,
                          2: 1.0,
                          3: 9.0,
                          4: 443.16388122792671,
                          5: 1.0},
             'Year': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}}
                            
book_path = os.path.join(op_dir, "electrical_requirements.xlsx")
electrical_onsite_requirements = pd.read_excel(book_path, sheet_name="On-Site")
electrical_inspections_requirements = pd.read_excel(book_path,
                                                    sheet_name="Inspections")

book_path = os.path.join(op_dir, "electrical_parts.xlsx")
electrical_onsite_parts = pd.read_excel(book_path, sheet_name="On-Site")

electrical_lead_times = {'Inter-Array Cables': 48.,
                         'Substations': 120.,
                         'Export Cable': 240.}
                         
substation_layout = {"array": [587850., 6651000]}

### MOORINGS AND FOUNDATIONS

moor_bom =  {'Cost': {0: 46595.722315912215,
                      1: 1389.3599999999999,
                      2: 67.5,
                      3: 1015.1542266412166,
                      4: 67.5,
                      5: 2641.0434122155366,
                      6: 67.5,
                      7: 746.27999999999997,
                      8: 67.5,
                      9: 1389.3599999999999,
                      10: 67.5,
                      11: 984.6647815996198,
                      12: 67.5,
                      13: 2658.3589043289548,
                      14: 67.5,
                      15: 746.27999999999997,
                      16: 67.5,
                      17: 1389.3599999999999,
                      18: 67.5,
                      19: 1183.2695849394572,
                      20: 67.5,
                      21: 2548.2325014520047,
                      22: 67.5,
                      23: 746.27999999999997,
                      24: 67.5,
                      25: 1389.3599999999999,
                      26: 67.5,
                      27: 1364.9571491938545,
                      28: 67.5,
                      29: 2452.9502245316494,
                      30: 67.5,
                      31: 746.27999999999997,
                      32: 67.5,
                      33: 629.4563710162322,
                      34: 629.4563710162322,
                      35: 21573.884218325431,
                      36: 3443.415596368885,
                      37: 376287.75594767794,
                      38: 26196.859407966593,
                      39: 26196.859407966593},
             'Key Identifier': {0: 'id743',
                                1: 'id472',
                                2: 'id316',
                                3: 'id69',
                                4: 'id316',
                                5: 'id422',
                                6: 'id316',
                                7: 'id339',
                                8: 'id316',
                                9: 'id472',
                                10: 'id316',
                                11: 'id69',
                                12: 'id316',
                                13: 'id422',
                                14: 'id316',
                                15: 'id339',
                                16: 'id316',
                                17: 'id472',
                                18: 'id316',
                                19: 'id69',
                                20: 'id316',
                                21: 'id422',
                                22: 'id316',
                                23: 'id339',
                                24: 'id316',
                                25: 'id472',
                                26: 'id316',
                                27: 'id69',
                                28: 'id316',
                                29: 'id422',
                                30: 'id316',
                                31: 'id339',
                                32: 'id316',
                                33: 'id516',
                                34: 'id516',
                                35: 'id528',
                                36: 'id516',
                                37: 'id718',
                                38: 'id528',
                                39: 'id528'},
             'Quantity': {0: 1.0,
                          1: 1.0,
                          2: 1.0,
                          3: 1.0,
                          4: 1.0,
                          5: 1.0,
                          6: 1.0,
                          7: 1.0,
                          8: 1.0,
                          9: 1.0,
                          10: 1.0,
                          11: 1.0,
                          12: 1.0,
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
                          39: 1.0},
             'Year': {0: 0.0,
                      1: 0.0,
                      2: 0.0,
                      3: 0.0,
                      4: 0.0,
                      5: 0.0,
                      6: 0.0,
                      7: 0.0,
                      8: 0.0,
                      9: 0.0,
                      10: 0.0,
                      11: 0.0,
                      12: 0.0,
                      13: 0.0,
                      14: 0.0,
                      15: 0.0,
                      16: 0.0,
                      17: 0.0,
                      18: 0.0,
                      19: 0.0,
                      20: 0.0,
                      21: 0.0,
                      22: 0.0,
                      23: 0.0,
                      24: 0.0,
                      25: 0.0,
                      26: 0.0,
                      27: 0.0,
                      28: 0.0,
                      29: 0.0,
                      30: 0.0,
                      31: 0.0,
                      32: 0.0,
                      33: 0.0,
                      34: 0.0,
                      35: 0.0,
                      36: 0.0,
                      37: 0.0,
                      38: 0.0,
                      39: 0.0}}
                          
book_path = os.path.join(op_dir, "moorings_requirements.xlsx")
moorings_onsite_requirements = pd.read_excel(book_path, sheet_name="On-Site")
moorings_inspections_requirements = pd.read_excel(book_path,
                                                  sheet_name="Inspections")

book_path = os.path.join(op_dir, "moorings_parts.xlsx")
moorings_onsite_parts = pd.read_excel(book_path, sheet_name="On-Site")

moorings_lead_times = {"Foundations": 48.}


# MAINTENANCE TYPE SELECTIONS

calendar_based_maintenance = True
condition_based_maintenance = True
                             
calendar_maintenance_interval = {'Prime Mover': 5.,
                                 'PTO': 1.,
                                 'Control': 5.,
                                 'Support Structure': 10.,
                                 'Umbilical Cable': 10.,
                                 'Inter-Array Cables': np.nan,
                                 'Substations': 10.,
                                 'Export Cable': 10.,
                                 'Foundations': 10.,
                                 'Mooring Lines': 10.}
                                 
condition_maintenance_soh = {'Prime Mover': 50.,
                             'PTO': 50.,
                             'Control': 50.,
                             'Support Structure': np.nan,
                             'Umbilical Cable': 50.,
                             'Inter-Array Cables': np.nan,
                             'Substations': 50.,
                             'Export Cable': 50.,
                             'Foundations': 50.,
                             'Mooring Lines': 50.}
                             
condition_maintenance_cost = {'Prime Mover': 30000.,
                              'PTO': 20000.,
                              'Control': 0.,
                              'Support Structure': 15000.,
                              'Umbilical Cable': np.nan,
                              'Inter-Array Cables': 0.,
                              'Substations': 0.,
                              'Export Cable': 0.,
                              'Foundations': 15000.,
                              'Mooring Lines': np.nan}
                              

### OPERATION TYPE SELECTIONS
                          
operations_onsite_maintenance = {'Prime Mover': True,
                                 'PTO': True,
                                 'Control': True,
                                 'Support Structure': True,
                                 'Umbilical Cable': True,
                                 'Inter-Array Cables': True,
                                 'Substations': True,
                                 'Export Cable': True,
                                 'Foundations': True,
                                 'Mooring Lines': True}
                                 
operations_replacements = {'Prime Mover': True,
                           'PTO': True,
                           'Control': True,
                           'Support Structure': True,
                           'Umbilical Cable': False,
                           'Mooring Lines': False}

operations_inspections = {'Prime Mover': True,
                          'PTO': True,
                          'Control': True,
                          'Support Structure': True,
                          'Umbilical Cable': True,
                          'Inter-Array Cables': True,
                          'Substations': True,
                          'Export Cable': True,
                          'Foundations': True,
                          'Mooring Lines': True}
                          
### OPERATION WEIGHTINGS

full_weightings = {'On-Site Maintenance': 4.,
                   'Replacement': 4.,
                   'Inspections': 2.}
                  
site_weightings = {'On-Site Maintenance': 4.,
                   'Inspections': 2.}
                   
                   
### OPERATION COSTS

transit_cost_multiplier = 0.03
loading_cost_multiplier = 0.01
                      
### PROJECT DATES

commissioning_date = dt.datetime(1992, 1, 5)
annual_maintenance_start = "April"
annual_maintenance_end = "October"
lifetime = 7 # 'project.lifetime',


### CREW SPECIFICATION

helideck = False
wage_specialist_day = 200.
wage_specialist_night = 300.
wage_technician_day = 100.
wage_technician_night = 150.
workdays_summer = 7
workdays_winter = 7

#### POWER

mean_power_per_device = {'device001': 1.2698047018309357, # 'project.mean_power_per_device'
                         'device002': 1.2698047018309357}
                         
annual_energy_per_device = {'device001': 11123.489188038995, # 'project.annual_energy_per_device'
                            'device002': 11123.489188038995}

                            
#### COMPONENTS

collection_point_cog = {11: [0,0,0],
                        12: [0,0,0],
                        22: [0,0,0],
                        23: [0,0,0],
                        24: [0,0,0],
                        25: [0,0,0]
                        }
                        
collection_point_found = {11: [[0,0,0],[0,0,0]],
                          12: [[0,0,0]],
                          22: [[0,0,0],[0,0,0]],
                          23: [[0,0,0],[0,0,0]],
                          24: [[0,0,0],[0,0,0]],
                          25: [[0,0,0],[0,0,0]]
                          }


#### RELIABILITY DATA

compdict = eval(open(os.path.join(moor_dir, 'dummycompdb.txt')).read())

component_data_path = os.path.join(elec_dir, 'mock_db.xlsx')
xls_file = pd.ExcelFile(component_data_path, encoding = 'utf-8')
elec_dict = compdict_from_mock(xls_file)

compdict.update(elec_dict)

comp_tables_rel = get_reliability_tables(compdict)


### LOAD VARIABLES

test_data = {
             "project.calendar_based_maintenance": calendar_based_maintenance,
             "project.condition_based_maintenance": condition_based_maintenance,
             "farm.helideck": helideck,
             "project.wage_specialist_day": wage_specialist_day,
             "project.wage_specialist_night": wage_specialist_night,
             "project.wage_technician_day": wage_technician_day,
             "project.wage_technician_night": wage_technician_night,
             "project.workdays_summer": workdays_summer,
             "project.workdays_winter": workdays_winter,
             "project.energy_selling_price": 0.2,
                
             "project.network_configuration": network_configuration,
             "project.layout": array_layout,
             "bathymetry.layers": strata,
             "project.commissioning_date": commissioning_date,
             'options.annual_maintenance_start': annual_maintenance_start,
             'options.annual_maintenance_end': annual_maintenance_end,
             "project.electrical_economics_data": elec_bom,
             "project.moorings_foundations_economics_data": moor_bom,
            
             "options.operations_onsite_maintenance":
                 operations_onsite_maintenance,
             "options.operations_replacements": operations_replacements,
             "options.operations_inspections": operations_inspections,
            
             'project.umbilical_operations_weighting': full_weightings,
             'project.array_cables_operations_weighting': site_weightings,
             'project.substations_operations_weighting': site_weightings,
             'project.export_cable_operations_weighting': site_weightings,
             'project.foundations_operations_weighting': site_weightings,
             'project.moorings_operations_weighting': full_weightings,
                          
             'options.condition_maintenance_soh': condition_maintenance_soh,
             'options.calendar_maintenance_interval':
                 calendar_maintenance_interval,
                 
             'device.subsystem_access': device_access,
             'device.subsystem_costs': device_costs,
             'device.subsystem_failure_rates': device_failure_rates,
             'device.subsystem_inspections': device_inspections_requirements,
             'device.subsystem_maintenance': device_onsite_requirements,
             'device.subsystem_maintenance_parts': device_onsite_parts,
             'device.subsystem_operation_weightings': device_weightings,
             'device.subsystem_replacement': device_replacement_requirements,
             
             'device.control_subsystem_access': control_access,
             'device.control_subsystem_costs': control_costs,
             'device.control_subsystem_failure_rates': control_failure_rates,
             'device.control_subsystem_inspections':
                 control_inspections_requirements,
             'device.control_subsystem_maintenance':
                 control_onsite_requirements,
             'device.control_subsystem_maintenance_parts':
                 control_onsite_parts,
             'device.control_subsystem_operation_weightings':
                 control_weightings,
             'device.control_subsystem_replacement':
                 control_replacement_requirements,
                 
             'project.electrical_onsite_maintenance_requirements':
                 electrical_onsite_requirements,
             'project.moorings_onsite_maintenance_requirements':
                 moorings_onsite_requirements,
            
             'project.electrical_replacement_requirements': None,
             'project.moorings_replacement_requirements': None,
             
             'project.electrical_inspections_requirements':
                 electrical_inspections_requirements,
             'project.moorings_inspections_requirements':
                 moorings_inspections_requirements,
            
             'project.electrical_onsite_maintenance_parts':
                 electrical_onsite_parts,
             'project.moorings_onsite_maintenance_parts': moorings_onsite_parts,

             'project.electrical_replacement_parts': None,
             'project.moorings_replacement_parts': None,
            
             'options.subsystem_monitering_costs': condition_maintenance_cost,
             'options.transit_cost_multiplier': transit_cost_multiplier,
             'options.loading_cost_multiplier': loading_cost_multiplier,
             
             "project.electrical_network": electrical_network,
             "project.moorings_foundations_network": mf_network,
             "component.moorings_chain_NCFR": comp_tables_rel["chain NCFR"],
             "component.moorings_chain_CFR": comp_tables_rel["chain CFR"],
             "component.moorings_forerunner_NCFR":
                 comp_tables_rel["forerunner NCFR"],
             "component.moorings_forerunner_CFR": 
                 comp_tables_rel["forerunner CFR"],
             "component.moorings_shackle_NCFR":
                 comp_tables_rel["shackle NCFR"],
             "component.moorings_shackle_CFR": comp_tables_rel["shackle CFR"],
             "component.moorings_swivel_NCFR": comp_tables_rel["swivel NCFR"],
             "component.moorings_swivel_CFR": comp_tables_rel["swivel CFR"],
             "component.foundations_anchor_NCFR":
                 comp_tables_rel["anchor NCFR"],
             "component.foundations_anchor_CFR": 
                 comp_tables_rel["anchor CFR"],
             "component.foundations_pile_NCFR": comp_tables_rel["pile NCFR"],
             "component.foundations_pile_CFR": comp_tables_rel["pile CFR"],
             "component.moorings_rope_NCFR":comp_tables_rel["rope NCFR"],
             "component.moorings_rope_CFR": comp_tables_rel["rope CFR"],
             "component.static_cable_NCFR":
                 comp_tables_rel["static_cable NCFR"],
             "component.static_cable_CFR": 
                 comp_tables_rel["static_cable CFR"],
             "component.dynamic_cable_NCFR":
                 comp_tables_rel["dynamic_cable NCFR"],
             "component.dynamic_cable_CFR": 
                 comp_tables_rel["dynamic_cable CFR"],
             "component.wet_mate_connectors_NCFR":
                 comp_tables_rel["wet_mate NCFR"],
             "component.wet_mate_connectors_CFR": 
                 comp_tables_rel["wet_mate CFR"],
             "component.dry_mate_connectors_NCFR":
                 comp_tables_rel["dry_mate NCFR"],
             "component.dry_mate_connectors_CFR": 
                 comp_tables_rel["dry_mate CFR"],
             "component.transformers_NCFR":
                 comp_tables_rel["transformer NCFR"],
             "component.transformers_CFR": 
                 comp_tables_rel["transformer CFR"],
             "component.collection_points_NCFR":
                 comp_tables_rel["collection_point NCFR"],
             "component.collection_points_CFR": 
                 comp_tables_rel["collection_point CFR"],

            'component.cable_burial': equipment_cable_burial,
            'project.cable_burial_safety_factors': cable_burial_sf,
            'component.collection_points': collection_point,
            "component.collection_point_cog": collection_point_cog,
            "component.collection_point_foundations": collection_point_found,
            'component.divers': equipment_divers,
            'project.divers_safety_factors': divers_sf,
            'component.drilling_rigs': equipment_drilling_rigs,
            'component.dry_mate_connectors': dry_mate,
            'component.equipment_penetration_rates':
                equipment_penetration_rates,
            'component.excavating': equipment_excavating,
            'project.fuel_cost_rate': fuel_cost_rate,
            'project.grout_rate': grout_rate,
            'component.hammer': equipment_hammer,
            'project.hammer_safety_factors': hammer_sf,
            'component.installation_soil_compatibility':
                installation_soil_compatibility,
            'project.loading_rate': loading_rate,
            'component.mattress_installation': equipment_mattress,
            'component.port_locations': port_locations,
            'project.port_safety_factors': port_sf,
            'component.ports': ports,
            'component.rock_bags_installation': equipment_rock_filter_bags,
            'component.rov': equipment_rov,
            'project.rov_safety_factors': rov_sf,
            'project.split_pipe_laying_rate': split_pipe_laying_rate,
            'project.split_pipe_safety_factors': split_pipe_sf,
            'component.split_pipes_installation': equipment_split_pipe,
            'component.static_cable': static_cables,
            'project.surface_laying_rate': surface_laying_rate,
            'component.transformers': transformer,
            'project.vessel_safety_factors': vessel_sf,
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
            'component.vibro_driver': equipment_vibro_driver,
            'project.vibro_driver_safety_factors': vibro_driver_sf,
            'component.wet_mate_connectors': wet_mate,
            'project.landfall_contruction_technique': landfall,
            'corridor.layers': export_strata,
            'device.assembly_duration': assembly_duration,
            'device.bollard_pull': bollard_pull,
            'device.connect_duration': connect_duration,
            'device.disconnect_duration': disconnect_duration,
            'device.load_out_method': load_out_method,
            'device.subsystem_installation': sub_device,
            'device.system_height': system_height,
            'device.system_length': system_length,
            'device.system_mass': system_mass,
            'device.system_width': system_width,
            'device.transportation_method': transportation_method,
            'project.cable_routes': cable_routes,
            'project.electrical_component_data': electrical_components,
            'project.lease_area_entry_point': entry_point_shapely,
            'project.foundations_component_data': foundations_data_df,
            'project.foundations_soil_data': foundations_layers_df,
            'project.moorings_line_data': line_data_df,
            'project.moorings_component_data': moorings_data_df,
            'project.selected_installation_tool': tool,
            'project.substation_props': substations,
            'farm.tidal_series_installation': tidal_series,
            'project.umbilical_cable_data': umbilicals,
            'project.umbilical_seabed_connection': umbilical_terminations,
            'farm.wave_series_installation': wave_series,
            'farm.wind_series_installation': wind_series,
            'project.commissioning_time': comissioning_time,
            'project.cost_contingency': cost_contingency,
            'project.port_percentage_cost': port_percentage_cost,
            'project.start_date': project_start_date,
            'project.lifetime': lifetime,
            'site.projection': lease_utm_zone,
            
            'project.mean_power_per_device': mean_power_per_device,
            'project.annual_energy_per_device': annual_energy_per_device,
            "project.substation_layout": substation_layout,
            
            'component.foundations_anchor': comp_tables["drag anchor"],
            'component.foundations_pile': comp_tables["pile"],
            'component.moorings_chain': comp_tables["chain"],
            'component.moorings_forerunner':
                                        comp_tables["forerunner assembly"],
            'component.moorings_rope': comp_tables["rope"],
            'component.moorings_rope_stiffness':
                                        comp_tables["rope axial stiffness"],
            'component.moorings_shackle': comp_tables["shackle"],
            'component.moorings_swivel': comp_tables["swivel"],
            "component.dynamic_cable" : dynamic_cables,
            'component.foundations_anchor_sand':
                                            comp_tables["drag anchor sand"],
            'component.foundations_anchor_soft':
                                            comp_tables["drag anchor soft"],
                                            
            'options.maintenance_data_points': 3,
            'project.discount_rate': 0.05

             }
             
if __name__ == "__main__":
    
    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)

