# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

# pylint: disable=redefined-outer-name,protected-access

import os
import shutil
import pickle
from copy import deepcopy

import pytest

from aneris.boundary.data import SerialBox
from aneris.control.simulation import Controller, _copy_all_sim_states
from aneris.control.pipeline import Sequencer
from aneris.control.data import DataValidation, DataStorage
from aneris.control.sockets import NamedSocket
from aneris.entity import Simulation
from aneris.entity.data import Data, DataCatalog, DataPool, DataState
from aneris.utilities.data import check_integrity

import aneris.test.interfaces as interfaces
import aneris.test.data as data_plugins


@pytest.fixture(scope="module")
def controller():
    
    data_store = DataStorage(data_plugins)
    sequencer = Sequencer(["SPTInterface"],
                          interfaces)
    control = Controller(data_store, sequencer)
    
    return control

def test_has_data(controller):
    
    '''Test for existing variable in a data state'''
    
    test_var = 'site:wave:dir'
    
    new_sim = Simulation("Hello World!")
    result = controller.has_data(new_sim, test_var)
    
    assert result == False

def test_add_datastate(controller):
    
    '''Test adding data to a data state from a chosen interface.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    series = controller.get_data_value(pool,
                                       new_sim,
                                       'site:wave:dir')
                                       
    pseudo_state = controller._merge_active_states(new_sim)

    assert check_integrity(pool, [new_sim])
    assert pseudo_state.count() == 1
    assert len(series) == 64
    
    
def test_add_datastate_obj(controller):
    
    '''Test adding data to a data state using existing Data objects.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    pre_pool_length = len(pool)
    
    # Get the data objects from the first datastate and create a new datastate
    # with them.
    test_state = new_sim._active_states[-1]
    
    var_objs = []
    
    for var_id in test_state.get_identifiers():
        
        data_index = test_state.get_index(var_id)
        data_obj = pool.get(data_index)
        var_objs.append(data_obj)
        
    controller.add_datastate(pool,
                             new_sim,
                             data_catalog=catalog,
                             identifiers=test_state.get_identifiers(),
                             values=var_objs,
                             use_objects=True)
                                       
    pseudo_state = controller._merge_active_states(new_sim)
    
    series = controller.get_data_value(pool,
                                       new_sim,
                                       'site:wave:dir')
    
    assert len(pool) == 2 * pre_pool_length
    assert check_integrity(pool, [new_sim])
    assert pseudo_state.count() == 1
    assert len(series) == 64


def test_copy_simulation(controller):
    
    '''Test copying a simulation.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])

                                       
    assert check_integrity(pool, [new_sim])    
    
    copy_sim = controller.copy_simulation(pool,
                                          new_sim,
                                          "Fork Off!")
                                                    
    new_levels = new_sim.get_all_levels()
    copy_levels = copy_sim.get_all_levels()
    
    assert copy_sim.get_title() == "Fork Off!"
    assert new_levels == copy_levels
    assert check_integrity(pool, [new_sim, copy_sim])
    
    series = controller.get_data_value(pool,
                                       copy_sim,
                                       'site:wave:dir')
                                       
    assert len(series) == 64


def test_import_simulation_from_clone(controller):
    
    '''Test importing a simulation from a cloned pool'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    
    assert check_integrity(pool, [new_sim])
    
    # Clone the pool
    src_pool = deepcopy(pool)
    
    assert check_integrity(src_pool, [new_sim])
    
    copy_sim = controller.import_simulation(src_pool,
                                            pool,
                                            new_sim,
                                            "Fork Off!")
    
    new_levels = new_sim.get_all_levels()
    copy_levels = copy_sim.get_all_levels()
    
    assert copy_sim.get_title() == "Fork Off!"
    assert new_levels == copy_levels
    assert check_integrity(pool, [new_sim, copy_sim])
    assert len(pool) == 1


def test_import_simulation_from_new(controller):
    
    '''Test importing a simulation from a new pool'''
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    pool = DataPool()
    new_sim = Simulation("Hello World!")
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    
    assert check_integrity(pool, [new_sim])
    
    # Create a new pool
    src_pool = DataPool()
    src_sim = Simulation("Goodbye World!")
    
    controller.add_datastate(src_pool,
                             src_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    assert check_integrity(src_pool, [src_sim])
    
    copy_sim = controller.import_simulation(src_pool,
                                            pool,
                                            src_sim,
                                            "Fork Off!")
    
    new_levels = src_sim.get_all_levels()
    copy_levels = copy_sim.get_all_levels()
    
    assert copy_sim.get_title() == "Fork Off!"
    assert new_levels == copy_levels
    assert check_integrity(pool, [new_sim, copy_sim])
    assert len(pool) == 2


def test_remove_simulation(controller):
    
    '''Test removing a simulation.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    assert check_integrity(pool, [new_sim])
    
    # Create a new pool
    src_pool = DataPool()
    src_sim = Simulation("Goodbye World!")
    
    assert src_sim.count_states() == 0
    
    controller.add_datastate(src_pool,
                             src_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    assert src_sim.count_states() == 1
    
    assert check_integrity(src_pool, [src_sim])
    
    copy_sim = controller.import_simulation(src_pool,
                                            pool,
                                            src_sim,
                                            "Fork Off!")
    
    new_levels = src_sim.get_all_levels()
    copy_levels = copy_sim.get_all_levels()
    
    assert copy_sim.get_title() == "Fork Off!"
    assert copy_sim.count_states() == 1
    assert new_levels == copy_levels
    assert check_integrity(pool, [new_sim, copy_sim])
    assert len(pool) == 2
    
    controller.remove_simulation(pool,
                                 copy_sim)
    
    assert check_integrity(pool, [new_sim])
    assert len(pool) == 1
    assert copy_sim.count_states() == 0


def test_convert_state_to_box(controller, tmpdir):
    
    '''Test saving a datastate.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    test_state = new_sim._active_states[-1]
    state_box = controller._convert_state_to_box(test_state,
                                                 "test",
                                                 str(tmpdir))
    
    assert isinstance(state_box, SerialBox)

    data_path = state_box.load_dict["file_path"]

    assert os.path.isfile(data_path)
    
def test_convert_box_to_state(controller, tmpdir):
    
    '''Test loading a datastate.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    test_state = new_sim._active_states[-1]
    state_box = controller._convert_state_to_box(test_state,
                                                 "test",
                                                 str(tmpdir))
    
    assert isinstance(state_box, SerialBox)

    loaded_state = controller._convert_box_to_state(state_box)
    
    data_index = loaded_state.get_index('site:wave:dir')
    new_data = pool.get(data_index)
    
    assert isinstance(new_data, Data)
    
def test_serialise_states(controller, tmpdir):
    
    '''Test saving a datastate.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    controller.serialise_states(new_sim, str(tmpdir))
    state_box = new_sim._active_states[0]
    
    assert isinstance(state_box, SerialBox)

    data_path = state_box.load_dict["file_path"]

    assert os.path.isfile(data_path)
    
def test_deserialise_states(controller, tmpdir):
    
    '''Test saving a datastate.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    controller.serialise_states(new_sim, str(tmpdir))
    state_box = new_sim._active_states[0]
    
    assert isinstance(state_box, SerialBox)

    controller.deserialise_states(new_sim)
    loaded_state = new_sim._active_states[0]

    assert isinstance(loaded_state, DataState)
    
    data_index = loaded_state.get_index('site:wave:dir')
    new_data = pool.get(data_index)
    
    assert isinstance(new_data, Data)
        
def test_save_simulation(controller, tmpdir):
    
    '''Test pickling a simulation.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])

                                       
    assert check_integrity(pool, [new_sim])
    
    controller.serialise_states(new_sim, str(tmpdir))
    
    test_path = os.path.join(str(tmpdir), "simulation.pkl")
    pickle.dump(new_sim, open(test_path, "wb"), -1)
    
    assert os.path.isfile(test_path)

def test_load_simulation(controller, tmpdir):
    
    '''Test pickling and unpickling a simulation.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])

    new_levels = new_sim.get_all_levels()
    
    controller.serialise_states(new_sim, str(tmpdir))
    
    test_path = os.path.join(str(tmpdir), "simulation.pkl")
    pickle.dump(new_sim, open(test_path, "wb"), -1)
    
    assert os.path.isfile(test_path)
    
    loaded_sim = pickle.load(open(test_path, "rb"))
    controller.deserialise_states(loaded_sim)
    
    assert check_integrity(pool, [loaded_sim])
                                                    
    loaded_levels = loaded_sim.get_all_levels()
    
    assert loaded_sim.get_title() == "Hello World!"
    assert new_levels == loaded_levels
    
def test_convert_state_to_box_root(controller, tmpdir):
    
    '''Test saving a datastate with a root directory.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    test_state = new_sim._active_states[-1]
    state_box = controller._convert_state_to_box(test_state,
                                                 "test",
                                                 str(tmpdir),
                                                 str(tmpdir))
    
    assert isinstance(state_box, SerialBox)

    data_path = os.path.join(str(tmpdir), state_box.load_dict["file_path"])

    assert os.path.isfile(data_path)
    
def test_convert_box_to_state_root(controller, tmpdir):
    
    '''Test loading a datastate with a root directory.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    test_state = new_sim._active_states[-1]
    state_box = controller._convert_state_to_box(test_state,
                                                 "test",
                                                 str(tmpdir),
                                                 str(tmpdir))
    
    assert isinstance(state_box, SerialBox)

    loaded_state = controller._convert_box_to_state(state_box,
                                                    str(tmpdir))
    
    data_index = loaded_state.get_index('site:wave:dir')
    new_data = pool.get(data_index)
    
    assert isinstance(new_data, Data)
    
def test_serialise_states_root(controller, tmpdir):
    
    '''Test saving a datastate with a root directory.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    controller.serialise_states(new_sim, str(tmpdir), str(tmpdir))
    state_box = new_sim._active_states[0]
    
    assert isinstance(state_box, SerialBox)

    data_path = os.path.join(str(tmpdir), state_box.load_dict["file_path"])

    assert os.path.isfile(data_path)
    
def test_deserialise_states_root(controller, tmpdir):
    
    '''Test saving a datastate with a root directory.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])
    
    controller.serialise_states(new_sim, str(tmpdir), str(tmpdir))
    state_box = new_sim._active_states[0]
    
    assert isinstance(state_box, SerialBox)

    controller.deserialise_states(new_sim, str(tmpdir))
    loaded_state = new_sim._active_states[0]

    assert isinstance(loaded_state, DataState)
    
    data_index = loaded_state.get_index('site:wave:dir')
    new_data = pool.get(data_index)
    
    assert isinstance(new_data, Data)

def test_load_simulation_root(controller, tmpdir):
    
    '''Test pickling and unpickling a simulation with a root directory.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
                                       
    assert check_integrity(pool, [new_sim])

    new_levels = new_sim.get_all_levels()
    
    controller.serialise_states(new_sim, str(tmpdir), str(tmpdir))
    
    test_path = os.path.join(str(tmpdir), "simulation.pkl")
    pickle.dump(new_sim, open(test_path, "wb"), -1)
    
    assert os.path.isfile(test_path)
    
    new_root = os.path.join(str(tmpdir), "test")
#    os.makedirs(new_root)
    move_path = os.path.join(str(tmpdir), "test", "simulation.pkl")
    shutil.copytree(str(tmpdir), new_root)
    
    loaded_sim = pickle.load(open(move_path, "rb"))
    controller.deserialise_states(loaded_sim, new_root)
    
    assert check_integrity(pool, [loaded_sim])
                                                    
    loaded_levels = loaded_sim.get_all_levels()
    
    assert loaded_sim.get_title() == "Hello World!"
    assert new_levels == loaded_levels


def test_copy_all_sim_states(controller):
    
    '''Test copying a simulation.'''
    
    pool = DataPool()
    
    test_interface = 'SPTInterface'
    test_variable = 'site:wave:dir'
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,
                             'data',
                             'test_spectrum_30min.spt'
                             )
    
    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)
    file_interface.set_file_path(test_path)
    
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    # Get the raw data from the interface
    file_interface.connect()
    raw_data = file_interface.get_data(test_variable)
    
    new_sim = Simulation("Hello World!")
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             [test_variable],
                             [raw_data])
    
    old_states = new_sim._active_states[:]
    old_states.extend(list(reversed(new_sim._redo_states[:])))
    
    copy_states = _copy_all_sim_states(new_sim)
    
    for old_state, copy_state in zip(old_states, copy_states):
        
        assert set(old_state.get_identifiers()) == \
                                        set(copy_state.get_identifiers())
        assert old_state != copy_state


def test_make_compact_state_same_var(controller):
    
    pool = DataPool()
    
    test_variable = 'site:wave:dir'
    
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    new_sim = Simulation("Hello World!")
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [test_variable],
                             [[1]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [test_variable],
                             [[2]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [test_variable],
                             [[3]])
    
    last_state = new_sim._active_states[-1]
    
    all_states = new_sim.mirror_active_states()
    
    test = controller._make_compact_state(all_states)
    
    assert len(test) == 1
    assert test.get_index(test_variable) == last_state.get_index(test_variable)


def test_make_compact_multi_vars(controller):
    
    pool = DataPool()
    
    var1 = 'site:wave:dir'
    var2 = 'site:wave:PSD1D'
    
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    new_sim = Simulation("Hello World!")
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[1]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var2],
                             [[2]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[3]])
    
    last_state = new_sim._active_states[-1]
    
    all_states = new_sim.mirror_active_states()
    
    test = controller._make_compact_state(all_states)
    
    assert len(test) == 2
    assert test.get_index(var1) == last_state.get_index(var1)


def test_compact_none_states(controller):
    
    pool = DataPool()
    
    var1 = 'site:wave:dir'
    
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    new_sim = Simulation("Hello World!")
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[1]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[2]])
    
    controller.add_datastate(pool,
                             new_sim,
                             "level1",
                             catalog,
                             [var1],
                             [[3]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[1]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[2]])
    
    controller.add_datastate(pool,
                             new_sim,
                             "level2",
                             catalog,
                             [var1],
                             [[3]])
    
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[1]])
    
    controller.add_datastate(pool,
                             new_sim,
                             None,
                             catalog,
                             [var1],
                             [[2]])
    
    all_states = new_sim.mirror_active_states()
    
    test = controller._compact_none_states(all_states)
    all_levels = [x.get_level() for x in test]
    
    assert len(test) == 5
    assert all_levels == [None, "level1", None, "level2", None]
