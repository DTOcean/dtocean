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
   :synopsis: Aneris interface for dtocean_demo package
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""


from aneris.boundary.interface import MapInterface

class DummyInterface(MapInterface):
    
    '''Class of interfaces for the purposes of this test.
    '''


class EarlyInterface(DummyInterface):
    
    '''Interface to test outputs generated later than table interface
          
    '''
        
    @classmethod
    def get_name(cls):
        
        return "Early Interface"

    @classmethod         
    def declare_inputs(cls):
        
        '''Declare all the variables required as inputs by this interface.

         Returns:
            list: List of internal variables names required as inputs.
        
        '''

        input_list  =  []
                        
        return input_list

    @classmethod        
    def declare_outputs(cls):
        
        '''Declare all the variables provided as outputs by this interface.
        
        Returns:
            list: List of internal variables names provided as outputs.
        '''
        
        output_list =  ['early:dummy:data',
                        ]
        
        return output_list
        
    @classmethod        
    def declare_optional(cls):
        
        return None
        
    @classmethod 
    def declare_id_map(cls):

        id_map = {'early': 'early:dummy:data'}
                  
        return id_map
                 
    def connect(self):
        
        self.data.early = 1
        
        return
        
class LaterInterface(DummyInterface):
    
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

        input_list  =  ['early:dummy:data']
                        
        return input_list

    @classmethod        
    def declare_outputs(cls):
        
        '''Declare all the variables provided as outputs by this interface.
        
        Returns:
            list: List of internal variables names provided as outputs.
        '''
        
        output_list =  ['later:dummy:data',
                        ]
        
        return output_list
        
    @classmethod        
    def declare_optional(cls):
        
        return None
        
    @classmethod 
    def declare_id_map(cls):

        id_map = {'early': 'early:dummy:data',
                  'later': 'later:dummy:data'}
                  
        return id_map
                 
    def connect(self):
        
        self.data.later = self.data.early + 1
        
        return
