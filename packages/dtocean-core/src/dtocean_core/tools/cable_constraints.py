# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2024 Mathew Topper
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

import pkg_resources

import matplotlib.pyplot as plt

from dtocean_electrical.main import Electrical
from dtocean_electrical.output import plot_devices
from dtocean_electrical.grid.grid_processing import grid_processing

from . import Tool
from ..interfaces.electrical import ElectricalInterface
from ..utils.version import Version

# Check module version
pkg_title = "dtocean-electrical"
major_version = 2
version = pkg_resources.get_distribution(pkg_title).version

if not Version(version).major == major_version:
    
    err_msg = ("Incompatible version of {} detected! Major version {} is "
               "required, but version {} is installed").format(pkg_title,
                                                               major_version,
                                                               version)
    raise ImportError(err_msg)


class CableConstraintsTool(Tool):
    
    """Generate a plot showing the constraints encountered by the 
    electrical subsystems module."""
        
    @classmethod         
    def get_name(cls):

        return "Cable Constraints Plot"
        
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

        return ElectricalInterface.declare_inputs()

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

        return None

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

        return ElectricalInterface.declare_optional()
    
    @classmethod
    def declare_id_map(cls):

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
        
        id_map = {
         'annual_energy': 'project.annual_energy',
         'bathymetry': 'bathymetry.layers',
         'collection_point_cog': 'component.collection_point_cog',
         'collection_point_foundations':
             'component.collection_point_foundations',
         'collection_points': 'component.collection_points',
         'constant_power_factor': 'device.constant_power_factor',
         'corridor_landing_point': 'corridor.landing_point',
         'corridor_nogo_areas': 'corridor.nogo_areas',
         'corridor_target_burial_depth': 'project.export_target_burial_depth',
         'corridor_voltage': 'project.export_voltage',
         'dev_umbilical_point': 'device.umbilical_connection_point',
         'device_connector_type': 'device.connector_type',
         'device_type': 'device.system_type',
         'devices_per_string': 'project.devices_per_string',
         'dry_mate_connectors': 'component.dry_mate_connectors',
         'dynamic_cable': 'component.dynamic_cable',
         'equipment_gradient_constraint':
             'project.equipment_gradient_constraint',
         'export_strata': 'corridor.layers',
         'footprint_coords': 'device.footprint_coords',
         'footprint_radius': 'device.prescribed_footprint_radius',
         'gravity': 'constants.gravity',
         'installation_soil_compatibility':
             'component.installation_soil_compatibility',
         'layout': 'project.layout',
         'main_direction': 'project.main_direction',
         'mean_power_hist_per_device': 'project.mean_power_hist_per_device',
         'network_configuration': 'project.network_configuration',
         'nogo_areas': 'farm.nogo_areas',
         'onshore_infrastructure_cost': 'project.onshore_infrastructure_cost',
         'power_factor': 'device.power_factor',
         'power_rating': 'device.power_rating',
         'static_cable': 'component.static_cable',
         'target_burial_depth': 'project.target_burial_depth',
         'transformers': 'component.transformers',
         'umbilical_sf': 'project.umbilical_safety_factor',
         'umbilical_type': 'device.umbilical_type',
         'sysdraft': 'device.system_draft',
         'users_tool': 'options.user_installation_tool',
         'voltage': 'device.voltage',
         'wet_mate_connectors': 'component.wet_mate_connectors',
         "boundary_padding": 'options.boundary_padding'
         }

        return id_map
        
    def configure(self, kwargs=None):
        
        """Does nothing in this case"""

        return
        
    def connect(self, **kwargs):
        
        elec, constrained_lines = get_constraints(self.data)

        fig = plot_devices(elec.grid,
                           constrained_lines,
                           elec.array_data.layout,
                           elec.array_data.landing_point,
                           elec.array_data.device_footprint,
                           [],
                           [],
                           [],
                           []
                           )
        plt.show()
            
        return
        
def get_constraints(data):
    
    input_dict = ElectricalInterface.get_input_dict(data)
    
    elec = Electrical(input_dict["site_data"],
                      input_dict["array_data"],
                      input_dict["export_data"],
                      input_dict["options"],
                      input_dict["database"])
    
    if elec.status < 0:

        all_errors = ". ".join(elec.error_string)
        errStr = 'Some errors in input data: {}'.format(all_errors)
        raise ValueError(errStr)

    else:

        elec.grid, constrained_polygons, constrained_lines = \
            grid_processing(elec.site_data, elec.export_data, elec.options)
            
        elec._fix_features_to_grid()
        
    return elec, constrained_lines
