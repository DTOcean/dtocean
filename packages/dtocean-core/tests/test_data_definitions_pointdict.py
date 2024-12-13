import pytest

import matplotlib.pyplot as plt
from geoalchemy2.elements import WKTElement

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import PointDict, PointDictColumn


def test_PointDict_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PointDict" in all_objs.keys()


def test_PointDict():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PointDict()
    
    raw = {"one"   : (0., 0.),
           "two"   : (1., 1.),
           "three" : (2., 2.)
           }

    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b["one"].x == 0.
    assert b["two"].y == 1.
            
    raw = {"one"   : (0., 0., 0.),
           "two"   : (1., 1., 1.),
           "three" : (2., 2., 2.)
           }

    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b["one"].x == 0.
    assert b["two"].y == 1.
    assert b["three"].z == 2.
            
    raw = {"one"   : (0., 0., 0., 0.),
           "two"   : (1., 1., 1., 1.),
           "three" : (2., 2., 2., 2.)
           }
    
    with pytest.raises(ValueError):
        test.get_data(raw, meta)
        
        
def test_get_None():
    
    test = PointDict()
    result = test.get_value(None)
    
    assert result is None
    

@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_PointDict_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raws = [{"one"   : (0., 0.),
             "two"   : (1., 1.),
             "three" : (2., 2.)},
            {"one"   : (0., 0., 0.),
             "two"   : (1., 1., 1.),
             "three" : (2., 2., 2.)}
            ]
    
    ztests = [False, True]
    
    for raw, ztest in zip(raws, ztests):
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test"})
    
        test = PointDict()
        
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
        
        assert result["one"].x == 0.
        assert result["two"].y == 1.
        assert result["one"].has_z == ztest


def test_PointDict_auto_plot(tmpdir):
        
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    raw = {"one"   : (0., 0.),
           "two"   : (1., 1.),
           "three" : (2., 2.)
           }
    
    test = PointDict()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_PointDictColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PointDictColumn" in all_objs.keys()
    

def test_PointDictColumn_auto_db(mocker):
    
    names = ["one", "two"]
    raw_data = [[WKTElement("POINT (0 0)"), WKTElement("POINT (1 1)")],
                [WKTElement("POINT (0 0 0)"), WKTElement("POINT (1 1 1)")]]
    
    for raw in raw_data:

        mock_lists = [names, raw]
        
        mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                     return_value=mock_lists,
                     autospec=True)
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test",
                             "tables": ["mock.mock", "position"]})
        
        test = PointDictColumn()
        
        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)
        
        query = QueryCls()
        query.meta.result = meta
        
        query.connect()
        result = test.get_data(query.data.result, meta)
            
        assert result["one"].x == 0.
        assert result["two"].y == 1.


def test_PointDictColumn_auto_db_empty(mocker):
    
    mock_lists = [[], []]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})

    test = PointDictColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_PointDictColumn_auto_db_none(mocker):
    
    mock_lists = [[None, None], [None, None]]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})
    
    test = PointDictColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None

