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

"""
Created on Fri Jul 29 17:44:49 2016

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

from aneris.boundary.interface import QueryInterface

from ..utils.database import (init_bathy_records,
                              bathy_records_to_strata,
                              tidal_series_records_to_xset)


class LeaseBathyInterface(QueryInterface):
    
    '''Interface to filter the database for a selected site and technology.
    '''
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Lease Area Bathymetry Filtering Interface"
    
    @classmethod
    def declare_inputs(cls):
        
        '''A class method to declare all the variables required as inputs by
        this interface. 
        
        Returns:
          list: List of inputs identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example:
          
              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''
        
        input_list  =  ["site.lease_boundary"]
        
        return input_list
    
    @classmethod
    def declare_outputs(cls):
        
        '''A class method to declare all the output variables provided by
        this interface.
        
        Returns:
          list: List of output identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example:
          
              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        '''
        
        outputs = ["bathymetry.layers"]
        
        return outputs
    
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
          appear in the declare_inputs output. For example:
          
              optional = ["My:first:variable",
                         ]
        '''
        
        option_list = None
        
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
          example:
          
              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }
        
        '''
        
        id_map = {"bathymetry": "bathymetry.layers",
                  "lease_poly": "site.lease_boundary"
                  }
        
        return id_map
    
    def connect(self):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
        # Manipulate wkt string for function requirements
        poly_wkt = self.data.lease_poly.to_wkt()
        func_poly_str = poly_wkt.replace("POLYGON ((", "")[:-2]
        
        query_str = ("SELECT "
                     "utm_point, "
                     "depth, "
                     "layer_order, "
                     "initial_depth, "
                     "sediment_type "
                     "FROM "
                     "filter.sp_select_bathymetry_by_polygon"
                     "('{}')").format(func_poly_str)
        
        result = self._db.server_execute_query(query_str)
        pre_bathy = init_bathy_records(result)
        
        raw_strata = bathy_records_to_strata(pre_bathy=pre_bathy)
        self.data.bathymetry = raw_strata
        
        return

class CorridorBathyInterface(QueryInterface):
    
    '''Interface to filter the database for a selected site and technology.
    '''
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Cable Corridor Bathymetry Filtering Interface"
    
    @classmethod
    def declare_inputs(cls):
        
        '''A class method to declare all the variables required as inputs by
        this interface. 
        
        Returns:
          list: List of inputs identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example:
          
              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''
        
        input_list  =  ["site.corridor_boundary"]
        
        return input_list
    
    @classmethod
    def declare_outputs(cls):
        
        '''A class method to declare all the output variables provided by
        this interface.
        
        Returns:
          list: List of output identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example:
          
              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        '''
        
        outputs = ["corridor.layers"]
        
        return outputs
    
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
          appear in the declare_inputs output. For example:
          
              optional = ["My:first:variable",
                         ]
        '''
        
        option_list = None
        
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
          example:
          
              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }
        
        '''
        
        id_map = {"corridor": "corridor.layers",
                  "corridor_poly": "site.corridor_boundary"
                  }
        
        return id_map
    
    def connect(self):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
        # Manipulate wkt string for function requirements
        poly_wkt = self.data.corridor_poly.to_wkt()
        func_poly_str = poly_wkt.replace("POLYGON ((", "")[:-2]
        
        query_str = (
             "SELECT "
             "utm_point, "
             "depth, "
             "layer_order, "
             "initial_depth, "
             "sediment_type "
             "FROM "
             "filter.sp_select_cable_corridor_bathymetry_by_polygon"
             "('{}')").format(func_poly_str)
        
        result = self._db.server_execute_query(query_str)
        
        raw_strata = bathy_records_to_strata(result)
        self.data.corridor = raw_strata
        
        return


class TidalEnergyInterface(QueryInterface):
    
    '''Interface to filter the database for a selected site and technology.
    '''
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Tidal Energy Time Series Filtering Interface"
    
    @classmethod
    def declare_inputs(cls):
        
        '''A class method to declare all the variables required as inputs by
        this interface. 
        
        Returns:
          list: List of inputs identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example:
          
              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''
        
        input_list  =  ["site.lease_boundary"]
        
        return input_list
    
    @classmethod
    def declare_outputs(cls):
        
        '''A class method to declare all the output variables provided by
        this interface.
        
        Returns:
          list: List of output identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example:
          
              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        '''
        
        outputs = ["farm.tidal_series"]
        
        return outputs
    
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
          appear in the declare_inputs output. For example:
          
              optional = ["My:first:variable",
                         ]
        '''
        
        option_list = None
        
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
          example:
          
              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }
        
        '''
        
        id_map = {"tidal_series": "farm.tidal_series",
                  "lease_poly": "site.lease_boundary"
                  }
        
        return id_map
    
    def connect(self):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
        # Manipulate wkt string for function requirements
        poly_wkt = self.data.lease_poly.to_wkt()
        func_poly_str = poly_wkt.replace("POLYGON ((", "")[:-2]
        
        query_str = (
                "SELECT "
                "utm_point, "
                "measure_date, "
                "measure_time, "
                "u, "
                "v, "
                "turbulence_intensity, "
                "ssh "
                "FROM "
                "filter.sp_select_tidal_energy_time_series_by_polygon"
                "('{}')").format(func_poly_str)
        
        result = self._db.server_execute_query(query_str)
        raw_strata = tidal_series_records_to_xset(result)
        self.data.tidal_series = raw_strata
        
        return
