# -*- coding: utf-8 -*-
"""
This module contains the package interface to the demonstration class
"Spreadsheet".

Each package interface will be a subclass of the PackageInterface and certain
attributes and methods must be defined for these to become "concrete".

The attribute to be defined is called "id_map". This is the mapping from
the internal data catalog to names used locally by the module for inputs.

There are 3 methods that also must be defined, as follows:

The methods "declare_inputs" and "declare_outputs" declare which variables from
the internal data catalog are used as inputs and which are provided as outputs.

The method "connect" is used to execute the function. Inputs can be collected
using the method "get_local" using the local variable name as the argument.
The outputs should be stored using the method "set_local", where the local
variable name and the data must be given.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: demo
   :platform: Windows
   :synopsis: Aneris interface for dtocean_dummy package
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""


from aneris.boundary.interface import MapInterface, MaskVariable
from dtocean_dummy import Spreadsheet

class DemoInterface(MapInterface):
    
    '''Class of interfaces for the purposes of this test.
    '''


class TableInterface(DemoInterface):
    
    '''Interface to the Spreadsheet class of dtocean_dummy, providing a table
    of random numbers.
          
    '''
        
    @classmethod
    def get_name(cls):
        
        return "Spreadsheet Generator"

    @classmethod         
    def declare_inputs(cls):
        
        '''Declare all the variables required as inputs by this interface.

         Returns:
            list: List of internal variables names required as inputs.
        
        '''

        input_list  =  [MaskVariable('demo:demo:low',
                                     'trigger.bool',
                                     [True]),
                        MaskVariable('demo:demo:high',
                                     'trigger.bool',
                                     [True]),
                        'demo:demo:rows'
                        ]
                        
        return input_list

    @classmethod        
    def declare_outputs(cls):
        
        '''Declare all the variables provided as outputs by this interface.
        
        Returns:
            list: List of internal variables names provided as outputs.
        '''
        
        output_list =  ['demo:demo:table',
                        ]
        
        return output_list
        
    @classmethod        
    def declare_optional(cls):
        
        optional_list  =  ['demo:demo:low',
                           'demo:demo:high',
                          ]
        
        return optional_list
        
    @classmethod
    def declare_id_map(cls):
                
        '''Declare the mapping between the internal variable names and local
        variable names.
        
        Returns:
            dict: Dictionary mapping of variable names, each entry being of the
              form "'local_name' : 'internal:name'".
        '''
        
        id_map = {'low': 'demo:demo:low',
                  'high': 'demo:demo:high',
                  'rows': 'demo:demo:rows',
                  'table': 'demo:demo:table'}
                  
        return id_map
                 
    def connect(self):
        
        '''This fucntion is used to extract the data from the interfacing
        package.
        
        Note: methods get_local and set_local are used to get the inputs and
          provide the outputs to and from the interface.
        '''
        
        rows = self.data.rows
        
        # Build optional data
        config = {}
        
        if self.data.low is not None: config["low"] = self.data.low
        if self.data.high is not None: config["high"] = self.data.high
        
        sheet = Spreadsheet(**config)

        sheet.make_table(rows)
        table_data = sheet.table.to_dict()
        
        self.data.table =  table_data
        
        return
        
class LaterInterface(DemoInterface):
    
    '''Interface to test outputs generated later than table interface
          
    '''
        
    @classmethod
    def get_name(cls):
        
        return "Later Interface"

    @classmethod         
    def declare_inputs(cls):
        
        '''Declare all the variables required as inputs by this interface.

         Returns:
            list: List of internal variables names required as inputs.
        
        '''

        input_list = ['demo:demo:rows']
                        
        return input_list

    @classmethod        
    def declare_outputs(cls):
        
        '''Declare all the variables provided as outputs by this interface.
        
        Returns:
            list: List of internal variables names provided as outputs.
        '''
        
        output_list =  ['demo:demo:table',
                        ]
        
        return output_list
        
    @classmethod        
    def declare_optional(cls):
        
        return None
        
    @classmethod 
    def declare_id_map(cls):

        id_map = {'rows': 'demo:demo:rows',
                  'table': 'demo:demo:table'}
                  
        return id_map
                 
    def connect(self):
        
        return
