# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import pytest
pytest.importorskip("dtocean_dummy")

from aneris.control.simulation import Controller, Loader
from aneris.control.sockets import NamedSocket
from aneris.control.pipeline import Sequencer
from aneris.control.data import DataValidation, DataStorage
from aneris.entity import Simulation
from aneris.entity.data import DataCatalog, DataPool
from aneris.utilities.data import check_integrity

from . import data_plugins as data_plugins
from . import interface_plugins as interfaces

@pytest.fixture(scope="module")
def catalog():
    
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    return catalog
    
@pytest.fixture(scope="module")
def loader():
    
    data_store = DataStorage(data_plugins)
    loader = Loader(data_store)  
    
    return loader

@pytest.fixture(scope="module")
def controller():
    
    data_store = DataStorage(data_plugins)
    sequencer = Sequencer(["DemoInterface"],
                          interfaces)

    control = Controller(data_store,
                         sequencer)  
    
    return control

def test_get_receiving_interfaces():

    test_var = 'demo:demo:high'
    
    interface = NamedSocket("DemoInterface")
    interface.discover_interfaces(interfaces)
    receivers = interface.get_receiving_interfaces(test_var)

    assert "TableInterface" in receivers
    
def test_get_next_interface(controller):
                       
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")
    
    next_interface = controller.get_next_interface(new_sim, "demo_hub")
    assert next_interface == "Spreadsheet Generator"
    
def test_input_status(controller):
    
    pool = DataPool()

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")
                                                
    input_status = controller.get_input_status(pool,
                                               new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")
                                                        
    status = set(input_status.values())

    assert 'required' == status.pop() 
    
    
def test_input_status_overwritten(controller):
        
    pool = DataPool()

    new_sim = Simulation("Hello World!")
    controller.create_new_pipeline(new_sim, "DemoInterface", "demo_pipe")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_pipe",
                                  "Spreadsheet Generator")
                                                
    controller.sequence_interface(new_sim,
                                  "demo_pipe",
                                  "Later Interface")
    
    input_status = controller.get_input_status(pool,
                                               new_sim,
                                               "demo_pipe",
                                               "Later Interface")
    
    input_status_values = set(input_status.values())

    assert "overwritten" in input_status_values
    

def test_input_status_trigger(catalog, controller):
    
    pool = DataPool()

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [True])
                                                 
    input_status = controller.get_input_status(pool,
                                               new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")
                                                        
    status = set(input_status.values())

    assert set(['required', 'optional']) == status                 

def test_demo_status(catalog, loader, controller):
    
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'demo:demo:low': 1,
                   'demo:demo:high': 2,
                   'demo:demo:rows': 5}
                   
    # High and low have no effect as they are masked by trigger.bool
                                      
    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")
                                               
    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)

    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)

    input_status = controller.get_input_status(pool,
                                               new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    output_status = controller.get_output_status(new_sim,
                                                 "demo_hub",
                                                 "Spreadsheet Generator")

    input_status_values = set(input_status.values())
    output_status_values = set(output_status.values())

    assert "satisfied" in input_status_values
    assert "unavailable" in output_status_values

    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])

    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")

    input_status = controller.get_input_status(pool,
                                               new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    output_status = controller.get_output_status(new_sim,
                                                 "demo_hub",
                                                 "Spreadsheet Generator")

    input_status_values = set(input_status.values())
    output_status_values = set(output_status.values())
    table = controller.get_data_value(pool,
                                      new_sim,
                                      test_variable)
                                      
    assert "unavailable" in input_status_values
    assert "satisfied" in output_status_values
    assert table["Random"].max() < 1
    assert len(table) == test_inputs['demo:demo:rows']
    
def test_demo_status_trigger(catalog, loader, controller):
    
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'trigger.bool': True,
                   'demo:demo:low': 1,
                   'demo:demo:high': 2,
                   'demo:demo:rows': 5}
                   
    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")
                                               
    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)

    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)

    input_status = controller.get_input_status(pool,
                                               new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    output_status = controller.get_output_status(new_sim,
                                                 "demo_hub",
                                                 "Spreadsheet Generator")

    input_status_values = set(input_status.values())
    output_status_values = set(output_status.values())

    assert "satisfied" in input_status_values
    assert "unavailable" in output_status_values

    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])

    
    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")

    input_status = controller.get_input_status(pool,
                                               new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    output_status = controller.get_output_status(new_sim,
                                                 "demo_hub",
                                                 "Spreadsheet Generator")

    input_status_values = set(input_status.values())
    output_status_values = set(output_status.values())
    table = controller.get_data_value(pool,
                                      new_sim,
                                      test_variable)
                                      
    assert "unavailable" in input_status_values
    assert "satisfied" in output_status_values
    assert table["Random"].min() >= 1
    assert len(table) == test_inputs['demo:demo:rows']
    
def test_merge_states(catalog, loader, controller):

    '''Test merging data states.'''
    
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'demo:demo:low': 0,
                   'demo:demo:high': 1,
                   'demo:demo:rows': 5}

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)

    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)

    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])

    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")
    

    another_state = controller._merge_active_states(new_sim)
    df = controller.get_data_value(pool, new_sim, test_variable)

    assert check_integrity(pool, [new_sim])
    assert another_state.count() == 4
    assert len(df.index) == 5

def test_check_next_interface(catalog, loader, controller):
    
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'demo:demo:low': 0,
                   'demo:demo:high': 1,
                   'demo:demo:rows': 5}

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")
                                                
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Later Interface")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)

    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)

    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")
    
    state = controller._merge_active_states(new_sim)

    assert state.count() == 4
    assert new_sim.count_states() == 2
    
    controller.check_next_interface(new_sim,
                                    "demo_hub",
                                    "Spreadsheet Generator")
 
    next_interface = controller.get_next_interface(new_sim, "demo_hub")    
    state = controller._merge_active_states(new_sim)

    assert next_interface == "Spreadsheet Generator"    
    
    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")

    state = controller._merge_active_states(new_sim)

    assert state.count() == 4
    assert new_sim.count_states() == 3
    
def test_undo_remove_states(catalog, loader, controller):

    '''Test adding data to a data state from a chosen interface.'''
    
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'demo:demo:low': 0,
                   'demo:demo:high': 1,
                   'demo:demo:rows': 5}
                                                              
    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")
                                                
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Later Interface")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)

    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)

    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")
                                                        
    state = controller._merge_active_states(new_sim)

    assert state.count() == 4
    assert new_sim.count_states() == 2
    assert len(pool) == 4
    
    new_sim.undo_state()
    new_sim.undo_state()

    state = controller._merge_active_states(new_sim)
    
    assert state is None
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [True])

    state = controller._merge_active_states(new_sim)   
    
    assert state.count() == 1
    assert len(pool) == 1


def test_masked_states(catalog, loader, controller):

    '''Test adding data to a data state from a chosen interface.'''
    
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'demo:demo:low': 0,
                   'demo:demo:high': 1,
                   'demo:demo:rows': 5}

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")
                                                
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Later Interface")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [False])
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [True])
                                      
    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)
 
    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                                 
    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")

    current_state = controller._merge_active_states(new_sim)

    assert current_state.count() == 5
    assert len(new_sim._active_states) == 4
    
    new_sim.mask_states(mask_after="input")
    current_state = controller._merge_active_states(new_sim)
    
    assert current_state.count() == 4
    
    new_sim.unmask_states()
    current_state = controller._merge_active_states(new_sim)
    
    assert current_state.count() == 5
    
    new_sim.undo_state()
    
    assert len(new_sim._active_states) == 3
    assert new_sim.count_states() == 4
    
    new_sim.mask_states(mask_after="input")
    new_sim.redo_state()
    
    current_state = controller._merge_active_states(new_sim)

    assert len(new_sim._active_states) == 4
    assert current_state.count() == 4    
    assert check_integrity(pool, [new_sim])

def test_delete_masked_states(catalog, loader, controller):

    '''Test adding data to a data state from a chosen interface and then
    masking it.'''
   
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'demo:demo:low': 0,
                   'demo:demo:high': 1,
                   'demo:demo:rows': 5}

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)
                                      
    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)
    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                                 
    controller.set_interface_completed(new_sim,
                                       "demo_hub",
                                       "Spreadsheet Generator")

    current_state = controller._merge_active_states(new_sim)

    assert current_state.count() == 4
    assert new_sim.count_states() == 2
    
    new_sim.mask_states("executed")
    current_state = controller._merge_active_states(new_sim)
    
    assert current_state.count() == 3
    assert new_sim.count_states() == 2
    
    # Note this will corrupt the data pool
    new_sim.pop_masked_states()
    
    with pytest.raises(ValueError):
    
        check_integrity(pool, [new_sim])
    
    current_state = controller._merge_active_states(new_sim)
    
    assert current_state.count() == 3
    assert new_sim.count_states() == 1
    
def test_nullify_data(catalog, loader, controller):
    
    '''Test adding data to a data state from a chosen interface.'''
    
    pool = DataPool()

    test_variable = 'demo:demo:table'
    test_inputs = {'demo:demo:low': 0,
                   'demo:demo:high': 1,
                   'demo:demo:rows': 5}

    new_sim = Simulation("Hello World!")
    controller.create_new_hub(new_sim, "DemoInterface", "demo_hub")
                                                  
    controller.sequence_interface(new_sim,
                                  "demo_hub",
                                  "Spreadsheet Generator")

    f_interface = controller.get_interface_obj(new_sim,
                                               "demo_hub",
                                               "Spreadsheet Generator")

    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)
                             
    assert check_integrity(pool, [new_sim])
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [False])
                             
    assert check_integrity(pool, [new_sim])
                                      
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             ['trigger.bool'],
                             [True])
                             
    assert check_integrity(pool, [new_sim])
                                      
    f_interface = loader.load_interface(pool,
                                        new_sim,
                                        f_interface)

    # Get the raw data from the interface
    f_interface.connect()
    raw_data = f_interface.get_data(test_variable)
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                             
    assert check_integrity(pool, [new_sim])

    current_state = controller._merge_active_states(new_sim)

    assert current_state.count() == 5
    
    # Hide the trigger.bool variable and test removing from the pool.
    controller.add_datastate(pool,
                             new_sim, 
                             "executed",
                             catalog, 
                             ['trigger.bool',
                              'trigger.bool',
                              'trigger.bool'],
                             [None,
                              True,
                              None])
                                                  
    assert check_integrity(pool, [new_sim])
                                      
    current_state = controller._merge_active_states(new_sim)

    assert len(current_state) == 4


