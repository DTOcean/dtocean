# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import pytest

dtocean_dummy = pytest.importorskip("dtocean_dummy")

from aneris.entity import Simulation
from aneris.entity.data import DataCatalog, DataPool
from aneris.control.pipeline import Sequencer
from aneris.control.simulation import Loader, Controller
from aneris.control.sockets import NamedSocket
from aneris.control.data import DataStorage, DataValidation

from . import data_plugins as data_plugins
from . import interface_plugins as interfaces


@pytest.fixture(scope="module")
def loader():
    
    data_store = DataStorage(data_plugins)
    loader = Loader(data_store)
    
    return loader


@pytest.fixture(scope="module")
def controller():
    
    data_store = DataStorage(data_plugins)
    sequencer = Sequencer(["DummyInterface"],
                          interfaces)
    control = Controller(data_store, sequencer)  
    
    return control


@pytest.fixture(scope="module")
def catalog():

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data_plugins.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog,
                                                    data_plugins)
    
    return catalog


@pytest.fixture(scope="module")
def interface():

    interfacer = NamedSocket("DemoInterface")
    interfacer.discover_interfaces(interfaces)
    interface = interfacer.get_interface_object("TableInterface")
    
    return interface
    
    
def test_can_load_false(loader, interface):
    
    pool = DataPool()
    new_sim = Simulation("Hello World!")
    
    result = loader.can_load(pool,
                             new_sim,
                             interface)
    
    assert not result
    
    
def test_can_load_true(loader, controller, catalog, interface):
    
    pool = DataPool()
    new_sim = Simulation("Hello World!")

    test_inputs = {'demo:demo:low': 1,
                   'demo:demo:high': 2,
                   'demo:demo:rows': 5}
                                               
    data_indentities = test_inputs.keys()
    data_values = test_inputs.values()
    
    controller.add_datastate(pool,
                             new_sim,
                             "input",
                             catalog,
                             data_indentities,
                             data_values)
    
    result = loader.can_load(pool,
                             new_sim,
                             interface)
    
    assert result
