# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import pytest

import os

from mdo_engine.control.pipeline import Sequencer
from mdo_engine.entity import Hub

from . import interface_plugins as interfaces

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def sequencer():
    
    try:
        sequencer = Sequencer(["DummyInterface"],
                              interfaces)
    except ModuleNotFoundError as e:
        if "dtocean_dummy" in str(e):
            pytest.skip("dtocean-dummy-module not installed")

    return sequencer

def test_create_new_hub(sequencer):
    
    hub = sequencer.create_new_hub("DummyInterface")

    assert isinstance(hub, Hub)

def test_sequence(sequencer):
    
    hub = sequencer.create_new_hub("DummyInterface")
    
    sequencer.sequence(hub, "Early Interface")

    assert 'EarlyInterface' in hub._scheduled_interface_map.keys()
    assert list(hub._scheduled_interface_map.keys()).index('EarlyInterface') == 0
    
def test_complete(sequencer):
    
    hub = sequencer.create_new_hub("DummyInterface")
    
    sequencer.sequence(hub, "Early Interface")
    sequencer.sequence(hub, "Later Interface")
    sequencer.complete(hub, "Early Interface")
    
    assert 'EarlyInterface' in hub._completed_interface_map.keys()
    assert list(hub._scheduled_interface_map.keys()).index('LaterInterface') == 0
                                            
                                            
def test_refresh(sequencer):
    
    hub = sequencer.create_new_hub("DummyInterface")
    
    sequencer.sequence(hub, "Early Interface")
    sequencer.sequence(hub, "Later Interface")
    sequencer.complete(hub, "Early Interface")
    
    next_interface = hub.get_next_scheduled()
    before_object = hub.get_interface_obj(next_interface)
    before_id = hex(id(before_object))
    
    sequencer.refresh_interfaces(hub)
    
    after_object = hub.get_interface_obj(next_interface)
    after_id = hex(id(after_object))
    
    assert before_id != after_id
    
def test_get_next_scheduled_none(sequencer):
    
    hub = sequencer.create_new_hub("DummyInterface")
    next_interface = hub.get_next_scheduled()
    
    assert next_interface is None
