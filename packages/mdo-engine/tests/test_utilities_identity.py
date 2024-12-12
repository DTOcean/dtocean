# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

from mdo_engine.utilities.identity import get_unique_id, id_generator


def test_id_generator():
    id_length = 8

    test_id = id_generator(id_length)

    assert test_id.isalnum()
    assert len(test_id) == id_length


def test_get_unique_id():
    """Test getting a unique id"""

    new_id = get_unique_id(None)

    assert isinstance(new_id, str)
