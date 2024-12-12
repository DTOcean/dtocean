# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 11:22:04 2016

@author: Mathew Topper
"""

import pprint

def check_integrity(data_pool, simulation_list):
    
    """Check the integrity of a list of Simulation objects against a given 
    DataPool.
    """
    
    # Process:
    #   1. Check that the simulations are unique
    #   2. Check that all the datastates are unique
    #   3. Check that the links are consistent with the DataPool
    
    if len(set(simulation_list)) != len(simulation_list):
        
        non_unique = len(simulation_list) - len(set(simulation_list))
        errStr = "{} simulations are non-unique".format(non_unique)
        raise ValueError(errStr)
        
    # Collect all the datastates from the simulations and test for uniqueness
    all_states = []        
    for simulation in simulation_list:
        all_states.extend(simulation.mirror_all_states())
        
    if len(set(all_states)) != len(all_states):
        
        non_unique = len(all_states) - len(set(all_states))
        errStr = "{} data states are non-unique".format(non_unique)
        raise ValueError(errStr)

    # Iterate through the datastates and form the number of links per data
    state_links = {}
    
    for state in all_states:
        
        data_map = state.mirror_map()
        data_indexes = data_map.values()
        
        for index in data_indexes:
            
            if index is None: continue
            
            if index in state_links: 
                state_links[index] += 1
            else:
                state_links[index] = 1
                
    pool_links = data_pool.mirror_links()
                
    unmatched_links = set(pool_links.items()) ^ set(state_links.items())
    
    if len(unmatched_links) != 0:
        
        pprint.pprint(pool_links)
        pprint.pprint(state_links)

        bad_idxs = set([x[0] for x in unmatched_links])
        bad_idxs_str = ", ".join("{}".format(x) for x in bad_idxs)
        errStr = ("Inconsistent number of links for index(es) "
                  "'{}'. Good luck working out why...").format(bad_idxs_str)
        raise ValueError(errStr)

    return True