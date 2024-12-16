# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Vincenzo Nava, Adam Collin
#    Copyright (C) 2017-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains the package interface to the dtocean installation module.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: installation
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package
   
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
.. moduleauthor:: Vincenzo Nava <vincenzo.nava@tecnalia.com>
.. moduleauthor:: Adam Collin <adam.collin@ieee.org>
"""

import os
import pickle
import logging
import pkg_resources

import utm
import numpy as np
import pandas as pd

from polite.paths import Directory, ObjDirectory, UserDataDirectory
from polite.configuration import ReadINI
from dtocean_installation.main import installation_main
from dtocean_installation.configure import get_operations_template
from dtocean_logistics.phases import EquipmentType

from aneris.boundary.interface import MaskVariable

from . import ModuleInterface
from ..utils.installation import (installation_phase_cost_output,
                                  installation_phase_time_result,
                                  find_marker_key_mf,
                                  installation_phase_date_result)

from ..utils.install_electrical import (set_collection_points,
                                        set_cables,
                                        set_connectors,
                                        get_umbilical_terminations,
                                        set_cable_cp_references)
from ..utils.version import Version

# Check module version
pkg_title = "dtocean-installation"
major_version = 2
version = pkg_resources.get_distribution(pkg_title).version

if not Version(version).major == major_version:
    
    err_msg = ("Incompatible version of {} detected! Major version {} is "
               "required, but version {} is installed").format(pkg_title,
                                                               major_version,
                                                               version)
    raise ImportError(err_msg)

# Set up logging
module_logger = logging.getLogger(__name__)


class InstallationInterface(ModuleInterface):
    
    '''Interface to the installation module
    
      Attributes:
        id_map (dict): Mapping of internal variable names to local variable
          names.
          
    '''
        
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Installation"
        
    @classmethod         
    def declare_weight(cls):
        
        return 4

    @classmethod         
    def declare_inputs(cls):
        
        '''A class method to declare all the variables required as inputs by
        this interface. 
        
        Returns:
          list: List of inputs identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example::
          
              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''

        input_list  =  ["site.projection",
                        "bathymetry.layers",
                        "corridor.layers",
                        "farm.wave_series_installation",
                        "farm.tidal_series_installation",
                        "farm.wind_series_installation",
                        
                        "device.system_type",
                        "device.system_length",
                        "device.system_width",
                        "device.system_height",
                        "device.system_mass",
                        "device.subsystem_installation",
                        "device.control_subsystem_installation",
                        "device.assembly_duration",
                        "device.load_out_method",
                        "device.transportation_method",
                        "device.bollard_pull",
                        "device.connect_duration",
                        "device.disconnect_duration",
                        "device.two_stage_assembly",
                        
                        "component.static_cable",

                        MaskVariable("component.dynamic_cable",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        
                        "component.dry_mate_connectors",
                        "component.wet_mate_connectors",
                        "component.rov",
                        "component.divers",
                        "component.cable_burial",
                        "component.excavating",
                        "component.mattress_installation",
                        "component.rock_bags_installation",
                        "component.split_pipes_installation",
                        "component.hammer",
                        "component.drilling_rigs",
                        "component.vibro_driver",
                        "component.vehicle_helicopter",
                        "component.vehicle_vessel_ahts",
                        "component.vehicle_vessel_multicat",
                        "component.vehicle_vessel_crane_barge",
                        "component.vehicle_vessel_barge",
                        "component.vehicle_vessel_crane_vessel",
                        "component.vehicle_vessel_csv",
                        "component.vehicle_vessel_ctv",
                        "component.vehicle_vessel_clb",
                        "component.vehicle_vessel_clv",
                        "component.vehicle_vessel_jackup_barge",
                        "component.vehicle_vessel_jackup_vessel",
                        "component.vehicle_vessel_tugboat",
                        "component.ports",
                        "component.port_locations",
                        "component.equipment_penetration_rates",
                        "component.installation_soil_compatibility",
                        "component.operations_limit_hs",
                        "component.operations_limit_tp",
                        "component.operations_limit_ws",
                        "component.operations_limit_cs",
                        
                        "project.start_date",
                        "project.commissioning_time",
                        
                        "project.layout",
                        "project.lease_area_entry_point",

                        "project.electrical_network",
                        "project.electrical_component_data",
                        "project.cable_routes",
                        "project.substation_props",
                        
                        MaskVariable("project.umbilical_cable_data",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("project.umbilical_seabed_connection",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        
                        "project.moorings_foundations_network",
                        "project.foundations_component_data",
                        
                        MaskVariable("project.moorings_line_data",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("project.moorings_component_data",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                                     
                        "project.surface_laying_rate",
                        "project.split_pipe_laying_rate",
                        "project.loading_rate",
                        "project.grout_rate",
                        "project.fuel_cost_rate",
                        
                        "project.port_percentage_cost",
                        "project.cost_contingency",

                        "project.port_safety_factors",
                        "project.vessel_safety_factors",
                        "project.rov_safety_factors",
                        "project.divers_safety_factors",
                        "project.hammer_safety_factors",
                        "project.vibro_driver_safety_factors",
                        "project.cable_burial_safety_factors",
                        "project.split_pipe_safety_factors",

                        "project.landfall_contruction_technique",
                        "project.selected_installation_tool",
                        
                        "options.skip_phase"
                        ]

        return input_list

    @classmethod        
    def declare_outputs(cls):
        
        '''A class method to declare all the output variables provided by
        this interface.
        
        Returns:
          list: List of output identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example::
          
              outputs = ["My:first:variable",
                         "My:third:variable",
                         
                        ]
        '''
        
        output_list = ["project.installation_completion_date",
                       "project.commissioning_date",
                       "project.total_installation_cost",
                       "project.installation_economics_data",
                       "project.port",
                       "project.port_distance",
                       "project.installation_journeys",
                       "project.installation_vessel_average_size",
                       "project.installation_plan",
                       "project.device_phase_installation_costs",
                       "project.device_phase_installation_cost_breakdown",
                       "project.device_phase_cost_class_breakdown",
                       "project.device_phase_installation_times",
                       "project.device_phase_installation_time_breakdown",
                       "project.device_phase_time_class_breakdown",
                       "project.electrical_phase_installation_costs",
                       "project.electrical_phase_installation_cost_breakdown",
                       "project.electrical_phase_cost_class_breakdown",
                       "project.electrical_phase_installation_times",
                       "project.electrical_phase_installation_time_breakdown",
                       "project.electrical_phase_time_class_breakdown",
                       "project.mooring_phase_installation_costs",
                       "project.mooring_phase_installation_cost_breakdown",
                       "project.mooring_phase_cost_class_breakdown",
                       "project.mooring_phase_installation_times",
                       "project.mooring_phase_installation_time_breakdown",
                       "project.mooring_phase_time_class_breakdown",
                       "project.installation_phase_cost_breakdown",
                       "project.installation_cost_class_breakdown",
                       "project.installation_phase_time_breakdown",
                       "project.installation_time_class_breakdown",
                       "project.total_installation_time",
                       "project.install_support_structure_dates",
                       "project.install_devices_dates",
                       "project.install_dynamic_cable_dates",
                       "project.install_export_cable_dates",
                       "project.install_array_cable_dates",
                       "project.install_surface_piercing_substation_dates",
                       "project.install_subsea_collection_point_dates",
                       "project.install_cable_protection_dates",
                       "project.install_driven_piles_dates",
                       "project.install_direct_embedment_dates",
                       "project.install_gravity_based_dates",
                       "project.install_pile_anchor_dates",
                       "project.install_drag_embedment_dates",
                       "project.install_suction_embedment_dates"
                       ]
                       
        return output_list
        
    @classmethod        
    def declare_optional(cls):
        
        '''A class method to declare all the variables which should be flagged
        as optional.
        
        Returns:
          list: List of optional variable identifiers
        
        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the declare_inputs output. For example::
          
              optional = ["My:first:variable",
                         ]
        '''
                
        optional = ["project.electrical_network",
                    "project.electrical_component_data",
                    "project.cable_routes",
                    "project.substation_props",
                    "project.umbilical_cable_data",
                    "project.umbilical_seabed_connection",
                    "project.moorings_foundations_network",
                    "project.moorings_foundations_network",
                    "project.foundations_component_data",
                    "project.moorings_line_data",
                    "project.moorings_component_data",
                    "component.dry_mate_connectors",
                    "component.dynamic_cable",
                    "component.static_cable",
                    "component.wet_mate_connectors",
                    "component.operations_limit_hs",
                    "component.operations_limit_tp",
                    "component.operations_limit_ws",
                    "component.operations_limit_cs",
                    "corridor.layers",
                    "project.landfall_contruction_technique",
                    "device.bollard_pull",
                    "device.control_subsystem_installation",
                    "device.two_stage_assembly",
                    "options.skip_phase"
                    ]
                    
        return optional
        
    @classmethod 
    def declare_id_map(self):
        
        '''Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.
        
        Returns:
          dict: Mapping of local to data description variable identifiers 
        
        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::
          
              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }
        
        '''
                  
        id_map = {"rov": "component.rov",
                  "divers": "component.divers",
                  "cable_burial": "component.cable_burial",
                  "excavating": "component.excavating",
                  "mattresses": "component.mattress_installation",
                  "rock_bags": "component.rock_bags_installation",
                  "split_pipes": "component.split_pipes_installation",
                  "hammer": "component.hammer",
                  "drilling_rigs": "component.drilling_rigs",
                  "vibro_driver": "component.vibro_driver",
                  "helicopter": "component.vehicle_helicopter",
                  "vessel_ahts": "component.vehicle_vessel_ahts",
                  "vessel_multicat": "component.vehicle_vessel_multicat",
                  "vessel_crane_barge": 
                      "component.vehicle_vessel_crane_barge",
                  "vessel_barge": "component.vehicle_vessel_barge",
                  "vessel_crane_vessel":
                      "component.vehicle_vessel_crane_vessel",
                  "vessel_csv": "component.vehicle_vessel_csv",
                  "vessel_ctv": "component.vehicle_vessel_ctv",
                  "vessel_clb": "component.vehicle_vessel_clb",
                  "vessel_clv": "component.vehicle_vessel_clv",
                  "vessel_jackup_barge":
                      "component.vehicle_vessel_jackup_barge",
                  "vessel_jackup_vessel":
                      "component.vehicle_vessel_jackup_vessel",
                  "vessel_tugboat": "component.vehicle_vessel_tugboat",
                  "ports": "component.ports",
                  "port_locations": "component.port_locations",
                  "site": "bathymetry.layers",
                  "export": "corridor.layers",
                  "sub_device": "device.subsystem_installation",
                  "control_system": "device.control_subsystem_installation",
                  "electrical_network": "project.electrical_network" ,
                  "electrical_components": "project.electrical_component_data",
                  "cable_routes": "project.cable_routes",
                  "substations": "project.substation_props",
                  "umbilicals": "project.umbilical_cable_data",
                  "umbilical_terminations":
                          "project.umbilical_seabed_connection",
                  "landfall": "project.landfall_contruction_technique",
                  "mf_network": "project.moorings_foundations_network",
                  "foundations_data": "project.foundations_component_data",
                  "line_summary_data": "project.moorings_line_data",
                  "line_component_data": "project.moorings_component_data",
                  "penetration_rates":
                          "component.equipment_penetration_rates",
                  "installation_soil_compatibility": 
                          "component.installation_soil_compatibility",
                  "surface_laying_rate": "project.surface_laying_rate",
                  "split_pipe_laying_rate":
                          "project.split_pipe_laying_rate",
                  "loading_rate": "project.loading_rate",
                  "grout_rate": "project.grout_rate",
                  "fuel_cost_rate": "project.fuel_cost_rate",
                  "port_cost": "project.port_percentage_cost",
                  "commission_time": "project.commissioning_time",
                  "cost_contingency": "project.cost_contingency",
                  "port_safety_factors": "project.port_safety_factors",
                  "vessel_safety_factors": "project.vessel_safety_factors",
                  "rov_safety_factors": "project.rov_safety_factors",
                  "divers_safety_factors": "project.divers_safety_factors",
                  "hammer_safety_factors": "project.hammer_safety_factors",
                  "vibro_driver_safety_factors":
                      "project.vibro_driver_safety_factors",
                  "cable_burial_safety_factors":
                      "project.cable_burial_safety_factors",
                  "split_pipe_safety_factors":
                      "project.split_pipe_safety_factors",
                  "entry_point": "project.lease_area_entry_point",
                  "layout": "project.layout",
                  "system_type": "device.system_type",
                  "system_length": "device.system_length",
                  "system_width": "device.system_width",
                  "system_height": "device.system_height",
                  "system_mass": "device.system_mass",
                  "assembly_duration": "device.assembly_duration",
                  "load_out_method": "device.load_out_method",
                  "transportation_method": "device.transportation_method",
                  "bollard_pull": "device.bollard_pull",
                  "connect_duration": "device.connect_duration",
                  "disconnect_duration": "device.disconnect_duration",
                  "project_start_date": "project.start_date",
                  "wave_series": "farm.wave_series_installation",
                  "tidal_series": "farm.tidal_series_installation",
                  "wind_series": "farm.wind_series_installation",
                  "lease_utm_zone": "site.projection", 
                  "end_date": "project.installation_completion_date",
                  "commissioning_date": "project.commissioning_date",
                  "port": "project.port",
                  "port_distance": "project.port_distance",
                  "journeys": "project.installation_journeys",
                  "vessel_average_size":
                          "project.installation_vessel_average_size",
                  "elec_db_dry_mate": "component.dry_mate_connectors",
                  "elec_db_dynamic_cable": "component.dynamic_cable",
                  "elec_db_static_cable": "component.static_cable",
                  "elec_db_wet_mate": "component.wet_mate_connectors",
                  "device_component_costs":
                      "project.device_phase_installation_costs",
                  "device_component_cost_breakdown":
                      "project.device_phase_installation_cost_breakdown",
                  "device_cost_class_breakdown":
                      "project.device_phase_cost_class_breakdown",
                  "device_component_times":
                      "project.device_phase_installation_times",
                  "device_component_time_breakdown":
                      "project.device_phase_installation_time_breakdown",
                  "device_time_class_breakdown":
                      "project.device_phase_time_class_breakdown",
                  "electrical_component_costs": 
                      "project.electrical_phase_installation_costs",
                  "electrical_component_cost_breakdown":
                      "project.electrical_phase_installation_cost_breakdown",
                  "electrical_cost_class_breakdown":
                      "project.electrical_phase_cost_class_breakdown",
                  "electrical_component_times":
                      "project.electrical_phase_installation_times",
                  "electrical_component_time_breakdown":
                      "project.electrical_phase_installation_time_breakdown",
                  "electrical_time_class_breakdown":
                      "project.electrical_phase_time_class_breakdown",
                  "mooring_component_costs": 
                      "project.mooring_phase_installation_costs",
                  "mooring_component_cost_breakdown":
                      "project.mooring_phase_installation_cost_breakdown",
                  "mooring_cost_class_breakdown":
                      "project.mooring_phase_cost_class_breakdown",
                  "mooring_component_times":
                      "project.mooring_phase_installation_times",
                  "mooring_component_time_breakdown":
                      "project.mooring_phase_installation_time_breakdown",
                  "mooring_time_class_breakdown":
                      "project.mooring_phase_time_class_breakdown",
                  "total_phase_costs":
                      "project.installation_phase_cost_breakdown",
                  "total_class_costs":
                       "project.installation_cost_class_breakdown",
                  "total_costs":
                       "project.total_installation_cost",
                  "total_phase_times":
                      "project.installation_phase_time_breakdown",
                  "total_class_times":
                       "project.installation_time_class_breakdown",
                  "total_times":
                       "project.total_installation_time",
                  "installation_bom": "project.installation_economics_data",
                  "cable_tool": "project.selected_installation_tool", 
                  "skip_phase": "options.skip_phase",
                  "install_support_structure_dates":
                      "project.install_support_structure_dates",
                  "install_devices_dates": "project.install_devices_dates",
                  "install_dynamic_cable_dates":
                      "project.install_dynamic_cable_dates",        
                  "install_export_cable_dates":
                      "project.install_export_cable_dates",               
                  "install_array_cable_dates":
                      "project.install_array_cable_dates",               
                  "install_surface_piercing_substation_dates":
                      "project.install_surface_piercing_substation_dates",
                  "install_subsea_collection_point_dates":
                      "project.install_subsea_collection_point_dates",               
                  "install_cable_protection_dates":
                      "project.install_cable_protection_dates",               
                  "install_driven_piles_dates":
                      "project.install_driven_piles_dates",               
                  "install_direct_embedment_dates":
                      "project.install_direct_embedment_dates",
                  "install_gravity_based_dates":
                      "project.install_gravity_based_dates",
                  "install_pile_anchor_dates":
                      "project.install_pile_anchor_dates",
                  "install_drag_embedment_dates":
                      "project.install_drag_embedment_dates",
                  "install_suction_embedment_dates":
                      "project.install_suction_embedment_dates",
                  "two_stage_assembly": "device.two_stage_assembly",
                  "plan": "project.installation_plan",
                  "limit_hs": "component.operations_limit_hs",
                  "limit_tp": "component.operations_limit_tp",
                  "limit_ws": "component.operations_limit_ws",
                  "limit_cs": "component.operations_limit_cs"
                  }

        return id_map

    def connect(self, debug_entry=False,
                      export_data=False):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
        # check that proj4 string is correctly formatted
        if not all(x in self.data.lease_utm_zone for x in ['utm', 'zone']): 

            errStr = ("Site projection not correctly defined. Must contain " +
                      "both 'utm' and 'zone' keys")

            raise ValueError(errStr)

        else:

            # could not get re search to work so using crude method between
            # two strings
            utm_zone = self.data.lease_utm_zone           
            zone = \
                utm_zone[utm_zone.find("zone=")+5:\
                         utm_zone.find(" +", utm_zone.find("zone=")+1)]

            zone = zone + ' U' # prepare for module

        input_dict = self.get_input_dict(self.data,
                                         self.meta,
                                         self.data.site,
                                         self.data.system_type,
                                         self.data.layout,
                                         self.data.electrical_network,
                                         self.data.mf_network,
                                         zone)

        ### M&F
        if self.data.mf_network is not None:
            
            # call the m&f functions from the tools
            foundations_data = self.data.foundations_data
            
            if foundations_data is None:
                
                var_name = self.meta.foundations_data.title
                errStr = ("Complete foundations data has not been provided. "
                          "Variable with title {} must be "
                          "satisfied").format(var_name)
                raise ValueError(errStr)
            
            network = self.data.mf_network['nodes']
            device_association = []

            for item, value in foundations_data.iterrows():

                marker = value['Marker']
                device_association.append(
                        find_marker_key_mf(network, marker, 'foundation'))

            # give foundations a label
            foundation_labels = ['foundation' + str(n).zfill(3)
                                 for n
                                 in range(len(device_association))]

            foundations_zone = [zone]*len(device_association)
            
            # add device_association and foundation_labels to dataframe
            foundations_data["Device"] = device_association
            foundations_data["Foundation"] = foundation_labels
            foundations_data["UTM Zone"] = foundations_zone

            foundations_data = foundations_data.drop('Depth', axis = 1)

            foundations_df = foundations_data

            name_map = {"Type": "type [-]",
                        "Sub-Type": "subtype [-]",
                        "UTM X": "x coord [m]",
                        "UTM Y": "y coord [m]",
                        "UTM Zone": "zone [-]",
                        "Length": "length [m]",
                        "Width": "width [m]",
                        "Height": "height [m]",
                        "Installation Depth": "installation depth [m]",
                        "Dry Mass": "dry mass [kg]",
                        "Grout Type": "grout type [-]",
                        "Grout Volume": "grout volume [m3]",
                        "Device": "devices [-]",
                        "Foundation": "foundations [-]"}
            
            foundations_df = foundations_df.rename(columns=name_map)
            
            # TEMP FIX: Change substation foundation to 'pile foundation'
            # to stop it being treated as floating
            array_idxs = foundations_df.index[
                            foundations_df["devices [-]"] == "array"].tolist()
            
            if array_idxs:
                foundations_df.at[array_idxs[0],
                                  "type [-]"] = 'pile foundation'
            
            # Add fixed or floating indicators to certain foundation types
            if "floating" in self.data.system_type.lower():
                append_this = ' anchor'
            else:
                append_this = ' foundation'
                
            foundation_map = {'directembedment': 'direct-embedment anchor',
                              'drag': 'drag-embedment anchor',
                              'gravity': 'gravity' + append_this,
                              'pile': 'pile' + append_this,
                              'shallowfoundation': 'shallow' + append_this,
                              'suctioncaisson': 'suction caisson anchor',
                              'pile foundation': 'pile foundation'}
                
            foundations_df['type [-]'] = foundations_df['type [-]'].map(
                                                                foundation_map)
            
        else:

            # make empty data structures
            foundations = {'type [-]': {},
                           'subtype [-]': {},
                           'x coord [m]': {},
                           'y coord [m]': {},
                           'length [m]': {},
                           'width [m]': {},
                           'height [m]': {},
                           'installation depth [m]': {},
                           'dry mass [kg]': {},
                           'grout type [-]': {},
                           'grout volume [m3]': {},
                           'zone [-]': {},
                           'layer information (layer number, soil type, ' + 
                               'soil depth) [-,-,m]': {},
                           'devices [-]': {},
                           'foundations [-]': {}}
            
            foundations_df = pd.DataFrame(foundations)

        if (self.data.mf_network is not None and
            "floating" in self.data.system_type.lower()):
            
            line_components = self.data.line_component_data
            line_data = self.data.line_summary_data
            
            missing_titles = []
            
            if line_components is None:
                missing_titles.append(self.meta.line_component_data.title)
            
            if line_data is None:
                missing_titles.append(self.meta.line_summary_data.title)
            
            if missing_titles:

                var_str = "Variable"
                if len(missing_titles) > 1: var_str += "s"
                
                title_str = "title"
                if len(missing_titles) > 1: title_str += "s"
                
                quote_missing = ["'{}'".format(x) for x in missing_titles]
                all_missing = ", ".join(quote_missing)
                
                errStr = ("Complete moorings data has not been provided. "
                          "{} with {} {} must be "
                          "satisfied.").format(var_str, title_str, all_missing)
                raise ValueError(errStr)

            # get first marker of each line id
            all_lines = line_components['Line Identifier'].unique()
        
            device_association = []
        
            for line in all_lines:
        
                marker = line_components[
                    line_components['Line Identifier'] == line].Marker.iloc[0]

                device_association.append(
                    find_marker_key_mf(network, marker, 'mooring'))

            # make table - then join on line identifier
            line_interm = pd.DataFrame({"Device": device_association, 
                                        "Line Identifier": all_lines})

            lines_df = pd.merge(line_data,
                                line_interm,
                                on = 'Line Identifier',
                                how ='inner')

            # set index
            ids = lines_df.index.tolist()
            ids = ['m' + str(val) for val in ids]
            lines_df.index = ids

            name_map = {"Device": "devices [-]",
                        "Line Identifier": "lines [-]",
                        "Type": "type [-]",
                        "Length": "length [m]",
                        "Dry Mass": "dry mass [kg]"}

            lines_df = lines_df.rename(columns=name_map)

        else:

            # make empty data structures
            empty_lines_df = {'devices [-]': [],
                              'lines [-]': [],
                              'component list [-]': [],
                              'type [-]': [],
                              'length [m]': [],
                              'dry mass [kg]': []}

            lines_df = pd.DataFrame(empty_lines_df)
            
        # Check if phases can be skipped:
        if self.data.skip_phase is None:
            skip_phase = False
        else:
            skip_phase = self.data.skip_phase

        if debug_entry:
            plan_only = True
        else:
            plan_only = False

        if export_data:
            
            arg_dict = {'lines_df': lines_df,
                        'foundations_df': foundations_df
                        }
            arg_dict.update(input_dict)
            
            userdir = UserDataDirectory("dtocean_core", "DTOcean", "config")
                    
            if userdir.isfile("files.ini"):
                configdir = userdir
            else:
                configdir = ObjDirectory("dtocean_core", "config")
            
            files_ini = ReadINI(configdir, "files.ini")
            files_config = files_ini.get_config()
            
            appdir_path = userdir.get_path("..")
            debug_folder = files_config["debug"]["path"]
            debug_path = os.path.join(appdir_path, debug_folder)
            debugdir = Directory(debug_path)
            debugdir.makedir()

            pkl_path = debugdir.get_path("installation_inputs.pkl")
            pickle.dump(arg_dict, open(pkl_path, "wb"))
                        
        ### Call module
        installation_output = installation_main(
                                    input_dict["vessels_df"],
                                    input_dict["equipment"],
                                    input_dict["ports_df"],
                                    input_dict["phase_order_df"],
                                    input_dict["schedule_OLC"],
                                    input_dict["penetration_rate_df"],
                                    input_dict["laying_rate_df"],
                                    input_dict["other_rates_df"],
                                    input_dict["port_safety_factor_df"],
                                    input_dict["vessel_safety_factor_df"],
                                    input_dict["equipment_safety_factor_df"],
                                    input_dict["whole_area"],
                                    input_dict["metocean_df"],
                                    input_dict["device_df"],
                                    input_dict["sub_device_df"],
                                    input_dict["landfall_df"],
                                    input_dict["entry_point_df"],
                                    input_dict["layout_df"],
                                    input_dict["collection_point_df"],
                                    input_dict["dynamic_cable_df"],
                                    input_dict["static_cable_df"],
                                    input_dict["cable_route_df"],
                                    input_dict["connectors_df"],
                                    input_dict["external_protection_df"],
                                    input_dict["topology"],
                                    lines_df,
                                    foundations_df,
                                    plan_only=plan_only,
                                    skip_phase=skip_phase
                                    )
        
        if debug_entry: return

        if export_data:
            
            pkl_path = debugdir.get_path("installation_outputs.pkl")
            pickle.dump(installation_output, open(pkl_path, "wb"))

        ### Collect outputs
        
        ### Dates 
        self.data.end_date = installation_output['DATE']['End Date']
        self.data.commissioning_date =\
            installation_output['DATE']['Comissioning Date']

        ### Port data
        self.data.port = \
            str(installation_output['PORT']['Port Name & ID [-]'][0])
        self.data.port_distance = \
            installation_output['PORT']['Distance Port-Site [km]']

        ### Environmental output from wp5
        self.data.journeys = installation_output['ENVIRONMENTAL']\
                ['Number Vessels Installation [-]']

        self.data.vessel_average_size = \
                installation_output['ENVIRONMENTAL']['Vessel Mean Length [m]']

        ### Planning phases       
        self.data.plan = \
            installation_output['PLANNING']['List of Operations [-]']

        # Need to logic test as they will not always be present
        installed_phases = installation_output['OPERATION'].keys()

        # Collect data per phase
        cost_dict, time_dict, date_dict = self._init_phase_dicts()
        
        ### Device phase
        if any('support structure' in phase for phase in installed_phases):
            
            values = installation_output['OPERATION'][
                                        'Installation of support structure']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)

            self.data.install_support_structure_dates = phase_date_dict
                
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Support Structure',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('devices' in phase for phase in installed_phases):
            
            values = installation_output['OPERATION'][
                                            'Installation of devices']
                
            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)

            self.data.install_devices_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Device',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)
                                      
        device_component_costs = pd.DataFrame(cost_dict)
        
        if device_component_costs.empty:
            
            device_component_costs = None
            device_component_cost_breakdown = None
            device_cost_class_breakdown = None
            
        else:

            device_component_costs = \
                            device_component_costs.set_index("Component")
            device_component_cost_breakdown = \
                            device_component_costs.sum(1).to_dict()
            device_cost_class_breakdown = device_component_costs.sum(
                                                 numeric_only=True).to_dict()
            device_component_costs = device_component_costs.reset_index()
        
        self.data.device_component_costs = device_component_costs
        self.data.device_component_cost_breakdown = \
                                        device_component_cost_breakdown
        self.data.device_cost_class_breakdown = \
                                        device_cost_class_breakdown
        
        device_component_times = pd.DataFrame(time_dict)
        
        if device_component_times.empty:
            
            device_component_times = None
            device_component_time_breakdown = None
            device_time_class_breakdown = None
            
        else:

            device_component_times = \
                                device_component_times.set_index("Component")
            device_component_time_breakdown = \
                                device_component_times.sum(1).to_dict()
            device_time_class_breakdown = device_component_times.sum(
                                                numeric_only=True).to_dict()
            device_component_times = device_component_times.reset_index()
                        
        self.data.device_component_times = device_component_times
        self.data.device_component_time_breakdown = \
                                        device_component_time_breakdown
        self.data.device_time_class_breakdown = \
                                        device_time_class_breakdown
                                        
        # Dates
        device_component_dates = pd.DataFrame(date_dict)
        
        if device_component_dates.empty:
            device_install_finish = None
        else:
            device_install_finish = device_component_dates["End"].max()
        
                                        
        ### Electrical phase
        cost_dict, time_dict, date_dict = self._init_phase_dicts()
        
        if any('dynamic' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                                            'Installation of dynamic cables']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_dynamic_cable_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Dynamic Cables',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('export' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                                    'Installation of static export cables']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_export_cable_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Export Cables',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('array' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                                    'Installation of static array cables']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)

            self.data.install_array_cable_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Inter-Array Cables',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('surface piercing' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                    'Installation of collection point (surface piercing)']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_surface_piercing_substation_dates = \
                                                                phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Collection Points',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)
        
        ### TODO: UPDATE
        # Mat - you may wish to combine with the above
        if any('seabed' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                    'Installation of collection point (seabed)']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_subsea_collection_point_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Collection Points',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('cable protection' in phase for phase in installed_phases):

            values = installation_output['OPERATION']\
                ['Installation of external cable protection']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_cable_protection_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'External Cable Protection',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)
            
        electrical_component_costs = pd.DataFrame(cost_dict)
        
        if electrical_component_costs.empty:
            
            electrical_component_costs = None
            electrical_component_cost_breakdown = None
            electrical_cost_class_breakdown = None
            
        else:

            electrical_component_costs = \
                            electrical_component_costs.set_index("Component")
            electrical_component_cost_breakdown = \
                            electrical_component_costs.sum(1).to_dict()
            electrical_cost_class_breakdown = electrical_component_costs.sum(
                                                 numeric_only=True).to_dict()
            electrical_component_costs = \
                            electrical_component_costs.reset_index()
                
        self.data.electrical_component_costs = electrical_component_costs
        self.data.electrical_component_cost_breakdown = \
                                        electrical_component_cost_breakdown
        self.data.electrical_cost_class_breakdown = \
                                        electrical_cost_class_breakdown
        
        electrical_component_times = pd.DataFrame(time_dict)
        
        if electrical_component_times.empty:
            
            electrical_component_times = None
            electrical_component_time_breakdown = None
            electrical_time_class_breakdown = None
            
        else:

            electrical_component_times = \
                            electrical_component_times.set_index("Component")
            electrical_component_time_breakdown = \
                            electrical_component_times.sum(1).to_dict()
            electrical_time_class_breakdown = electrical_component_times.sum(
                                                numeric_only=True).to_dict()
            electrical_component_times = \
                            electrical_component_times.reset_index()
                        
        self.data.electrical_component_times = electrical_component_times
        self.data.electrical_component_time_breakdown = \
                                        electrical_component_time_breakdown
        self.data.electrical_time_class_breakdown = \
                                        electrical_time_class_breakdown
                                        
        # Dates
        electrical_component_dates = pd.DataFrame(date_dict)
        
        if electrical_component_dates.empty:
            electrical_install_finish = None
        else:
            electrical_install_finish = electrical_component_dates["End"].max()
        
        
        ### M&F phase
        cost_dict, time_dict, date_dict = self._init_phase_dicts()
                                        
        if any('driven piles' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                        'Installation of driven piles anchors/foundations']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)

            self.data.install_driven_piles_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                'Driven Piles',
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('direct-embedment' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
               'Installation of mooring systems with direct-embedment anchors']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_direct_embedment_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                "Direct-Embedment Anchors",
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)
            
        if any('gravity based' in phase for phase in installed_phases):
            
            values = installation_output['OPERATION'][
                                'Installation of gravity based foundations']

            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_gravity_based_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                "Gravity Based Foundations",
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)
                
        if any('pile anchor' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                        'Installation of mooring systems with pile anchors']
                
            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)
            
            self.data.install_pile_anchor_dates = phase_date_dict
            
            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                "Pile Anchors",
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('drag-embedment' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
                'Installation of mooring systems with drag-embedment anchors']
            
            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)

            self.data.install_drag_embedment_dates = phase_date_dict

            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                "Drag-Embedment Anchors",
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        if any('suction-embedment' in phase for phase in installed_phases):

            values = installation_output['OPERATION'][
              'Installation of mooring systems with suction-embedment anchors']
              
            phase_cost_dict = installation_phase_cost_output(values)
            phase_time_dict = installation_phase_time_result(values)
            phase_date_dict = installation_phase_date_result(values)

            self.data.install_suction_embedment_dates = phase_date_dict

            self._compile_phase(cost_dict,
                                time_dict,
                                date_dict,
                                "Suction-Caisson Anchors",
                                phase_cost_dict,
                                phase_time_dict,
                                phase_date_dict)

        mooring_component_costs = pd.DataFrame(cost_dict)
        
        if mooring_component_costs.empty:
            
            mooring_component_costs = None
            mooring_component_cost_breakdown = None
            mooring_cost_class_breakdown = None
            
        else:

            mooring_component_costs = \
                            mooring_component_costs.set_index("Component")
            mooring_component_cost_breakdown = \
                            mooring_component_costs.sum(1).to_dict()
            mooring_cost_class_breakdown = mooring_component_costs.sum(
                                                 numeric_only=True).to_dict()
            mooring_component_costs = \
                            mooring_component_costs.reset_index()
                
        self.data.mooring_component_costs = mooring_component_costs
        self.data.mooring_component_cost_breakdown = \
                                        mooring_component_cost_breakdown
        self.data.mooring_cost_class_breakdown = \
                                        mooring_cost_class_breakdown
        
        mooring_component_times = pd.DataFrame(time_dict)
        
        if mooring_component_times.empty:
            
            mooring_component_times = None
            mooring_component_time_breakdown = None
            mooring_time_class_breakdown = None
            
        else:

            mooring_component_times = \
                            mooring_component_times.set_index("Component")
            mooring_component_time_breakdown = \
                            mooring_component_times.sum(1).to_dict()
            mooring_time_class_breakdown = mooring_component_times.sum(
                                                numeric_only=True).to_dict()
            mooring_component_times = \
                            mooring_component_times.reset_index()
                        
        self.data.mooring_component_times = mooring_component_times
        self.data.mooring_component_time_breakdown = \
                                        mooring_component_time_breakdown
        self.data.mooring_time_class_breakdown = \
                                        mooring_time_class_breakdown
                                        
        # Dates
        mooring_component_dates = pd.DataFrame(date_dict)
        
        if mooring_component_dates.empty:
            mooring_install_finish = None
        else:
            mooring_install_finish = mooring_component_dates["End"].max()

            
        ### Cost & year agregation
        phase_costs = {}
        phase_years = {}

        if device_component_cost_breakdown is not None:
                            
            cost = sum(device_component_cost_breakdown.values())
            year = device_install_finish.year - \
                            self.data.project_start_date.year + 1
            
            phase_costs["Devices"] = cost
            phase_years["Devices"] = year
            
        if electrical_component_cost_breakdown is not None:
            
            cost = sum(electrical_component_cost_breakdown.values())
            year = electrical_install_finish.year - \
                            self.data.project_start_date.year + 1
            
            phase_costs["Electrical Sub-Systems"] = cost
            phase_years["Electrical Sub-Systems"] = year
            
        if mooring_component_cost_breakdown is not None:
            
            cost = sum(mooring_component_cost_breakdown.values())
            year = mooring_install_finish.year - \
                            self.data.project_start_date.year + 1
            
            phase_costs["Mooring and Foundations"] = cost
            phase_years["Mooring and Foundations"] = year
        
                                    
        if not phase_costs: phase_costs = None
        
        cost_classes = {'Equipment': 0.,
                        'Vessel': 0.,
                        'Port': 0.}
        record_classes = False
                    
        if device_cost_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in ['Equipment', 'Vessel', 'Port']:
                
                cost_classes[class_name] += \
                                    device_cost_class_breakdown[class_name]

        if electrical_cost_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in ['Equipment', 'Vessel', 'Port']:
                
                cost_classes[class_name] += \
                                    electrical_cost_class_breakdown[class_name]

        if mooring_cost_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in ['Equipment', 'Vessel', 'Port']:
                
                cost_classes[class_name] += \
                                    mooring_cost_class_breakdown[class_name]

        if not record_classes:
            
            cost_classes = None
            
        else:

            # Assert against module values
            assert np.isclose(cost_classes['Equipment'],
                              installation_output['COST'][
                                                'Total Equipment Cost [EUR]'])

            assert np.isclose(cost_classes['Vessel'],
                              installation_output['COST'][
                                                  'Total Vessel Cost [EUR]'])

            assert np.isclose(cost_classes['Port'],
                              installation_output['COST'][
                                                  'Total Port Cost [EUR]'])

        if phase_costs is not None and cost_classes is not None:
            
            total_phase_costs = sum(phase_costs.values())
            total_class_costs = sum(cost_classes.values())
            
            assert np.isclose(total_phase_costs, total_class_costs)

            total_costs = total_phase_costs

            assert np.isclose(total_costs,
                              installation_output['COST'][
                                          'Total Installation Cost [EUR]'])
            
        else:
            
            total_costs = None

        ### Contingency
        contingency = installation_output['COST'][
                                            'Total Contingency Costs [EUR]']

        if contingency > 0.:
            
            phase_costs['Contingency'] = contingency
            cost_classes['Contingency'] = contingency

            if total_costs is None:
                total_costs = contingency
            else:
                total_costs += contingency
                
            # Get latest date
            max_date = max(phase_years.values())
            phase_years['Contingency'] = max_date
                
        self.data.total_phase_costs = phase_costs
        self.data.total_class_costs = cost_classes
        self.data.total_costs = total_costs
            
        ### Time agregation
        phase_times = {}

        if device_component_time_breakdown is not None:
            phase_times["Devices"] = \
                            sum(device_component_time_breakdown.values())
            
        if electrical_component_time_breakdown is not None:
            phase_times["Electrical Sub-Systems"] = \
                            sum(electrical_component_time_breakdown.values())
            
        if mooring_component_time_breakdown is not None:
            phase_times["Mooring and Foundations"] = \
                            sum(mooring_component_time_breakdown.values())
                                    
        if not phase_times: phase_times = None
        
        time_classes = {'Preparation': 0.,
                        'Transit': 0.,
                        'Waiting': 0.,
                        'Operations': 0.}
        time_class_names = ['Preparation', 'Transit', 'Waiting', 'Operations']
        record_classes = False
                    
        if device_time_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in time_class_names:
                
                time_classes[class_name] += \
                                    device_time_class_breakdown[class_name]

        if electrical_time_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in time_class_names:
                
                time_classes[class_name] += \
                                    electrical_time_class_breakdown[class_name]

        if mooring_time_class_breakdown is not None:
            
            record_classes = True
                
            for class_name in time_class_names:
                
                time_classes[class_name] += \
                                    mooring_time_class_breakdown[class_name]

        if not record_classes:
            
            time_classes = None
            
        else:

            # Assert against module values
            assert np.isclose(time_classes['Waiting'],
                              installation_output['TIME'][
                                                  'Total Waiting Time [h]'])

            assert np.isclose(time_classes['Preparation'],
                              installation_output['TIME'][
                                            'Total Preparation Time [h]'])

            assert np.isclose(time_classes['Transit'],
                              installation_output['TIME'][
                                              'Total Sea Transit Time [h]'])
            
            assert np.isclose(time_classes['Operations'],
                              installation_output['TIME'][
                                              'Total Sea Operation Time [h]'])

        if phase_times is not None and time_classes is not None:
            
            total_phase_times = sum(phase_times.values())
            total_class_times = sum(time_classes.values())
            
            assert np.isclose(total_phase_times, total_class_times)

            total_times = total_phase_times

            assert np.isclose(total_times,
                              installation_output['TIME'][
                                          'Total Installation Time [h]'])
            
        else:
            
            total_times = None
            
        self.data.total_phase_times = phase_times
        self.data.total_class_times = time_classes
        self.data.total_times = total_times
        
        ### BOM
        key_ids = []
        costs = []
        years = []
        
        for key_id in phase_costs.keys():
            
            key_ids.append(key_id)
            costs.append(phase_costs[key_id])
            years.append(phase_years[key_id])
        
        bom_dict = {"Key Identifier": key_ids,
                    "Cost": costs,
                    "Quantity": [1] * len(phase_costs),
                    "Year": years}

        bom_df = pd.DataFrame(bom_dict)
        
        self.data.installation_bom = bom_df
        
        return
    
    @classmethod    
    def get_input_dict(cls, data,
                            meta,
                            bathymetry,
                            system_type,
                            array_layout,
                            electrical_network,
                            moorings_foundations_network,
                            zone):
        
        ### Equipment
        name_map = {"Class": "ROV class [-]",
                    "Depth Rating": "Depth rating [m]",
                    "Length": "Length [m]",
                    "Width": "Width [m]",
                    "Height": "Height [m]",
                    "Dry Mass": "Weight [t]",
                    "Payload": "Payload [t]",
                    "Manipulator Grip Force": "Manipulator grip force [N]",
                    "Additional Equipment Footprint": "AE footprint [m^2]",
                    "Additional Equipment Mass": "AE weight [t]",
                    "Number of Supervisors": "AE supervisor [-]",
                    "Number of Technicians": "AE technician [-]",
                    "Equipment Day Rate": "ROV day rate [EURO/day]",
                    "Supervisor Day Rate": "Supervisor rate [EURO/12h]",
                    "Technician Day Rate": "Technician rate [EURO/12h]"
                    }

        rov_df = data.rov
        rov_df = rov_df.drop(["Name"], 1)
        rov_df.loc[:, "Supervisor Day Rate"] *= 0.5
        rov_df.loc[:, "Technician Day Rate"] *= 0.5
        rov_df = rov_df.rename(columns=name_map)
        
        assert set(name_map.values()).issubset(set(rov_df.columns))

        # divers
        name_map = {"Max Operating Depth": "Max operating depth [m]",
                    "Deployment Equipment Footprint":
                        "Deployment eq. footprint [m^2]",
                    "Deployment Equipment Mass": "Deployment eq. weight [t]",
                    "Total Day Rate": "Total day rate [EURO/day]"
                    }

        divers_df = data.divers
        divers_df = divers_df.drop(["Name"], 1)
        divers_df = divers_df.rename(columns=name_map)
        
        assert set(name_map.values()).issubset(set(divers_df.columns))
        
        # cable_burial
        name_map = {"Max Operating Depth": "Max operating depth [m]",
                    "Tow Force Required": "Tow force required [t]",
                    "Length": "Length [m]",
                    "Width": "Width [m]",
                    "Height": "Height [m]",
                    "Dry Mass": "Weight [t]",
                    "Jetting Capability": "Jetting capability [yes/no]",
                    "Ploughing Capability": "Ploughing capability [yes/no]",
                    "Cutting Capability": "Cutting capability [yes/no]",
                    "Jetting Trench Depth": "Jetting trench depth [m]",
                    "Ploughing Trench Depth": "Ploughing trench depth [m]",
                    "Cutting Trench Depth": "Cutting trench depth [m]",
                    "Max Cable Diameter": "Max cable diameter [mm]",
                    "Min Cable Bending Radius":
                        "Min cable bending radius [m]",
                    "Additional Equipment Footprint": "AE footprint [m^2]",
                    "Additional Equipment Mass": "AE weight [t]",
                    "Equipment Day Rate": "Burial tool day rate [EURO/day]",
                    "Personnel Day Rate": "Personnel day rate [EURO/12h]"
                    }
        
        cable_burial_df = data.cable_burial
        cable_burial_df = cable_burial_df.drop(["Name"], 1)
        cable_burial_df.loc[:, "Personnel Day Rate"] *= 0.5
        cable_burial_df = cable_burial_df.rename(columns=name_map)
        
        assert set(name_map.values()).issubset(set(cable_burial_df.columns))
        
        # Map boolean columns to yes/no
        yes_no_map = {True: "yes",
                      False: "no"}
        
        cable_burial_df = cable_burial_df.replace(
                                {"Jetting capability [yes/no]": yes_no_map,
                                 "Ploughing capability [yes/no]": yes_no_map,
                                 "Cutting capability [yes/no]": yes_no_map
                                 })
        
        # excavating
        name_map = {"Depth Rating": "Depth rating [m]",
                    "Width": "Width [m]",
                    "Height": "Height [m]",
                    "Dry Mass": "Weight [t]",
                    "Equipment Day Rate": "Excavator day rate [EURO/day]",
                    "Personnel Day Rate": "Personnel day rate [EURO/12h]"
                    }

        excavating_df = data.excavating
        excavating_df = excavating_df.drop(["Name"], 1)
        excavating_df.loc[:, "Personnel Day Rate"] *= 0.5
        excavating_df = excavating_df.rename(columns=name_map)
        
        assert set(name_map.values()).issubset(set(excavating_df.columns))

        # mattresses
        name_map = {"Length": "Unit lenght [m]",
                    "Width": "Unit width [m]",
                    "Thickness": "Unit thickness [m]",
                    "Dry Mass": "Unit weight air [t]",
                    "Cost": "Cost per unit [EURO]"
                    }
        
        mattresses_df = data.mattresses
        mattresses_df = mattresses_df.drop(["Name"], 1)
        mattresses_df = mattresses_df.rename(columns=name_map)

        assert set(name_map.values()).issubset(set(mattresses_df.columns))
        
        # rock bags
        name_map = {"Dry Mass": "Weight [t]",
                    "Diameter": "Diameter [m]",
                    "Height": "Height [m]",
                    "Cost": "Cost per unit [EURO]"
                    }

        rock_bags_df = data.rock_bags
        rock_bags_df = rock_bags_df.drop(["Name"], 1)
        rock_bags_df = rock_bags_df.rename(columns=name_map)

        assert set(name_map.values()).issubset(set(rock_bags_df.columns))
        
        # split_pipes
        name_map = {"Length": "Unit length [mm]",
                    "Cost": "Cost per unit [EURO]"
                    }

        split_pipes_df = data.split_pipes
        split_pipes_df = split_pipes_df.drop(["Name"], 1)
        split_pipes_df = split_pipes_df.rename(columns=name_map)

        assert set(name_map.values()).issubset(set(split_pipes_df.columns))

        # hammer
        name_map = {"Depth Rating": "Depth rating [m]",
                    "Length": "Length [m]",
                    "Dry Mass": "Weight in air [t]",
                    "Min Pile Diameter": "Min pile diameter [mm]",
                    "Max Pile Diameter": "Max pile diameter [mm]",
                    "Additional Equipment Footprint": "AE footprint [m^2]",
                    "Additional Equipment Mass": "AE weight [t]",
                    "Equipment Day Rate": "Hammer day rate [EURO/day]",
                    "Personnel Day Rate": "Personnel day rate [EURO/12h]"
                    }

        hammer_df = data.hammer
        hammer_df = hammer_df.drop(["Name"], 1)
        hammer_df.loc[:, "Personnel Day Rate"] *= 0.5
        hammer_df = hammer_df.rename(columns=name_map)

        assert set(name_map.values()).issubset(set(hammer_df.columns))

        # drilling rigs
        name_map = {"Diameter": "Diameter [m]",
                    "Length": "Length [m]",
                    "Dry Mass": "Weight [t]",
                    "Drilling Diameter Range": "Drilling diameter range [m]",
                    "Max Drilling Depth": "Max drilling depth [m]",
                    "Max Water Depth": "Max water depth [m]",
                    "Additional Equipment Footprint": "AE footprint [m^2]",
                    "Additional Equipment Mass": "AE weight [t]",
                    "Equipment Day Rate": "Drill rig day rate [EURO/day]",
                    "Personnel Day Rate": "Personnel day rate [EURO/day]"
                    }

        drilling_rigs_df = data.drilling_rigs
        drilling_rigs_df = drilling_rigs_df.drop(["Name"], 1)
        drilling_rigs_df = drilling_rigs_df.rename(columns=name_map)

        assert set(name_map.values()).issubset(set(drilling_rigs_df.columns))

        # vibro driver
        name_map = {"Width": "Width [m]",
                    "Length": "Length [m]",
                    "Height": "Height [m]",
                    "Vibro Driver Mass": "Vibro driver weight [m]",
                    "Clamp Mass": "Clamp weight [m]",
                    "Min Pile Diameter": "Min pile diameter [mm]",
                    "Max Pile Diameter": "Max pile diameter [mm]",
                    "Max Pile Mass": "Max pile weight [t]",
                    "Additional Equipment Footprint": "AE footprint [m^2]",
                    "Additional Equipment Mass": "AE weight [t]",
                    "Equipment Day Rate": "Vibro diver day rate [EURO/day]",
                    "Personnel Day Rate": "Personnel day rate [EURO/day]"
                    }

        vibro_driver_df = data.vibro_driver
        vibro_driver_df = vibro_driver_df.drop(["Name"], 1)
        vibro_driver_df = vibro_driver_df.rename(columns=name_map)
        
        assert set(name_map.values()).issubset(set(vibro_driver_df.columns))

        ### make equipment class here
        # Divide cable burial equipments per trenching capabilities
        jetting_trenchers = (
            cable_burial_df[
                cable_burial_df['Jetting capability [yes/no]'] == 'yes'])
        plough_trenchers = (
            cable_burial_df[
                cable_burial_df['Ploughing capability [yes/no]'] == 'yes'])
        cutting_trenchers = (
            cable_burial_df[
                cable_burial_df['Cutting capability [yes/no]'] == 'yes'])
        
        equipment = {'rov': EquipmentType("rov", rov_df),
                     'divers': EquipmentType("divers", divers_df),
                     'jetter': EquipmentType("jetter", jetting_trenchers),
                     'plough': EquipmentType("plough", plough_trenchers),
                     'cutter': EquipmentType("cutter", cutting_trenchers),
                     'cable burial': EquipmentType("cable burial",
                                                   cable_burial_df),
                     'excavating': EquipmentType("excavating", excavating_df),
                     'mattress': EquipmentType("mattress", mattresses_df),
                     'rock filter bags': EquipmentType("rock_filter_bags",
                                                       rock_bags_df),
                     'split pipe': EquipmentType("split pipe",
                                                 split_pipes_df),
                     'hammer': EquipmentType("hammer", hammer_df),
                     'drilling rigs': EquipmentType("drilling rigs",
                                                    drilling_rigs_df),
                     'vibro driver': EquipmentType("vibro driver",
                                                   vibro_driver_df)
                     }
                     
        ### Ports
        name_map = {"Name": "Name [-]",
                    "Country": "Country [-]",
                    "Type of Terminal": "Type of terminal [Quay/Dry-dock]",
                    "Entrance Width": "Entrance width [m]",
                    "Terminal Length": "Terminal length [m]",
                    "Terminal Load Bearing": "Terminal load bearing [t/m^2]",
                    "Terminal Draught": "Terminal draught [m]",
                    "Terminal Area": "Terminal area [m^2]",
                    "Max Gantry Crane Lift Capacity":
                        "Max gantry crane lift capacity [t]",
                    "Max Tower Crane Lift Capacity":
                        "Max tower crane lift capacity [t]",
                    "Jacking Capability": "Jacking capability [yes/no]"
                    }

        ports_df = data.ports
        ports_df = ports_df.rename(columns=name_map)

        assert set(name_map.values()).issubset(set(ports_df.columns))
        
        # Add utm point and zone
        port_x = []
        port_y = []
        port_names = []
        port_utm_zone = []

        for name, point in data.port_locations.iteritems():
            
            port_names.append(name)
            
            lonlat = list(point.coords)[0]
            latlon = list(reversed(lonlat))
            x, y, utm_number, utm_letter = utm.from_latlon(*latlon)
            utm_zone_str = "{} {}".format(utm_number, utm_letter)
                        
            port_x.append(x)
            port_y.append(y)
            port_utm_zone.append(utm_zone_str)
            
        port_location_dict = {"Name [-]": port_names,
                              "UTM x [m]": port_x,
                              "UTM y [m]": port_y,
                              "UTM zone [-]": port_utm_zone}
        port_location_df = pd.DataFrame(port_location_dict)
        
        ports_df = pd.merge(ports_df, port_location_df, on="Name [-]")
        
        ports_df = ports_df.replace(
                                {"Jacking capability [yes/no]": yes_no_map})
        
        ### Vessels
        name_map = {"Vessel Type": "Vessel type [-]",
                    "Gross Tonnage": "Gross tonnage [ton]",
                    "Length": "Length [m]",
                    "Beam": "Beam [m]",
                    "Max Draft": "Max. draft [m]",
                    "Consumption": "Consumption [l/h]",
                    "Towing Consumption": "Consumption towing [l/h]",
                    "Transit Speed": "Transit speed [m/s]",
                    "Deck Space": "Deck space [m^2]",
                    "Max Deck Pressure": "Deck loading [t/m^2]",
                    "Max Cargo Mass": "Max. cargo [t]",
                    "Max Crane Load Mass": "Crane capacity [t]",
                    "Bollard Pull": "Bollard pull [t]",
                    "Number of Turntables": "Turntable number [-]",
                    "Turntable loading": "Turntable loading [t]",
                    "Max Turntable Load Mass": "Turntable loading [t]",
                    "Turntable Inner Diameter":
                        "Turntable inner diameter [m]",
                    "Cable Splice Capabilities": "Cable splice [yes/no]",
                    "Dynamic Positioning Capabilities": "DP [-]",
                    "Max Jack-Up Water Depth":
                        "JackUp max water depth [m]",
                    "Jack-Up Lowering Velocity": "JackUp speed down [m/min]",
                    "Max Jack-Up Payload": "JackUp max payload [t]",
                    "Anchor Handling Drum Capacity": "AH drum capacity [m]",
                    "Anchor Handling Winch Rated Pull":
                        "AH winch rated pull [t]",
                    "External  Personnel": "External  personnel [-]",
                    "Max Towing Hs": "OLC: Towing maxHs [m]",
                    "Max Jacking Hs": "OLC: Jacking maxHs [m]",
                    "Max Jacking Tp": "OLC: Jacking maxTp [s]",
                    "Max Jacking Current Velocity":
                        "OLC: Jacking maxCs [m/s]",
                    "Max Jacking Wind Velocity":
                        "OLC: Jacking maxWs [m/s]",
                    "Max Transit Hs": "OLC: Transit maxHs [m]",
                    "Max Transit Tp": "OLC: Transit maxTp [s]",
                    "Max Transit Current Velocity":
                        "OLC: Transit maxCs [m/s]",
                    "Max Transit Wind Velocity":
                        "OLC: Transit maxWs [m/s]",
                    "Mobilisation Time": "Mob time [h]",
                    "Mobilisation Percentage Cost": "Mob percentage [%]",
                    "Min Day Rate": "Op min Day Rate [EURO/day]",
                    "Max Day Rate": "Op max Day Rate [EURO/day]"
                    }
            
        data.helicopter["Vessel type [-]"] = "Helicopter"
        data.vessel_ahts["Vessel type [-]"] = "AHTS"
        data.vessel_multicat["Vessel type [-]"] = "Multicat"
        data.vessel_barge["Vessel type [-]"] = "Barge"
        data.vessel_crane_barge["Vessel type [-]"] = "Crane Barge"
        data.vessel_crane_vessel["Vessel type [-]"] = "Crane Vessel"
        data.vessel_csv["Vessel type [-]"] = "CSV"
        data.vessel_ctv["Vessel type [-]"] = "CTV"
        data.vessel_clb["Vessel type [-]"] = "CLB"
        data.vessel_clv["Vessel type [-]"] = "CLV"
        data.vessel_jackup_barge["Vessel type [-]"] = "JUP Barge"
        data.vessel_jackup_vessel["Vessel type [-]"] = "JUP Vessel"
        data.vessel_tugboat["Vessel type [-]"] = "Tugboat"

        vessels_df = pd.concat([data.helicopter,
                                data.vessel_ahts,
                                data.vessel_multicat,
                                data.vessel_crane_barge,
                                data.vessel_barge,
                                data.vessel_crane_vessel,
                                data.vessel_csv,
                                data.vessel_ctv,
                                data.vessel_clb,
                                data.vessel_clv,
                                data.vessel_jackup_barge,
                                data.vessel_jackup_vessel,
                                data.vessel_tugboat],
                                ignore_index=True,
                                sort=False)
        vessels_df = vessels_df.rename(columns=name_map)

        assert set(name_map.values()).issubset(set(vessels_df.columns))
        
        # Map boolean columns
        vessels_df = vessels_df.replace({"Cable splice [yes/no]": yes_no_map})
        
        ### Site
        site_df_unsort = bathymetry.to_dataframe()
                
        site_df = site_df_unsort.unstack(level='layer')
        site_df = site_df.swaplevel(1, 1, axis=1)
        site_df = site_df.sort_index(axis=1, level=1)
        site_df = site_df.reset_index()

        site_df.columns = [' '.join(col).strip()
                                        for col in site_df.columns.values]
        
        # Remove NaN points
        nullrows = pd.isnull(site_df).any(axis=1)
        site_df = site_df[~nullrows]
                
        mapping = {"x":"x","y":"y"}

        for i in range (3,(len(site_df.columns))):
            split_name = site_df.columns.values[i].split()
            if split_name[0] == "sediment":
                mapping[site_df.columns.values[i]]= "layer {} type".format(
                                                                split_name[2])  
            elif split_name[0] == "depth":
                mapping[site_df.columns.values[i]]= "layer {} start".format(
                                                                split_name[2]) 

        site_df = site_df.rename(columns=mapping)
        
        # drop all layers above 1 for now
        layer_cols = [col for col in site_df.columns if 'layer' in col]

        if len(layer_cols) > 2:

            #drop cols greater than 1
            n_layers = len(layer_cols)/2
            layer_start_remove = ['layer ' + str(layer) + ' start' 
                                    for layer in range(2, n_layers+1)]
            layer_type_remove = ['layer ' + str(layer) + ' type' 
                                    for layer in range(2, n_layers+1)]
            layer_remove = layer_start_remove + layer_type_remove
            site_df.drop(layer_remove, axis=1)

        # Convert soil types to short codes
        soil_map = {'loose sand': 'ls',
                    'medium sand': 'ms',
                    'dense sand': 'ds',
                    'very soft clay': 'vsc',
                    'soft clay': 'sc',
                    'firm clay': 'fc',
                    'stiff clay': 'stc',
                    'hard glacial till': 'hgt',
                    'cemented': 'cm',
                    'soft rock coral': 'src',
                    'hard rock': 'hr',
                    'gravel cobble': 'gc'}

        site_df["layer 1 type"] = \
            site_df["layer 1 type"].map(soil_map)

        name_map = {
            "x": "x coord [m]",
            "y": "y coord [m]",
            # "zone": "zone [-]",
            "depth layer 1": "bathymetry [m]",
            "layer 1 type": "soil type [-]"
            }

        site_df = site_df.rename(columns=name_map)
        
        site_zone = [zone] * len(site_df)
        site_df.loc[:, 'zone [-]'] = site_zone
        
        ### Export
        if data.export is not None:
        
            export_df_unsort = data.export.to_dataframe()
            
            export_df = export_df_unsort.unstack(level = 'layer')
            export_df = export_df.swaplevel(1, 1, axis=1)
            export_df = export_df.sort_index(axis=1, level=1)
            export_df = export_df.reset_index()
    
            export_df.columns = [' '.join(col).strip()
                                        for col in export_df.columns.values]
            
            # Remove NaN points
            nullrows = pd.isnull(export_df).any(axis=1)
            export_df = export_df[~nullrows]
    
            mapping = {"x":"x","y":"y"}
    
            for i in range (3,(len(export_df.columns))):
                split_name = export_df.columns.values[i].split()
                if split_name[0] == "sediment":
                    mapping[export_df.columns.values[i]] = \
                                        "layer {} type".format(split_name[2])  
                elif split_name[0] == "depth":
                    mapping[export_df.columns.values[i]] = \
                                        "layer {} start".format(split_name[2]) 
    
            export_df = export_df.rename(columns=mapping)
            
            # drop all layers above 1 for now
            layer_cols = [col for col in export_df.columns if 'layer' in col]
    
            if len(layer_cols) > 2:
    
                #drop cols greater than 1
                n_layers = len(layer_cols)/2
                layer_start_remove = ['layer ' + str(layer) + ' start' 
                                        for layer in range(2, n_layers+1)]
                layer_type_remove = ['layer ' + str(layer) + ' type' 
                                        for layer in range(2, n_layers+1)]
                layer_remove = layer_start_remove + layer_type_remove
                export_df.drop(layer_remove, axis=1)
    
            # Convert soil types to short codes
            soil_map = {'loose sand': 'ls',
                        'medium sand': 'ms',
                        'dense sand': 'ds',
                        'very soft clay': 'vsc',
                        'soft clay': 'sc',
                        'firm clay': 'fc',
                        'stiff clay': 'stc',
                        'hard glacial till': 'hgt',
                        'cemented': 'cm',
                        'soft rock coral': 'src',
                        'hard rock': 'hr',
                        'gravel cobble': 'gc'}
    
            export_df["layer 1 type"] = \
                export_df["layer 1 type"].map(soil_map)
    
            name_map = {
                "x": "x coord [m]",
                "y": "y coord [m]",
                # "zone": "zone [-]",
                "depth layer 1": "bathymetry [m]",
                "layer 1 type": "soil type [-]"
                }
    
            export_df = export_df.rename(columns=name_map)
    
            export_zone = [zone] * len(export_df)
            export_df.loc[:, 'zone [-]'] = export_zone
                
            # merge export and site data
            whole_area = export_df.append(site_df)
            
            # Remove dupilcate points
            whole_area = whole_area.drop_duplicates(subset=["x coord [m]",
                                                            "y coord [m]"])

        else:
            
            whole_area = site_df
            
        # Ensure that the index is monotonic
        whole_area = whole_area.reset_index(drop=True)
            
        # Switch sign on depths
        whole_area["bathymetry [m]"] = - whole_area["bathymetry [m]"]

        ### Metocean
        wave_series_df = data.wave_series
        tidal_series = data.tidal_series
        wind_series = data.wind_series
        
        wave_series_df = wave_series_df.sort_index()
        tidal_series = tidal_series.sort_index()
        wind_series = wind_series.sort_index()
        
        tidal_series_df = tidal_series.to_frame(name="Cs")
        wind_series_df = wind_series.to_frame(name="Ws")
        
        # Allow dates to differ by resetting to a default
        new_start = pd.to_datetime("01/01/1900", infer_datetime_format=True)
        
        start_offet = new_start - wave_series_df.index[0]
        wave_series_df = wave_series_df.shift(freq=start_offet)
        
        start_offet = new_start - tidal_series_df.index[0]
        tidal_series_df = tidal_series_df.shift(freq=start_offet)
        
        start_offet = new_start - wind_series_df.index[0]
        wind_series_df = wind_series_df.shift(freq=start_offet)
        
        # merge these on datetime index
        metocean_df = pd.merge(wave_series_df,
                               tidal_series_df,
                               how='left',
                               left_index=True, 
                               right_index=True)

        metocean_df = pd.merge(metocean_df,
                               wind_series_df,
                               how='left',
                               left_index=True,
                               right_index=True)
        
        # Ensure the index of the merged dataframe has a name
        metocean_df.index.name = 'DateTime'
            
        year = metocean_df.index.year
        month = metocean_df.index.month
        day = metocean_df.index.day
        hour = metocean_df.index.hour
        
        metocean_df.loc[:, 'year'] = year
        metocean_df.loc[:, 'month'] = month
        metocean_df.loc[:, 'day'] = day
        metocean_df.loc[:, 'hour'] = hour
                
        metocean_df.reset_index(inplace=True)
        metocean_df.drop('DateTime', axis=1, inplace=True)

        name_map = {
            "year": "year [-]",
            "month": "month [-]",
            "day": "day [-]",
            "hour": "hour [-]",
            "Hs": "Hs [m]",
            "Tp": "Tp [s]",
            "Ws": "Ws [m/s]",
            "Cs": "Cs [m/s]"
            }

        metocean_df = metocean_df.rename(columns=name_map)

        ### Device
        # get sub system list from sub systems var
        sub_system_list = []

        name_map = {"Prime Mover": "A",
                    "PTO": "B",
                    "Support Structure": "D"}

        sub_systems = data.sub_device
        sub_systems = sub_systems.rename(index=name_map)
        
        if data.control_system is not None:
            
            control_system = data.control_system
            control_system = control_system.rename(
                                               index={"Control System": "C"})
            
            sub_systems = pd.concat([sub_systems, control_system])
            
        # Ensure sub_systems is numeric
        sub_systems = sub_systems.apply(pd.to_numeric, args=('coerce',))
        
        # place limitation - A, B, C must be assembled at Port.
        restricted_stages = "[A,B,C"

        if data.two_stage_assembly:
            sub_assembly_strategy = restricted_stages + "],D"
        else:
            sub_assembly_strategy = restricted_stages + ",D]"

        sub_assembly_strategy = "({})".format(sub_assembly_strategy)

        # map device type to required strings        
        if 'floating' in system_type.lower():

            device_type ='float'

        else:

            device_type = 'fixed'

        if 'tidal' in system_type.lower():

            device_type = device_type + ' TEC'

        else:

            device_type = device_type + ' WEC'
            
        # Check a bollard pull has been given when towed
        if data.transportation_method == "Tow" and data.bollard_pull is None:
            
            errStr = ("If device is towed fo deployment, a bollard pull value "
                      "must be given.")
            raise ValueError(errStr)
            
        # Get installation limits from subsystems
        max_hs = sub_systems["Max Hs"].max()
        max_tp = sub_systems["Max Tp"].max()
        max_ws = sub_systems["Max Wind Velocity"].max()
        max_cs = sub_systems["Max Current Velocity"].max()

        device_dict = {
            "Type": [device_type],
            "Length": [data.system_length],
            "Width": [data.system_width],
            "Height": [data.system_height],
            "Dry Mass": [data.system_mass],
            "Sub-System List": [sub_system_list],
            "Assembly Strategy": [sub_assembly_strategy],
            "Assembly Duration": [data.assembly_duration],
            "Load Out": [data.load_out_method.lower()],
            "Transportation Method": [data.transportation_method.lower()],
            "Bollard Pull": [data.bollard_pull],
            "Connect Duration": [data.connect_duration],
            "Disconnect Duration": [data.disconnect_duration],
            "Max Hs": [max_hs],
            "Max Tp": [max_tp],
            "Max Wind Speed": [max_ws],
            "Max Current Speed": [max_cs],
            "Project Start Date": [data.project_start_date]
            }

        device_df = pd.DataFrame(device_dict)
        
        name_map = {
            "Type": "type [-]",
            "Length": "length [m]",
            "Width": "width [m]",
            "Height": "height [m]",
            "Dry Mass": "dry mass [kg]",
            "Sub-System List": "sub system list [-]",
            "Assembly Strategy": "assembly strategy [-]",
            "Assembly Duration": "assembly duration [h]",
            "Load Out": "load out [-]",
            "Transportation Method": "transportation method [-]",
            "Bollard Pull": "bollard pull [t]",
            "Connect Duration": "connect duration [h]",
            "Disconnect Duration": "disconnect duration [h]",
            "Max Hs": "max Hs [m]",
            "Max Tp": "max Tp [s]",
            "Max Wind Speed": "max wind speed [m/s]",
            "Max Current Speed": "max current speed [m/s]",
            "Project Start Date": "Project start date [-]"
            }

        device_df = device_df.rename(columns=name_map)
        
        ### Subdevice
        name_map = {
            "Length": "length [m]",
            "Width": "width [m]",
            "Height": "height [m]",
            "Dry Mass": "dry mass [kg]"}

        sub_device_df = sub_systems[name_map.keys()]
        sub_device_df = sub_device_df.rename(columns=name_map)

        ### Rates
        # Equipment penetration rate
        name_map = {
            "Loose Sand": "ls",
            "Medium Sand": "ms",
            "Dense Sand": "ds",
            "Very Soft Clay": "vsc",
            "Soft Clay": "sc",
            "Firm Clay": "fc",
            "Stiff Clay": "stc",
            "Hard Glacial Till": "hgt",
            "Cemented": "cm",
            "Soft Rock Coral": "src",
            "Hard Rock": "hr",
            "Gravel Cobble": "gc"
            }

        penetration_rate_df = data.penetration_rates
        penetration_rate_df = penetration_rate_df.rename(columns=name_map)
        
        technique_map = {"Drilling rig": "Drilling rig [m/h]",
                         "Hammer": "Hammer [m/h]",
                         "Vibro driver": "Vibro driver [m/h]",
                         "ROV with suction pump":
                             "ROV with suction pump [m/h]",
                         "ROV with jetting": "ROV with jetting [m/h]"}
        
        penetration_rate_df = penetration_rate_df.reset_index()
        penetration_rate_df = penetration_rate_df.replace(
                                                {"Technique": technique_map})
        penetration_rate_df = penetration_rate_df.set_index("Technique")

        # Installation soil compatibility/laying rate
        name_map = {
            "Loose Sand": "ls",
            "Medium Sand": "ms",
            "Dense Sand": "ds",
            "Very Soft Clay": "vsc",
            "Soft Clay": "sc",
            "Firm Clay": "fc",
            "Stiff Clay": "stc",
            "Hard Glacial Till": "hgt",
            "Cemented": "cm",
            "Soft Rock Coral": "src",
            "Hard Rock": "hr",
            "Gravel Cobble": "gc"
            }

        laying_rate_df = data.installation_soil_compatibility
        laying_rate_df = laying_rate_df.rename(columns=name_map)

        index_map = {"Ploughing": "Ploughing [m/h]",
                     "Jetting": "Jetting [m/h]",
                     "Cutting": "Cutting [m/h]",
                     "Dredging": "Dredging [m/h]"
                     }
        
        laying_rate_df = laying_rate_df.rename(index = index_map)

        # other rates
        vals = [data.surface_laying_rate,
                data.split_pipe_laying_rate,
                data.loading_rate,
                data.grout_rate,       
                data.fuel_cost_rate,
                data.port_cost,
                data.commission_time,
                data.cost_contingency]

        idx = ['Surface laying [m/h]',
               'Installation of iron cast split pipes [m/h]',
               'Loading rate [m/h]',
               'Grout rate [m3/h]',
               'Fuel cost rate [EUR/l]',
               'Port percentual cost [%]',
               'Comissioning time [weeks]',
               'Cost Contingency [%]'
               ]

        other_rates_df = pd.DataFrame({"Default values": vals}, index = idx)

        ### Safety factors
        # port
        name_map = {
            "Parameter": "Port parameter and unit [-]",
            "Safety Factor": "Safety factor (in %) [-]"
            }

        port_safety_factor_df = data.port_safety_factors.reset_index()
        port_safety_factor_df = port_safety_factor_df.rename(columns=name_map)
        port_safety_factor_df = port_safety_factor_df.apply(pd.to_numeric,
                                                            errors='ignore')
        
        
        # Fix nans
        if np.isnan(port_safety_factor_df["Safety factor (in %) [-]"]).any():
            
            logMsg = ("Detected missing safety factors for ports. Setting to "
                      "1")
            module_logger.warning(logMsg)
            
            port_safety_factor_df = port_safety_factor_df.fillna(1)
        
        # Correct safety factors
        port_safety_factor_df["Safety factor (in %) [-]"] += -1
        
        # vessel
        name_map = {
            "Parameter": "Vessel parameter and unit [-]",
            "Safety Factor": "Safety factor (in %) [-]"
            }

        vessel_safety_factor_df = data.vessel_safety_factors.reset_index()
        vessel_safety_factor_df = vessel_safety_factor_df.rename(
            columns=name_map)
        vessel_safety_factor_df = vessel_safety_factor_df.apply(
                                                            pd.to_numeric,
                                                            errors='ignore')
        
        # Fix nans
        if np.isnan(vessel_safety_factor_df["Safety factor (in %) [-]"]).any():
            
            logMsg = ("Detected missing safety factors for vessels. Setting "
                      "to 1")
            module_logger.warning(logMsg)
            
            vessel_safety_factor_df = vessel_safety_factor_df.fillna(1)
        
        # Correct safety factors
        vessel_safety_factor_df["Safety factor (in %) [-]"] += -1

        # equipment
        equipment_tables = [data.rov_safety_factors,
                            data.divers_safety_factors,
                            data.hammer_safety_factors,
                            data.vibro_driver_safety_factors,
                            data.cable_burial_safety_factors,
                            data.split_pipe_safety_factors]
                            
        type_ids = ['rov',
                    'divers',
                    'hammer',
                    'vibro_driver',
                    'cable_burial',
                    'split_pipe']
        
        column_map = {"Parameter": "Equipment parameter and unit [-]",
                      "Safety Factor": "Safety factor (in %) [-]",
                      }
                      
        mapped_tables = []
        
        for type_id, equipment_table in zip(type_ids, equipment_tables):
            
            equipment_table = equipment_table.reset_index()
            equipment_table = equipment_table.rename(columns=column_map)
            equipment_table["Equipment type id [-]"] = type_id

            mapped_tables.append(equipment_table)
        
        equipment_safety_factor_df = pd.concat(mapped_tables,
                                               ignore_index=True)
        equipment_safety_factor_df = equipment_safety_factor_df.apply(
                                                            pd.to_numeric,
                                                            errors='ignore')
        
        # Fix nans
        if np.isnan(
                equipment_safety_factor_df["Safety factor (in %) [-]"]).any():
            
            logMsg = ("Detected missing safety factors for equipment. Setting "
                      "to 1")
            module_logger.warning(logMsg)
            
            equipment_safety_factor_df = equipment_safety_factor_df.fillna(1)
        
        # Correct safety factors
        equipment_safety_factor_df["Safety factor (in %) [-]"] += -1
        
        ### Configuration options
        # Installation order
        device_order_dict = {
             u'Default order': {12: 0,
                                13: 1},
             u'id': {12: u'S_structure',
                     13: u'Device'},
             u'logistic phases group': {
                      12: u'Installation of devices',
                      13: u'Installation of devices'}}
                      
        device_order_df = pd.DataFrame(device_order_dict)
        
        device_order_increment = 0
        phase_order_tables = []
        
        if electrical_network is not None:

            # Increment the device installation order
            device_order_increment += 4

            electrical_order_dict = {
                 u'Default order': {0: 1,
                                    1: 3,
                                    2: 4,
                                    3: 0,
                                    4: 2,
                                    5: 4},
                 u'id': {0: u'E_export',
                         1: u'E_array',
                         2: u'E_external',
                         3: u'E_cp_seabed',
                         4: u'E_cp_surface',
                         5: u'E_dynamic'},
                 u'logistic phases group': {
                      0: u'Installation of electrical infrastructure',
                      1: u'Installation of electrical infrastructure',
                      2: u'Installation of static cable external protection',
                      3: u'Installation of electrical infrastructure',
                      4: u'Installation of electrical infrastructure',
                      5: u'Installation of electrical infrastructure'}}
                          
            electrical_order_df = pd.DataFrame(electrical_order_dict)
            phase_order_tables.append(electrical_order_df)
            
        if moorings_foundations_network is not None:

            # Increment the device installation order
            device_order_increment += 1

            mf_order_dict = {
             u'Default order': {6: 0,
                                7: 0,
                                8: 0,
                                9: 0,
                                10: 0,
                                11: 0},
             u'id': {6: u'Driven',
                     7: u'Gravity',
                     8: u'M_pile',
                     9: u'M_drag',
                     10: u'M_direct',
                     11: u'M_suction'},
             u'logistic phases group': {
                      6: u'Installation of moorings & foundations',
                      7: u'Installation of moorings & foundations',
                      8: u'Installation of moorings & foundations',
                      9: u'Installation of moorings & foundations',
                      10: u'Installation of moorings & foundations',
                      11: u'Installation of moorings & foundations'}}
                          
            mf_order_df = pd.DataFrame(mf_order_dict)
            phase_order_tables.append(mf_order_df)
            
        # Increment the order of device installation
        if device_order_increment > 4: device_order_increment = 4

        device_order_df['Default order'] += device_order_increment
        phase_order_tables.append(device_order_df)
        
        # Joint the tables
        phase_order_tables = [x for x in phase_order_tables if x is not None]
        phase_order_df = pd.concat(phase_order_tables)
        phase_order_df = phase_order_df.reindex()

        # Entry point
        entry_point_data = {'x coord [m]': data.entry_point.x,
                            'y coord [m]': data.entry_point.y,
                            'zone [-]': zone}

        entry_point_df = pd.DataFrame(entry_point_data, index = [0])

        # Operational limit conditions and algorithm control
        schedule_OLC = get_operations_template()
        start_shape = schedule_OLC.shape
                
        # Update default limits if provided
        if data.limit_hs is not None:
            
            limit_hs_series = pd.Series(data.limit_hs)
            limit_hs_series.name = "OLC: Hs [m]"
            limit_hs_series.index.name = "Logitic operation [-]"
            limit_hs_df = limit_hs_series.reset_index()
            
            merged = pd.merge(schedule_OLC,
                              limit_hs_df,
                              on="Logitic operation [-]",
                              how="left")
            
            has_value = pd.notnull(merged["OLC: Hs [m]_y"])
            to_update = merged["OLC: Hs [m]_y"][has_value]
            
            olc_updated = merged["OLC: Hs [m]_x"]
            olc_updated.update(to_update)
            olc_updated.index = schedule_OLC.index
                        
            schedule_OLC["OLC: Hs [m]"] = olc_updated

            # Check that the shape hasn't changed
            assert schedule_OLC.shape == start_shape
        
        if data.limit_tp is not None:

            limit_tp_series = pd.Series(data.limit_tp)
            limit_tp_series.name = "OLC: Tp [s]"
            limit_tp_series.index.name = "Logitic operation [-]"
            limit_tp_df = limit_tp_series.reset_index()
            
            merged = pd.merge(schedule_OLC,
                              limit_tp_df,
                              on="Logitic operation [-]",
                              how="left")
            
            has_value = pd.notnull(merged["OLC: Tp [s]_y"])
            to_update = merged["OLC: Tp [s]_y"][has_value]
            
            olc_updated = merged["OLC: Tp [s]_x"]
            olc_updated.update(to_update)
            olc_updated.index = schedule_OLC.index
            
            schedule_OLC["OLC: Tp [s]"] = olc_updated
            
            # Check that the shape hasn't changed
            assert schedule_OLC.shape == start_shape

        if data.limit_ws is not None:

            limit_ws_series = pd.Series(data.limit_ws)
            limit_ws_series.name = "OLC: Ws [m/s]"
            limit_ws_series.index.name = "Logitic operation [-]"
            limit_ws_df = limit_ws_series.reset_index()
            
            merged = pd.merge(schedule_OLC,
                              limit_ws_df,
                              on="Logitic operation [-]",
                              how="left")
            
            has_value = pd.notnull(merged["OLC: Ws [m/s]_y"])
            to_update = merged["OLC: Ws [m/s]_y"][has_value]
            
            olc_updated = merged["OLC: Ws [m/s]_x"]
            olc_updated.update(to_update)
            olc_updated.index = schedule_OLC.index
            
            schedule_OLC["OLC: Ws [m/s]"] = olc_updated
            
            # Check that the shape hasn't changed
            assert schedule_OLC.shape == start_shape

        if data.limit_cs is not None:

            limit_cs_series = pd.Series(data.limit_cs)
            limit_cs_series.name = "OLC: Cs [m/s]"
            limit_cs_series.index.name = "Logitic operation [-]"
            limit_cs_df = limit_cs_series.reset_index()
            
            merged = pd.merge(schedule_OLC,
                              limit_cs_df,
                              on="Logitic operation [-]",
                              how="left")
            
            has_value = pd.notnull(merged["OLC: Cs [m/s]_y"])
            to_update = merged["OLC: Cs [m/s]_y"][has_value]
            
            olc_updated = merged["OLC: Cs [m/s]_x"]
            olc_updated.update(to_update)
            olc_updated.index = schedule_OLC.index
            
            schedule_OLC["OLC: Cs [m/s]"] = olc_updated
            
            # Check that the shape hasn't changed
            assert schedule_OLC.shape == start_shape
                
        ### Hydrodynamics                            
        device, x, y  = zip(*[(key.lower(), item.x, item.y)
                            for key, item in array_layout.items()])      
        
        layout_dict = {'Device': device,
                       'UTM X': x,
                       'UTM Y': y}

        layout_df = pd.DataFrame(layout_dict)
        
        name_map = {"Device": "device [-]",
                    "UTM X": "x coord [m]",
                    "UTM Y": "y coord [m]"}

        layout_df = layout_df.rename(columns=name_map)

        layout_zone = [zone]*len(layout_df)
        layout_df.loc[:, 'zone [-]'] = pd.Series(layout_zone)

        index = layout_df.index.tolist()
        index = ['d' + str(val) for val in index]
        layout_df.index = index

        ### Electrical
        topology = 'type 1' # to be mapped from wp3

        if electrical_network is not None:
            
            if data.export is None:
                
                errStr = ("Cable corridor bathymetry must be provided"
                          " if electrical network is set")
                raise ValueError(errStr)
            
            elec_network_design = electrical_network['nodes']
            elec_hierarchy = electrical_network['topology']

            elec_component_data_df = data.electrical_components
            elec_substation_data = data.substations
            elec_static_cables_df = data.elec_db_static_cable
            elec_dry_mate_df = data.elec_db_dry_mate
            elec_wet_mate_df = data.elec_db_wet_mate
            cable_route_df = data.cable_routes
            landfall = data.landfall
            
            missing_titles = []
            
            if elec_component_data_df is None:
                missing_titles.append(meta.electrical_components.title)
            
            if elec_substation_data is None:
                missing_titles.append(meta.substations.title)
                
            if elec_static_cables_df is None:
                missing_titles.append(meta.elec_db_static_cable.title)
            
            if elec_dry_mate_df is None:
                missing_titles.append(meta.elec_db_dry_mate.title)
                
            if elec_wet_mate_df is None:
                missing_titles.append(meta.elec_db_wet_mate.title)
                
            if cable_route_df is None:
                missing_titles.append(meta.cable_routes.title)
                
            if landfall is None:
                missing_titles.append(meta.landfall.title)
                
            if data.cable_tool is None:
                missing_titles.append(meta.cable_tool.title)
            
            if missing_titles:

                var_str = "Variable"
                if len(missing_titles) > 1: var_str += "s"
                
                title_str = "title"
                if len(missing_titles) > 1: title_str += "s"
                
                quote_missing = ["'{}'".format(x) for x in missing_titles]
                all_missing = ", ".join(quote_missing)
                
                errStr = ("Complete electrical network data has not been "
                          "provided. {} with {} {} must be "
                          "satisfied.").format(var_str, title_str, all_missing)
                raise ValueError(errStr)
            
            collection_point_df = set_collection_points(elec_component_data_df,
                                                        elec_network_design,
                                                        elec_hierarchy,
                                                        elec_substation_data)

            cp_zone = [zone]*len(collection_point_df)
            collection_point_df.loc[:, 'Zone'] = pd.Series(cp_zone)

            name_map = {"Downstream Interface Type": "downstream ei type [-]",
                        "Pigtail Cable Mass":
                                "pigtails cable dry mass [kg/m]",
                        "Downstream Interface Marker": "downstream ei id [-]",
                        "Upstream Interface Marker": "upstream ei id [-]",
                        "N Pigtails": "nr pigtails [-]",
                        "Pigtail Total Mass": "pigtails total dry mass [kg]",
                        "Height": "height [m]",
                        "Width": "width [m]",
                        "Length": "length [m]",
                        "Upstream Interface Type": "upstream ei type [-]",
                        "Mass": "dry mass [kg]",
                        "X Coord": "x coord [m]",
                        "Y Coord": "y coord [m]",
                        "Pigtail Length": "pigtails length [m]",
                        "Type": "type [-]",
                        "Pigail Diameter": "pigtails diameter [mm]",
                        "Zone": "zone [-]"}

            collection_point_df = collection_point_df.rename(columns=name_map)

            static_cable_df = set_cables(elec_component_data_df,
                                         elec_network_design,
                                         elec_hierarchy,
                                         elec_static_cables_df,
                                         'static')

            static_cable_df = set_cable_cp_references(static_cable_df,
                                                      collection_point_df)

            name_map = {"Type": "type [-]",
                        "Length": "length [m]",
                        "Upstream Interface Marker": "upstream ei id [-]",
                        "Downstream Interface Marker": "downstream ei id [-]",
                        "Upstream Interface Type": "upstream ei type [-]",
                        "Downstream Interface Type": "downstream ei type [-]",
                        "Upstream Component Type":
                            "upstream termination type [-]",
                        "Upstream Component Id": "upstream termination id [-]",
                        "Downstream Component Type":
                            "downstream termination type [-]",
                        "Downstream Component Id":
                            "downstream termination id [-]",
                        "Mass": "dry mass [kg/m]",
                        "Diameter": "diameter [mm]",
                        "MBR": "MBR [m]",
                        "MBL": "MBL [N]",
                        "Total Mass": "total dry mass [kg]"}

            static_cable_df = static_cable_df.rename(columns=name_map)

            trenching = [[data.cable_tool.lower()]]*len(static_cable_df)
            static_cable_df.loc[:, 'trench type [-]'] = pd.Series(trenching)
            static_cable_df = static_cable_df.set_index('Marker')
            static_cable_df.index.name = 'id [-]'
            
            if 'floating' in system_type.lower():
                
                if data.elec_db_dynamic_cable is None:
                    
                    errStr = ("The dynamic electrical cable database must be "
                              "provided for electrical network installation "
                              "of floating devices")
                    raise ValueError(errStr)
                
                if data.umbilical_terminations is None:
                    
                    errStr = ("The umbilical seabed connection points must be "
                              "provided for electrical network installation "
                              "of floating devices")
                    raise ValueError(errStr)

                dynamic_cable_df = set_cables(elec_component_data_df,
                                              elec_network_design,
                                              elec_hierarchy,
                                              data.elec_db_dynamic_cable,
                                              'dynamic')

                umbilical_ends = {name.lower(): val for name, val in
                                      data.umbilical_terminations.items()}

                terminations = get_umbilical_terminations(
                                    electrical_network['nodes'],
                                    umbilical_ends,
                                    dynamic_cable_df,
                                    layout_df)

                dynamic_cable_df = pd.merge(dynamic_cable_df,
                                            terminations,
                                            on=['Marker'])
                    
                dynamic_cable_df = set_cable_cp_references(dynamic_cable_df,
                                                           collection_point_df)

                name_map = {"Type": "type [-]",
                            "Length": "length [m]",
                            "Upstream Interface Marker": "upstream ei id [-]",
                            "Downstream Interface Marker":
                            "downstream ei id [-]",
                            "Upstream Interface Type": "upstream ei type [-]",
                            "Downstream Interface Type":
                            "downstream ei type [-]",
                            "Upstream Component Type":
                                "upstream termination type [-]",
                            "Upstream Component Id":
                            "upstream termination id [-]",
                            "Downstream Component Type":
                                "downstream termination type [-]",
                            "Downstream Component Id":
                                "downstream termination id [-]",
                            "Mass": "dry mass [kg/m]",
                            "Diameter": "diameter [mm]",
                            "MBR": "MBR [m]",
                            "MBL": "MBL [N]",
                            "Total Mass": "total dry mass [kg]",
                            'Upstream UTM X' :
                                'upstream termination x coord [m]',
                            'Upstream UTM Y' :
                                'upstream termination y coord [m]',
                            'Downstream UTM X' :
                                'downstream termination x coord [m]',
                            'Downstream UTM Y' :
                                'downstream termination y coord [m]'}

                dynamic_cable_df = dynamic_cable_df.rename(columns=name_map)

                dynamic_cable_zone = [zone]*len(dynamic_cable_df)

                dynamic_cable_df.loc[:, 'downstream termination zone [-]'] = \
                    pd.Series(dynamic_cable_zone)

                dynamic_cable_df.loc[:, 'upstream termination zone [-]'] = \
                    pd.Series(dynamic_cable_zone)
                                    
                ### TODO: UPDATE
                # If wp4 runs this data can be added
                buoyancy_number = []*len(dynamic_cable_df)
                buoyancy_diameter = []*len(dynamic_cable_df)
                buoyancy_length = []*len(dynamic_cable_df)
                buoyancy_weight = []*len(dynamic_cable_df)
                cable_weight = [1]*len(dynamic_cable_df)
                
                dynamic_cable_df.loc[:, 'buoyancy number [-]'] = \
                    pd.Series(buoyancy_number)
                
                dynamic_cable_df.loc[:, 'buoyancy length [m]'] = \
                    pd.Series(buoyancy_length)
                
                dynamic_cable_df.loc[:, 'buoyancy weigth [kg]'] = \
                    pd.Series(buoyancy_weight)
                
                dynamic_cable_df.loc[:, 'buoyancy diameter [mm]'] = \
                    pd.Series(buoyancy_diameter)
                
                dynamic_cable_df.loc[:, 'dry mass [kg/m]'] = \
                    pd.Series(cable_weight)

            else:

                dynamic_cable = {"dry mass [kg/m]": {},
                                 "total dry mass [kg]": {},
                                 "length [m]": {},
                                 "diameter [mm]": {},
                                 "MBR [m]": {},
                                 "MBL [N]": {},
                                 "upstream termination type [-]": {},
                                 "upstream termination id [-]": {},
                                 "upstream termination x coord [m]": {},
                                 "upstream termination y coord [m]": {},
                                 "upstream termination zone [-]": {},
                                 "downstream termination type [-]": {},
                                 "downstream termination id [-]": {},
                                 "downstream termination x coord [m]": {},
                                 "downstream termination y coord [m]": {},
                                 "downstream termination zone [-]": {},
                                 "upstream ei type [-]": {},
                                 "upstream ei id [-]": {},
                                 "downstream ei type [-]": {},
                                 "downstream ei id [-]": {},
                                 "buoyancy number [-]": {},
                                 "buoyancy diameter [mm]": {},
                                 "buoyancy length [m]": {},
                                 "buoyancy weigth [kg]": {}} # typo in wp5
    
                dynamic_cable_df = pd.DataFrame(dynamic_cable, dtype = object)

            name_map = {"Burial Depth": "burial depth [m]",
                        "Split Pipe": "split pipe [-]",
                        "UTM X": "x coord [m]",
                        "UTM Y": "y coord [m]",
                        "Depth": 'bathymetry [m]',
                        "Sediment": 'soil type [-]',
                        "Marker": "static cable id [-]",
                        }

            cable_route_df = data.cable_routes.rename(columns=name_map)
            
            cable_zone = [zone]*len(data.cable_routes)
            cable_route_df['zone [-]'] = cable_zone
            cable_route_df['bathymetry [m]'] = \
                                            - cable_route_df['bathymetry [m]']
            cable_route_df = cable_route_df.replace(
                                            {"split pipe [-]": yes_no_map})
                                            
            # Convert soil types to short codes
            soil_map = {'loose sand': 'ls',
                        'medium sand': 'ms',
                        'dense sand': 'ds',
                        'very soft clay': 'vsc',
                        'soft clay': 'sc',
                        'firm clay': 'fc',
                        'stiff clay': 'stc',
                        'hard glacial till': 'hgt',
                        'cemented': 'cm',
                        'soft rock coral': 'src',
                        'hard rock': 'hr',
                        'gravel cobble': 'gc'}
    
            cable_route_df['soil type [-]'] = \
                cable_route_df['soil type [-]'].map(soil_map)
                
            connector_db = elec_dry_mate_df.append(elec_wet_mate_df,
                                                   sort=False)

            connectors_df = \
                set_connectors(elec_component_data_df, connector_db)

            connectors_df.index.name = 'id [-]'

            name_map = {"Demating Force": "demating force [N]",
                        "Height": "height [m]",
                        "Length": "lenght [m]",
                        "Mass": "dry mass [kg]",
                        "Mating Force": "mating force [N]",
                        "Width": "width [m]"
                        }

            connectors_df = connectors_df.rename(columns=name_map)

            external_protection = {"protection type [-]": {},
                                   "x coord [m]": {},
                                   "y coord [m]": {},
                                   "zone [-]": {}}

            external_protection_df = \
                    pd.DataFrame(external_protection, dtype = object)
                    
            ### Landfall
            technique_map = {"Horizontal Directional Drilling": "HDD",
                             "Open Cut Trenching": "OCT"}
            technique = technique_map[landfall]
            
            landfall_dict = {"method [-]": [technique]}
            landfall_df = pd.DataFrame(landfall_dict)

        else:

            # make empty data structures
            collection_point = {"type [-]": {},
                                 "x coord [m]": {},
                                 "y coord [m]": {},
                                 "zone [-]": {},
                                 "length [m]": {},
                                 "width [m]": {},
                                 "height [m]": {},
                                 "dry mass [kg]": {},
                                 "upstream ei type [-]": {},
                                 "upstream ei id [-]": {},
                                 "downstream ei type [-]": {},
                                 "downstream ei id [-]": {},
                                 "nr pigtails [-]": {},
                                 "pigtails length [m]": {},
                                 "pigtails diameter [mm]": {},
                                 "pigtails cable dry mass [kg/m]": {},
                                 "pigtails total dry mass [kg]": {}}

            collection_point_df = pd.DataFrame(collection_point)

            dynamic_cable = {"dry mass [kg/m]": {},
                             "total dry mass [kg]": {},
                             "length [m]": {},
                             "diameter [mm]": {},
                             "MBR [m]": {},
                             "MBL [N]": {},
                             "upstream termination type [-]": {},
                             "upstream termination id [-]": {},
                             "upstream termination x coord [m]": {},
                             "upstream termination y coord [m]": {},
                             "upstream termination zone [-]": {},
                             "downstream termination type [-]": {},
                             "downstream termination id [-]": {},
                             "downstream termination x coord [m]": {},
                             "downstream termination y coord [m]": {},
                             "downstream termination zone [-]": {},
                             "upstream ei type [-]": {},
                             "upstream ei id [-]": {},
                             "downstream ei type [-]": {},
                             "downstream ei id [-]": {},
                             "buoyancy number [-]": {},
                             "buoyancy diameter [mm]": {},
                             "buoyancy length [m]": {},
                             "buoyancy weigth [kg]": {}}

            dynamic_cable_df = pd.DataFrame(dynamic_cable, dtype = object)

            static_cable = {"type [-]": {},
                            "dry mass [kg/m]": {},
                            "total dry mass [kg]": {},
                            "length [m]": {},
                            "diameter [mm]": {},
                            "MBR [m]": {},
                            "MBL [N]": {},
                            "upstream termination type [-]": {},
                            "upstream termination id [-]": {},
                            "upstream ei type [-]": {},
                            "upstream ei id [-]": {},
                            "downstream termination type [-]": {},
                            "downstream termination id [-]": {},
                            "downstream ei type [-]": {},
                            "downstream ei id [-]": {},
                            "trench type [-]": {}}

            static_cable_df = pd.DataFrame(static_cable, dtype = object)

            cable_route = {"static cable id [-]": {},
                           "x coord [m]": {},
                           "y coord [m]": {},
                           "zone [-]": {},
                           "soil type [-]": {},
                           "bathymetry [m]": {},
                           "burial depth [m]": {},
                           "split pipe [-]": {}}

            cable_route_df = pd.DataFrame(cable_route, dtype = object)

            connectors = {"type [-]": {},
                          "dry mass [kg]": {},
                          "lenght [m]": {},
                          "width [m]": {},
                          "height [m]": {},
                          "mating force [N]": {},
                          "demating force [N]": {}}

            connectors_df = pd.DataFrame(connectors)

            external_protection = {"protection type [-]": {},
                                   "x coord [m]": {},
                                   "y coord [m]": {},
                                   "zone [-]": {}}

            external_protection_df = \
                    pd.DataFrame(external_protection, dtype = object)

            topology = None
            landfall_df = None
            
        arg_dict = {'equipment': equipment,
                    'ports_df': ports_df,
                    'phase_order_df': phase_order_df,
                    'vessels_df': vessels_df,
                    'schedule_OLC': schedule_OLC,
                    'penetration_rate_df': penetration_rate_df,
                    'laying_rate_df': laying_rate_df,
                    'other_rates_df': other_rates_df,
                    'port_safety_factor_df': port_safety_factor_df,
                    'vessel_safety_factor_df': vessel_safety_factor_df,
                    'equipment_safety_factor_df':
                        equipment_safety_factor_df,
                    'whole_area': whole_area,
                    'metocean_df': metocean_df,
                    'device_df': device_df,
                    'sub_device_df': sub_device_df,
                    'landfall_df': landfall_df,
                    'entry_point_df': entry_point_df,
                    'layout_df': layout_df,
                    'collection_point_df': collection_point_df,
                    'dynamic_cable_df': dynamic_cable_df,
                    'static_cable_df': static_cable_df,
                    'cable_route_df': cable_route_df,
                    'connectors_df': connectors_df,
                    'external_protection_df': external_protection_df,
                    'topology': topology}
                    
        return arg_dict
        
    def _init_phase_dicts(self):
        
        cost_dict = {"Component": [],
                     "Equipment": [],
                     "Port": [],
                     "Vessel": []}

        time_dict = {"Component": [],
                     "Preparation": [],
                     "Operations": [],
                     "Transit": [],
                     "Waiting": []}
        
        date_dict = {"Component": [],
                     "Start": [],
                     "Depart": [],
                     "End": []}

        return cost_dict, time_dict, date_dict
        
    def _compile_phase(self, cost_dict,
                             time_dict,
                             date_dict,
                             phase_name,
                             phase_cost_dict,
                             phase_time_dict,
                             phase_date_dict):
        
        cost_dict["Component"].append(phase_name)
        cost_dict["Equipment"].append(phase_cost_dict['Equipment'])
        cost_dict["Port"].append(phase_cost_dict['Port'])
        cost_dict["Vessel"].append(phase_cost_dict['Vessel'])
        
        time_dict["Component"].append(phase_name)
        time_dict["Preparation"].append(phase_time_dict['Prep'])
        time_dict["Operations"].append(phase_time_dict['Sea'])
        time_dict["Transit"].append(phase_time_dict['Transit'])
        time_dict["Waiting"].append(phase_time_dict['Wait'])
        
        date_dict["Component"].append(phase_name)
        date_dict["Start"].append(phase_date_dict["Start"])
        date_dict["Depart"].append(phase_date_dict["Depart"])
        date_dict["End"].append(phase_date_dict["End"])
        
        return
        
