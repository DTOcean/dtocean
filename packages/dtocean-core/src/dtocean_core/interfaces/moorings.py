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
This module contains the package interface to the dtocean mooring and
foundations module.

Note:
  The function decorators (such as '@classmethod', etc) must not be removed.

.. module:: moorings
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package
   
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
.. moduleauthor:: Vincenzo Nava <vincenzo.nava@tecnalia.com>
"""

# Built in modules
import os
import pickle
import pkg_resources

# External 3rd party libraries
import numpy as np
import pandas as pd

# External DTOcean libraries
from polite.paths import Directory, ObjDirectory, UserDataDirectory
from polite.configuration import ReadINI
from aneris.boundary.interface import MaskVariable
from dtocean_moorings.main import Variables, Main

# DTOcean Core modules
from . import ModuleInterface
from ..utils.moorings import get_component_dict
from ..utils.version import Version

# Check module version
pkg_title = "dtocean-moorings"
major_version = 2
version = pkg_resources.get_distribution(pkg_title).version

if not Version(version).major == major_version:
    
    err_msg = ("Incompatible version of {} detected! Major version {} is "
               "required, but version {} is installed").format(pkg_title,
                                                               major_version,
                                                               version)
    raise ImportError(err_msg)


class MooringsInterface(ModuleInterface):
    
    '''Interface to the moorings and foundations module.

    '''
        
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return 'Mooring and Foundations'
        
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
          
              inputs = ['My:first:variable',
                        'My:second:variable',
                       ]
        '''

        input_list  =  [ 
                 'bathymetry.layers',
                 
                 'farm.current_profile',
                 'farm.max_hs_100_year',
                 'farm.max_tp_100_year',
                 'farm.wave_direction_100_year',
                 'farm.max_gamma_100_year',
                 'farm.max_surface_current_10_year',
                 'farm.direction_of_max_surface_current',
                 'farm.mean_wind_direction_100_year',
                 'farm.mean_wind_speed_100_year',
                 'farm.max_gust_wind_direction_100_year',
                 'farm.max_gust_wind_speed_100_year',
                 'farm.min_water_level_50_year',
                 'farm.max_water_level_50_year',
                 'farm.soil_sensitivity',
                 
                 'device.system_type',
                 'device.system_mass',
                 'device.system_roughness',

                 MaskVariable('device.depth_variation_permitted',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                 MaskVariable('device.maximum_displacement',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                              
                 'device.system_profile',
                 'device.system_height',
                 'device.system_length',
                 'device.system_width',
                 'device.dry_beam_area',
                 'device.dry_frontal_area',
                 'device.wet_beam_area',
                 'device.wet_frontal_area',
                 'device.system_centre_of_gravity',
                 'device.system_displaced_volume',
                 
                 MaskVariable('device.system_draft',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                              
                 'device.foundation_type',

                 MaskVariable('device.mooring_system_type',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                              
                 'device.foundation_location',

                 MaskVariable('device.fairlead_location',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                              
                 'device.prescribed_footprint_radius',

                 MaskVariable('device.turbine_performance',
                              'device.system_type',
                              ['Tidal Fixed', 'Tidal Floating']),
                 MaskVariable('device.turbine_hub_height',
                              'device.system_type',
                              ['Tidal Fixed', 'Tidal Floating']),
                 MaskVariable('device.turbine_diameter',
                              'device.system_type',
                              ['Tidal Fixed', 'Tidal Floating']),
                 MaskVariable('device.turbine_interdistance',
                              'device.system_type',
                              ['Tidal Fixed', 'Tidal Floating']),
                 MaskVariable('device.umbilical_type',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                 MaskVariable('project.umbilical_safety_factor',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                 MaskVariable("device.umbilical_connection_point",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                
                 'device.external_forces',

                 "component.foundations_anchor",
                 'component.foundations_anchor_sand',
                 'component.foundations_anchor_soft',
                 "component.foundations_pile",
                 
                 MaskVariable("component.moorings_chain",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']), 
                 MaskVariable("component.moorings_forerunner",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']), 
                 MaskVariable("component.moorings_rope",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),                  
                 MaskVariable("component.moorings_shackle",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),                    
                 MaskVariable("component.moorings_swivel",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),                  
                 MaskVariable("component.moorings_rope_stiffness",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),                  
                 MaskVariable("component.dynamic_cable",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                              
                 'project.layout',
                 'project.main_direction',
                 'project.predefined_mooring_list',
                 "project.substation_props",
                 'project.substation_layout',
                 'project.substation_cog',
                 'project.substation_foundation_location',
                 
                 MaskVariable("project.umbilical_seabed_connection",
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                 
                 'project.foundation_safety_factor',
                 'project.grout_strength_safety_factor',
                 
                 MaskVariable('project.mooring_ALS_safety_factor',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                 MaskVariable('project.mooring_ULS_safety_factor',
                              'device.system_type',
                              ['Tidal Floating', 'Wave Floating']),
                              
                 'project.cost_of_concrete',
                 'project.cost_of_grout',
                 'project.cost_of_steel',
                 'project.fabrication_cost',

                 'constants.line_bearing_capacity_factor',
                 'constants.pile_Am_moment_coefficient',
                 'constants.pile_Bm_moment_coefficient',
                 'constants.pile_deflection_coefficients',
                 'constants.pile_skin_friction_end_bearing_capacity',
                 'constants.soilprops',
                 'constants.soil_cohesionless_reaction_coefficient',
                 'constants.soil_cohesive_reaction_coefficient',
                 'constants.soil_drained_holding_capacity_factor',
                 'constants.cylinder_drag',
                 'constants.cylinder_wake_amplificiation',
                 'constants.rectangular_current_drag',
                 'constants.rectangular_drift',
                 'constants.rectangular_wind_drag',
                 'constants.rectangular_wave_inertia',
                 'constants.gravity',
                 'constants.sea_water_density',
                 'constants.air_density',
                 'constants.steel_density',
                 'constants.concrete_density',
                 'constants.grout_density',
                 'constants.grout_compressive_strength',
                 
                 'options.repeat_foundations',
                 'options.apply_fex',
                 
                 MaskVariable("options.use_max_thrust",
                              "device.system_type",
                              ["Tidal Fixed", "Tidal Floating"])
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
          
              outputs = ['My:first:variable',
                         'My:third:variable',
                        ]
        '''
        
        output_list = ["project.moorings_foundations_network",
                       "project.moorings_foundations_economics_data",
                       "project.foundations_component_data",
                       "project.foundations_soil_data",
                       "project.moorings_component_data",
                       "project.moorings_line_data",
                       "project.umbilical_cable_data",
                       "project.moorings_dimensions"]
        
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
          
              optional = ['My:first:variable',
                         ]
        '''
        
        option_list = ["project.fabrication_cost",
                       "project.predefined_mooring_list",
                       'device.foundation_type',
                       'device.mooring_system_type',
                       'device.prescribed_footprint_radius',
                       "device.turbine_interdistance",
                       "device.external_forces",
                       'device.umbilical_type',
                       "farm.soil_sensitivity",
                       "project.substation_props",
                       'project.substation_layout',
                       'project.substation_cog',
                       'project.substation_foundation_location',
                       'options.repeat_foundations',
                       'options.apply_fex',
                        "options.use_max_thrust"
                       ]
                
        return option_list
        
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
          
              id_map = {'var1': 'My:first:variable',
                        'var2': 'My:second:variable',
                        'var3': 'My:third:variable'
                       }
        
        '''
                  
        id_map = {  
                    "bathymetry": "bathymetry.layers",
                    'airden': 'constants.air_density',
                    'conden': 'constants.concrete_density',
                    'costcon': 'project.cost_of_concrete',
                    'costgrout': 'project.cost_of_grout',
                    'coststeel': 'project.cost_of_steel',
                    'currentdir': 'farm.direction_of_max_surface_current',
                    'currentdragcoefrect':
                        'constants.rectangular_current_drag',
                    'currentprof': 'farm.current_profile',
                    'currentvel': 'farm.max_surface_current_10_year',
                    'depvar': 'device.depth_variation_permitted',
                    'dragcoefcyl': 'constants.cylinder_drag',
                    'driftcoeffloatrect': 'constants.rectangular_drift',
                    'fairloc': 'device.fairlead_location',
                    'foundloc': 'device.foundation_location',
                    'foundsf': 'project.foundation_safety_factor',
                    'gamma': 'farm.max_gamma_100_year',
                    'gravity': 'constants.gravity',
                    'groutden': 'constants.grout_density',
                    'groutsf': 'project.grout_strength_safety_factor',
                    'groutstr': 'constants.grout_compressive_strength',
                    'hcfdrsoil':
                        'constants.soil_drained_holding_capacity_factor',
                    'hs': 'farm.max_hs_100_year',
                    'k1coef': 'constants.soil_cohesive_reaction_coefficient',
                    'hub_height': 'device.turbine_hub_height',
                    'linebcf': 'constants.line_bearing_capacity_factor',
                    'maxdisp': 'device.maximum_displacement',
                    'moorsfals': 'project.mooring_ALS_safety_factor',
                    'moorsfuls': 'project.mooring_ULS_safety_factor',
                    'piledefcoef': 'constants.pile_deflection_coefficients',
                    'pilefricresnoncal':
                        'constants.pile_skin_friction_end_bearing_capacity',
                    'pilemomcoefam': 'constants.pile_Am_moment_coefficient',
                    'pilemomcoefbm': 'constants.pile_Bm_moment_coefficient',
                    'prefootrad': 'device.prescribed_footprint_radius',
                    'prefound': 'device.foundation_type',
                    'premoor': 'device.mooring_system_type',
                    'preumb': 'device.umbilical_type',
                    'rotor_diam': 'device.turbine_diameter',
                    'seaden': 'constants.sea_water_density',
                    'soilsen': 'farm.soil_sensitivity',
                    'steelden': 'constants.steel_density',
                    'subgradereaccoef':
                        'constants.soil_cohesionless_reaction_coefficient',
                    'syscog': 'device.system_centre_of_gravity',
                    'sysdraft': 'device.system_draft',
                    'sysdryba': 'device.dry_beam_area',
                    'sysdryfa': 'device.dry_frontal_area',
                    'sysheight': 'device.system_height',
                    'syslength': 'device.system_length',
                    'sysmass': 'device.system_mass',
                    'sysorienang': 'project.main_direction',
                    'sysprof': 'device.system_profile',
                    'sysrough': 'device.system_roughness',
                    'sysvol': 'device.system_displaced_volume',
                    'syswetba': 'device.wet_beam_area',
                    'syswetfa': 'device.wet_frontal_area',
                    'syswidth': 'device.system_width',
                    'system_position': 'project.layout',
                    'system_type': 'device.system_type',
                    'turbine_performance': 'device.turbine_performance',
                    'tp': 'farm.max_tp_100_year',
                    'turbine_interdist': 'device.turbine_interdistance',
                    'umbsf': 'project.umbilical_safety_factor',
                    'wakeampfactorcyl':
                        'constants.cylinder_wake_amplificiation',
                    'wavedir': 'farm.wave_direction_100_year',
                    'winddir': 'farm.mean_wind_direction_100_year',
                    'winddragcoefrect': 'constants.rectangular_wind_drag',
                    'windgustdir': 'farm.max_gust_wind_direction_100_year',
                    'windgustvel': 'farm.max_gust_wind_speed_100_year',
                    'windvel': 'farm.mean_wind_speed_100_year',
                    'wlevmax': 'farm.max_water_level_50_year',
                    'wlevmin': 'farm.min_water_level_50_year',
                    'waveinertiacoefrect':
                        'constants.rectangular_wave_inertia',
                    'preline': 'project.predefined_mooring_list',
                    'fabcost': 'project.fabrication_cost',
                    'soilprops': 'constants.soilprops',
                    'fex': 'device.external_forces',
                    "substparams" : "project.substation_props",
                    "umbilical_data" : "project.umbilical_cable_data",
                    "dev_umbilical_point": "device.umbilical_connection_point",
                    "foundations_anchor": "component.foundations_anchor",
                    'foundations_anchor_sand':
                        'component.foundations_anchor_sand',
                    'foundations_anchor_soft':
                        'component.foundations_anchor_soft',
                    "foundations_pile": "component.foundations_pile",
                    "moorings_chain": "component.moorings_chain",
                    "moorings_forerunner": "component.moorings_forerunner",
                    "moorings_rope": "component.moorings_rope",
                    "moorings_shackle": "component.moorings_shackle",
                    "moorings_swivel": "component.moorings_swivel",
                    "moorings_umbilical": "component.dynamic_cable",
                    "rope_stiffness": "component.moorings_rope_stiffness",
                    'substation_layout': 'project.substation_layout',
                    'substation_cog': 'project.substation_cog',
                    'substation_foundations':
                      'project.substation_foundation_location',
                    'network': "project.moorings_foundations_network",
                    "economics_data":
                        "project.moorings_foundations_economics_data",
                    "foundations_data": "project.foundations_component_data",
                    "foundations_soil_data": "project.foundations_soil_data",
                    "seabed_connection": "project.umbilical_seabed_connection",
                    "moorings_data": "project.moorings_component_data",
                    "line_data": "project.moorings_line_data",
                    "dimensions_data": "project.moorings_dimensions",
                    'repeat_foundations': 'options.repeat_foundations',
                    'apply_fex': 'options.apply_fex',
                    "use_max_thrust": "options.use_max_thrust"
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
        
        ## ENVIRONMENT
        
        # Bathymetry (**assume layer 1 in uppermost**)
        zv = self.data.bathymetry["depth"].sel(layer="layer 1").values.T
        xv, yv = np.meshgrid(self.data.bathymetry["x"].values,
                             self.data.bathymetry["y"].values)
        bathy_table = np.dstack([xv.flatten(), yv.flatten(), zv.flatten()])[0]
        safe_bathy = bathy_table[~np.isnan(bathy_table).any(axis=1)]
        
        # Sediments
        sv = self.data.bathymetry["sediment"].sel(layer="layer 1").values
        
        # Convert to short codes
        sv[sv == 'loose sand'] = 'ls'
        sv[sv == 'medium sand'] = 'ms'
        sv[sv == 'dense sand'] = 'ds'
        sv[sv == 'very soft clay'] = 'vsc'
        sv[sv == 'soft clay'] = 'sc'
        sv[sv == 'firm clay'] = 'fc'
        sv[sv == 'stiff clay'] = 'stc'
        sv[sv == 'hard glacial till'] = 'hgt'
        sv[sv == 'cemented'] = 'cm'
        sv[sv == 'soft rock coral'] = 'src'
        sv[sv == 'hard rock'] = 'hr'
        sv[sv == 'gravel cobble'] = 'gc'
        
        infv = np.ones(sv.shape) * np.inf
        
        soil_table = np.dstack([xv.flatten(),
                                yv.flatten(),
                                sv.flatten(),
                                infv.flatten()])[0]
        safe_soil = soil_table[~np.equal(soil_table, None).any(axis=1)]
                                                
        # Distances
        a = self.data.bathymetry["x"].values[:-1]
        b = self.data.bathymetry["x"].values[1:]
        bathy_deltax = (b - a).mean()    

        a = self.data.bathymetry["y"].values[:-1]
        b = self.data.bathymetry["y"].values[1:]
        bathy_deltay = (b - a).mean() 

        # Soil properties
        name_map = {"Drained Soil Friction Angle": "dsfang",
                    "Relative Soil Density": "relsoilden",
                    "Buoyant Unit Weight of Soil": "soilweight",
                    "Undrained Soil / Rock Shear Strength 1": "unshstr0",
                    "Undrained Soil / Rock Shear Strength 2": "unshstr1",
                    "Effective Drained Cohesion": "draincoh",
                    "Seafloor Friction Coefficient": "seaflrfriccoef",
                    "Soil Sensitivity": "soilsen",
                    "Rock Compressive Strength": "rockcompstr"
                     }
                     
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
                             
        soilprops_df = self.data.soilprops
                    
        soilprops_df["Soil Type"] = soilprops_df["Soil Type"].map(soil_map)
        soilprops_df = soilprops_df.set_index("Soil Type")
        soilprops_df = soilprops_df.rename(columns=name_map)
                
        ## STRUCTURES
                   
        # Translate device type
        dev_translate = {'Tidal Fixed': 'tidefixed',
                         'Tidal Floating': 'tidefloat',
                         'Wave Fixed': 'wavefixed',
                         'Wave Floating': 'wavefloat'}
        systype = dev_translate[self.data.system_type]
        
        # Build tidal device characteristics
        use_max_thrust = False
        
        if 'Tidal' in self.data.system_type:
            
            Clen = (self.data.rotor_diam, self.data.turbine_interdist)
            hubheight = self.data.hub_height
            thrustcurv = self.data.turbine_performance[
                            'Coefficient of Thrust'].reset_index().values
            
            # Change frame of reference for floating devices from sea level
            # to bottom of device
            if "floating" in self.data.system_type.lower():
                hubheight += self.data.sysdraft
            
            # Check for max thrust option
            if self.data.use_max_thrust is not None:
                use_max_thrust = self.data.use_max_thrust
        
        else:
            
            Clen = None
            hubheight = None
            thrustcurv = None
            
        # Predefined foundation option
        translate = {'Shallow': 'shallowfoundation',
                     'Gravity': 'gravity',
                     'Pile': 'pile',
                     'Suction Caisson': 'suctioncaisson',
                     'Direct Embedment': 'directembedment',
                     'Drag': 'drag'}
                
        if self.data.repeat_foundations is None:
            prefound = ''
        else:
            prefound = 'uniary'

        if self.data.prefound is not None:
            prefound += translate[self.data.prefound]
            
        if not prefound: prefound = None
        
        # Floating Device characteristics
        if "floating" in self.data.system_type.lower():
            
            # Conversion from sea level reference frame to device bottom.
            # Add draft to vertical coordinate
            
            # Centre of gravity
            syscog = self.data.syscog[:]
            syscog[2] += self.data.sysdraft
            
            # Fairleads
            fair_loc_list = []
            
            for fair_loc in self.data.fairloc:
                new_fair_loc = fair_loc[:]
                new_fair_loc[2] += self.data.sysdraft
                fair_loc_list.append(new_fair_loc)
            
            # Predefined mooring types (optional)
            if self.data.premoor is not None:
                premoor_low = self.data.premoor.lower()
            else:
                premoor_low = None
                
            # Umbilical data
            seabed_connection = self.data.seabed_connection
            umbilical_connection = self.data.dev_umbilical_point[:]
            umbilical_connection[2] += self.data.sysdraft
            
            seabed_connection_dict = {}
            
            for dev, point in seabed_connection.iteritems():
                seabed_connection_dict[dev.lower()] = list(point.coords[0])
            
        else:
            
            syscog = self.data.syscog[:]
            fair_loc_list = None
            premoor_low = None
            umbilical_connection = None
            seabed_connection_dict = None
            
        # Single device forces
        fex_list = None
        
        if self.data.fex is not None and self.data.apply_fex:
            
            fex = self.data.fex
            fex_list = [fex["Te"].values, 
                        fex["Dir"].values,
                        fex["Modes"].values,
                        np.swapaxes(fex.values, 1, 2)]
        
        # Device layout
        sysorig = {key.lower(): np.append(position, 0.).tolist()
                        for key, position in self.data.system_position.items()}
                            
        devices = sysorig.keys()
        
        # Substations
        if self.data.substparams is None:
            
            substation_props = None
            
        else:
            
            name_map = { "Substation Identifier" : "substid",
                         "Type" : "presubstfound",
                         "Mass" : "submass",
                         "Volume" : "subvol",
                         "Length" : "sublength",
                         "Width" : "subwidth",
                         "Height" : "subheight",
                         "Profile" : "subprof",
                         "Wet Frontal Area" : "subwetfa",
                         "Wet Beam Area" : "subwetba",
                         "Dry Frontal Area" : "subdryfa",
                         "Dry Beam Area" : "subdryba",
                         "Surface Roughness" : "subrough",
                         "Orientation Angle" : "suborienang",
                         }
                         
            substation_props = self.data.substparams.rename(columns=name_map)
            substation_props = substation_props.set_index("substid")
            substation_props = substation_props.drop(["Marker"], axis=1)
            
            suborig = pd.Series(name='suborig')
            subcog = pd.Series(name='subcog')
            substloc = pd.Series(name='substloc')
            
            # Build in positional data for substations
            for sub_id in substation_props.index:
                local_orig = list(
                                self.data.substation_layout[sub_id].coords[0])
                if len(local_orig) == 2: local_orig.append(0.)
                
                suborig[sub_id] = str(local_orig)
                subcog[sub_id] = str(self.data.substation_cog[sub_id].tolist())
                                   
                substloc[sub_id] = str(self.data.substation_foundations[
                                                            sub_id].tolist())
                
            substation_props = pd.concat([substation_props,
                                          suborig,
                                          subcog,
                                          substloc],
                                          axis=1)
                

        ## COMPONENTS
        compdict = self.get_all_components(self.data.system_type,
                                           self.data.foundations_anchor,
                                           self.data.foundations_anchor_sand,
                                           self.data.foundations_anchor_soft,
                                           self.data.foundations_pile,
                                           self.data.moorings_chain,
                                           self.data.moorings_forerunner,
                                           self.data.moorings_rope,
                                           self.data.rope_stiffness,
                                           self.data.moorings_shackle,
                                           self.data.moorings_swivel,
                                           self.data.moorings_umbilical)
            
        # No umbilical unlesss floating
        preumb = None
            
        if "floating" in self.data.system_type.lower():
            
            # Check umbilical definition
            if self.data.preumb in compdict:
                preumb = self.data.preumb
            elif int(self.data.preumb) in compdict:
                preumb = int(self.data.preumb)
            elif long(self._variables.preumb) in compdict:
                preumb = long(self.data.preumb) 
            else:
                errStr = ("Selected umbilical component '{}' not found in "
                          "component dictionary").format(
                                                      self._variables.preumb)
                raise KeyError(errStr)
                
        # Data tweaks
        if self.data.hs == 0.0:
            hs_max= []
        else:
            hs_max = [self.data.hs]
            
        if self.data.wavedir == 0.0:
            wavedir_max = [0.]
        else:
            wavedir_max = [self.data.wavedir]
            
        if self.data.tp == 0.0:
            tp_max= []
        else:
            tp_max = [self.data.tp]
            
        if self.data.gamma == 0.0:
            gamma_max= []
        else:
            gamma_max = [self.data.gamma]
            
        # Add header rows where necessary
        self.data.hcfdrsoil.loc[-1] = [20, 25, 30, 35, 40]
        self.data.hcfdrsoil = self.data.hcfdrsoil.sort_index()
        
        self.data.pilemomcoefam.loc[-1] = [10, 5, 4, 3, 2]
        self.data.pilemomcoefam = self.data.pilemomcoefam.sort_index()
        
        self.data.pilemomcoefbm.loc[-1] = [10, 5, 4, 3, 2]
        self.data.pilemomcoefbm = self.data.pilemomcoefbm.sort_index()
        
        self.data.subgradereaccoef.loc[-1] = [35, 50, 65, 85]
        self.data.subgradereaccoef = self.data.subgradereaccoef.sort_index()
        
        self.data.wakeampfactorcyl.loc[-1] = [0.65, 1.05]
        self.data.wakeampfactorcyl = self.data.wakeampfactorcyl.sort_index()
        
        self.data.winddragcoefrect.loc[-1] = [0, 1, 2, 4, 6, 10, 20]
        self.data.winddragcoefrect = self.data.winddragcoefrect.sort_index()
                
#    #-------------------------------------------------------------------------- 
#    #--------------------------------------------------------------------------
#    #------------------ WP4 Variables class
#    #--------------------------------------------------------------------------
#    #-------------------------------------------------------------------------- 
#    Input of variables into this class 
#
#    Functions:        
#
#    Args:        
#        devices (list) [-]: list of device identification numbers
#        gravity (float) [m/s2]: acceleration due to gravity
#        seaden (float) [kg/m3]: sea water density
#        airden (float) [kg/m3]: air density
#        steelden (float) [kg/m3]: steel density
#        conden (float) [kg/m3]: concrete density
#        groutden (float) [kg/m3]: grout density
#        compdict (dict) [various]: component dictionary
#        soiltypgrid (numpy.ndarray): soil type grid: X coordinate (float) [m], 
#                                    Y coordinate (float) [m], 
#                                    soil type options (str) [-]: 'ls': loose sand,
#                                                            'ms': medium sand,
#                                                            'ds': dense sand,
#                                                            'vsc': very soft clay,
#                                                            'sc': soft clay,
#                                                            'fc': firm clay,
#                                                            'stc': stiff clay,
#                                                            'hgt': hard glacial till,
#                                                            'cm': cemented,
#                                                            'src': soft rock coral,
#                                                            'hr': hard rock,
#                                                            'gc': gravel cobble,
#                                    depth (float) [m]    
#        seaflrfriccoef (float) [-]: optional soil friction coefficient
#        bathygrid (numpy.ndarray): bathymetry grid: X coordinate (float) [m], 
#                                                    Y coordinate (float) [m], 
#                                                    Z coordinate (float) [m]
#        bathygriddeltax (float) [m]: bathymetry grid X axis grid spacing
#        bathygriddeltay (float) [m]: bathymetry grid Y axis grid spacing
#        wlevmax (float) [m]: maximum water level above mean sea level
#                             (50 year return period)
#        wlevmin (float) [m]: minimum water level below mean sea level
#                             (50 year return period)
#        currentvel (float) [m/s]: maximum current velocity magnitude
#                                  (10 year return period)
#        currentdir (float) [deg]: current direction at maximum velocity 
#        currentprof (str) [-]: current profile options: 'uniform', 
#                                                        '1/7 power law'
#        wavedir (float) [deg]: predominant wave direction(s)
#        hs (list) [m]: maximum significant wave height (100 year return period)
#        tp (list) [s]: maximum peak period (100 year return period)
#        gamma (float) [-]: jonswap shape parameter(s)
#        windvel (float) [m/s]: mean wind velocity magnitude
#                               (100 year return period)
#        winddir (float) [deg]: predominant wind direction 
#        windgustvel (float) [m/s]: wind gust velocity magnitude
#                                   (100 year return period)
#        windgustdir (float) [deg]: wind gust direction
#        soilprops (pandas) [-]: default soil properties table:  drained soil friction angle [deg],
#                                                                relative soil density [%],
#                                                                buoyant unit weight of soil [N/m^3],
#                                                                undrained soil shear strengths [N/m^2, N/m^2] or rock shear strengths [N/m^2],
#                                                                effective drained cohesion [N/m^2],
#                                                                Seafloor friction coefficient [-],
#                                                                Soil sensitivity [-],
#                                                                rock compressive strength [N/m^2]        
#        linebcf (numpy.ndarray): buried mooring line bearing capacity factor:   soil friction angle [deg],
#                                                                                bearing capacity factor[-]
#        k1coef (numpy.ndarray): coefficient of subgrade reaction (cohesive soils):  allowable deflection/diameter[-],
#                                                                                    soft clay coefficient [-],
#                                                                                    stiff clay coefficient [-]
#        soilsen (float) [-]: soil sensitivity
#        subgradereaccoef (numpy.ndarray): coefficient of subgrade reaction (cohesionless soils): allowable deflection/diameter[-],
#                                                                                                35% relative density coefficient [-],
#                                                                                                50% relative density coefficient [-],
#                                                                                                65% relative density coefficient [-],
#                                                                                                85% relative density coefficient [-]
#                                           Note that the first row of the array contains the percentiles themselves using 0.0 as the
#                                           value for the first column
#        piledefcoef (numpy.ndarray): pile deflection coefficients:  depth coefficient[-],
#                                                                    coefficient ay [-],
#                                                                    coefficient by [-]
#                                                                    
#        pilemomcoefam (numpy.ndarray): pile moment coefficient am:  depth coefficient[-],
#                                                                    pile length/relative soil-pile stiffness = 10 [-],
#                                                                    pile length/relative soil-pile stiffness = 5 [-],	
#                                                                    pile length/relative soil-pile stiffness = 4 [-],	
#                                                                    pile length/relative soil-pile stiffness = 3 [-],	
#                                                                    pile length/relative soil-pile stiffness = 2 [-]
#                                       Note that the first row of the array contains the stiffnesses themselves using 
#                                       0.0 as the value for the first column
#        pilemomcoefbm (numpy.ndarray): pile moment coefficient bm:  depth coefficient[-],
#                                                                    pile length/relative soil-pile stiffness = 10 [-],
#                                                                    pile length/relative soil-pile stiffness = 5 [-],	
#                                                                    pile length/relative soil-pile stiffness = 4 [-],	
#                                                                    pile length/relative soil-pile stiffness = 3 [-],	
#                                                                    pile length/relative soil-pile stiffness = 2 [-]
#                                       Note that the first row of the array contains the stiffnesses themselves using 
#                                       0.0 as the value for the first column
#        pilefricresnoncal (numpy.ndarray): pile skin friction and end bearing capacity: soil friction angle [deg],
#                                                                                        friction angle sand-pile [deg],	
#                                                                                        max bearing capacity factor [-],
#                                                                                        max unit skin friction [N/m2],
#                                                                                        max end bearing capacity [N/m2]
#        hcfdrsoil (numpy.ndarray): holding capacity factor for drained soil condition: relative embedment depth [-],
#                                                                                        drained friction angle = 20deg [-],
#                                                                                        drained friction angle = 25deg [-],	
#                                                                                        drained friction angle = 30deg [-],	
#                                                                                        drained friction angle = 35deg [-],	
#                                                                                        drained friction angle = 40deg [-]
#                                   Note that the first row of the array contains the drained friction angle using 
#                                   0.0 as the value for the first column        
#        systype (str) [-]: system type: options:    'tidefloat', 
#                                                    'tidefixed', 
#                                                    'wavefloat', 
#                                                    'wavefixed'                            
#        depvar (bool) [-]: depth variation permitted: options:   True,
#                                                                False                                                            
#        sysprof (str) [-]: system profile: options:    'cylindrical', 
#                                                        'rectangular'
#        sysmass (float) [kg]: system mass
#        syscog (numpy.ndarray): system centre of gravity in local coordinates:  X coordinate (float) [m], 
#                                                                                Y coordinate (float) [m], 
#                                                                                Z coordinate (float) [m]
#        sysvol (float) [m3]: system submerged volume
#        sysheight (float) [m]: system height
#        syswidth (float) [m]: system width
#        syslength (float) [m]: system length        
#        sysrough (float) [m]: system roughness
#        sysorig (dict): system origin (UTM):   {deviceid: (X coordinate (float) [m], 
#                                                           Y coordinate (float) [m], 
#                                                           Z coordinate (float) [m])}
#        fairloc (numpy.ndarray): fairlead locations in local coordinates for N lines:   X coordinate (float) [m], 
#                                                                                        Y coordinate (float) [m], 
#                                                                                        Z coordinate (float) [m]
#        foundloc (numpy.ndarray): foundation locations in local coordinates for N foundations:      X coordinate (float) [m], 
#                                                                                                    Y coordinate (float) [m], 
#                                                                                                    Z coordinate (float) [m]
#        umbconpt (numpy.ndarray): umbilical connection point:   X coordinate (float) [m], 
#                                                                Y coordinate (float) [m], 
#                                                                Z coordinate (float) [m] 
#        sysdryfa (float) [m2]: system dry frontal area
#        sysdryba (float) [m2]: system dry beam area
#        dragcoefcyl (numpy.ndarray): cylinder drag coefficients:    reynolds number [-],
#                                                                    smooth coefficient [-],	
#                                                                    roughness = 1e-5	coefficient [-],
#                                                                    roughness = 1e-2 coefficient [-]
#        wakeampfactorcyl (numpy.ndarray): cylinder wake amplificiation factors: kc/steady drag coefficient [-],
#                                                                                smooth cylinder amplification factor [-],
#                                                                                rough cylinder amplification factor [-]
#        winddragcoefrect (numpy.ndarray): rectangular wind drag coefficients:   width/length [-],
#                                                                                0<height/breadth<1 [-],
#                                                                                height/breadth = 1 [-],
#                                                                                height/breadth = 2 [-],
#                                                                                height/breadth = 4	 [-],
#                                                                                height/breadth = 6	 [-],
#                                                                                height/breadth = 10 [-],
#                                                                                height/breadth = 20 [-]
#        currentdragcoefrect (numpy.ndarray): rectangular current drag coefficients: width/length [-],
#                                                                                    thickness/width = 0 [-]
#        driftcoeffloatrect (numpy.ndarray): rectangular drift coefficients: wavenumber*draft [m],
#                                                                            reflection coefficient [-]        
#        Clen (tuple): rotor parameters: rotor diameter [m],
#                                        distance from centreline [m]
#        thrustcurv (numpy.ndarray): thrust curve:   inflow velocity magnitude [m/s],
#                                                    thrust coefficient [-]
#        hubheight (float) [m]: rotor hub height 
#        sysorienang (float) [deg]: system orientation angle
#        fex (numpy.ndarray): first-order wave excitation forces: analysed frequencies (list) [Hz],
#                                                                 complex force amplitudes (nxm list) for n directions and m degrees of freedom                                                                 
#        premoor (str) [-]: predefined mooring system type: options:     'catenary', 
#                                                                        'taut' 
#        maxdisp (numpy.ndarray): optional maximum device displacements:  surge (float) [m], 
#                                                                         sway (float) [m], 
#                                                                         heave (float) [m]
#        prefound (str) [-]: predefined foundation type: options:    'shallowfoundation', 
#                                                                    'gravity',
#                                                                    'pile',
#                                                                    'suctioncaisson',
#                                                                    'directembedment',
#                                                                    'drag'                                                                    
#        coststeel (float) [euros/kg]: cost of steel
#        costgrout (float) [euros/kg]: cost of grout
#        costcon (float) [euros/kg]: cost of concrete
#        groutstr (float) [N/mm2]: grout compressive strength
#        preumb (str) [-]: predefined umbilical type
#        umbsf (float) [-]: umbilical safety factor
#        foundsf (float) [-]: foundation safety factor
#        prefootrad (float) [m]: predefined foundation radius
#        subcabconpt (dict) [-]: subsea cable connection point for each device:     X coordinate (float) [m], 
#                                                                                        Y coordinate (float) [m], 
#                                                                                        Z coordinate (float) [m] 
#        presubstfound (str) [-]: predefined foundation type: options:   'gravity',
#                                                                        'pile'                                                                         
#        suborig (numpy.ndarray): substation origin(s) (UTM): 'array'   X coordinate (float) [m], 
#                                                                    Y coordinate (float) [m], 
#                                                                    Z coordinate (float) [m]
#                                                             'subhubXXX'   X coordinate (float) [m], 
#                                                                           Y coordinate (float) [m], 
#                                                                           Z coordinate (float) [m]
#        submass (float) [kg]: substation mass
#        subvol (float) [m3]: substation submerged volume
#        subcog (numpy.ndarray): substation centre of gravity in local coordinates:  X coordinate (float) [m], 
#                                                                                Y coordinate (float) [m], 
#                                                                                Z coordinate (float) [m]
#        subwetfa (float) [m]: substation wet frontal area
#        subdryfa (float) [m]: substation dry frontal area
#        subwetba (float) [m]: substation wet beam area
#        subdryba (float) [m]: substation dry beam area
#        substloc (numpy.ndarray): substation foundation locations in local coordinates for N foundations:   X coordinate (float) [m], 
#                                                                                                            Y coordinate (float) [m], 
#                                                                                                            Z coordinate (float) [m]    
#        moorsfuls (float) [-]: mooring ultimate limit state safety factor
#        moorsfals (float) [-]: mooring accident limit state safety factor
#        groutsf (float) [-]: grout strength safety factor
#        syswetfa (float) [m2]: system wet frontal area
#        syswetba (float) [m2]: system wet beam area
#        sysdraft (float) [m]: system draft
#        sublength (float) [m]: substation length
#        subwidth (float) [m]: substation width
#        subheight (float) [m]: substation height
#        subprof (str) [-]: substation profile: options:    'cylindrical', 
#                                                            'rectangular'
#        subrough (float) [m]: substation roughness
#        suborienang (float) [deg]: substation orientation angle
#        waveinertiacoefrect (numpy.ndarray): rectangular wave inertia coefficients: width/length [-],
#                                                                                    inertia coefficients [-] 
#        preline (list) [-]: predefined mooring component list
#        fabcost (float) [-]: optional fabrication cost factor
#        maxlines (int, optional) [-]: maximum number of lines per device.
#                                      Defaults to 12.
#        use_max_thrust (bool, optional) [-]:
#            Use the maximum thrust coefficient when calculating tidal turbine
#            loads. Defaults to False.
            
        input_data = Variables(
                           devices,
                           self.data.gravity,
                           self.data.seaden,
                           self.data.airden,
                           self.data.steelden,
                           self.data.conden,
                           self.data.groutden,
                           compdict,
                           safe_soil, 
                           None,
                           safe_bathy,
                           bathy_deltax,
                           bathy_deltay,
                           self.data.wlevmax,
                           self.data.wlevmin,
                           self.data.currentvel,
                           self.data.currentdir,
                           self.data.currentprof.lower(),
                           wavedir_max,
                           hs_max,
                           tp_max,
                           gamma_max,
                           self.data.windvel,
                           self.data.winddir,
                           self.data.windgustvel,
                           self.data.windgustdir,
                           soilprops_df,
                           self.data.linebcf,
                           self.data.k1coef.reset_index().values,
                           self.data.soilsen,
                           self.data.subgradereaccoef.reset_index().values,
                           self.data.piledefcoef.reset_index().values,
                           self.data.pilemomcoefam.reset_index().values,
                           self.data.pilemomcoefbm.reset_index().values,
                           self.data.pilefricresnoncal.reset_index().values,
                           self.data.hcfdrsoil.reset_index().values,                               
                           systype,
                           self.data.depvar,
                           self.data.sysprof.lower(),
                           self.data.sysmass,
                           syscog,
                           self.data.sysvol,
                           self.data.sysheight,
                           self.data.syswidth,
                           self.data.syslength,
                           self.data.sysrough,
                           sysorig,
                           fair_loc_list,
                           self.data.foundloc,
                           umbilical_connection,
                           self.data.sysdryfa,
                           self.data.sysdryba,
                           self.data.dragcoefcyl.reset_index().values,
                           self.data.wakeampfactorcyl.reset_index().values,
                           self.data.winddragcoefrect.reset_index().values,
                           self.data.currentdragcoefrect.reset_index().values,
                           self.data.driftcoeffloatrect.reset_index().values,
                           Clen,
                           thrustcurv,
                           hubheight,
                           self.data.sysorienang,
                           fex_list,
                           premoor_low,
                           self.data.maxdisp,
                           prefound,
                           self.data.coststeel,
                           self.data.costgrout,
                           self.data.costcon,
                           self.data.groutstr,
                           preumb,
                           self.data.umbsf,
                           self.data.foundsf,
                           self.data.prefootrad,
                           seabed_connection_dict,
                           substation_props,
                           self.data.moorsfuls,
                           self.data.moorsfals,
                           self.data.groutsf,
                           self.data.syswetfa,
                           self.data.syswetba,
                           self.data.sysdraft,
                           self.data.waveinertiacoefrect.reset_index().values,
                           self.data.preline,
                           self.data.fabcost,
                           use_max_thrust=use_max_thrust
                           )
        
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

            pkl_path = debugdir.get_path("moorings_inputs.pkl")
            pickle.dump(input_data, open(pkl_path, "wb"))
        
        main = Main(input_data)
        
        if debug_entry: return
        
        # Run the module
        main()
        
        if export_data:
            
            result = {"economics": main.sysecobom,
                      "bom": main.sysrambom,
                      "hierarchy": main.syshier,
                      "foundations": main.sysfoundinsttab,
                      "environmental": main.sysenv}
                      
            if "floating" in self.data.system_type.lower():
                
                result["moorings"] = main.sysmoorinsttab
                result["umbilical"] = main.sysumbinsttab
                      
            pkl_path = debugdir.get_path("moorings_outputs.pkl")
            pickle.dump(result, open(pkl_path, "wb"))
        
        # Raise an error on foundation not found output
        if main.sysfoundinsttab['type [-]'].isin(
                            ["Foundation solution not found"]).any():
            
            errStr = "One or more foundations could not be designed"
            raise RuntimeError(errStr)
        
        name_map = {"compid [-]" : "Key Identifier",
                    "component cost [euros] [-]" : "Cost",
                    "quantity [-]" : "Quantity",
                    "project year" : "Year"
                    }

        economics_data = main.sysecobom.rename(columns=name_map)
        economics_data = economics_data.loc[
                            economics_data["Quantity"].astype(str) != "n/a"]
        
        # Remove any rows with n/a in the quantity column.
        economics_data["Quantity"] = pd.to_numeric(economics_data["Quantity"])
        economics_data = economics_data.dropna()
                            
        self.data.economics_data = economics_data
                        
        # Build network dictionary
        raw_network = {"topology": main.syshier,
                       "nodes": main.sysrambom}
                       
        self.data.network = raw_network
        
        foundations_data = main.sysfoundinsttab

        # Manipulate the table
        foundations_data = foundations_data.drop('devices [-]', axis=1)
        foundations_data = foundations_data.drop('foundations [-]', axis=1)
        foundations_data = foundations_data[
            ~ foundations_data["type [-]"].str.contains(
                                                    "Foundation not required")]
        
        layer_lists = foundations_data.pop(
            'layer information (layer number, soil type, soil depth) [-,-,m]')
        
        change_cols = ['x coord [m]',
                       'y coord [m]',
                       'bathymetry at MSL [m]',
                       'length [m]',
                       'width [m]',
                       'height [m]',
                       'installation depth [m]',
                       'dry mass [kg]',
                       'grout volume [m3]',
                       'marker [-]']
        
        foundations_data[change_cols] = \
            foundations_data[change_cols].apply(pd.to_numeric, errors='coerce')
        
        name_map = {'type [-]': 'Type',
                    'subtype [-]': 'Sub-Type',
                    'x coord [m]': 'UTM X',
                    'y coord [m]': 'UTM Y',
                    'bathymetry at MSL [m]': 'Depth',
                    'length [m]': 'Length',
                    'width [m]': 'Width',
                    'height [m]': 'Height',
                    'installation depth [m]': 'Installation Depth',
                    'dry mass [kg]': 'Dry Mass',
                    'grout type [-]': 'Grout Type',
                    'grout volume [m3]': 'Grout Volume',
                    'marker [-]': 'Marker'}
                    
        self.data.foundations_data = \
                        foundations_data.rename(columns=name_map)

        # Break down the list of tuples              
        layer_numbers = []
        soil_types = []
        soil_depths = []
        
        for layer_list in layer_lists:
            
            layer_tuple = layer_list[0]
            
            layer_numbers.append(layer_tuple[0])
            soil_types.append(layer_tuple[1])
            soil_depths.append(layer_tuple[2])
            
        layers_dict = {"Layer Number": layer_numbers,
                       "Soil Type": soil_types,
                       "Depth": soil_depths}
                               
        foundations_layers = pd.DataFrame(layers_dict)
        foundations_layers["Marker"] = foundations_data['marker [-]'].values
            
        # Convert soil types to long codes
        inv_soil_map = {'cm' : 'cemented',
                        'ds' : 'dense sand',
                        'fc' : 'firm clay',
                        'gc' : 'gravel cobble',
                        'hgt': 'hard glacial till',
                        'hr' : 'hard rock',
                        'ls' : 'loose sand',
                        'ms' : 'medium sand',
                        'sc' : 'soft clay',
                        'src': 'soft rock coral',
                        'stc': 'stiff clay',
                        'vsc': 'very soft clay'}

        foundations_layers["Soil Type"] = \
                        foundations_layers["Soil Type"].map(inv_soil_map)
                        
        self.data.foundations_soil_data = foundations_layers

        # Record the system dimensions
        env_data = main.sysenv
        
        footprint_list = []
        volume_list = []
        dev_list = []
        
        for dev_id, env_dict in env_data.iteritems():
            dev_list.append(dev_id)
            footprint_list.append(env_dict[
                                        'Configuration footprint area [m2]'])
            volume_list.append(env_dict["Configuration volume [m3]"][0])
            
        raw_env = {"System Identifier": dev_list,
                   "Footprint Area": footprint_list,
                   "Volume": volume_list}
        env_df = pd.DataFrame(raw_env)
        env_df = env_df.sort_values(["System Identifier"])
        
        self.data.dimensions_data = env_df
        
        if "floating" in self.data.system_type.lower():
            
            # Record the lines and moorings components results
            moorings_df = main.sysmoorinsttab
            
            marker_list = []
            line_list = []
            
            # Unroll the component list in the line specifications
            for _, line in moorings_df.iterrows():
                
                line_marker_strs = line["marker [-]"]
                line_markers = [int(x) for x in line_marker_strs]
                
                line_id = line["lines [-]"]
                line_ids = [line_id]*len(line_markers)
                
                marker_list.extend(line_markers)
                line_list.extend(line_ids)
                
            moorings_raw = {"Line Identifier": line_list,
                            "Marker": marker_list}
            moorings_data = pd.DataFrame(moorings_raw)
            
            line_data = moorings_df.drop(["devices [-]", "marker [-]"],
                                              axis=1)
                                              
            name_map = {'dry mass [kg]': 'Dry Mass',
                        'length [m]': 'Length',
                        'lines [-]': 'Line Identifier',
                        'type [-]': 'Type'}
                        
            line_data = line_data.rename(columns=name_map)
            
            self.data.line_data = line_data
            self.data.moorings_data = moorings_data
            
            # Set the umbilical data
            umbilical_data = main.sysumbinsttab
            
            umbilical_data = umbilical_data.drop(
                                            ["devices [-]",
                                             "subsea connection x coord [m]",
                                             "subsea connection y coord [m]",
                                             "subsea connection z coord [m]"],
                                            axis=1)
                                            
            name_map = {'component id [-]': 'Key Identifier',
                        'dry mass [kg]': 'Dry Mass',
                        'flotation length [m]': 'Floatation Length',
                        'length [m]': 'Length',
                        'required flotation [N/m]': 'Required Floatation',
                        'marker [-]': 'Marker'}
                        
            self.data.umbilical_data = umbilical_data.rename(columns=name_map)

        return
    
    @classmethod
    def get_all_components(cls, system_type,
                                foundations_anchor,
                                foundations_anchor_sand,
                                foundations_anchor_soft,
                                foundations_pile,
                                moorings_chain,
                                moorings_forerunner,
                                moorings_rope,
                                rope_stiffness,
                                moorings_shackle,
                                moorings_swivel,
                                moorings_umbilical):
        
        compdict = {}
        
        # Foundations
        anchor_dict = get_component_dict(
                                "drag anchor",
                                foundations_anchor,
                                sand_data=foundations_anchor_sand,
                                soft_data=foundations_anchor_soft)
        compdict.update(anchor_dict)
            
        pile_dict = get_component_dict("pile",
                                       foundations_pile,
                                       check_keys=compdict.keys())
        compdict.update(pile_dict)
        
        # Moorings
        if "floating" in system_type.lower():
            
            chain_dict = get_component_dict("chain",
                                            moorings_chain,
                                            check_keys=compdict.keys())
            compdict.update(chain_dict)
                
            forerunner_dict = get_component_dict("forerunner assembly",
                                                 moorings_forerunner,
                                                 check_keys=compdict.keys())
            compdict.update(forerunner_dict)
                
            rope_dict = get_component_dict("rope",
                                           moorings_rope,
                                           rope_data=rope_stiffness,
                                           check_keys=compdict.keys())
            compdict.update(rope_dict)
                
            shackle_dict = get_component_dict("shackle",
                                              moorings_shackle,
                                              check_keys=compdict.keys())
            compdict.update(shackle_dict)
                
            swivel_dict = get_component_dict("swivel",
                                             moorings_swivel,
                                             check_keys=compdict.keys())
            compdict.update(swivel_dict)
            
            umbilical_dict = get_component_dict("cable",
                                                moorings_umbilical,
                                                check_keys=compdict.keys())
            compdict.update(umbilical_dict)
            
        return compdict
