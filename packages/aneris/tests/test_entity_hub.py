# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import pytest

from aneris.control.pipeline import Sequencer

from . import interface_plugins as interfaces

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def sequencer():

    sequencer = Sequencer(["DummyInterface"],
                          interfaces)

    return sequencer

def test_undo(sequencer):

    '''Test adding data to a data state from a chosen interface.'''
    
    pipeline = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(pipeline, "Early Interface")
    sequencer.sequence(pipeline, "Later Interface")
    
    pipeline.set_completed('EarlyInterface')

    assert pipeline.is_completed('EarlyInterface')
    
    pipeline.undo()
    
    assert not pipeline.is_completed('EarlyInterface')
    
def test_rollback(sequencer):

    '''Test adding data to a data state from a chosen interface.'''
    
    pipeline = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(pipeline, "Early Interface")
    sequencer.sequence(pipeline, "Later Interface")
    
    pipeline.set_completed('EarlyInterface')
    pipeline.set_completed('LaterInterface')

    assert pipeline.is_completed('LaterInterface')
    
    pipeline.rollback('EarlyInterface')
    
    assert not pipeline.is_completed('EarlyInterface')

