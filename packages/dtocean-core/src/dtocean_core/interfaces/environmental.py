# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Vincenzo Nava
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
This module contains the package interface to the dtocean Environmental Impact 
Assessment functions.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: environmental
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package
   
.. moduleauthor:: Vincenzo Nava <vincenzo.nava@tecnalia.com>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import math
import pickle
import pkg_resources

import pandas as pd
import numpy as np

from polite.paths import Directory, ObjDirectory, UserDataDirectory
from polite.configuration import ReadINI
from aneris.boundary.interface import MaskVariable
from dtocean_environment.main import (HydroStage,
                                      ElectricalStage,
                                      MooringStage,
                                      InstallationStage,
                                      OperationMaintenanceStage)
                                     
from . import ThemeInterface
from ..utils.version import Version

# Check module version
pkg_title = "dtocean-environment"
major_version = 2
version = pkg_resources.get_distribution(pkg_title).version

if not Version(version).major == major_version:
    
    err_msg = ("Incompatible version of {} detected! Major version {} is "
               "required, but version {} is installed").format(pkg_title,
                                                               major_version,
                                                               version)
    raise ImportError(err_msg)


class EnvironmentalInterface(ThemeInterface):
    
    '''Interface to the environmental thematic functions.
    '''
    
    def __init__(self):
        
        super(EnvironmentalInterface, self).__init__()
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Environmental Impact Assessment (Experimental)"
    
    @classmethod
    def declare_weight(cls):
        
        return 3
    
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

        input_list  =  ["device.system_type",
                        "project.layout",
                        "site.lease_boundary",
                        "project.fishery_restricted_area",
                        "bathymetry.layers",
                        "project.number_of_devices",
                        
                         MaskVariable('device.system_draft',
                                      'device.system_type',
                                      ['Tidal Floating', 'Wave Floating']),
                        
                        "device.system_width",
                        "device.system_height",
                        "device.system_length",
                        "project.substation_props",
                        "project.substation_layout",                        
                        "project.moorings_dimensions",
                        "project.installation_journeys",
                        "project.installation_vessel_average_size",
                        "project.operation_journeys_mode",
                        "project.operat_vessel_average_size",
                        "farm.direction_of_max_surface_current", 
                        "project.resource_reduction",
                        "farm.initial_turbidity",
                        "project.hydro_measured_turbidity",
                        "project.install_measured_turbidity",
                        "project.operat_measured_turbidity",
                        "farm.initial_noise",
                        "project.hydro_measured_noise",
                        "project.elec_measured_noise",
                        "project.moor_measured_noise", 
                        "project.install_measured_noise",
                        "project.operat_measured_noise",
                        "farm.initial_elec_field",
                        "project.elec_measured_elec_field",
                        "farm.initial_magnetic_field",
                        "project.elec_measured_magnetic_field",
                        "farm.initial_temperature",
                        "project.elec_measured_temperature",
                        "project.install_import_chem_pollutant",
                        "project.operat_import_chem_pollutant",
                        "farm.protected_species",
                        "farm.receptor_species",
                        "farm.hydro_energy_modif_weight",
                        "project.hydro_collision_risk_weight",
                        "farm.hydro_turbidity_risk_weight",
                        "device.hydro_underwater_noise_risk_weight",
                        "farm.hydro_reserve_effect_weight",
                        "device.hydro_reef_effect_weight",
                        "device.hydro_resting_place_weight",
                        "project.elec_collision_risk_weight",
                        "project.elec_elec_field_weight",
                        "project.elec_footprint_weight",
                        "project.elec_magnetic_field_weight",
                        "project.elec_reef_effect_weight",
                        "farm.elec_reserve_effect_weight",
                        "project.elec_resting_place_weight",
                        "project.elec_temp_modif_weight",
                        "project.elec_underwater_noise_risk_weight", 
                        "project.moor_collision_risk_weight",
                        "project.moor_footprint_weight",
                        "project.moor_reef_effect_weight",
                        "project.moor_underwater_noise_risk_weight",
                      
                        "project.install_collision_risk_weight",
                        "project.install_footprint_weight",
                        "project.install_turbidity_risk_weight",
                        "project.install_chemical_pollution_weight",
                        "project.install_underwater_noise_risk_weight",
                        
                        "project.operat_collision_risk_weight",
                        "project.operat_footprint_weight",
                        "project.operat_turbidity_risk_weight",
                        "project.operat_chemical_pollution_weight",
                        "project.operat_underwater_noise_risk_weight",
                        
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
        
        output_list = ["project.global_eis",
                       'project.hydro_global_eis',
                       'project.hydro_eis',
                       'project.hydro_confidence',
                       'project.hydro_season',
                       'project.hydro_recommendation_dict',
                       'project.elec_global_eis',
                       'project.elec_eis',
                       'project.elec_confidence',
                       'project.elec_season',
                       'project.elec_recommendation_dict',
                       'project.moor_global_eis',
                       'project.moor_eis',
                       'project.moor_confidence',
                       'project.moor_season',
                       'project.moor_recommendation_dict',
                       'project.install_global_eis',
                       'project.install_eis',
                       'project.install_confidence',
                       'project.install_season',
                       'project.install_recommendation_dict',
                       'project.operat_global_eis',
                       'project.operat_eis',
                       'project.operat_confidence',
                       'project.operat_season',
                       'project.operat_recommendation_dict',                       
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
        
        optional = ["farm.protected_species",
                    "farm.receptor_species",
                    "farm.hydro_energy_modif_weight",
                    "project.hydro_collision_risk_weight",
                    "farm.hydro_turbidity_risk_weight",
                    "device.hydro_underwater_noise_risk_weight",
                    "farm.hydro_reserve_effect_weight",
                    "device.hydro_reef_effect_weight",
                    "device.hydro_resting_place_weight",
                    "farm.initial_turbidity",
                    "project.hydro_measured_turbidity",
                    "farm.initial_noise",
                    "project.hydro_measured_noise",
                    "project.number_of_devices",
                    "device.system_draft",
                    "device.system_width",
                    "farm.direction_of_max_surface_current",
                    "project.fishery_restricted_area",
                    "site.lease_boundary",
                    "bathymetry.layers",
                    "bathymetry.layers",
                    "device.system_height",
                    "device.system_length",
                    "project.elec_collision_risk_weight",
                    "project.elec_elec_field_weight",
                    "project.elec_footprint_weight",
                    "project.elec_magnetic_field_weight",
                    "project.elec_reef_effect_weight",
                    "farm.elec_reserve_effect_weight",
                    "project.elec_resting_place_weight",
                    "project.elec_temp_modif_weight",
                    "project.elec_underwater_noise_risk_weight",
                    "project.elec_measured_noise",
                    "farm.initial_elec_field",
                    "project.elec_measured_elec_field",
                    "farm.initial_magnetic_field",
                    "project.elec_measured_magnetic_field",
                    "farm.initial_temperature",
                    "project.elec_measured_temperature",
                    "project.substation_props",
                    "project.substation_layout",
                    "project.resource_reduction",
                    "project.moor_collision_risk_weight",
                    "project.moor_footprint_weight",
                    "project.moor_reef_effect_weight",
                    "project.moor_underwater_noise_risk_weight",
                    "project.moor_measured_noise",
                    "project.moorings_dimensions",
                    "project.install_collision_risk_weight",
                    "project.install_footprint_weight",
                    "project.install_turbidity_risk_weight",
                    "project.install_chemical_pollution_weight",
                    "project.install_underwater_noise_risk_weight",
                    "project.install_measured_turbidity",
                    "project.install_measured_noise",
                    "project.installation_journeys",  
                    "project.installation_vessel_average_size",
                    "project.install_import_chem_pollutant",
                    "project.operat_collision_risk_weight",
                    "project.operat_footprint_weight",
                    "project.operat_turbidity_risk_weight",
                    "project.operat_chemical_pollution_weight",
                    "project.operat_underwater_noise_risk_weight",
                    "project.operat_measured_turbidity",
                    "project.operat_measured_noise",
                    "project.operation_journeys_mode",  
                    "project.operat_vessel_average_size",
                    "project.operat_import_chem_pollutant",                    
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
                  
        id_map = { "device_type": "device.system_type",
                   "hydro_energy_modif_weight":
                       "farm.hydro_energy_modif_weight",
                   "hydro_collision_risk_weight":
                       "project.hydro_collision_risk_weight",
                   "hydro_turbidity_risk_weight":
                       "farm.hydro_turbidity_risk_weight",
                   "hydro_underwater_noise_risk_weight":
                       "device.hydro_underwater_noise_risk_weight",
                   "hydro_reserve_effect_weight":
                       "farm.hydro_reserve_effect_weight",
                   "hydro_reef_effect_weight":
                       "device.hydro_reef_effect_weight",
                   "hydro_resting_place_weight":
                       "device.hydro_resting_place_weight",
                   "resource_reduction": "project.resource_reduction",
                   "layout": "project.layout",
                   "initial_turbidity": "farm.initial_turbidity",
                   "hydro_measured_turbidity":
                       "project.hydro_measured_turbidity",
                   "initial_noise": "farm.initial_noise",
                   "hydro_measured_noise": "project.hydro_measured_noise",
                   "number_of_devices": "project.number_of_devices",
                   "device_draft": "device.system_draft",
                   "device_width": "device.system_width",
                   "current_direction":
                       "farm.direction_of_max_surface_current",
                   "fishery_restricted_area":
                       "project.fishery_restricted_area",
                   "lease_boundary": "site.lease_boundary",
                   "strata": "bathymetry.layers", 
                   "hydro_confidence": "project.hydro_confidence",
                   "hydro_eis": "project.hydro_eis",
                   "hydro_season": "project.hydro_season",
                   "hydro_recommendation_dict":
                       "project.hydro_recommendation_dict",
                   "hydro_global_eis": "project.hydro_global_eis",
                   "elec_global_eis": "project.elec_global_eis",
                   "moor_global_eis": "project.moor_global_eis",
                   "elec_confidence": "project.elec_confidence",
                   "elec_eis": "project.elec_eis",
                   "elec_season": "project.elec_season",
                   "elec_recommendation_dict":
                       "project.elec_recommendation_dict",
                   "device_height": "device.system_height",
                   "device_length": "device.system_length",
                   "elec_collision_risk_weight":
                       "project.elec_collision_risk_weight",
                   "elec_elec_field_weight": "project.elec_elec_field_weight",
                   "elec_footprint_weight": "project.elec_footprint_weight",
                   "elec_magnetic_field_weight":
                       "project.elec_magnetic_field_weight",
                   "elec_reef_effect_weight":
                       "project.elec_reef_effect_weight",
                   "elec_reserve_effect_weight":
                       "farm.elec_reserve_effect_weight",
                   "elec_resting_place_weight":
                       "project.elec_resting_place_weight",
                   "elec_temp_modif_weight":
                       "project.elec_temp_modif_weight",
                   "elec_underwater_noise_risk_weight":
                       "project.elec_underwater_noise_risk_weight",
                   "elec_measured_noise":"project.elec_measured_noise",
                   "initial_elec_field": "farm.initial_elec_field",
                   "elec_measured_elec_field":
                       "project.elec_measured_elec_field",
                   "initial_magnetic_field":
                       "farm.initial_magnetic_field",
                   "elec_measured_magnetic_field":
                       "project.elec_measured_magnetic_field",
                   "initial_temperature": "farm.initial_temperature",
                   "elec_measured_temperature": 
                       "project.elec_measured_temperature",
                   "substation_props": "project.substation_props",
                   "substation_layout": "project.substation_layout",
                   "moor_collision_risk_weight":
                       "project.moor_collision_risk_weight",
                   "moor_footprint_weight":
                       "project.moor_footprint_weight",
                   "moor_reef_effect_weight":
                       "project.moor_reef_effect_weight",
                   "moor_underwater_noise_risk_weight":
                       "project.moor_underwater_noise_risk_weight",
                   "moor_measured_noise": "project.moor_measured_noise",
                   "moor_confidence": "project.moor_confidence",
                   "moor_eis": "project.moor_eis",
                   "moor_season": "project.moor_season",
                   "moor_recommendation_dict":
                        "project.moor_recommendation_dict",
                   "moorings_dimensions": "project.moorings_dimensions",
                   "number_vessels": "project.installation_journeys",
                   "average_size_vessels_inst":
                        "project.installation_vessel_average_size",
                   "install_import_chem_pollutant":
                        "project.install_import_chem_pollutant",
                   "install_collision_risk_weight":
                        "project.install_collision_risk_weight",
                   "install_footprint_weight":
                        "project.install_footprint_weight",
                   "install_turbidity_risk_weight":
                        "project.install_turbidity_risk_weight",
                   "install_chemical_pollution_weight":
                        "project.install_chemical_pollution_weight",
                   "install_underwater_noise_risk_weight":
                       "project.install_underwater_noise_risk_weight",
                   "install_measured_noise":
                       "project.install_measured_noise", 
                   "install_measured_turbidity":
                       "project.install_measured_turbidity",
                   "install_eis": "project.install_eis", 
                   "install_confidence": "project.install_confidence",
                   "install_global_eis": "project.install_global_eis",
                   "install_recommendation_dict":
                        "project.install_recommendation_dict",
                   "install_season": "project.install_season",
                   "operat_import_chem_pollutant":
                        "project.operat_import_chem_pollutant",
                   "operat_collision_risk_weight":
                       "project.operat_collision_risk_weight",
                   "operat_footprint_weight":
                        "project.operat_footprint_weight",
                   "operat_turbidity_risk_weight":
                        "project.operat_turbidity_risk_weight",
                   "operat_chemical_pollution_weight":
                        "project.operat_chemical_pollution_weight",
                   "operat_underwater_noise_risk_weight":
                        "project.operat_underwater_noise_risk_weight",
                   "operat_measured_noise": "project.operat_measured_noise", 
                   "operat_measured_turbidity":
                        "project.operat_measured_turbidity",
                   "operat_eis": "project.operat_eis", 
                   "operat_confidence": "project.operat_confidence",
                   "operat_global_eis": "project.operat_global_eis",
                   "operat_recommendation_dict":
                        "project.operat_recommendation_dict",
                   "operat_season": "project.operat_season",
                   "operat_number_vessels": "project.operation_journeys_mode",
                   "operat_average_size_vessels":
                        "project.operat_vessel_average_size",
                   "protected_dict": "farm.protected_species",
                   "receptor_species": "farm.receptor_species",
                   "global_eis": "project.global_eis"
                   }
                  
        return id_map
                 
    def connect(self, debug_entry=False, export_data=False):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        name_protected = ["subclass or group", "observed"]
        
        protected_dict = self.data.protected_dict
        if protected_dict is None:
            protected_dict = {"Sei whale": None,
                              "Blue whale": None,
                              "Fin whale": None,
                              "North Atlantic right whale": None,
                              "Humpback whale": None,
                              "Long finned pilot whale": None,
                              "Rissos dolphin": None,
                              "Killer whale": None,
                              "Striped dolphin": None,
                              "Rough toothed dolphin": None,
                              "Common bottlenose dolphin": None,
                              "Sperm whale": None,
                              "Harbour porpoise": None,
                              "Mediterranean monk seal": None,
                              "Lesser white fronted goose": None,
                              "Red breasted goose": None,
                              "Slender billed curlew": None,
                              "Steller eider": None,
                              "Audouin gull": None,
                              "White tailed eagle": None,
                              "Loggerhead sea turtle": None,
                              "Green sea turtle": None,
                              "Kemp ridley": None
                              }
                    
        protected_table_df2 = pd.DataFrame(protected_dict.items(),
                                           columns=name_protected)
        protected_table_df = protected_table_df2.set_index('subclass or group')
        
        column_names =  ["subclass or group",
                         "observed",
                         "observed january",
                         "observed february",
                         "observed march",
                         "observed april",
                         "observed may",
                         "observed june",
                         "observed july",
                         "observed august",
                         "observed september",
                         "observed october",
                         "observed november",
                         "observed december"]
                     
        mapping_columns =  { "Year": "observed",
                             "January": "observed january",
                             "February": "observed february",
                             "March": "observed march",
                             "April": "observed april",
                             "May": "observed may",
                             "June": "observed june",
                             "July": "observed july",
                             "August": "observed august",
                             "September": "observed september",
                             "October": "observed october",
                             "November": "observed november",
                             "December": "observed december" }
                     
        mapping_index = {
         "Observation of Hard substrate benthic habitat":
            "Hard substrate benthic habitat",
         "Observation of Soft substrate benthic habitat":
            "Soft substrate benthic habitat",
         "Observation of Particular habitat": "Particular habitat",
         "Observation of Shallow diving birds": "Shallow diving birds",
         "Observation of Medium diving birds": "Medium diving birds",
         "Observation of Deep diving birds": "Deep diving birds",
         "Observation of Fishes": "Fishes",
         "Observation of Elasmobranchs": "Elasmobranchs",
         "Observation of Large odontocete_Mysticete":
            "Large odontocete_Mysticete",
         "Observation of Odontoncete_dolphinds": "Odontoncete_dolphinds",
         "Observation of Seals": "Seals",
         "Observation of Magnetosensitive species": "Magnetosensitive species",
         "Observation of Electrosensitive species": "Electrosensitive species"}

        null_months = [None] * 13
                     
        if self.data.receptor_species is None:
            values = [["Hard substrate benthic habitat"] + null_months,
                      ["Soft substrate benthic habitat"] + null_months,
                      ["Particular habitat"] + null_months,
                      ["Shallow diving birds"] + null_months,
                      ["Medium diving birds"] + null_months,
                      ["Deep diving birds"] + null_months,
                      ["Fishes"] + null_months,
                      ["Elasmobranchs"] + null_months,
                      ["Large odontocete_Mysticete"] + null_months,
                      ["Odontoncete_dolphinds"] + null_months,
                      ["Seals"] + null_months,
                      ["Magnetosensitive species"] + null_months,
                      ["Electrosensitive species"] + null_months]
            receptor_species=pd.DataFrame(data=values,columns=column_names)
            receptor_table_df = receptor_species.set_index("subclass or group")
            
        else:
            receptors_species_df = self.data.receptor_species
            receptors_species_df.rename(columns=mapping_columns, 
                                                            inplace=True)
            receptors_species_df.replace(["true", "false", "unknown"],
                                     [True, False, None],
                                        inplace=True) 
            receptor_table_df= receptors_species_df.rename(index=mapping_index)
            receptor_table_df.index.name = "subclass or group"
        
        receptor_table_df= receptor_table_df.rename(index= mapping_index)

        if self.data.hydro_energy_modif_weight is None:
             hydro_energy_modif_weight_map = None
        else:         
            translate_hydro_energy_mod_dict = {
                                    "Loose Sand": "Loose sand",
                                    "Medium Sand": "Medium sand",
                                    "Dense Sand": "Dense sand",
                                    "Very Soft Clay": "Very soft clay",
                                    "Soft Clay": "Soft clay",
                                    "Firm Clay": "Firm clay",
                                    "Stiff Clay": "Stiff clay",
                                    "Cemented": "Cemented",
                                    "Soft Rock Coral": "Soft rock coral",
                                    "Hard Glacial Till": "Hard glacial till",
                                    "Gravel Cobble": "Gravel cobble",
                                    "Hard Rock": "Hard rock"}
            hydro_energy_modif_weight_map = \
                translate_hydro_energy_mod_dict[
                                        self.data.hydro_energy_modif_weight]
                                        
        if self.data.hydro_collision_risk_weight is None:
             hydro_collision_risk_weight_map = None
        else:         
            translate_hydro_collision_risk_dict = {
                    "Open Water/ Devices In Parallel":
                        "open water/ devices in parallel",
                    "Sea Loch Entrance/ Devices In Parallel":
                        "sea loch entrance/ devices in parallel",
                    "Sounds/ Devices In Parallel":
                        "sounds/ devices in parallel",
                    "Open Water/ Devices In Series":
                        "open water/ devices in serie",
                    "Sea Loch Entrances/ Devices In Series":
                        "sea loch entrances/ devices in serie",
                    "Sounds / Devices In Series":
                        "sounds / devices in serie"}
            hydro_collision_risk_weight_map = \
                translate_hydro_collision_risk_dict[
                                        self.data.hydro_collision_risk_weight]


        if self.data.hydro_underwater_noise_risk_weight is None:
             hydro_underwater_noise_risk_weight_map = None
        else:                                         
            translate_hydro_underwater_noise_risk_dict = {
                "Noise Device 0 - 90 dB re 1muPa":
                    "noise device 0 - 90 dB re 1muPa",
                "Noise Device 90 - 100 dB re 1muPa":
                    "noise device 90 - 100 dB re 1muPa",
                "Noise Device 100 - 150 dB re 1muPa":
                    "noise device 100 - 150 dB re 1muPa",
                "Noise Device 150 - 200  dB re 1muPa":
                    "noise device 150 - 200  dB re 1muPa",
                "Noise Device > 200 dB re 1muPa":
                    "noise device > 200 dB re 1muPa"}
            hydro_underwater_noise_risk_weight_map = \
                translate_hydro_underwater_noise_risk_dict[
                                self.data.hydro_underwater_noise_risk_weight]

        if self.data.hydro_reserve_effect_weight is None:
             hydro_reserve_effect_weight_map = None
        else:        
            translate_hydro_reserve_effect_weight_dict = {
                "Fishery Complete Prohibition": "Fishery complete prohibition",
                "Cast Net Fishing (Using Gillnets And Entangling Nets)":
                    "Cast net fishing (using gillnets and entangling nets)",
                "Trawler Fishing": "Trawler fishing",
                "Others": "others",
                "No Restriction": "no restriction"      
                }
            hydro_reserve_effect_weight_map = \
                translate_hydro_reserve_effect_weight_dict[
                                        self.data.hydro_reserve_effect_weight]
                                        

        if self.data.hydro_reef_effect_weight is None:
             hydro_reef_effect_weight_map = None
        else:         
            translate_hydro_reef_effect_weight_dict = {
                    "Wave Design Horizontal": "Wave design horizontal",
                    "Wave Design Vertical": "Wave design vertical",
                    "Tidal Design Horizontal": "Tidal design horizontal",
                    "Tidal Design Vertical": "Tidal design vertical"
                    }
            hydro_reef_effect_weight_map = \
                translate_hydro_reef_effect_weight_dict[
                                        self.data.hydro_reef_effect_weight]

        if self.data.hydro_resting_place_weight is None:
             hydro_resting_place_weight_map = None
        else:          
            translate_hydro_resting_place_weight_dict = {
                    "No Dangerous Part Of Devices":
                        "No dangerous part of devices",
                    "Blades": "blades",
                    "Turbine Shroud": "turbine shroud",
                    "Oscillating Water Column With Cavity":
                        "oscillating water column with cavity",
                    "Oscillating Bodies With Translation Part":
                        "oscillating bodies with translation part",
                    "Oscillating Bodies With Rotating Part":
                        "oscillating bodies with rotating part",
                    "Flexible Sleeve Between Each Box Of Pelamis":
                        "flexible sleeve between each box of pelamis"
                    }
            hydro_resting_place_weight_map = \
                translate_hydro_resting_place_weight_dict[
                                        self.data.hydro_resting_place_weight]  
                                        
        hydro_weighting_dict = {
                  "Energy Modification": hydro_energy_modif_weight_map,
                  "Collision Risk": hydro_collision_risk_weight_map,
                  "Turbidity": self.data.hydro_turbidity_risk_weight,
                  "Underwater Noise": hydro_underwater_noise_risk_weight_map,
                  "Reserve Effect": hydro_reserve_effect_weight_map,
                  "Reef Effect": hydro_reef_effect_weight_map,
                  "Resting Place": hydro_resting_place_weight_map}
        
        if self.data.layout is None:
            device_coord = None
        else:
            device_coord_three_coords = [list(item.coords)[0]
                        for item in self.data.layout.values()]                            
            device_coord_x = [item[0] for item in device_coord_three_coords]
            device_coord_y = [item[1] for item in device_coord_three_coords]            
            device_coord = (device_coord_x,device_coord_y)
                            
        lease_area = self.data.lease_boundary.area
        
        bathymetry_pd_unsort = self.data.strata.to_dataframe()
        
        if max(bathymetry_pd_unsort.values[:,0])<0:
            min_depth= -max(bathymetry_pd_unsort.values[:,0])
        else:
            min_depth=0
          
        if "floating" in self.data.device_type.lower():
            device_wet_height = self.data.device_draft
        else: 
            device_wet_height = self.data.device_height
        
        if None not in (device_wet_height,
                        self.data.device_width,
                        self.data.device_length):
                        
            device_surface_underwater_part = \
                2. * device_wet_height * \
                            (self.data.device_width + self.data.device_length)
            device_emerged_surface = self.data.device_width * \
                                                    self.data.device_length
                                                    
        elif (device_wet_height is None and
              None not in (self.data.device_width, self.data.device_length)):
              
            device_surface_underwater_part  = None
            device_emerged_surface = self.data.device_width * \
                                                    self.data.device_length
                                                    
        else:
        
            device_surface_underwater_part = None
            device_emerged_surface = None
            
        hydro_input_dict = {
              "Energy Modification": self.data.resource_reduction,
              "Coordinates of the Devices": device_coord,
              "Size of the Devices":
                  max(self.data.device_width,self.data.device_length),
              "Immersed Height of the Devices": device_wet_height,
              "Water Depth": min_depth,
              "Current Direction": self.data.current_direction,
              "Initial Turbidity": self.data.initial_turbidity,
              "Measured Turbidity": self.data.hydro_measured_turbidity,
              "Initial Noise dB re 1muPa": self.data.initial_noise,
              "Measured Noise dB re 1muPa": self.data.hydro_measured_noise,
              "Fishery Restriction Surface": self.data.fishery_restricted_area,
              "Total Surface Area": lease_area,
              "Number of Objects": self.data.number_of_devices,
              "Object Emerged Surface": device_emerged_surface,
              "Surface Area of Underwater Part": device_surface_underwater_part
              } #this should be split
             
        HydroStage_assessment = HydroStage(protected_table_df,
                                           receptor_table_df,
                                           hydro_weighting_dict)
                                                         
        ( hydro_confidence, 
          hydro_eis, 
          hydro_recommendation_dict, 
          hydro_season, 
          hydro_global_eis ) = HydroStage_assessment(hydro_input_dict)          
          
        if any(x is not None for x in hydro_confidence.values()):
            self.data.hydro_confidence = hydro_confidence
            
        if any(x is not None for x in hydro_eis.values()): 
            self.data.hydro_eis = hydro_eis
            
        if any(x is not None for x in hydro_recommendation_dict.values()): 
            self.data.hydro_recommendation_dict = hydro_recommendation_dict
                        
        if any(x is not None for x in hydro_season.values): 
            hydro_season.index.name = "Impact"
            hydro_season_mod = hydro_season.reset_index()
            self.data.hydro_season = hydro_season_mod
            self.data.hydro_season.columns = [
                            x.title() for x in self.data.hydro_season.columns]
            
        if any(not(math.isnan(x)) for x in hydro_global_eis.values()): 
            self.data.hydro_global_eis = hydro_global_eis              

        if self.data.elec_collision_risk_weight is None:
            elec_collision_risk_weight_map = None
        else:
            translate_elec_collision_risk_dict = {
                                    "Cable Buried": "cable buried",
                                    "Cable Not Buried": "cable not buried"}
            elec_collision_risk_weight_map = \
                            translate_elec_collision_risk_dict[
                                        self.data.elec_collision_risk_weight]
                                    
        if self.data.elec_elec_field_weight is None:
            elec_elec_field_weight_map = None
        else:    
            translate_elec_elec_field_dict = {"Cable Buried": "cable buried",
                                        "Cable Not Buried": "cable not buried"}
            elec_elec_field_weight_map = translate_elec_elec_field_dict[
                                            self.data.elec_elec_field_weight]  
                                        
                                      
        if self.data.elec_footprint_weight is None:
            elec_footprint_weight_map = None
        else:                                  
            translate_elec_footprint_dict = {
                                        "Cable Buried": "cable buried",
                                        "Cable Not Buried": "cable not buried"}
            elec_footprint_weight_map = translate_elec_footprint_dict[
                                            self.data.elec_footprint_weight]  
                                        
        if self.data.elec_magnetic_field_weight is None:
            elec_magnetic_field_weight_map = None
        else:                                        
            translate_elec_magnetic_field_dict = {
                                        "Cable Buried": "cable buried",
                                        "Cable Not Buried": "cable not buried"}
            elec_magnetic_field_weight_map = \
                        translate_elec_magnetic_field_dict[
                                        self.data.elec_magnetic_field_weight]  
#        
        if self.data.elec_reef_effect_weight is None:
            elec_reef_effect_weight_map = None
        else:         
            translate_elec_reef_effect_dict = {
                                        "Substation": "substation",
                                        "Hub": "hub",
                                        "Transformer": "transformer",
                                        "Cable Not Buried": "cable not buried"}
            elec_reef_effect_weight_map = translate_elec_reef_effect_dict[
                                            self.data.elec_reef_effect_weight]                               
                                        
        if self.data.elec_reserve_effect_weight is None:
             elec_reserve_effect_weight_map = None
        else:                                        
            translate_elec_reserve_effect_dict = {
                "Fishery Complete Prohibition":
                    "Fishery complete prohibition",
                "Cast Net Fishing (Using Gillnets And Entangling Nets)": 
                    "Cast net fishing (using gillnets and entangling nets)",
                "Trawler Fishing": "Trawler fishing",
                "Others": "others"
                }
                
            elec_reserve_effect_weight_map = \
                            translate_elec_reserve_effect_dict[
                                        self.data.elec_reserve_effect_weight] 
                                        
                                
        if self.data.elec_resting_place_weight is None:
             elec_resting_place_weight_map = None
        else:         
            translate_elec_resting_place_dict = {
                "No Constraint": "no constraint"
                }
            elec_resting_place_weight_map = translate_elec_resting_place_dict[
                                        self.data.elec_resting_place_weight] 
                                            
        if self.data.elec_temp_modif_weight is None:
             elec_temp_modif_weight_map = None
        else:                
            translate_elec_temp_modif_dict = {
                                        "Cable Buried": "cable buried",
                                        "Cable Not Buried": "cable not buried"}
            elec_temp_modif_weight_map = translate_elec_temp_modif_dict[
                                            self.data.elec_temp_modif_weight]   
                                              
        if self.data.elec_underwater_noise_risk_weight is None:
             elec_underwater_noise_risk_weight_map = None
        else:          
            translate_elec_underwater_noise_risk_dict = {
                "Noise Electrical Components 0 - 90 dB re 1muPa":   
                    "noise electrical components 0 dB re 1muPa",
                "Noise Electrical Components 90 - 100 dB re 1muPa":
                    "noise electrical components 90 dB re 1muPa",
                "Noise Electrical Components 100 - 150 dB re 1muPa":
                    "noise electrical components 100 dB re 1muPa",
                "Noise Electrical Components 150 - 200  dB re 1muPa":
                    "noise electrical components 150 dB re 1muPa",
                "Noise Electrical Components > 200 dB re 1muPa":
                    "noise electrical components 200 dB re 1muPa"}
            elec_underwater_noise_risk_weight_map = \
                        translate_elec_underwater_noise_risk_dict[
                                self.data.elec_underwater_noise_risk_weight]
         
        elec_weighting_dict = {
            "Electric Fields": elec_elec_field_weight_map,
            "Magnetic Fields": elec_magnetic_field_weight_map,
            "Temperature Modification": elec_temp_modif_weight_map,
            "Collision Risk": elec_collision_risk_weight_map,
            "Underwater Noise": elec_underwater_noise_risk_weight_map,
            "Reserve Effect": elec_reserve_effect_weight_map,
            "Reef Effect": elec_reef_effect_weight_map,
            "Resting Place": elec_resting_place_weight_map,
            "Footprint": elec_footprint_weight_map,
            } 
        
        if self.data.substation_layout is None:
            substation_coord = None
            number_substation = None
            size_of_device = None
            height_of_device = None
            substation_underwater = None
            substation_emerged_surface = None
            substation_surface_area_covered = None
        else:
            substation_coord_three_coords = [list(item.coords)[0]
                            for item in self.data.substation_layout.values()]
                                
            substation_coord_x = [item[0]
                                    for item in substation_coord_three_coords]
            substation_coord_y = [item[1]
                                    for item in substation_coord_three_coords]
            
            substation_coord = (substation_coord_x,substation_coord_y)
            number_substation = len(substation_coord_x)
            
            size_of_device = max(self.data.substation_props['Length'].max(),
                                     self.data.substation_props['Width'].max())
            
            height_of_device = self.data.substation_props['Height'].max()
            
    #        dry_area = max (self.data.substation_props['Dry Frontal Area'].max(),
    #                       self.data.substation_props['Dry Beam Area'].max())
    #                       
    #        wet_area = max (self.data.substation_props['Wet Frontal Area'].max(),
    #                       self.data.substation_props['Wet Beam Area'].max())
            
            substation_props_df = self.data.substation_props
            substation_props_df["Cross Area"] = \
                substation_props_df["Length"] * substation_props_df["Width"]
            substation_surface_area_covered = \
                                        substation_props_df["Cross Area"].sum()
            substation_emerged_surface = \
                                        substation_props_df["Cross Area"].max()
            
            substation_props_df["Underwater Area"] = 2 * (
                substation_props_df["Length"] * substation_props_df["Width"] +
                substation_props_df["Height"] * substation_props_df["Width"] +
                substation_props_df["Length"] * substation_props_df["Height"]
                ) * (substation_props_df["Type"] == "subsea substation")
            
            substation_underwater = \
                                substation_props_df["Underwater Area"].max()
#        
        elec_input_dict = {
                "Initial Electric Field": self.data.initial_elec_field,
                "Measured Electric Field": self.data.elec_measured_elec_field,
                "Initial Magnetic Field": self.data.initial_magnetic_field,
                "Measured Magnetic Field":
                    self.data.elec_measured_magnetic_field,
                "Initial Temperature": self.data.initial_temperature,
                "Measured Temperature": self.data.elec_measured_temperature,
                "Coordinates of the Devices": substation_coord,
                "Size of the Devices": size_of_device,
                "Immersed Height of the Devices":  height_of_device,
                "Water Depth": min_depth,
                "Current Direction": self.data.current_direction,
                "Initial Noise dB re 1muPa":  self.data.initial_noise,
                "Measured Noise dB re 1muPa":  self.data.elec_measured_noise,
                "Total Surface Area": lease_area,
                "Number of Objects": number_substation,
                "Surface Area of Underwater Part":  substation_underwater,
                "Object Emerged Surface": substation_emerged_surface,
                "Surface Area Covered": substation_surface_area_covered,
                "Fishery Restriction Surface":
                    self.data.fishery_restricted_area
                } #this should be split
             
        ElecStage_assessment = ElectricalStage(protected_table_df,
                                               receptor_table_df,
                                               elec_weighting_dict)
                                                 
        if export_data:
            
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

            pkl_path = debugdir.get_path(
                                    "environmental_ElectricalStage_inputs.pkl")
            pickle.dump(elec_input_dict, open(pkl_path, "wb"))
                                                 
        ( elec_confidence, 
          elec_eis, 
          elec_recommendation_dict, 
          elec_season, 
          elec_global_eis ) = ElecStage_assessment(elec_input_dict)
          
        if any(x is not None for x in elec_confidence.values()):
            self.data.elec_confidence = elec_confidence
            
        if any(x is not None for x in elec_eis.values()): 
            self.data.elec_eis = elec_eis
            
        if any(x is not None for x in elec_recommendation_dict.values()): 
            self.data.elec_recommendation_dict = elec_recommendation_dict
            
        if any(x is not None for x in elec_season.values): 
            elec_season.index.name = "Impact"
            elec_season_mod = elec_season.reset_index()
            self.data.elec_season = elec_season_mod
            self.data.elec_season.columns = [x.title()
                                        for x in self.data.elec_season.columns]
            
        if any(not(math.isnan(x)) for x in elec_global_eis.values()): 
            self.data.elec_global_eis = elec_global_eis  

        if self.data.moor_collision_risk_weight is None:
             moor_collision_risk_weight_map = None
        else:         
            translate_moor_collision_risk_dict = {
                "Catenary & Chains": "catenary&chains",
                "Catenary & Chains & Nylon Ropes":
                    "catenary&chains&nylon ropes",
                "Catenary & Chains & Polyester Ropes":
                    "catenary&chains&polyester ropes",
                "Taut": "taut",
                "Catenary & Accessory Buoy": "catenary&accessory buoy",
                "Taut & Accessory Buoy": "taut&accessory buoy"}
                
            moor_collision_risk_weight_map = \
                        translate_moor_collision_risk_dict[
                                        self.data.moor_collision_risk_weight]
                                        
        if self.data.moor_underwater_noise_risk_weight is None:
             moor_underwater_noise_risk_weight_map = None
        else:        
            translate_moor_underwater_noise_risk_dict = { 
                        "Chafing 0 dB re 1muPa": "chafing 0 dB re 1muPa",
                        "Chafing 90 dB re 1muPa": "chafing 90 dB re 1muPa",
                        "Chafing 100 dB re 1muPa": "chafing 100 dB re 1muPa",
                        "Chafing 150 dB re 1muPa": "chafing 150 dB re 1muPa",
                        "Chafing 200 dB re 1muPa": "chafing 200 dB re 1muPa"
                        }
            moor_underwater_noise_risk_weight_map = \
                    translate_moor_underwater_noise_risk_dict[
                                self.data.moor_underwater_noise_risk_weight]                                
                                        
        moor_weighting_dict = {
            "Collision Risk": moor_collision_risk_weight_map,
            "Underwater Noise": moor_underwater_noise_risk_weight_map,
            "Reef Effect": self.data.moor_reef_effect_weight,
            "Footprint": self.data.moor_footprint_weight}
        
        if self.data.substation_layout is not None:
        
            moor_objects_x = device_coord_x + substation_coord_x
            moor_objects_y = device_coord_y + substation_coord_y
            
            moor_objects = (moor_objects_x,moor_objects_y)
            
        else:
        
            moor_objects_x = device_coord_x 
            moor_objects_y = device_coord_y 
            
            moor_objects = (moor_objects_x,moor_objects_y)

        if self.data.moorings_dimensions is not None:
            moor_size = self.data.moorings_dimensions
            moor_size['height'] = \
                        moor_size["Volume"] / moor_size["Footprint Area"]
            moor_size['diameter'] = \
                        2 * np.sqrt(moor_size["Footprint Area"] / np.pi)
            moor_size["surface"] = \
                        np.pi * moor_size['diameter'] * moor_size['height']
            moor_size_max = moor_size['diameter'].max()
            moor_imm_height = moor_size["height"].min()
            moor_depth = moor_size["height"].min()
            number_moor_objects = len(moor_size.index)
            moor_surface = moor_size["surface"].max()
            moor_covered = moor_size["Footprint Area"].sum()
        else:
            moor_size = None
            moor_size_max = None
            moor_imm_height = None
            moor_depth = None
            number_moor_objects = None
            moor_surface = None
            moor_covered = None            
                
        moor_input_dict = {
                      "Coordinates of the Devices": moor_objects,
                      "Size of the Devices": moor_size_max,
                      "Immersed Height of the Devices": moor_imm_height,
                      "Water Depth": moor_depth,
                      "Current Direction": self.data.current_direction,
                      "Initial Noise dB re 1muPa": self.data.initial_noise,
                      "Measured Noise dB re 1muPa":
                        self.data.moor_measured_noise,
                      "Total Surface Area": lease_area,
                      "Number of Objects": number_moor_objects,
                      "Surface Area of Underwater Part": moor_surface,
                      "Surface Area Covered": moor_covered}
        
        MoorStage_assessment = MooringStage(protected_table_df,
                                            receptor_table_df,
                                            moor_weighting_dict)
#                                                 
        ( moor_confidence, 
          moor_eis, 
          moor_recommendation_dict, 
          moor_season, 
          moor_global_eis ) = MoorStage_assessment(moor_input_dict)
          
        if any(x is not None for x in moor_confidence.values()):
            self.data.moor_confidence = moor_confidence
            
        if any(x is not None for x in moor_eis.values()): 
            self.data.moor_eis = moor_eis
            
        if any(x is not None for x in moor_recommendation_dict.values()):
            self.data.moor_recommendation_dict = moor_recommendation_dict
            
        if any(x is not None for x in moor_season.values): 
            moor_season.index.name = "Impact"
            moor_season_mod = moor_season.reset_index()
            self.data.moor_season = moor_season_mod
            self.data.moor_season.columns = [x.title()
                                    for x in self.data.moor_season.columns]
            
        if any(not(math.isnan(x)) for x in moor_global_eis.values()): 
            self.data.moor_global_eis = moor_global_eis

        if self.data.install_underwater_noise_risk_weight is None:
             install_underwater_noise_risk_weight_map = None
        else:        
            translate_install_underwater_noise_risk_dict = { 
                "Noise Vessels or Tools 0 - 90 dB re 1muPa":
                    "noise vessels or tools 0 - 90 dB re 1muPa",
                "Noise Vessels or Tools 90 - 100 dB re 1muPa":
                    "noise vessels or tools 90 - 100 dB re 1muPa",
                "Noise Vessels or Tools 100 - 150 dB re 1muPa":
                    "noise vessels or tools 100 - 150 dB re 1muPa",
                "Noise Vessels or Tools 150 - 200 dB re 1muPa":
                    "noise vessels or tools 150 - 200 dB re 1muPa",
                "Noise Vessels or Tools > 200 dB re 1muPa":
                    "noise vessels or tools > 200 dB re 1muPa"}
            install_underwater_noise_risk_weight_map = \
                    translate_install_underwater_noise_risk_dict[
                                self.data.install_underwater_noise_risk_weight]                                
                                        
        if self.data.install_chemical_pollution_weight is None:
            install_chemical_pollution_weight_map = None
        else:        
            translate_install_chemical_pollution_dict = { 
                    "Bunker Oil": "bunker oil",
                    "Highly Toxic Antifouling": "highly toxic antifouling",
                    "Moderate Toxic Antifouling": "moderate toxic antifouling",
                    "Natural Antifouling": "natural antifouling"}
            install_chemical_pollution_weight_map = \
                    translate_install_chemical_pollution_dict[
                                self.data.install_chemical_pollution_weight]

        install_weighting_dict = {
            "Collision Risk Vessel": self.data.install_collision_risk_weight,
            "Underwater Noise": install_underwater_noise_risk_weight_map,
            "Turbidity": self.data.install_turbidity_risk_weight,
            "Footprint": self.data.install_footprint_weight,
            "Chemical Pollution": install_chemical_pollution_weight_map}
          
        if (self.data.number_vessels is not None and 
                self.data.average_size_vessels_inst is not None):
            surface_covered = self.data.number_vessels * \
                    np.pi * (0.5 * self.data.average_size_vessels_inst) ** 2
        else:
            surface_covered = None
        
        install_input_dict = {
            "Import of Chemical Polutant"     : self.data.install_import_chem_pollutant,
            "Number of Vessels"               : self.data.number_vessels,
            "Initial Noise dB re 1muPa"       : self.data.initial_noise,
            "Measured Noise dB re 1muPa"      : self.data.install_measured_noise,
            "Total Surface Area"              : lease_area,
            "Size of Vessels"                 : self.data.average_size_vessels_inst,
            "Surface Area Covered"            : surface_covered,
            "Initial Turbidity"               : self.data.initial_turbidity,
            "Measured Turbidity"              : self.data.install_measured_turbidity,        
             }
        
        InstallStage_assessment = InstallationStage(protected_table_df,
                                                 receptor_table_df,
                                                 install_weighting_dict)
#                                                 
        ( install_confidence, 
          install_eis, 
          install_recommendation_dict, 
          install_season, 
          install_global_eis ) = InstallStage_assessment(install_input_dict)
          
        if any(x is not None for x in install_confidence.values()):
            self.data.install_confidence = install_confidence
            
        if any(x is not None for x in install_eis.values()): 
            self.data.install_eis = install_eis
            
        if any(x is not None for x in install_recommendation_dict.values()):
            self.data.install_recommendation_dict = install_recommendation_dict
            
        if any(x is not None for x in install_season.values): 
            install_season.index.name = "Impact"
            install_season_mod = install_season.reset_index()
            self.data.install_season = install_season_mod
            self.data.install_season.columns = [x.title() for x in self.data.install_season.columns]
            
        if any(not(math.isnan(x)) for x in install_global_eis.values()): 
            self.data.install_global_eis = install_global_eis
            
            
            
            
        if self.data.operat_underwater_noise_risk_weight is None:
             operat_underwater_noise_risk_weight_map = None
        else:        
            translate_operat_underwater_noise_risk_dict = { 
                            "Noise Vessels or Tools 0 - 90 dB re 1muPa": "noise vessels or tools 0 - 90 dB re 1muPa",
                            "Noise Vessels or Tools 90 - 100 dB re 1muPa": "noise vessels or tools 90 - 100 dB re 1muPa",
                            "Noise Vessels or Tools 100 - 150 dB re 1muPa": "noise vessels or tools 100 - 150 dB re 1muPa",
                            "Noise Vessels or Tools 150 - 200 dB re 1muPa": "noise vessels or tools 150 - 200 dB re 1muPa",
                            "Noise Vessels or Tools > 200 dB re 1muPa": "noise vessels or tools > 200 dB re 1muPa"
                            }
            operat_underwater_noise_risk_weight_map = translate_operat_underwater_noise_risk_dict[
                                        self.data.operat_underwater_noise_risk_weight]                                
                                        

        if self.data.operat_chemical_pollution_weight is None:
            operat_chemical_pollution_weight_map = None
        else:        
            translate_operat_chemical_pollution_dict = { 
                            "Bunker Oil": "bunker oil",
                            "Highly Toxic Antifouling": "highly toxic antifouling",
                            "Moderate Toxic Antifouling": "moderate toxic antifouling",
                            "Natural Antifouling": "natural antifouling"
                            }
            operat_chemical_pollution_weight_map = translate_operat_chemical_pollution_dict[
                                        self.data.operat_chemical_pollution_weight]


  
        operat_weighting_dict = {
            "Collision Risk Vessel": self.data.operat_collision_risk_weight,
            "Underwater Noise": operat_underwater_noise_risk_weight_map,
            "Turbidity": self.data.operat_turbidity_risk_weight,
            "Footprint": self.data.operat_footprint_weight,
            "Chemical Pollution": operat_chemical_pollution_weight_map
        }
        
          
        if (self.data.operat_number_vessels is not None and 
                self.data.operat_average_size_vessels is not None):
            operat_surface_covered = self.data.operat_number_vessels * np.pi * (0.5 * 
                                    self.data.operat_average_size_vessels)^2 
        else:
            operat_surface_covered = None
        
        operat_input_dict = {
            "Import of Chemical Polutant"     : self.data.operat_import_chem_pollutant,
            "Number of Vessels"               : self.data.operat_number_vessels,
            "Initial Noise dB re 1muPa"       : self.data.initial_noise,
            "Measured Noise dB re 1muPa"      : self.data.operat_measured_noise,
            "Total Surface Area"              : lease_area,
            "Size of Vessels"                 : self.data.operat_average_size_vessels,
            "Surface Area Covered"            : operat_surface_covered,
            "Initial Turbidity"               : self.data.initial_turbidity,
            "Measured Turbidity"              : self.data.operat_measured_turbidity,        
             }
        
        OperatStage_assessment = OperationMaintenanceStage(protected_table_df,
                                                 receptor_table_df,
                                                 operat_weighting_dict)
#                                                 
        ( operat_confidence, 
          operat_eis, 
          operat_recommendation_dict, 
          operat_season, 
          operat_global_eis ) = OperatStage_assessment(operat_input_dict)
          
        if any(x is not None for x in operat_confidence.values()):
            self.data.operat_confidence = operat_confidence
            
        if any(x is not None for x in operat_eis.values()): 
            self.data.operat_eis = operat_eis
            
        if any(x is not None for x in operat_recommendation_dict.values()):
            self.data.operat_recommendation_dict = operat_recommendation_dict
            
        if any(x is not None for x in operat_season.values): 
            operat_season.index.name = "Impact"
            operat_season_mod = operat_season.reset_index()
            self.data.operat_season = operat_season_mod
            self.data.operat_season.columns = [x.title() for x in self.data.operat_season.columns]
            
        if any(not(math.isnan(x)) for x in operat_global_eis.values()): 
            self.data.operat_global_eis = operat_global_eis
        
        global_eis = {}            
        global_list = [hydro_global_eis, 
                       elec_global_eis, 
                       moor_global_eis, 
                       install_global_eis,
                       operat_global_eis]
#        keys = list(set().union(*(d.keys() for d in global_list)))
        keys = ["Negative Impact", "Positive Impact"]
        
        for key in keys:
            impacts = [impact[key] for impact in global_list
                                                       if impact is not None]
            if ~np.isnan(impacts).all():
                global_eis[key] = np.nanmean(impacts)
            else:
                global_eis[key] = np.nan
                
        self.data.global_eis = global_eis
        
        return