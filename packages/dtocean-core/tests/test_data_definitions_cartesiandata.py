import pytest

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import CartesianData, CartesianDataColumn


def test_CartesianData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianData" in all_objs.keys()


def test_CartesianData():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = CartesianData()
    
    raw = (0, 1)
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b[0] == 0
    assert b[1] == 1
            
    raw = (0, 1, -1)
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b[0] == 0
    assert b[1] == 1 
    assert b[2] == -1
            
    raw = (0, 1, -1, 1)
    
    with pytest.raises(ValueError):
        test.get_data(raw, meta)
        
        
def test_get_None():
    
    test = CartesianData()
    result = test.get_value(None)
    
    assert result is None
    

@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_CartesianData_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raws = [(0, 1), (0, 1, -1)]
    
    for raw in raws:
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test"})
    
        test = CartesianData()
        
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
        
        assert result[0] == 0
        assert result[1] == 1


def test_CartesianDataColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianDataColumn" in all_objs.keys()
    

def test_CartesianDataColumn_auto_db(mocker):
    
    raws = [(0, 1), (0, 1, -1)]
    
    for raw in raws:

        mock_list = [raw]
        
        mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                     return_value=mock_list,
                     autospec=True)
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test",
                             "tables": ["mock.mock", "position"]})
        
        test = CartesianDataColumn()
        
        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)
        
        query = QueryCls()
        query.meta.result = meta
        
        query.connect()
        result = test.get_data(query.data.result, meta)
            
        assert result[0] == 0
        assert result[1] == 1


def test_CartesianDataColumn_auto_db_empty(mocker):
    
    mock_list = None
        
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})

    test = CartesianDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_CartesianDataColumn_auto_db_none(mocker):
    
    mock_list = [None]
        
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})
    
    test = CartesianDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None

