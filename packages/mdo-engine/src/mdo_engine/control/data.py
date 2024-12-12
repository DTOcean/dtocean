# -*- coding: utf-8 -*-
"""
Control classes relating to Data entities
"""

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

import os
import traceback
from copy import deepcopy

from ..entity.data import Data, DataPool, DataState, MetaData
from ..boundary.data import SerialBox
from ..utilities.plugins import (Plugin,
                                 create_object_list)


class DataValidation(Plugin):

    '''Class to validate data'''

    def __init__(self, meta_cls=MetaData):

        self._meta_cls = meta_cls

        return

    def update_data_catalog_from_definitions(self, data_catalog,
                                                   package,
                                                   super_cls='DataDefinition'):

        '''Create a data catalog searching for DataDefinition classes in the
        given package directory'''

        # Discover the available classes and load the instances
        cls_map = self._discover_plugins(package, super_cls)
        def_list = create_object_list(cls_map)

        for definition in def_list:

            for metadef_list in definition.get_metadef_lists():
                
                if metadef_list is None: continue

                obj_list = self.obj_list_from_metadef_list(metadef_list)

                data_catalog.variable_map_from_objects(obj_list)

        return

    def get_valid_variables(self, data_catalog, variables):

        '''Return all valid variables in the given data catalog from variables
        list.
        '''

        compare_vars = set(variables)
        catalog_vars = set(data_catalog.get_variable_identifiers())

        valid_vars = compare_vars & catalog_vars

        return list(valid_vars)

    def obj_list_from_metadef_list(self, metadef_list):

        '''Build a ConcreteMetaData object map from a list of dictionaries.'''

        obj_list = []

        for metadef in metadef_list:

            new_metadata = self.obj_from_metadef_dict(metadef)

            obj_list.append(new_metadata)

        return obj_list

    def obj_from_metadef_dict(self, metadef_dict):

        '''Build a ConcreteMetaData object map from a dictionaries.'''

        # Collect the public attributes of MetaData
        required_attrs = set(self._meta_cls.get_base_properties())

        # Get the keys of the dict and check they match
        metadef_keys = set(metadef_dict.keys())

        if required_attrs - metadef_keys:

            errStr = ('Dictionary keys "{}" do not match MetaData '
                      'attributes "{}". Aborting.').format(
                                                  " ,".join(metadef_keys),
                                                  " ,".join(required_attrs))
            raise ValueError(errStr)

        new_metadata = self._meta_cls(metadef_dict)

        return new_metadata


class DataStorage(Plugin):

    '''Control class for creating, modifying, and storing data entities'''

    def __init__(self, definition_module, super_cls="Structure"):

        self._structures = self._init_structures(definition_module,
                                                 super_cls)

        return
        
    def _init_structures(self,  definition_module, super_cls="Structure"):
        
        log_msg = 'Searching for {} classes'.format(super_cls)
        module_logger.debug(log_msg)

        cls_map = self._discover_plugins(definition_module,
                                         super_cls)
        obj_map = {k: v() for k, v in cls_map.items()}
                                         
        return obj_map

    def get_structure(self, cls_name):
        
        if cls_name not in self._structures:
            
            errStr = ('Unrecognised structure "{}".').format(cls_name)
            raise KeyError(errStr)

        return self._structures[cls_name]

    def discover_structures(self, definition_module, super_cls="Structure"):

        '''Retrieve all of the structure classes'''

        obj_map = self._init_structures(definition_module,
                                        super_cls)
                                         
        self._structures.update(obj_map)

        return

    def create_new_datastate(self, level=None, force_map=None):

        new_state = DataState(level, force_map)
        
        if level is None:
            log_msg = 'DataState created'.format(level)
        else:
            log_msg = 'DataState with level "{}" created'.format(level)

        module_logger.debug(log_msg)

        return new_state
        
    def copy_datastate(self, pool, datastate, level=None):
        
        _check_valid_datastate(datastate)
        new_datastate = self._copy_datastate_meta(datastate, level)
            
        data_map = datastate.mirror_map()
        
        for data_identifier, data_index in data_map.items():
            
            new_datastate.add_index(data_identifier, data_index)
            if data_index is not None: pool.link(data_index)
        
        return new_datastate
    
    def import_datastate(self, src_pool, dst_pool, datastate, level=None):
        
        _check_valid_datastate(datastate)
        new_datastate = self._copy_datastate_meta(datastate, level)
            
        data_map = datastate.mirror_map()
        
        for data_identifier, data_index in data_map.items():
            
            if data_index is None: continue
            
            dst_contains_data = False
            dst_structure_name = None
            
            src_data = src_pool.get(data_index)
            src_structure_name = src_data.get_structure_name()
            
            # Check for matching indexes and data
            if data_index in dst_pool:
                
                dst_data = dst_pool.get(data_index)
                dst_structure_name = dst_data.get_structure_name()
            
            if (dst_structure_name is not None and
                dst_structure_name == src_structure_name):
            
                dst_structure = self.get_structure(dst_structure_name)
                
                src_value = self._get_value(src_data)
                dst_value = self._get_value(dst_data)
                
                try:
                    if dst_structure.equals(src_value, dst_value):
                        dst_contains_data = True
                except Exception:
                    msgStr = ("Comparison of data with identifier {} failed "
                              "with an unexpected error:"
                              "\n{}").format(data_identifier,
                                             traceback.format_exc())
                    raise Exception(msgStr)
            
            if not dst_contains_data:
                data_index = dst_pool.add(src_data)
            
            dst_pool.link(data_index)
            new_datastate.add_index(data_identifier, data_index)
        
        return new_datastate
    
    def add_data_to_state(self, pool,
                                datastate,
                                data_identifier,
                                data_obj=None):
        
        '''OK, so if the data state already contains the data then its 
        overwritten and we must remove it. Otherwise add the index'''
        
        if not hasattr(datastate, "add_index"):
            
            errStr = ("Given datastate is of wrong type. Expected DataState "
                      "but recieved {}.").format(datastate.__class__.__name__)
            raise ValueError(errStr)
        
        if data_obj is None:
            
            data_index = None
        
        else:
            
            data_index = pool.add(data_obj)
            pool.link(data_index)
            
            log_msg = ('New "{}" data stored with index '
                       '{}').format(data_identifier, data_index)
            module_logger.info(log_msg)
        
        if (datastate.has_index(data_identifier) and
                datastate.get_index(data_identifier) is not None):
            
            self.remove_data_from_state(pool, datastate, data_identifier)
        
        datastate.add_index(data_identifier, data_index)
        
        return
    
    def remove_state(self, pool, datastate):
        
        '''Remove an indentifier from the datastate and unlink it from the
        pool. If the data in the pool has no remaining links then delete it.'''
        
        if datastate.get_level() is not None:
            log_msg = ('Trying to remove datastate with level '
                       '{}').format(datastate.get_level())
        else:
            log_msg = 'Trying to remove datastate'
        
        module_logger.info(log_msg)
        
        for data_identifier in datastate.get_identifiers():
            self.remove_data_from_state(pool,
                                        datastate,
                                        data_identifier)
        
        return
    
    def remove_data_from_state(self, pool, datastate, data_identifier):
        
        '''Remove an indentifier from the datastate and unlink it from the
        pool. If the data in the pool has no remaining links then delete it.'''
        
        if not hasattr(datastate, "pop_index"):
            
            errStr = ("Given datastate is of wrong type. Expected DataState "
                      "but recieved {}.").format(datastate.__class__.__name__)
            raise ValueError(errStr)
        
        data_index = datastate.get_index(data_identifier)
        datastate.pop_index(data_identifier)
        
        log_msg = ('Removing "{}" data stored with index '
                   '{} from state').format(data_identifier,
                                           data_index)
        module_logger.info(log_msg)
        
        if data_index is None: return
        
        pool.unlink(data_index)
        
        if not pool.has_link(data_index):
            
            pool.pop(data_index)
            
            log_msg = ('Removing "{}" data stored with index '
                       '{} from pool').format(data_identifier,
                                              data_index)
            module_logger.info(log_msg)
        
        return
    
    def create_new_data(self, pool,
                              datastate,
                              data_catalog,
                              raw_data,
                              metadata):
        
        if not self.is_valid(data_catalog, metadata.identifier):
            
            errStr = "Data {} not in data catalog. Aborting.".format(
                                                        metadata.identifier)
            raise ValueError(errStr)
        
        data_form = metadata.structure
        data_identifier = metadata.identifier
        
        if data_form not in self._structures:
                        
            errStr = ('Unrecognised structure "{}" for data identifier: '
                      '{}').format(data_form, data_identifier)
            raise KeyError(errStr)
        
        # Create a data object
        if raw_data is None:
            
            data_obj = None
            
        else:
            
            data_obj = self._get_data_obj(metadata, raw_data)
        
        self.add_data_to_state(pool, 
                               datastate,
                               data_identifier,
                               data_obj)
        
        return
    
#    def modify_data(self, data_pool, datastate, data_identifier, raw_data):
#
#        '''Creates a copy of the data in the pool with the new raw data, and 
#        assosiates the copy to the datastate, unlinking the original. If the 
#        original has no remaining links in the data pool it is deleted.
#        '''
#        
#        data_pool_copy = deepcopy(data_pool)
#        datastate_copy = deepcopy(datastate)
#
#        data_index = datastate.get_index(data_identifier)
#        copy_index = data_pool_copy.copy(data_index)
#        
#        data_pool_copy, datastate_copy = self.add_data_to_state(data_pool_copy,
#                                                                datastate_copy,
#                                                                copy_index)
#        
#        old_data = data_pool_copy.get(copy_index)
#        new_data = self._get_data_obj(old_data.get_structure_name(), raw_data)
#        data_pool_copy.replace(copy_index, new_data)
#        
#        return data_pool_copy, datastate_copy
        
    def has_data(self, datastate, data_identifier):
        
        if datastate is None: return False
        
        result = False        
        has_index = datastate.has_index(data_identifier)
                
        if has_index and datastate.get_index(data_identifier) is not None:
            result = True
            
        return result
        
    def get_data_value(self, data_pool, datastate, data_identifier):
        
        if not self.has_data(datastate, data_identifier):
            
            errStr = ("Data with identifier {} is not contained in the "
                      "given datastate").format(data_identifier)
            raise ValueError(errStr)
        
        data_index = datastate.get_index(data_identifier)
        
        log_msg = ('Retrieving "{}" data stored with index '
                   '{} from pool').format(data_identifier,
                                          data_index)
        module_logger.debug(log_msg)
        
        data_obj = data_pool.get(data_index)
        value = self._get_value(data_obj)
        
        return value
        
    def get_data_metadata(self, data_pool, datastate, data_identifier):
        
        if not self.has_data(datastate, data_identifier):
            
            errStr = ("Data with identifier {} is not contained in the "
                      "given datastate").format(data_identifier)
            raise ValueError(errStr)
        
        data_index = datastate.get_index(data_identifier)
        data_obj = data_pool.get(data_index)
        meta_data = data_obj.get_meta_data()
        
        return meta_data
        
    def serialise_data(self, data_pool,
                             data_indexes,
                             data_dir="data",
                             root_dir=None,
                             warn_save=True):

        for data_index in data_indexes:
            self._convert_data_to_box(data_pool,
                                      data_index,
                                      data_dir,
                                      root_dir,
                                      warn_save)

        return
        
    def deserialise_data(self, data_catalog,
                               data_pool,
                               data_indexes,
                               root_dir=None,
                               warn_missing=False,
                               warn_unpickle=False):

        for data_index in data_indexes:
            self._convert_box_to_data(data_catalog,
                                      data_pool,
                                      data_index,
                                      root_dir,
                                      warn_missing=warn_missing,
                                      warn_unpickle=warn_unpickle)

        return
        
    def serialise_pool(self, data_pool,
                             data_dir="data",
                             root_dir=None,
                             warn_save=True):
                                                                  
        self.serialise_data(data_pool,
                            data_pool,
                            data_dir,
                            root_dir,
                            warn_save)

        return
        
    def deserialise_pool(self, data_catalog,
                               data_pool,
                               root_dir=None,
                               warn_missing=False,
                               warn_unpickle=False):
                                                                  
        self.deserialise_data(data_catalog,
                              data_pool,
                              data_pool,
                              root_dir,
                              warn_missing=warn_missing,
                              warn_unpickle=warn_unpickle)

        return
    
    def create_pool_subset(self, data_pool, datastate):
        
        new_pool = DataPool()
        new_datastate = DataState()
        
        var_ids = datastate.get_identifiers()
        
        for var_id in var_ids:
            
            data_index = datastate.get_index(var_id)
            data_obj = data_pool.get(data_index)
            new_data_obj = deepcopy(data_obj)
            
            self.add_data_to_state(new_pool,
                                   new_datastate,
                                   var_id,
                                   new_data_obj)
            
        return new_pool, new_datastate

    @classmethod
    def is_valid(cls, data_catalog, variable_id):

        '''Return true if variable in the given data catalog.
        '''

        result = False
        catalog_vars = data_catalog.get_variable_identifiers()

        if variable_id in catalog_vars: result = True

        return result
    
    def _copy_datastate_meta(self, datastate,
                                   level=None):
    
        if level is None: level = datastate.get_level()
                
        new_datastate = self.create_new_datastate(level)
        if datastate.ismasked(): new_datastate.mask()
        
        return new_datastate
    
    def _get_value(self, data_obj):
        
        data_structure = self.get_structure(data_obj.get_structure_name())
        value = data_structure(data_obj._data)
        
        return value
    
    def _get_data_obj(self, metadata, raw):
        
        data_structure = self.get_structure(metadata.structure)
        
        # Catch errors here to provide more informative output
        try:
            
            data = data_structure.get_data(raw, metadata)
            
        except Exception:
            
            error = traceback.format_exc()
            
            errStr = ("Reading variable {} led to the following "
                      "traceback:\n\n{}").format(metadata.identifier,
                                                 error)
            raise RuntimeError(errStr)

        # Create a data entity
        data_obj = Data(metadata.identifier, metadata.structure, data)
        
        return data_obj

    def _convert_data_to_box(self, data_pool,
                                   data_index,
                                   data_dir,
                                   root_dir=None,
                                   warn_save=True):
                                  
        data_obj = data_pool.get(data_index)
        
        if isinstance(data_obj, SerialBox): return
        
        structure_name = data_obj.get_structure_name()
        data_structure = self.get_structure(structure_name)

        root_path = os.path.join(data_dir, data_index)
        
        try:
            file_path = data_structure.save_value(data_obj._data, root_path)
        except Exception:
            msgStr = ("Saving of data with index {} failed with an unexpected "
                      "error:\n{}").format(data_index, traceback.format_exc())
            if warn_save:
                module_logger.warning(msgStr)
                return
            else:
                raise Exception(msgStr)
                
        if root_dir is None:
            store_path = file_path
        else:
            remove_root = os.path.join(os.path.normpath(root_dir), "")
            store_path = file_path.replace(remove_root, "")
                
        identifier = data_obj.get_id()
        load_dict = {"file_path": store_path,
                     "structure_name": structure_name}

        data_box = SerialBox(identifier, load_dict)
        data_pool.replace(data_index, data_box)

        return
        
    def _convert_box_to_data(self, data_catalog,
                                   data_pool,
                                   data_index,
                                   root_dir=None,
                                   warn_missing=False,
                                   warn_unpickle=False):
                                  
        data_box = data_pool.get(data_index)
        
        if not isinstance(data_box, SerialBox): return
            
        file_path = data_box.load_dict["file_path"]
        structure_name = data_box.load_dict["structure_name"]

        if root_dir is None:
            load_path = file_path
        else:
            load_path = os.path.join(root_dir, file_path)
            
        data_structure = self.get_structure(structure_name)
        
        try:
            data = data_structure.load_data(load_path)
        except Exception:
            msgStr = ("Unpickling of data with id {} failed with an "
                      "unexpected error:\n{}").format(data_box.identifier,
                                                      traceback.format_exc())
            if warn_unpickle:
                module_logger.warning(msgStr)
                data = None
            else:
                raise Exception(msgStr)
    
        # Create and store the data object
        data_obj = self._make_data(data_catalog,
                                   data_box.identifier,
                                   data,
                                   warn_missing=warn_missing)
        
        if data_obj is None:
            
            warnStr = ("No valid data object found for data with index "
                       "{}").format(data_index)
            module_logger.warning(warnStr)
            
            data_obj = Data(data_box.identifier,
                            structure_name,
                            None)
       
        data_pool.replace(data_index, data_obj)

        return

    def _make_data(self, data_catalog, identifier, data, warn_missing=False):
        
        if not self.is_valid(data_catalog, identifier):

            msgStr = "Data {} not found in data catalog".format(identifier)
            
            if warn_missing:
                module_logger.warning(msgStr)
                return None
            else:
                raise ValueError(msgStr)
            
        metadata = data_catalog.get_metadata(identifier)
        
        if metadata.structure not in self._structures:
            
            errStr = ('Unrecognised structure "{}" for data identifier: '
                      '{}').format(metadata.structure,
                                   identifier)
            raise KeyError(errStr)

        # Create a Data object
        data_obj = Data(identifier, metadata.structure, data)

        return data_obj


def _check_valid_datastate(datastate):
    
    if not hasattr(datastate, "add_index"):
            
        errStr = ("Given datastate is of wrong type. Expected DataState "
                  "but recieved {}.").format(datastate.__class__.__name__)
        raise ValueError(errStr)
    
    return
