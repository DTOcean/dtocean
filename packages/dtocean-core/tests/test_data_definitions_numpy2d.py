
import numpy as np
import pandas as pd

from mdo_engine.control.factory import InterfaceFactory
from dtocean_core.core import (AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Numpy2D, Numpy2DColumn


def test_Numpy2D_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "Numpy2D" in all_objs.keys()


def test_Numpy2D():
    
    raw = np.random.rand(10, 8)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x"]})
    
    test = Numpy2D()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b.shape == (10, 8)
    assert np.isclose(b, raw).all()
    
    
def test_get_None():
    
    test = Numpy2D()
    result = test.get_value(None)
    
    assert result is None


def test_Numpy2DColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "Numpy2DColumn" in all_objs.keys()
    

def test_Numpy2DColumn_auto_db(mocker):
    
    raw = np.random.rand(3, 2)
    
    XX, YY = np.meshgrid(np.arange(raw.shape[0]),
                         np.arange(raw.shape[1]),
                         indexing='ij')
    
    mock_dict = {"i": XX.ravel(),
                 "j": YY.ravel(),
                 "x": raw.ravel()}
    mock_df = pd.DataFrame(mock_dict)

    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x"],
                         "tables": ["mock.mock", "i", "j", "x"]})

    test = Numpy2DColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
    result = test.get_data(query.data.result, meta)
            
    assert result.shape == (3, 2)
    assert np.isclose(result, raw).all()


def test_Numpy2DColumn_auto_db_empty(mocker):
    
    mock_dict = {"i": [],
                 "j": [],
                 "x": []}
    mock_df = pd.DataFrame(mock_dict)

    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x"],
                         "tables": ["mock.mock", "i", "j", "x"]})

    test = Numpy2DColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_Numpy2DColumn_auto_db_none(mocker):
    
    mock_dict = {"i": [None] * 6,
                 "j": [None] * 6,
                 "x": np.random.rand(6)}
    mock_df = pd.DataFrame(mock_dict)

    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x"],
                         "tables": ["mock.mock", "i", "j", "x"]})

    test = Numpy2DColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None
