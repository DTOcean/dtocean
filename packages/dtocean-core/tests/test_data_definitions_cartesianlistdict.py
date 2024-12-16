
import pytest
import numpy as np

from mdo_engine.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import (CartesianListDict,
                                           CartesianListDictColumn)


def test_CartesianListDict_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianListDict" in all_objs.keys()


def test_CartesianListDict():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "types": ["str"]})
    
    test = CartesianListDict()
    
    raw = {"a": [(0, 1), (1, 2)],
           "b": [(3, 4), (4, 5)],
           1: [(6, 7), (7, 8)]}
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert len(b) == 3
    assert b["a"][0][0] == 0
    assert b["a"][0][1] == 1
    assert "1" in b
            
    raw = {"a": [(0, 1, -1), (1, 2, -2)], "b": [(3, 4, -3), (4, 5, -5)]}
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert len(b) == 2
    assert b["a"][0][0] == 0
    assert b["a"][0][1] == 1 
    assert b["a"][0][2] == -1
            
    raw = {"a": [(0, 1, -1, 1)]}
    
    with pytest.raises(ValueError):
        test.get_data(raw, meta)


def test_get_None():
    
    test = CartesianListDict()
    result = test.get_value(None)
    
    assert result is None


def test_CartesianListDict_equals():
    
    left = {"a": np.array([(0, 1, -1), (1, 2, -2)]),
            "b": np.array([(3, 4, -3), (4, 5, -5)])}
    right = {"a": np.array([(0, 1, -1), (1, 2, -2)]),
             "b": np.array([(3, 4, -3), (4, 5, -5)])}
    
    assert CartesianListDict.equals(left, right)


def test_CartesianListDict_not_equal_values():
    
    left = {"a": np.array([(0, 1, -1), (1, 2, -2)]),
            "b": np.array([(3, 4, -3), (4, 5, -5)])}
    right = {"a": np.array([(0, 1, -1), (1, 2, -2)]),
             "b": np.array([(3, 4, -3), (4, 1, -5)])}
    
    assert not CartesianListDict.equals(left, right)


def test_CartesianListDict_not_equal_keys():
    
    left = {"a": np.array([(0, 1, -1), (1, 2, -2)]),
            "b": np.array([(3, 4, -3), (4, 5, -5)])}
    right = {"a": np.array([(0, 1, -1), (1, 2, -2)]),
             "d": np.array([(3, 4, -3), (4, 5, -5)])}
    
    assert not CartesianListDict.equals(left, right)


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_CartesianListDict_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raws = [{"a": [(0, 1), (1, 2)], "b": [(3, 4), (4, 5)]},
            {"a": [(0, 1, -1), (1, 2, -2)], "b": [(3, 4, -3), (4, 5, -5)]}]
    
    for raw in raws:
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test"})
    
        test = CartesianListDict()
        
        fout_factory = InterfaceFactory(AutoFileOutput)
        FOutCls = fout_factory(meta, test)
        
        fout = FOutCls()
        fout._path = test_path_str
        fout.data.result = test.get_data(raw, meta)
    
        fout.connect()
        
        assert len(tmpdir.listdir()) == 1
                  
        fin_factory = InterfaceFactory(AutoFileInput)
        FInCls = fin_factory(meta, test)
                  
        fin = FInCls()
        fin._path = test_path_str
        
        fin.connect()
        result = test.get_data(fin.data.result, meta)
        
        assert len(result) == 2
        assert result["a"][0][0] == 0
        assert result["a"][0][1] == 1


def test_CartesianListDictColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianListDictColumn" in all_objs.keys()
    

def test_CartesianListDictColumn_auto_db(mocker):
    
    raws = [{"a": [(0, 1), (1, 2)], "b": [(3, 4), (4, 5)]},
            {"a": [(0, 1, -1), (1, 2, -2)], "b": [(3, 4, -3), (4, 5, -5)]}]
    
    for raw in raws:

        mock_lists = [raw.keys(), raw.values()]
        
        mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                     return_value=mock_lists,
                     autospec=True)
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test",
                             "tables": ["mock.mock", "name", "position"]})
        
        test = CartesianListDictColumn()
        
        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)
        
        query = QueryCls()
        query.meta.result = meta
        
        query.connect()
        result = test.get_data(query.data.result, meta)
        
        assert len(result) == 2
        assert result["a"][0][0] == 0
        assert result["a"][0][1] == 1


def test_CartesianListDictColumn_auto_db_empty(mocker):
    
    mock_lists = [[], []]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})

    test = CartesianListDictColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_CartesianListDictColumn_auto_db_none(mocker):
    
    mock_lists = [[None, None], [None, None]]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})
    
    test = CartesianListDictColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None

