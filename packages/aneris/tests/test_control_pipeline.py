# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import pytest

from aneris.control.pipeline import Sequencer
from aneris.entity import Pipeline

from . import interface_plugins as interfaces

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def sequencer():

    sequencer = Sequencer(["DummyInterface"],
                          interfaces)

    return sequencer

def test_create_new_pipeline(sequencer):
    
    pipeline = sequencer.create_new_pipeline("DummyInterface")

    assert type(pipeline) == Pipeline
    
def test_sequence(sequencer):
    
    pipeline = sequencer.create_new_pipeline("DummyInterface")
    
    sequencer.sequence(pipeline, "Early Interface")

    assert 'EarlyInterface' in pipeline._scheduled_interface_map.keys()
    assert sequencer.get_next_name(pipeline) == "Early Interface"
    
def test_complete(sequencer):
    
    pipeline = sequencer.create_new_pipeline("DummyInterface")
    
    sequencer.sequence(pipeline, "Early Interface")
    sequencer.sequence(pipeline, "Later Interface")
    sequencer.complete(pipeline, "Early Interface")
    
    assert sequencer.get_next_name(pipeline) == 'Later Interface'

