# -*- coding: utf-8 -*-
"""
Created on Tue Aug 08 12:36:48 2017

@author: mtopper
"""

import pytest
import pandas as pd


@pytest.fixture(scope="module")
def bom():
    
    bom_dict = {'phase': [None, None, None, "Test", "Test", "Test"],
                'unitary_cost': [0.0, 100000.0, 100000.0, 1, 1, 1],
                'project_year': [0, 1, 2, 0, 1, 2],
                'quantity': [1, 1, 1, 1, 10, 20]
                }
    
    bom_df = pd.DataFrame(bom_dict)
    
    return bom_df


@pytest.fixture(scope="module")
def energy_record():
    
    energy_dict = {'project_year': [0, 1, 2, 3, 4, 5],
                   'energy 0': [0, 1, 2, 0, 10, 20],
                   'energy 1': [0, 1, 32, 0, 0, 20]
                   }
    
    energy_df = pd.DataFrame(energy_dict)
    
    return energy_df


@pytest.fixture(scope="module")
def opex_costs():
    
    opex_dict = {'project_year': [0, 1, 2, 3, 4, 5],
                 'cost 0': [0.0, 100000.0, 100000.0, 1, 1, 1],
                 'cost 1': [0.0, 100000.0, 0, 1, 1, 100000.0]
                 }
    
    opex_df = pd.DataFrame(opex_dict)
    
    return opex_df
