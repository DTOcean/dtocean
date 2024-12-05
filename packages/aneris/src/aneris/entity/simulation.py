# -*- coding: utf-8 -*-
"""
Entity class(es) relating to the simulation
"""

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

from copy import deepcopy

class Simulation(object):
    
    '''The main class is the simulation which holds all of the information
    about the system.'''
    
    def __init__(self, title=None):
        
        self._title = title
        self._hubs = {}
        self._active_states = []
        self._redo_states = []
        self._merged_state = None
        
        log_msg = 'Created new Simulation'
        if title is not None: log_msg += ' with title "{}"'.format(title)
        module_logger.info(log_msg)
    
    def set_title(self, title):
        
        self._title = title
        
        return
    
    def get_title(self):
        
        return self._title
    
    def set_hub(self, hub_id, hub):
                
        self._hubs[hub_id] = hub
        
        return
    
    def get_hub(self, hub_id):
        
        new_hub = self._hubs[hub_id]
        
        return new_hub
    
    def get_hub_ids(self):
        
        return self._hubs.keys()
    
    def set_merged_state(self, pseudo_state):
        
        self._merged_state = pseudo_state
        
        return
    
    def get_merged_state(self):
        
        return self._merged_state
    
    def mirror_active_states(self):
        
        """This is a dangerous action if the datastates are stored without
        updating the datapool."""
        
        return deepcopy(self._active_states)
    
    def mirror_all_states(self):
        
        """This is a dangerous action if the datastates are stored without
        updating the datapool."""
        
        mirror_states = deepcopy(self._active_states)
        redo_copy = deepcopy(self._redo_states)
        mirror_states.extend(list(reversed(redo_copy)))
        
        return mirror_states
    
    def count_states(self):
        
        '''Count the number of datastates in the simulation'''
        
        state_count = len(self._active_states) + len(self._redo_states)
        
        return state_count
    
    def add_state(self, datastate,
                        overwrite=False):
        
        '''Add a datastate to the simulation'''
        
        if overwrite:
            
            self._active_states[-1] = datastate
            
        else:
        
            self._active_states.append(datastate)
            
        # Reset the redo list and return the removed list
        removed_states = self._redo_states[:]
        self._redo_states = []
        self._merged_state = None
        
        return removed_states
    
    def mask_states(self, search_str=None, mask_after=None):
        
        '''Apply a mask to all states that have levels which partially match
        the given search string. Optionally start masking after the given
        mask after state name'''
        
        # Search for masks in the active and redo state stacks in two passes. 
        # It's important to learn whether the masking started in the active 
        # state stack or the redo state stack.   
        if mask_after is not None:
            
            active_observed, active_start = self._get_start_index(
                                                        self._active_states,
                                                        mask_after)
                                                                           
            redo_observed, redo_start = self._get_start_index(
                                                        self._redo_states,
                                                        mask_after,
                                                        list_reversed=True)
                                               
        else:
            
            active_observed = True
            redo_observed = False
            active_start = 0
            redo_start = 0
            
        mask_count = 0
            
        if active_observed and not redo_observed and active_start is not None:                                                
        
            (self._active_states,
             local_count) = self._mask_state_list(self._active_states,
                                                  search_str,
                                                  active_start)
                                                  
            mask_count += local_count
            
        if active_observed and not redo_observed:

            (self._redo_states,
             local_count) = self._mask_state_list(self._redo_states,
                                                  search_str,
                                                  list_reversed=True)
                                                  
            mask_count += local_count
                                                      
        if redo_observed and redo_start is not None:

            (self._redo_states,
             local_count) = self._mask_state_list(self._redo_states,
                                                  search_str,
                                                  redo_start,
                                                  list_reversed=True)
                                                
            mask_count += local_count

        if mask_count > 0: self._merged_state = None
        
        return mask_count
    
    def unmask_states(self, search_str=None):
        
        '''Remove any masks on states matching the search string if given
        otherwise unmask all states'''
        
        unmask_count = 0
        
        for state in self._active_states:
            
            if not state.ismasked(): continue
            
            state_level = state.get_level()

            if (search_str is None or
               (state_level is not None and search_str in state_level)):
                   
                if state_level is None:
                    log_msg = 'Unmasking DataState'
                else:
                    log_msg = ('Unmasking DataState at level '
                               '"{}".').format(state.get_level())
    
                module_logger.debug(log_msg)
                                   
                state.unmask()
                unmask_count += 1
                
        for state in self._redo_states:
            
            if not state.ismasked(): continue
            
            state_level = state.get_level()
            
            if (search_str is None or
               (state_level is not None and search_str in state_level)):
                   
                if state_level is None:
                    log_msg = 'Unmasking DataState'
                else:
                    log_msg = ('Unmasking DataState at level '
                               '"{}".').format(state.get_level())
    
                module_logger.debug(log_msg)
                
                state.unmask()
                unmask_count += 1
                
        if unmask_count > 0: self._merged_state = None
        
        return unmask_count
    
    def pop_masked_states(self):
                        
        delete_active = [state for state in self._active_states
                                                    if state.ismasked()]
        new_active = [state for state in self._active_states
                                                    if not state.ismasked()]
                                                        
        delete_redo = [state for state in self._redo_states
                                                    if state.ismasked()]
        new_redo = [state for state in self._redo_states
                                                    if not state.ismasked()]
        
        self._active_states = new_active
        self._redo_states = new_redo
        self._merged_state = None
            
        return delete_active + delete_redo
    
    def undo_state(self):
        
        '''Move the active state backwards through the state history'''
        
        if not self._active_states: return
        
        last_state = self._active_states.pop()
        self._redo_states.append(last_state)
        self._merged_state = None     
        
        return
    
    def redo_state(self):
        
        '''Return a datastate in the redo states back to the state history'''
        
        if not self._redo_states: return
            
        next_state = self._redo_states.pop()
        self._active_states.append(next_state)
        self._merged_state = None
        
        return
    
    def clear_states(self):
        
        self._active_states = []
        self._redo_states = []
        self._merged_state = None
        
        return
    
    def get_active_levels(self, show_none=False,
                                show_masked=True):
        
        result = []
        
        for state in self._active_states:
            
            if show_none or state.get_level() is not None:
                
                if show_masked or not state.ismasked():
                    result.append(state.get_level())
            
        return result
    
    def get_all_levels(self, show_none=False,
                             show_masked=True):
        
        result = self.get_active_levels()
            
        for state in self._redo_states:
            
            if show_none or state.get_level() is not None:
                
                if show_masked or not state.ismasked():
                    result.append(state.get_level())
            
        return result
    
    def get_last_level(self, show_none=False,
                             show_masked=True):
        
        if not self._active_states:
            
            result = None
            
        else:
            
            active_levels = self.get_active_levels(show_none, show_masked)
            result = active_levels[-1]
            
        return result
    
    def stamp(self, simulation):
        
        return simulation
    
    def _get_start_index(self,
                         state_list,
                         mask_after,
                         list_reversed=False):
        
        observed = False
        start_index = None
                
        # Some complex logic for masking after the final appearance of a given
        # level
        if list_reversed:
            iter_states = reversed(state_list)
        else:
            iter_states = iter(state_list)
        
        for i, state in enumerate(iter_states):
            
            if observed:
                
                if start_index is None and state.get_level() != mask_after:
                    
                    start_index = i
                
                if start_index is not None and state.get_level() == mask_after:
                
                    start_index = None
            
            elif state.get_level() == mask_after:
                
                observed = True
        
        if observed:
            result = observed, start_index
        else:
            result = observed, False
        
        return result
    
    def _mask_state_list(self,
                         state_list,
                         search_str=None,
                         start_index=0,
                         list_reversed=False):
                             
        if not state_list: return state_list, 0
        
        mask_count = 0
        
        new_states = state_list[:]
        
        if list_reversed:
            end_index = len(new_states) - start_index
            iter_states = reversed(new_states[:end_index])
        else:
            iter_states = iter(new_states[start_index:])
        
        for state in iter_states:
            
            if state.ismasked(): continue
            
            state_level = state.get_level()
            
            if (search_str is None or
               (state_level is not None and search_str in state_level)):
                
                if state_level is None:
                    log_msg = 'Masking DataState'
                else:
                    log_msg = ('Masking DataState at level '
                               '"{}".').format(state.get_level())
                
                module_logger.debug(log_msg)
                
                state.mask()
                mask_count += 1
        
        return new_states, mask_count
