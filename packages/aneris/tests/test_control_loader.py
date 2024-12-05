# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import pytest

from aneris.entity import Simulation
from aneris.entity.data import DataCatalog, DataPool
from aneris.control.pipeline import Sequencer
from aneris.control.simulation import Loader, Controller
from aneris.control.data import DataStorage, DataValidation

from . import data_plugins as data_plugins
from . import interface_plugins as interfaces
from .data_plugins.definitions import UnitData


@pytest.fixture(scope="module")
def loader():
    
    data_store = DataStorage(data_plugins)
    loader = Loader(data_store)
    
    return loader


@pytest.fixture(scope="module")
def controller():
    
    data_store = DataStorage(data_plugins)
    
    try:
        sequencer = Sequencer(["DummyInterface"],
                              interfaces)
    except ModuleNotFoundError as e:
        if "dtocean_dummy" in str(e):
            pytest.skip("dtocean-dummy-module not installed")
    
    control = Controller(data_store, sequencer)
    
    return control


@pytest.fixture(scope="module")
def catalog():

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    return catalog


def test_init_loader(loader):
    
    assert isinstance(loader, Loader)


def test_get_structure(loader):
    
    unitdata = loader.get_structure("UnitData")
    
    assert isinstance(unitdata, UnitData)


def test_has_data(loader):
    
    '''Test for existing variable in a data state'''
    
    test_var = 'site:wave:dir'
    
    new_sim = Simulation("Hello World!")
    result = loader.has_data(new_sim, test_var)
    
    assert result == False
    
    
def test_get_data_value(loader, controller, catalog):
    
    pool = DataPool()
    new_sim = Simulation("Hello World!")
    
    controller.add_datastate(pool,
                             new_sim,
                             "executed",
                             catalog,
                             ["Technology:Common:DeviceType"],
                             ["Tidal"])
    
    new_data_value = loader.get_data_value(pool,
                                           new_sim,
                                           "Technology:Common:DeviceType")

    assert new_data_value == "Tidal"


def test_create_merged_state_none(loader):
    
    new_sim = Simulation("Hello World!")
    result = loader.create_merged_state(new_sim)
    
    assert result is None
    
    
def test_create_merged_state(loader, controller, catalog):
    
    pool = DataPool()
    new_sim = Simulation("Hello World!")
    
    test_inputs = {'demo:demo:high': 2,
                   'demo:demo:rows': 5}
                                               
    controller.add_datastate(pool,
                             new_sim,
                             "input1",
                             catalog,
                             test_inputs.keys(),
                             test_inputs.values())
    
    controller.add_datastate(pool,
                             new_sim,
                             "input2",
                             catalog,
                             ['demo:demo:low'],
                             [1])
    
    new_sim.set_merged_state(None)
    
    result = loader.create_merged_state(new_sim)
    
    assert len(result) == 3


def test_create_merged_state_existing(loader, controller, catalog):

    pool = DataPool()
    new_sim = Simulation("Hello World!")
    
    test_inputs = {'demo:demo:high': 2,
                   'demo:demo:rows': 5}
                                               
    controller.add_datastate(pool,
                             new_sim,
                             "input1",
                             catalog,
                             test_inputs.keys(),
                             test_inputs.values())
    
    controller.add_datastate(pool,
                             new_sim,
                             "input2",
                             catalog,
                             ['demo:demo:low'],
                             [1])
    
    existing = new_sim.get_merged_state()
    
    result = loader.create_merged_state(new_sim)
    
    assert result == existing
    
    
def test_create_merged_state_not_existing(loader, controller, catalog):

    pool = DataPool()
    new_sim = Simulation("Hello World!")
    
    test_inputs = {'demo:demo:high': 2,
                   'demo:demo:rows': 5}
                                               
    controller.add_datastate(pool,
                             new_sim,
                             "input1",
                             catalog,
                             test_inputs.keys(),
                             test_inputs.values())
    
    controller.add_datastate(pool,
                             new_sim,
                             "input2",
                             catalog,
                             ['demo:demo:low'],
                             [1])
    
    existing = new_sim.get_merged_state()
    
    result = loader.create_merged_state(new_sim, use_existing=False)
    
    assert existing != result

