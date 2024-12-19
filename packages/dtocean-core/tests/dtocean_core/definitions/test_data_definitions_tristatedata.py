
# pylint: disable=protected-access

import pytest

from dtocean_core.core import Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import TriStateData


def test_TriStateData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures
    
    assert "SimpleData" in all_objs.keys()


@pytest.mark.parametrize("raw", ["true", "false", "unknown"])
def test_TriStateData(raw):
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"
                         })
    
    test = TriStateData()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b == raw


def test_TriStateData_bad_input():
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"
                         })
    
    test = TriStateData()
    
    with pytest.raises(ValueError):
        test.get_data("bad", meta)


def test_TriStateData_get_value_None():
    
    test = TriStateData()
    result = test.get_value(None)
    
    assert result is None


@pytest.mark.parametrize("left, right", [("true", "true"),
                                         ("false", "false"),
                                         ("unknown", "unknown")])
def test_SimpleData_equals(left, right):
    
    assert TriStateData.equals(left, right)


@pytest.mark.parametrize("left, right", [("true", "false"),
                                         ("false", "true"),
                                         ("unknown", "true"),
                                         ("unknown", "false")])
def test_SimpleData_not_equals(left, right):
    
    assert not TriStateData.equals(left, right)
