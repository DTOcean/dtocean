 # -*- coding: utf-8 -*-
"""This module defines classes which can be used to build interfaces from
external packages to the data description and assosiated objects.

Each interface type is a subclass of the Interface abstract class and certain
attributes and methods must be defined for these to become "concrete".

The methods "declare_inputs" and "declare_outputs" declare which variables from
the internal data  catalog are used as inputs and which are provided as outputs.
The method "declare_optional" describes any optional inputs, i.e. those that
may be fulfilled or not (fulfilled means not None).

For the MapInterface class another method "declare_id_map" is required. This
is the mapping from the internal data  catalog to names used locally by the module
for inputs. This means changes to variable names on either side of the
interface only effects this variable.

The method "connect" is used to execute the function. Inputs can be collected
using the method "get_local" using the local variable name as the argument.
The outputs should be stored using the method "set_local", where the local
variable name and the data must be given.

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>

.. module:: interface
   :platform: Windows
   :synopsis: Interfaces classes

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

import os
import abc
from abc import ABC

import pandas as pd
from box import Box
from sqlalchemy.exc import DBAPIError

from ..utilities.misc import Injective


class MaskVariable():
    
    '''Class for declaring a masked variable. A masked variable is not
    registered as an input (not for outputs yet) if a variable does not
    exist in a given datastate or that variable does not have a certain
    value'''
    
    def __init__(self, var_id, unmask_variable=None, unmask_values=None):
        
        self.variable_id = var_id
        self.unmask_variable = unmask_variable
        self.unmask_values = unmask_values
        
        return

class Interface(ABC):
    '''The base abstract class for all interface types'''

    def __init__(self):

        # The data map should have keys which are the union of the inputs and
        # outputs.
        self.data = None
        self.init_maps()
        
        # Check that the optional identifiers have been set correctly
        self._check_optional_valid()

        return

    @classmethod
    @abc.abstractmethod
    def get_name(cls):

        '''A class method for the common name of the interface.

        Returns:
          str: A unique string
        '''

        pass

    @classmethod
    @abc.abstractmethod
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

        pass

    @classmethod
    @abc.abstractmethod
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

        pass

    @classmethod
    @abc.abstractmethod
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

        pass

    @abc.abstractmethod
    def connect(self):

        '''The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value


        '''

        return
        
    def init_maps(self):

        all_keys = self._get_all_ids()

        new_map = {}

        for key in all_keys:

            new_map[key] = None

        self.data = new_map

        return
        

    def put_data(self, identifier, data):

        '''Put data into the interface, before connecting

         Args:
          identifier (str): Universal identifier for the data to set
          data: Value of the data to set

        '''
        
        if identifier not in self.data:
            
            errStr = ("Identifier {} not recognised for "
                      "interface {}.").format(identifier,
                                              self.get_name())
            raise KeyError(errStr)

        self.data[identifier] = data

        return

    def get_data(self, identifier):

        '''Get data from the interface after connecting

        Args:
          identifier (str): Universal identifier for the data to get'''

        data = self.data[identifier]

        return data
    
    @classmethod    
    def get_inputs(cls, drop_masks=False):

        """Get all inputs provided by the interface"""
        
        if cls.declare_inputs() is None: return ([], [])
                                                
        input_declaration = cls.declare_inputs()
        if input_declaration is None: input_declaration = []
            
        input_ids = []
                                                
        for declared_input in input_declaration:
            
            if isinstance(declared_input, str):
                
                input_ids.append(declared_input)
                
            elif isinstance(declared_input, MaskVariable):
                
                input_ids.append(declared_input.variable_id)
                
        all_inputs = set(input_ids)
        
        if cls.declare_optional() is None:
            
            all_optional = set()
            
        else: 

            all_optional = set(cls.declare_optional())
        
        optional_inputs = list(all_inputs & all_optional)
        
        if drop_masks:
            required_inputs = input_ids
        else:
            required_inputs = input_declaration

        return required_inputs, optional_inputs
    
    @classmethod
    def get_outputs(cls):

        """Get all ouptuts provided by the interface"""
        
        outputs = cls.declare_outputs()
        
        if outputs is None: outputs = []

        return outputs

    def _update_data(self, data_dict):

        if data_dict is None: return

        for key, value in data_dict.items():

            self.put_data(key, value)

        return
        
    def _check_optional_valid(self):
        
        input_identifiers = self.declare_inputs()
        optional_indentifiers = self.declare_optional()
        
        if input_identifiers is None: input_identifiers = []
        if optional_indentifiers is None: return
        
        all_identifiers = []
            
        for identifier in input_identifiers:
            
            if isinstance(identifier, MaskVariable):

                all_identifiers.append(identifier.variable_id)
                
            else:
                
                all_identifiers.append(identifier)
                
        all_inputs = set(all_identifiers)
        all_optional = set(optional_indentifiers)
        
        # Resolve erroneous mappings
        err_mapped = all_optional - all_inputs
        
        if err_mapped:
            
            bad_ids_str = ", ".join(err_mapped)
            errStr = ("The following identifiers are declared optional  "
                      "without being declared as inputs in interface {}: "
                      "{}").format(self.get_name(), bad_ids_str)
                      
            raise KeyError(errStr)
            
        return
    
    @classmethod
    def _check_ids(cls, given_keys, valid_keys):

        invalid_keys = set(given_keys) - set(valid_keys)

        if len(invalid_keys) > 0:

            if len(invalid_keys) == 1:
                key_string = "".join(invalid_keys)
            else:
                key_string = ", ".join(invalid_keys)

            errStr = "The keys {} are not valid.".format(key_string)
            raise KeyError(errStr)
            
        return
    
    @classmethod
    def _get_all_ids(cls):

        if cls.declare_inputs():

            all_keys = cls.declare_inputs()

        else:

            all_keys = []

        if cls.declare_outputs():

            all_keys.extend(cls.declare_outputs())

        return all_keys


class WeightedInterface(Interface):

    @classmethod
    @abc.abstractmethod
    def declare_weight(cls):

        '''A class method to declare interface weighting
        '''

        pass


class MapInterface(Interface):

    def __init__(self):

        self.valid_id_map = None
        super(MapInterface, self).__init__()

        return

    @classmethod
    @abc.abstractmethod
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

        return {}

    def put_data(self, identifier, data):

        local_key = self.valid_id_map.get(identifier)
        
        if local_key not in self.data:
            
            errStr = ("Identifier {} not recognised for "
                      "interface {}.").format(local_key,
                                              self.get_name())
            raise KeyError(errStr)
        
        setattr(self.data, local_key, data)

        return

    def get_data(self, identifier):

        local_key = self.valid_id_map.get(identifier)

        if local_key not in self.data:
            
            errStr = ("Identifier {} not recognised for "
                      "interface {}.").format(local_key,
                                              self.get_name())
            raise KeyError(errStr)
        
        data = getattr(self.data, local_key)

        return data

    def init_maps(self):
        
        self._check_map_valid()

        id_map: dict = self.declare_id_map()

        self.valid_id_map = Injective()
        self.data = Box()

        for local, universal in id_map.items():
            
            if "." in local:
                
                errStr = ("The character '.' may not be included in id_map "
                          "key for variable {}").format(universal)
                raise ValueError(errStr)

            self.valid_id_map.add(local, universal)
            setattr(self.data, local, None)

        return

    def _update_data(self, data_dict):

        if data_dict is None: return

        for key, value in data_dict.items():

            local_key = self.valid_id_map.get(key)
            setattr(self.data, local_key, value)

        return
        
    def _check_map_valid(self):
        
        '''Test to see if all the input and output variables are in the map.
        '''
        
        input_identifiers = self.declare_inputs()
        output_indentifiers = self.declare_outputs()
        
        raw_identifiers = []
        all_identifiers = []

        if input_identifiers is not None:
            raw_identifiers.extend(input_identifiers)
            
        if output_indentifiers is not None:
            raw_identifiers.extend(output_indentifiers)
            
        for identifier in raw_identifiers:
            
            if isinstance(identifier, MaskVariable):

                all_identifiers.append(identifier.variable_id)
                
            else:
                
                all_identifiers.append(identifier)
                
        all_identifiers = set(all_identifiers)
                
        test_id_map = self.declare_id_map()
        all_mapped = set(test_id_map.values())
        
        # Resolve missing mappings
        not_mapped = all_identifiers - all_mapped
        
        if not_mapped:
            
            bad_ids_str = ", ".join(not_mapped)
            errStr = ("The following identifiers have not been mapped in "
                      "interface {}: {}").format(self.get_name(), bad_ids_str)
                      
            raise KeyError(errStr)
        
        # Resolve duplicate mappings
        dupes = list(test_id_map.values())
        for x in all_mapped: dupes.remove(x)
            
        if dupes:
            
            bad_ids_str = ", ".join(dupes)
            errStr = ("The following identifiers have multiple mappings in "
                      "interface {}: {}").format(self.get_name(), bad_ids_str)
                      
            raise KeyError(errStr)

        # Resolve erroneous mappings
        err_mapped = all_mapped - all_identifiers
        
        if err_mapped:
            
            bad_ids_str = ", ".join(err_mapped)
            errStr = ("The following identifiers have been erroneously "
                      "mapped in interface {}: {}").format(self.get_name(),
                                                           bad_ids_str)
                      
            raise KeyError(errStr)
            
        return


class MetaInterface(MapInterface):

    """Mapped interface which retains metadata"""

    def __init__(self):

        self.meta = None
        super(MetaInterface, self).__init__()

        return

    def init_maps(self):
        
        self._check_map_valid()

        id_map: dict = self.declare_id_map()

        self.valid_id_map = Injective()
        self.data = Box()
        self.meta = Box()

        for local, universal in id_map.items():
            
            if "." in local:
                
                errStr = ("The character '.' may not be included in id_map "
                          "key for variable {}").format(universal)
                raise ValueError(errStr)

            self.valid_id_map.add(local, universal)
            setattr(self.data, local, None)
            setattr(self.meta, local, None)

        return

    def put_meta(self, identifier, metadata):

        '''Put metadata into the interface, before connecting

         Args:
          identifier (str): Universal identifier for the data to set
          metadata: MetaData object for the variable

        '''
        
        local_key = self.valid_id_map.get(identifier)
        
        if local_key not in self.data:
            
            errStr = ("Identifier {} not recognised for "
                      "interface {}.").format(local_key,
                                              self.get_name())
            raise KeyError(errStr)
        
        setattr(self.meta, local_key, metadata)

        return

class RawInterface(Interface):

    '''Interface for collecting any number of declared inputs using python
    objects.'''

    def __init__(self):

        super(RawInterface, self).__init__()

        return

    @classmethod
    def declare_inputs(cls):

        return None

    @classmethod
    def declare_optional(cls):

        return None

    def get_data(self, identifier):

        data = super(RawInterface, self).get_data(identifier)

        return data

    def set_variables(self, var_dict):

        '''Add variables to the interface using a dictionary such that the
        items are provided using identifier: value pairs

        Args:
          var_dict (dict): Dictionary of identifier: data pairs
        '''

        self._update_data(var_dict)

        return

    def connect(self):

        return None


class FileInterface(MapInterface):

    def __init__(self):

        super(FileInterface, self).__init__()
        self._path = None

        return
        
    @classmethod
    @abc.abstractmethod
    def get_valid_extensions(cls):
        
        return cls

    @abc.abstractmethod
    def connect(self):
        
        self.check_path()

        return

    def get_data(self, identifier):
        
        self.check_path()

        data = super(FileInterface, self).get_data(identifier)

        return data

    def get_file_path(self):

        '''Get the path to the file to be read'''

        return self._path

    def set_file_path(self, file_path):

        '''Set the path to the file to be read

         Args:
          file_path (str): File path'''
          
        self._path = file_path

        return
        
    def check_path(self, check_exists=False):
        
        # Test for file path
        if self._path is None:

            errStr = ('The file path must be set for FileInterface '
                      'classes.')
            raise ValueError(errStr)
            
        _, file_ext = os.path.splitext(self._path)
        
        if file_ext not in self.get_valid_extensions():
            
            extStr = ", ".join(self.get_valid_extensions())
            errStr = ("File extension '{}' is not valid. Available are "
                      "'{}'").format(file_ext, extStr)
                      
            raise IOError(errStr)
            
        if check_exists and not os.path.exists(self._path):
            
            errStr = ("No file or directory exists for path "
                      "'{}'").format(self._path)
            raise IOError(errStr)
            
        return


class QueryInterface(MetaInterface):

    """Interface for making database queries"""

    def __init__(self):

        super(QueryInterface, self).__init__()
        self._db = None

        return

    def put_database(self, database):

        self._db = database

        return

    def get_dataframe(self, table_name):

        df = pd.read_sql(table_name, self._db._engine)

        return df
        
    def safe_connect(self, attempts=3):
        
        """Retry database actions on failure and rollback if necessary"""
        
        while attempts:
            
            attempts -= 1
            success = False
            
            try:
                
                self.connect()
                self._db.session.commit()
                success = True
                
            except DBAPIError as exc:
                
                if (hasattr(exc, "connection_invalidated") and
                    exc.connection_invalidated):
                    self._db.session.rollback()
                    
                if not attempts:
                    raise exc
                    
            finally:
                
                self._db.session.close()
                
            if success: return
                    
            msg = "Remaining database connection attempts: {}".format(attempts)
            module_logger.info(msg)
                
        return
        

class AutoInterface(MetaInterface):

    '''AutoInterface subclass for creating automated simple interfaces
    '''

    unavailable_ids = []

    def __init__(self):

        super(AutoInterface, self).__init__()

        return
        
    @classmethod
    @abc.abstractmethod
    def get_connect_name(cls):

        '''A class method for returning the name of the automatic interface
        connect method

        Returns:
          str: The method name
        '''
        
        pass
    
    @classmethod
    def get_method_names(cls):

        '''A class method for returning the names of additional automatic
        class methods

        Returns:
          str: The method name
        '''
        
        return None

