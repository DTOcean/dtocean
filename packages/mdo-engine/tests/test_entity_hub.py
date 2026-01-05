# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import pytest

from mdo_engine.control.pipeline import Sequencer

from . import interface_plugins as interfaces


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def sequencer():
    try:
        sequencer = Sequencer(["DummyInterface"], [interfaces])
    except ModuleNotFoundError as e:
        if "dtocean_dummy" in str(e):
            pytest.skip("dtocean-dummy-module not installed")

    return sequencer


def test_undo(sequencer):
    """Test adding data to a data state from a chosen interface."""

    pipeline = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(pipeline, "Early Interface")
    sequencer.sequence(pipeline, "Later Interface")

    pipeline.set_completed("EarlyInterface")

    assert pipeline.is_completed("EarlyInterface")

    pipeline.undo()

    assert not pipeline.is_completed("EarlyInterface")


def test_rollback(sequencer):
    """Test adding data to a data state from a chosen interface."""

    pipeline = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(pipeline, "Early Interface")
    sequencer.sequence(pipeline, "Later Interface")

    pipeline.set_completed("EarlyInterface")
    pipeline.set_completed("LaterInterface")

    assert pipeline.is_completed("LaterInterface")

    pipeline.rollback("EarlyInterface")

    assert not pipeline.is_completed("EarlyInterface")


def test_pipeline_equality(sequencer):
    pipeline = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(pipeline, "Early Interface")
    sequencer.sequence(pipeline, "Later Interface")
    pipeline.set_completed("EarlyInterface")

    other = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(other, "Early Interface")
    sequencer.sequence(other, "Later Interface")
    other.set_completed("EarlyInterface")

    assert pipeline is not other
    assert pipeline == other


def test_hub_equality(sequencer):
    hub = sequencer.create_new_hub("DummyInterface")
    sequencer.sequence(hub, "Early Interface")
    sequencer.sequence(hub, "Later Interface")
    hub.set_completed("EarlyInterface")

    other = sequencer.create_new_hub("DummyInterface")
    sequencer.sequence(other, "Early Interface")
    sequencer.sequence(other, "Later Interface")
    other.set_completed("EarlyInterface")

    assert hub is not other
    assert hub == other


def test_hub_pipeline_inequality(sequencer):
    pipeline = sequencer.create_new_pipeline("DummyInterface")
    hub = sequencer.create_new_hub("DummyInterface")
    assert pipeline != hub


def test_pipeline_inequality(sequencer):
    pipeline = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(pipeline, "Early Interface")
    sequencer.sequence(pipeline, "Later Interface")
    pipeline.set_completed("EarlyInterface")

    other = sequencer.create_new_pipeline("DummyInterface")
    sequencer.sequence(other, "Early Interface")
    sequencer.sequence(other, "Later Interface")

    assert pipeline != other
