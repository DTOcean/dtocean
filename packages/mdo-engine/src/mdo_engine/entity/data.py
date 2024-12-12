# -*- coding: utf-8 -*-

from copy import deepcopy
from collections import OrderedDict
from collections.abc import Sequence

from ..utilities.identity import get_unique_id

class Frozen():

    __isfrozen = False

    def __setattr__(self, key, value):

        if self.__isfrozen and not hasattr(self, key):

            errStr = ("{} is not an attribute of frozen "
                      "class {}.").format(key, self.__class__.__name__)
            raise TypeError(errStr)

        object.__setattr__(self, key, value)

        return

    def _freeze(self):

        self.__isfrozen = True

        return


class MetaData(Frozen):

    '''Concrete MetaData class for storing metadata for a variable in memory.

    '''

    def __init__(self, props_dict):

        self._identifier = None
        self._structure = None

        self._freeze()
        self._set_properties(props_dict)

        return

    @classmethod
    def get_base_properties(cls):
        '''Properties that must be provided'''
        return ["identifier", "structure"]

    @property
    def identifier(self):
        '''The unique identifier for this variable.'''
        return self._identifier

    @property
    def structure(self):
        '''The data storage class to be used.'''
        return self._structure
        
    def _set_properties(self, props_dict):

        for key, value in props_dict.items():

            private_key = "_{}".format(key)
            setattr(self, private_key, value)

        return


class DataCatalog():

    '''Data catalog contains a map of all of the valid metadata within the
    system. This is loaded in a dynamic plugin based methodology and all
    entered data is validated against this catalog.

    The variable map links variable identifiers to metadata class objects.
    '''

    def __init__(self):

        self._metadata_variable_map = OrderedDict()

        return

    def get_variable_identifiers(self):

        '''Return the variable identifiers in the data catalog'''

        identities = self._metadata_variable_map.keys()

        return identities

    def set_metadata_maps(self, variable_map):

        '''Set the mapping of MetaData classes to the variable id'''

        self._metadata_variable_map = variable_map

        return

    def variable_map_from_objects(self, object_list):

        '''Convert an attrribute map from plugin discovery to a variable
        mapping'''

        # Iterate through the list of objects
        for instance in object_list:

            self.add_metadata(instance)

        return

    def add_metadata(self, metadata):

        '''Add a MetaData instance to the catalog'''

        var_key = metadata.identifier

        self._metadata_variable_map[var_key] = metadata

        return

    def get_metadata(self, variable_id):

        '''Get the MetaData for a given variable ID'''

        try:
        
            metadata = self._metadata_variable_map[variable_id]
            
        except KeyError:
            
            errStr = ("Metadata for variable {} not found in the data "
                      "catalog.").format(variable_id)
            raise KeyError(errStr)

        return deepcopy(metadata)
        
    def filter_by_meta(self, meta_attr, value):

        '''Get the MetaData with a given attribute and value'''
        
        return_dict = OrderedDict()
        
        for var_id, meta in self._metadata_variable_map.items():
            
            if not hasattr(meta, meta_attr): continue

            meta_value = getattr(meta, meta_attr)
            
            if meta_value is None: continue
            
            is_list = lambda x: (isinstance(x, Sequence) and
                                 not isinstance(x, str))
            
            if ((is_list(meta_value) and value in meta_value) or
                meta_value == value):
                
                return_dict[var_id] = meta
                
        return return_dict
        

class DataPool():
    
    '''This class is used to hold all of the Data objects that are created.
    Each must have a unique index (not the identifier in MetaData) which
    is referenced by DataStates.
    
    Data is only stored here to minise the level of copying the to make 
    serialising simulations or a group of simulations more straightfoward.
    
    The pool must track the number of links to each data object, so that
    only necessary copies are created.
    '''
    
    def __init__(self):
        
        self._data_indexes = set()
        self._data = {}
        self._links = {}
        
    def add(self, data):
        
#        print "\nadd:", self._data.keys()

        data_index = get_unique_id(self._data_indexes)
        
        self._data_indexes.add(data_index)
        self._data[data_index] = data
        self._links[data_index] = 0
        
        return data_index
        
    def get(self, data_index):
        
#        print "\nget:", self._data.keys()

        data = self._data[data_index]
        
        return data
        
    def copy(self, data_index):
        
#        print "\ncopy:", self._data.keys()

        data = self._data[data_index]
        copy_data = deepcopy(data)
        copy_index = self.add(copy_data)
        
        return copy_index
        
    def replace(self, data_index, data):
        
#        print "\nreplace:", self._data.keys()

        self._data[data_index] = data
        
        return
        
    def pop(self, data_index):
        
#        print "\npop:", self._data.keys()

        self._data_indexes.remove(data_index)
        data = self._data.pop(data_index)
        self._links.pop(data_index)
        
        return data
        
    def link(self, data_index):
        
        self._links[data_index] += 1
        
        return
        
    def unlink(self, data_index):
        
        if self._links[data_index] == 0:
            
            errStr = ("Data with index {} has no recorded "
                      "links.").format(data_index)
            raise ValueError(errStr)
        
        self._links[data_index] -= 1
        
        return
        
    def has_link(self, data_index):
        
        result = False
        
        if self._links[data_index] > 0:
            
            result = True
            
        return result
        
    def mirror_links(self):
        
        """This is a dangerous action and should be used with care."""
        
        mirror_links = deepcopy(self._links)
        
        return mirror_links
        
    def count(self):
        
        return len(self._data)
          
    def __len__(self):
        
        return self.count()
        
    def __iter__(self):
        
        return iter(self._data_indexes)
        

class BaseState():
    
    '''Base class for NameState and DataState
    '''
    
    __slots__ = ["_data", "_level"]
    
    def __init__(self, data_map=None, level=None):
        
        self._data = None
        self._level = None
        
        self._data = self._init_data(data_map)
        self._level = self._init_level(level)
        
        return
    
    def _init_data(self, data_map):
        
        if data_map is None: return {}
        
        if not all(isinstance(x, str) for x in data_map.keys()):
            
            errStr = "All keys in data_map must be strings."
            raise ValueError(errStr)
            
        if not all(isinstance(x, (str, type(None)))
                                    for x in data_map.values()):
            
            errStr = "All values in data_map must be strings or None."
            raise ValueError(errStr)
            
        return data_map
    
    def _init_level(self, level):
        
        result = None
        
        if level is not None: result = level.lower()
        
        return result
    
    def get_level(self):
        return self._level
    
    def get_identifiers(self):
        return list(self._data.keys())
    
    def has_index(self, data_id):
        '''Test if a variable is in a datastate'''
        return data_id in self._data
    
    def get_index(self, data_id):
        return self._data[data_id]
    
    def add_index(self, data_id, data_index):
        self._data[data_id] = data_index
    
    def mirror_map(self):
        
        """This is a dangerous action if the data indexes are stored without
        updating the datapool."""
        
        return self._data.copy()
    
    def count(self):
        
        return len(self._data)
    
    def dump(self):
        
        dump_dict = {"type": "BaseState",
                     "level": self._level,
                     "data": self._data}
        
        return dump_dict
    
    def __len__(self):
        
        return self.count()


class PseudoState(BaseState):

    '''Relates data indentifiers and data pool indexes. A pseudo state is a
    static record which can not be altered after initialisation, nor can it
    be used to manipulate the content of a datapool (i.e. no links are created)
    
    Each psuedo state can have a level which can be compared to other levels
    in the simulation or compared to datastates with the same level in
    other simulations.
    '''
    

    def __init__(self, data_map,
                       level=None):
        
        data = self._init_data(data_map)
        level = self._init_level(level)
        
        super(PseudoState, self).__setattr__("_data", data)
        super(PseudoState, self).__setattr__("_level", level)

        return
        
    def dump(self):
        
        dump_dict = super(PseudoState, self).dump()
        dump_dict["type"] = "PseudoState"
        
        return dump_dict
    
    def __setattr__(self, name, value):
        """"""
        msg = "Class '{}' is immutable".format(self.__class__.__name__)
        raise AttributeError(msg)
        
    def __copy__(self):
        
        return self
        
    def __deepcopy__(self, *args):
        
        return self


class DataState(BaseState):

    '''Relates data indentifiers and data pool indexes. A data state is a
    record of data stored within the data pool and links are created and 
    removed when datastates are created or destroyed.
    
    Data states can have masks applied to them for varios purposes.

    Each data state can have a level which can be compared to other levels
    in the simulation or compared to datastates with the same level in
    other simulations.
    '''

    def __init__(self, level=None, force_map=None):

        super(DataState, self).__init__(force_map, level)
        self._masked = False
        
        return
        
    def set_level(self, level):
        
        self._level = level

        return
        
    def mask(self):
                
        self._masked = True
        
        return
        
    def unmask(self):
        
        self._masked = False
        
        return
        
    def ismasked(self):
        
        return self._masked
        
    def pop_index(self, data_id):

        return self._data.pop(data_id)
    
    def dump(self):
        
        dump_dict = super(DataState, self).dump()
        dump_dict["type"] = "DataState"
        dump_dict["masked"] = self._masked
        
        return dump_dict


class Data():

    '''Holds a unit of data in various formats.'''

    def __init__(self, identifier, structure_name, data):

        self._id = identifier
        self._structure_name = structure_name
        self._data = data

        return

    def get_id(self):

        return self._id
        
    def get_structure_name(self):
        
        return self._structure_name


