# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

# pylint: disable=redefined-outer-name

import pytest

from aneris.control.simulation import Controller
from aneris.control.pipeline import Sequencer
from aneris.control.data import DataValidation, DataStorage
from aneris.entity import Simulation
from aneris.entity.data import DataCatalog, DataPool

from . import data_plugins as data_plugins
from . import interface_plugins as interfaces


@pytest.fixture(scope="module")
def controller():
    
    data_store = DataStorage(data_plugins)
    sequencer = Sequencer(["DummyInterface"],
                          interfaces)
    
    control = Controller(data_store, sequencer)  
    
    return control

def test_undo_state(controller):
    
    '''Test reversing from one data state to the previous one.'''
    
    pool = DataPool()
    
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DummyInterface", "dummy_hub")
    
    controller.sequence_interface(new_sim,
                                  "dummy_hub",
                                  "Early Interface")
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [False])
    
    assert new_sim.get_last_level() == "input"
    
    f_interface = controller.get_interface_obj(new_sim,
                                               "dummy_hub",
                                               "Early Interface")
    
    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data('early:dummy:data')
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             ['early:dummy:data'],
                             [raw_data])
    
    assert new_sim.get_last_level() == "executed"
    
    new_sim.undo_state()
        
    assert new_sim.get_last_level() ==  "input"

def test_redo_state(controller):
    
    '''Test reversing from one data state to the previous one.'''
    
    pool = DataPool()
    
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DummyInterface", "dummy_hub")
    
    controller.sequence_interface(new_sim,
                                  "dummy_hub",
                                  "Early Interface")
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [False])
    
    assert new_sim.get_last_level() == "input"
    
    f_interface = controller.get_interface_obj(new_sim,
                                               "dummy_hub",
                                               "Early Interface")
    
    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data('early:dummy:data')
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             ['early:dummy:data'],
                             [raw_data])
    
    assert new_sim.get_last_level() == "executed"
    
    new_sim.undo_state()
    
    assert new_sim.get_last_level() == "input"
    
    new_sim.redo_state()
    
    assert new_sim.get_last_level() == "executed"


def test_clear_states(controller):
    
    '''Test reversing from one data state to the previous one.'''
    
    pool = DataPool()
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DummyInterface", "dummy_hub")
    
    controller.sequence_interface(new_sim,
                                  "dummy_hub",
                                  "Early Interface")
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [False])
    
    f_interface = controller.get_interface_obj(new_sim,
                                               "dummy_hub",
                                               "Early Interface")
    
    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data('early:dummy:data')
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             ['early:dummy:data'],
                             [raw_data])
    
    new_sim.undo_state()
    
    assert new_sim.count_states() == 2
    
    new_sim.clear_states()
    
    assert new_sim.count_states() == 0
