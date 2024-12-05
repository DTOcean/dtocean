# -*- coding: utf-8 -*-
"""
Control classes related to the simulation entity.

Created on Wed Jan 21 12:59:34 2015

@author: Mathew Topper
"""

import sys

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

import os
import json
from copy import deepcopy
from collections import OrderedDict

from ..boundary.data import SerialBox
from ..boundary.interface import MaskVariable
from ..entity.data import BaseState, PseudoState, DataState # Used by eval
from ..utilities.identity import get_unique_id
from ..utilities.misc import OrderedSet


class Loader(object):
    
    """Class for working with simulations and a datastore. Loader should
    not contain methods that modify pools or simulations but can work 
    directly with interfaces, which Controller can not.
    """
    
    def __init__(self, datastore):
        
        self._store = datastore
        
        return
        
    def get_structure(self, structure_class_name):
        
        cls = self._store.get_structure(structure_class_name)
        
        return cls
        
    def has_data(self, simulation, data_identity):
        
        merged_state = self.create_merged_state(simulation)
        result = self._store.has_data(merged_state, data_identity)
                                                     
        return result

    def get_data_value(self, pool, simulation, data_identity):
        
        log_msg = 'Retrieving data with identity "{}".'.format(data_identity)
        module_logger.debug(log_msg)
        
        merged_state = self.create_merged_state(simulation)
        data_value = self._store.get_data_value(pool,
                                                merged_state,
                                                data_identity)
                                             
        return data_value

    def input_available(self, pool,
                              simulation,
                              interface,
                              check_id):
                                  
        input_declaration, _ = interface.get_inputs()
        
        active_inputs = self._get_active_inputs(pool,
                                                simulation,
                                                input_declaration)
        
        result = False
        if check_id in active_inputs: result = True 

        return result
        
    def can_load(self, pool,
                       simulation,
                       interface):
                           
        input_declaration, optional_inputs = interface.get_inputs()
        
        active_inputs = self._get_active_inputs(pool,
                                                simulation,
                                                input_declaration)
                                                      
        merged_state = self.create_merged_state(simulation)
        
        if merged_state is None:
            state_data_ids = set()
        else:
            state_data_ids = set(merged_state.get_identifiers())
                                                                
        required_inputs = set(active_inputs) - set(optional_inputs)
        
        if required_inputs <= state_data_ids:
            result = True
        else:
            result = False
            
        return result
        
    def load_interface(self, pool,
                             simulation,
                             interface,
                             skip_vars=None):
                                 
        input_declaration, optional_inputs = interface.get_inputs()
        
        active_inputs = self._get_active_inputs(pool,
                                                simulation,
                                                input_declaration)
        
        if skip_vars is not None:
            remaining_inputs = set(active_inputs) - set(skip_vars)
            active_inputs = list(remaining_inputs)
        
        for putvar in active_inputs:
            
            if self.has_data(simulation, putvar):
                data_value = self.get_data_value(pool, simulation, putvar)
            else:
                data_value = None
            
            # Allow None values from optional inputs
            if data_value is None and putvar not in optional_inputs:
                
                errStr = ("Input {} is required by interface {} but is"
                          "not satisfied.").format(putvar,
                                                   interface.get_name())
                raise ValueError(errStr)
            
            interface.put_data(putvar, data_value)
            
        return interface
    
    def add_datastate(self, pool,
                            simulation,
                            level=None,
                            data_catalog=None,
                            identifiers=None,
                            values=None,
                            no_merge=False,
                            use_objects=False,
                            log_exceptions=False):
        
        # We always create a new datastate
        new_state = self._store.create_new_datastate(level)
        
        if identifiers is None:
            data_list = ()
        else:            
            data_list = zip(identifiers, values)
            
        if data_list and data_catalog is None:
            
            errStr = "A DataCatelog must be provided to add data"
            raise ValueError(errStr)
        
        for ident, data in data_list:

            # Test that the variable is in the data catalog
            if not self._store.is_valid(data_catalog, ident):
    
                errStr = ('Variable ID "{}" is not contained in the data '
                          'catalog.').format(ident)
    
                raise ValueError(errStr)
    
            # Get the meta data from the catalog
            metadata = data_catalog.get_metadata(ident)
            
            # Data is always stored using a datastate and the built-in
            # data pool. If the use_objects flag is True then Data object
            # creation is the responcibility of the caller
            if use_objects:
                
                self._store.add_data_to_state(pool,
                                              new_state,
                                              ident,
                                              data)
                
            elif log_exceptions:
                
                try:
                    
                    self._store.create_new_data(pool,
                                                new_state,
                                                data_catalog,
                                                data,
                                                metadata)
                    
                except:
                    
                    e = sys.exc_info()[0]
                    msg = ("Reading variable {} generated error: "
                           "{}").format(ident, e)
                    logging.exception(msg)
                    
                    continue
                
            else:
    
                self._store.create_new_data(pool,
                                            new_state,
                                            data_catalog,
                                            data,
                                            metadata)

        # Add it to the simulation.
        removed_states = simulation.add_state(new_state)
                        
        for kill_state in removed_states:
            
            self._store.remove_state(pool, kill_state)
            
        if level is None:
            log_msg = 'Datastate stored'
        else:
            log_msg = 'Datastate with level "{}" stored'.format(level)
            
        module_logger.info(log_msg)
                
        if no_merge: return
            
        # Update the merged state stored in the simulation
        merged_state = self._merge_active_states(simulation)
        simulation.set_merged_state(merged_state)
            
        return
    
    def create_merged_state(self, simulation, use_existing=True):
        
        if use_existing:
            merged_state = simulation.get_merged_state()
        else:
            merged_state = None

        if merged_state is None:
            merged_state = self._merge_active_states(simulation)
            
        return merged_state
        
    def serialise_states(self, simulation,
                               state_dir="states",
                               root_dir=None):
        
        used_identifiers = []
        
        active_states = simulation._active_states
        active_boxes = []
        
        for state in active_states:
        
            safe_id = get_unique_id(used_identifiers)
            state_box = self._convert_state_to_box(state,
                                                   safe_id,
                                                   state_dir,
                                                   root_dir)
            active_boxes.append(state_box)
            
        redo_states = simulation._redo_states
        redo_boxes = []
        
        for state in redo_states:
        
            safe_id = get_unique_id(used_identifiers)
            state_box = self._convert_state_to_box(state,
                                                   safe_id,
                                                   state_dir,
                                                   root_dir)
            redo_boxes.append(state_box)

        simulation._active_states = active_boxes
        simulation._redo_states = redo_boxes
        
        if simulation._merged_state is not None:
            
            safe_id = get_unique_id(used_identifiers)
            state_box = self._convert_state_to_box(simulation._merged_state,
                                                   safe_id,
                                                   state_dir,
                                                   root_dir)
            simulation._merged_state = state_box
            
        return
        
    def deserialise_states(self, simulation,
                                 root_dir=None):
                
        active_boxes = simulation._active_states
        active_states = []
        
        for serial_box in active_boxes:
        
            state = self._convert_box_to_state(serial_box, root_dir)
            active_states.append(state)
            
        redo_boxes = simulation._redo_states
        redo_states = []
        
        for serial_box in redo_boxes:
        
            state = self._convert_box_to_state(serial_box, root_dir)
            redo_states.append(state)
            
        simulation._active_states = active_states
        simulation._redo_states = redo_states
        
        if simulation._merged_state is not None:
            
            state = self._convert_box_to_state(simulation._merged_state,
                                               root_dir)
            simulation._merged_state = state
        
        return
        
    def _get_active_inputs(self, pool,
                                 simulation,
                                 input_declaration):
                    
        input_ids = []
        
        if input_declaration is None: return input_ids
        
        for declared_input in input_declaration:
            
            if isinstance(declared_input, str):
                
                input_ids.append(declared_input)
                
            elif isinstance(declared_input, MaskVariable):
                
                log_msg = ('Checking mask status for input '
                           '"{}".').format(declared_input.variable_id)
                module_logger.debug(log_msg)
                
                if declared_input.unmask_variable is None:
                    
                    input_ids.append(declared_input.variable_id)
                    continue
                
                merged_state = self.create_merged_state(simulation)
                
                if merged_state is None: continue
                    
                if merged_state.has_index(declared_input.unmask_variable):
                    
                    if declared_input.unmask_values is None:
                        
                        input_ids.append(declared_input.variable_id)
                        continue
                
                    data_value = self.get_data_value(
                                            pool,
                                            simulation,
                                            declared_input.unmask_variable)
                                            
                    for unmask_value in declared_input.unmask_values:
                                            
                        if unmask_value == data_value:
                            
                            input_ids.append(declared_input.variable_id)
                            break

            else:
                
                errStr = "Variable identifier has wrong type."
                raise ValueError(errStr)
        
        return input_ids
        
    def _merge_active_states(self, simulation,
                                   level=None,
                                   remove_none_keys=True):
        
        '''Combine all the datastates into one datastate. If the datastate is
        masked then ignore it. If remove_none_keys is True then should a 
        variable have None value when merging a state it should be deleted
        from the final output.'''
        
        active_states = simulation.mirror_active_states()
        
        log_msg = 'Merging active DataStates.'
        module_logger.debug(log_msg)
        
        if not active_states:
            
            return None
            
        merged_map = {}
        
        for state in active_states:

            # Loop if the state is masked.
            if state.ismasked(): continue
            
            data_map = state.mirror_map()
            merged_map = self._update_dict(merged_map,
                                           data_map,
                                           remove_none_keys)
                                           
        merged_state = PseudoState(merged_map, level)

        return merged_state
        
    def _update_dict(self, old_dict, new_dict, remove_none_keys=False):
        
        if remove_none_keys:
        
            add_data = {k: v for k, v in new_dict.items() if v is not None}
            remove_keys = [k for k, v in new_dict.items() if v is None]
            
            final_dict = {k: old_dict[k] for k in old_dict
                                                    if k not in remove_keys}
            final_dict.update(add_data)
                    
        else:
            
            final_dict = deepcopy(old_dict)
            final_dict.update(new_dict)
        
        return final_dict
        
    def _convert_state_to_box(self, state,
                                    identifier,
                                    save_dir,
                                    root_dir=None):
        
        if not isinstance(state, (BaseState, PseudoState, DataState)):
            
            errStr = ("Only objects of type BaseState, PseudoState & "
                      "DataState are accepted. Passed object type was "
                      "{}").format(type(state).__name__)
            raise ValueError(errStr)
                
        file_name = "datastate_{}.json".format(identifier)
        file_path = os.path.join(save_dir, file_name)
        
        if root_dir is None:
            store_path = file_path
        else:
            remove_root = os.path.join(os.path.normpath(root_dir), "")
            store_path = file_path.replace(remove_root, "")
        
        state_dict = state.dump()
        
        with open(file_path, 'wb') as json_file:
            json.dump(state_dict, json_file)
                        
        load_dict = {"file_path": store_path}

        data_box = SerialBox(identifier, load_dict)
            
        return data_box
        
    def _convert_box_to_state(self, serial_box,
                                    root_dir=None):
        
        if not isinstance(serial_box, SerialBox):
            
            errStr = ("Only SerialBox objects are "
                      "accepted. Passed type was "
                      "{}").format(type(serial_box).__name__)
            raise ValueError(errStr)
                
        file_path = serial_box.load_dict["file_path"]

        if root_dir is None:
            load_path = file_path
        else:
            load_path = os.path.join(root_dir, file_path)
                        
        with open(load_path, 'rb') as json_file:
            dump_dict = json.load(json_file)
            
        state_type = dump_dict["type"]
        state_level = dump_dict["level"]
        state_data = dump_dict["data"]

        StateCls = eval(state_type)
        new_state = StateCls(state_level)
                
        if "masked" in dump_dict and dump_dict["masked"]: new_state.mask()
        
        for data_id, data_index in state_data.items():
            new_state.add_index(data_id, data_index)

        return new_state


class Controller(Loader):

    '''This is a control class for working with Simulations using a
    DataStore and a Sequencer.
    '''

    def __init__(self, datastore,
                       sequencer):
        
        super(Controller, self).__init__(datastore)
        self._sequencer = sequencer
        
        return
    
    def copy_simulation(self, pool,
                              simulation,
                              force_title=None,
                              null_title=False,
                              no_merge=False,
                              compact_none_states=True):
        
        # Copy simulation class
        new_simulation = _copy_sim_class(simulation,
                                         force_title,
                                         null_title)
        
        # Copy hubs
        _copy_sim_hubs(simulation, new_simulation)
        
        # Copy the active states
        active_states = self._copy_active_sim_states(simulation,
                                                     compact_none_states)
        
        for state in active_states:
            new_state = self._store.copy_datastate(pool, state)
            new_simulation.add_state(new_state)
        
        # Do any final copying steps
        new_simulation = self._merge_and_stamp(simulation,
                                               new_simulation,
                                               no_merge)
        
        return new_simulation
    
    def import_simulation(self, src_pool,
                                dst_pool,
                                simulation,
                                force_title=None,
                                null_title=False,
                                no_merge=False,
                                compact_none_states=True):
        
        # Copy simulation class
        new_simulation = _copy_sim_class(simulation,
                                         force_title,
                                         null_title)
        
        # Copy hubs
        _copy_sim_hubs(simulation, new_simulation)
        
        # Copy the active states
        active_states = self._copy_active_sim_states(simulation,
                                                     compact_none_states)
        
        for state in active_states:
            
            new_state = self._store.import_datastate(src_pool,
                                                     dst_pool,
                                                     state)
            new_simulation.add_state(new_state)
        
        # Do any final copying steps
        new_simulation = self._merge_and_stamp(simulation,
                                               new_simulation,
                                               no_merge)
        
        return new_simulation
    
    def remove_simulation(self, pool,
                                simulation):
        
        # Copy all states
        all_states = _copy_all_sim_states(simulation)
        
        for state in all_states:
            self._store.remove_state(pool, state)
        
        simulation.clear_states()
        
        return
    
    def create_new_hub(self, simulation,
                             interface_type,
                             hub_id,
                             no_complete=False):
        
        hub = self._sequencer.create_new_hub(interface_type,
                                             no_complete)
        simulation.set_hub(hub_id, hub)
        
        return
                                             
    def create_new_pipeline(self, simulation,
                                  interface_type,
                                  hub_id,
                                  no_complete=False):
        
        hub = self._sequencer.create_new_pipeline(interface_type,
                                                  no_complete)
        simulation.set_hub(hub_id, hub)
        
        return
        
    def get_available_interfaces(self, simulation,
                                       hub_id):

        hub = simulation.get_hub(hub_id)
        names = self._sequencer.get_available_names(hub)

        return names
        
    def get_sequenced_interfaces(self, simulation,
                                       hub_id):
                                           
        hub = simulation.get_hub(hub_id)
        names = self._sequencer.get_sequenced_names(hub)
        
        return names
        
    def get_scheduled_interfaces(self, simulation,
                                       hub_id):
                                           
        hub = simulation.get_hub(hub_id)
        names = self._sequencer.get_scheduled_names(hub)
        
        return names
    
    def get_completed_interfaces(self, simulation,
                                       hub_id):
                                           
        hub = simulation.get_hub(hub_id)
        names = self._sequencer.get_completed_names(hub)
        
        return names
        
    def has_interface(self, simulation,
                            hub_id,
                            interface_name):
        
        hub = simulation.get_hub(hub_id)
        result = self._sequencer.has_name(hub, interface_name)
        
        return result
        
    def get_next_interface(self, simulation,
                                 hub_id):

        hub = simulation.get_hub(hub_id)
        next_interface = self._sequencer.get_next_name(hub)

        return next_interface
        
    def get_interface_weight(self, simulation,
                                   hub_id,
                                   interface_name):
    
        '''Get the weighting of the interface if set'''

        hub = simulation.get_hub(hub_id)
        result = self._sequencer.get_weight(hub, interface_name)

        return result
        
    def sequence_interface(self, simulation,
                                 hub_id,
                                 interface_name):
                            
        hub = simulation.get_hub(hub_id)
                                                                   
        if not self._sequencer.is_available(hub, interface_name):
            
            errStr = ("Interface {} not available for hub  "
                      "{}").format(interface_name, hub_id)
            raise ValueError(errStr)

        self._sequencer.sequence(hub, interface_name)
                
        return
        
    def check_next_interface(self, simulation,
                                   hub_id,
                                   interface_name):
        
        hub = simulation.get_hub(hub_id)
        self._sequencer.check_next(hub, interface_name)
        
        return
        
    def is_interface_completed(self, simulation,
                                     hub_id,
                                     interface_name):

        hub = simulation.get_hub(hub_id)
        result = self._sequencer.is_complete(hub, interface_name)
        
        return result
        
    def set_interface_completed(self, simulation,
                                      hub_id,
                                      interface_name):
        
        hub = simulation.get_hub(hub_id)
        self._sequencer.complete(hub, interface_name)
        
        return
        
    def get_interface_cls_name(self, simulation,
                                     hub_id,
                                     interface_name):
    
        hub = simulation.get_hub(hub_id)
        interface_cls_name = self._sequencer.get_cls_name(hub, interface_name)
        
        return interface_cls_name
        
    def get_interface_obj(self, simulation,
                                hub_id,
                                interface_name):
          
        hub = simulation.get_hub(hub_id)
        interface_cls_name = self.get_interface_cls_name(simulation,
                                                         hub_id,
                                                         interface_name)
        interface_obj = hub.get_interface_obj(interface_cls_name)
        
        return interface_obj
    
    def mask_states(self, simulation,
                          search_str=None,
                          mask_after=None,
                          no_merge=False):
                                   
        n_masks = simulation.mask_states(search_str,
                                         mask_after)

        if no_merge or n_masks == 0: return n_masks
                                      
        # Update the merged state stored in the simulation
        merged_state = self._merge_active_states(simulation)
        simulation.set_merged_state(merged_state)
        
        return n_masks

    def unmask_states(self, simulation,
                            search_str=None,
                            no_merge=False):

        # Sanitise the search string
        if search_str is not None: search_str = search_str.lower()

        n_unmasks = simulation.unmask_states(search_str)
                
        if no_merge or n_unmasks == 0:
            return n_unmasks
                                      
        # Update the merged state stored in the simulation
        merged_state = self._merge_active_states(simulation)
        simulation.set_merged_state(merged_state)
        
        return n_unmasks
        
    def delete_masked_states(self, pool,
                                   simulation,
                                   no_merge=False):
        
        # Kill masked states          
        removed_states = simulation.pop_masked_states()
                        
        for kill_state in removed_states:
            
            self._store.remove_state(pool, kill_state)
            
        if no_merge: return
                
        # Update the merged state stored in the simulation
        merged_state = self._merge_active_states(simulation)
        simulation.set_merged_state(merged_state)
            
        return
        
    def get_input_status(self, pool,
                               simulation,
                               hub_id,
                               interface_name,
                               all_overwritten=None):

        """Get all inputs required for the module, as a dictionary with the
        value representing a status of required, satisfied or unavailable
        
        Note:
          Inputs to completed interfaces are marked as unavailable.
          Inputs to interfaces that are inputs or outputs of preceding 
            interfaces are marked as overwritten.
          Optional inputs to interfaces that are outputs of preceding 
            interfaces are marked as overwritten_option.
        
        """
        
        log_msg = ('Getting input status for interface '
                  '"{}".').format(interface_name)
        module_logger.debug(log_msg)
        
        hub = simulation.get_hub(hub_id)
        interface_cls_name = self.get_interface_cls_name(simulation,
                                                         hub_id,
                                                         interface_name)
        interface_obj = self.get_interface_obj(simulation,
                                               hub_id,
                                               interface_name)
        (input_declaration,
         optional_inputs) = interface_obj.get_inputs()

        all_inputs = self._get_active_inputs(pool,
                                             simulation,
                                             input_declaration)           

        # Check if the interface has been completed already
        if hub.force_completed or hub.is_completed(interface_cls_name):

            # All inputs are unavailable
            new_input_status = {input_id: "unavailable" for
                                                    input_id in all_inputs}

        else:

            # Need to interate through any interfaces before the given one
            # in the interface map of the hub, excluding the completed
            # ones.
            preceeding_interfaces = hub.get_preceding_interfaces(
                                                        interface_cls_name,
                                                        ignore_completed=True)


            # Get all the outputs provided for the proceeding items
            if all_overwritten is None: all_overwritten = []

            for interface_obj in preceeding_interfaces.itervalues():
                
                prec_input_declaration, _ = interface_obj.get_inputs()
                prec_inputs = self._get_active_inputs(pool,
                                                      simulation,
                                                      prec_input_declaration)
                
                all_overwritten.extend(prec_inputs)

                outputs = interface_obj.get_outputs()
                all_overwritten.extend(outputs)

            # Inputs are required unless optional
            input_status = {}

            for input_id in all_inputs:
                
                if input_id in optional_inputs:
                    
                    input_status[input_id] = "optional"
                    
                else:

                    input_status[input_id] = "required"

            for var_id in all_overwritten:

                if var_id in input_status.keys():
                    
                    if var_id in optional_inputs:
                    
                        input_status[var_id] = "overwritten_option"
                    
                    else:
                    
                        input_status[var_id] = "overwritten"

            # Update the input and output status if the data is in the data
            # state                
            merged_state = self.create_merged_state(simulation)
                
            if merged_state is None:
                return input_status

            state_data_ids = merged_state.get_identifiers()
            new_input_status = input_status.copy()
    
            for data_id, status in input_status.items():
                
                new_input_status[data_id] = input_status[data_id]
    
                if data_id in state_data_ids:
                    
                    # If the variable is satisfied if in the datastate and 
                    # its marked as required or optional
                    if status == "required" or status == "optional":
                        
                        new_input_status[data_id] = "satisfied"

        return new_input_status

    def get_output_status(self, simulation,
                                hub_id,
                                interface_name,
                                exectuted_outputs=None,
                                force_last_completed=None):

        """Get all the outputs of the module, as a dictionary with the
        value representing a status of satisfied, unavailable or overwritten"""
        
        log_msg = ('Getting output status for interface '
                  '"{}".').format(interface_name)
        module_logger.debug(log_msg)
        
        # Get all the inputs for the interface
        hub = simulation.get_hub(hub_id)
        interface_cls_name = self.get_interface_cls_name(simulation,
                                                         hub_id,
                                                         interface_name)
        interface_obj = self.get_interface_obj(simulation,
                                               hub_id,
                                               interface_name)
        output_declaration = interface_obj.get_outputs()

        # Get all the outputs provided by the interface
        output_status = {output_id: "unavailable"
                                        for output_id in output_declaration}
        
        # Update the output status if the data is in the data state
        merged_state = self.create_merged_state(simulation)
            
        if merged_state is None:
            return output_status

        # Find all the "exectuted outputs"
        if exectuted_outputs is None: exectuted_outputs = []
        completed_interfaces = hub.get_completed_map()
        
        if force_last_completed is not None:
                
            lc_cls_name = self.get_interface_cls_name(simulation,
                                                      hub_id,
                                                      force_last_completed)
            last_completed = lc_cls_name
            
        else:
            
            lc_cls_name = None
            last_completed = hub.get_last_completed()
        
        if (interface_cls_name in completed_interfaces and not
                                last_completed == interface_cls_name):
                                    
            completed_interface_names = completed_interfaces.keys()
        
            interface_index = completed_interface_names.index(
                                                        interface_cls_name)
            
            
            start_index = interface_index + 1
            end_index = len(completed_interface_names)
            
            if lc_cls_name is not None:
                
                if lc_cls_name in completed_interface_names:
                                        
                    last_completed_index = completed_interface_names.index(
                                                                   lc_cls_name)
                    
                    end_index = last_completed_index + 1

                    if end_index < start_index: end_index = None
                    
            if end_index is not None:
                
                exectuted_outputs = _get_executed_outputs(completed_interfaces,
                                                          start_index,
                                                          end_index,
                                                          exectuted_outputs)
                
            else:
                
                # If the end index is None then all values should be
                # unavailable
                return output_status
                
        elif hub.has_order and interface_cls_name not in completed_interfaces:
            
            # If the interface has yet to be completed in an ordered hub 
            # return all outputs as unavailable
            return output_status

        state_data_ids = merged_state.get_identifiers()
        new_output_status = output_status.copy()
                     
        for data_id, status in output_status.items():
            
            new_output_status[data_id] = output_status[data_id]

            if data_id in state_data_ids:
                
                if data_id in exectuted_outputs:
                    
                    new_output_status[data_id] = "overwritten"
                    
                else:
                        
                    new_output_status[data_id] = "satisfied"

        return new_output_status
        
    def get_data_value(self, pool,
                             simulation,
                             data_identity,
                             level=None,
                             check_identity=False):        

        if level is not None:
            read_simulation = deepcopy(simulation)
            self._mask_after_level(read_simulation,
                                   level)
        else:
            read_simulation = simulation
                                                       
        if (check_identity and
            not self.has_data(read_simulation, data_identity)): return None
                        
        data_value = super(Controller, self).get_data_value(pool,
                                                            read_simulation,
                                                            data_identity)
                                                            
        return data_value
        
    def get_level_values(self, pool,
                               simulation,
                               data_identity,
                               levels=None,
                               force_masks=None):
        
        simulation_copy = deepcopy(simulation)
        
        if levels is None: levels = OrderedSet(simulation.get_active_levels())
                                                        
        level_results = OrderedDict()
                                                        
        for level_key in levels:
            
            self._mask_after_level(simulation_copy,
                                   level_key,
                                   force_masks)
            
            if not self.has_data(simulation_copy,
                                 data_identity):
                                     
                continue
                                
            level_value = self.get_data_value(pool,
                                              simulation_copy,
                                              data_identity)
                                              
            level_results[level_key] = level_value
        
        return level_results
        
    def input_available(self, pool,
                              simulation,
                              hub_id,
                              interface_name,
                              check_id):
                                  
        interface_obj = self.get_interface_obj(simulation,
                                               hub_id,
                                               interface_name)
                                  
        result = super(Controller, self).input_available(pool,
                                                         simulation,
                                                         interface_obj,
                                                         check_id)

        return result
        
    def can_load(self, pool,
                       simulation,
                       hub_id,
                       interface_name):
                           
        interface_obj = self.get_interface_obj(simulation,
                                               hub_id,
                                               interface_name)
        
        result = super(Controller, self).can_load(pool,
                                                  simulation,
                                                  interface_obj)
            
        return result
        
    def load_interface(self, pool,
                             simulation,
                             hub_id,
                             interface_name,
                             skip_vars=None):
                                 
        interface_obj = self.get_interface_obj(simulation,
                                               hub_id,
                                               interface_name)
        
        interface_obj = super(Controller, self).load_interface(pool,
                                                               simulation,
                                                               interface_obj,
                                                               skip_vars)
                                                        
        return interface_obj
    
    @classmethod
    def reset_hub(self, simulation,
                        hub_id):
        
        hub = simulation.get_hub(hub_id)
        hub.reset()
        
        return
    
    def _copy_active_sim_states(self, simulation,
                                      compact_none_states=False):
    
        active_states = simulation.mirror_active_states()
        
        if compact_none_states:
           active_states = self._compact_none_states(active_states)
        
        return active_states
    
    def _compact_none_states(self, state_list):
        """Merge groups of states without levels into single states, while 
        preserving ordering between labelled states"""
        
        new_states = []
        none_states = []
        
        for state in state_list:
            
            if state.get_level() is None:
                
                # Raise an error if any None states are masked.
                if state.ismasked():
                    
                    errStr = ("State list can not be compacted if states "
                              "without levels are masked")
                    raise RuntimeError(errStr)
                
                none_states.append(state)
                
                continue
            
            if none_states:
                
                compact_state = self._make_compact_state(none_states)
                new_states.append(compact_state)
                none_states = []
            
            new_states.append(state)
        
        if none_states:
            compact_state = self._make_compact_state(none_states)
            new_states.append(compact_state)
        
        return new_states
    
    def _make_compact_state(self, state_list, level=None):
        
        merged_map = {}
            
        for state in state_list:
            
            data_map = state.mirror_map()
            merged_map = self._update_dict(merged_map,
                                           data_map)
        
        compact_state = self._store.create_new_datastate(
                                                level=level,
                                                force_map=merged_map)
        
        return compact_state
    
    def _merge_and_stamp(self, old_simulation,
                               new_simulation,
                               no_merge=False):
        
        if not no_merge:
            
            # Update the merged state stored in the simulation
            merged_state = self._merge_active_states(new_simulation)
            new_simulation.set_merged_state(merged_state)
        
        # Do any final copying steps
        new_simulation = old_simulation.stamp(new_simulation)
        
        return new_simulation
    
    def _mask_after_level(self, simulation, level, force_masks=None):
                        
        # Remove all existing masks
        self.unmask_states(simulation,
                           no_merge=True)
            
        # Mask all output states after the given level
        self.mask_states(simulation,
                         mask_after=level,
                         no_merge=True)
        
        # If a list of masks to force are given, mask them and then try to
        # unmask the original given level again.        
        if force_masks is not None:
            
            for mask in force_masks:
                           
                self.mask_states(simulation,
                                 search_str=mask,
                                 no_merge=True)
                                 
            self.unmask_states(simulation,
                               search_str=level,
                               no_merge=True)
                               
        # Update the merged state stored in the simulation
        merged_state = self._merge_active_states(simulation)
        simulation.set_merged_state(merged_state)
                                                      
        return


def _copy_sim_class(simulation,
                    force_title=None,
                    null_title=False):
    
    # Set the title
    if null_title:
        title = None
    elif force_title is None:
        title = simulation.get_title()
    else:
        title = force_title
    
    # Create an instance of the given class
    SimCls = simulation.__class__
    new_simulation = SimCls(title)
    
    return new_simulation


def _copy_sim_hubs(old_simulation,
                   new_simulation):
    
    hub_ids = old_simulation.get_hub_ids()
    
    for hub_id in hub_ids:
        hub = old_simulation.get_hub(hub_id)
        hub_copy = deepcopy(hub)
        new_simulation.set_hub(hub_id, hub_copy)
    
    return


def _copy_all_sim_states(simulation):
    all_states = simulation.mirror_all_states()
    return all_states


def _get_executed_outputs(completed_interfaces,
                          start_index,
                          end_index,
                          exectuted_outputs):
    
    completed_interface_names = completed_interfaces.keys()
    
    next_completed_interfaces = completed_interface_names[
                                                  start_index:end_index]
    
    for next_cls_name in next_completed_interfaces:
        
        interface_obj = completed_interfaces[next_cls_name]
        outputs = interface_obj.get_outputs()
        exectuted_outputs.extend(outputs)
    
    return exectuted_outputs
