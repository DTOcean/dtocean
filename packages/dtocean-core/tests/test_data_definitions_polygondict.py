import pytest

import pandas as pd
import matplotlib.pyplot as plt
from geoalchemy2.elements import WKTElement

from mdo_engine.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import PolygonDict, PolygonDictColumn


def test_PolygonDict_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PolygonDict" in all_objs.keys()


def test_PolygonDict():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})

    raw = {"block 1": [(0., 0.),
                       (1., 1.),
                       (2., 2.)],
           "block 2": [(10., 10.),
                       (11., 11.),
                       (12., 12.)]
           }
    
    test = PolygonDict()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b["block 1"].exterior.coords[0][0] == 0.
    assert b["block 2"].exterior.coords[2][1] == 12.
            
    raw = {"block 1": [(0., 0., 0.),
                       (1., 1., 1.),
                       (2., 2., 2.)],
           "block 2": [(10., 10., 10.),
                       (11., 11., 11.),
                       (12., 12., 12.)]
           }
    
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b["block 1"].exterior.coords[0][0] == 0.
    assert b["block 2"].exterior.coords[2][1] == 12.
    assert b["block 1"].exterior.coords[1][2] == 1.

    raw = {"block 1": [(0., 0., 0., 0),
                       (1., 1., 1., 1.),
                       (2., 2., 2., 2.)],
           "block 2": [(10., 10., 10., 10.),
                       (11., 11., 11., 11.),
                       (12., 12., 12., 12.)]
           }
    
    with pytest.raises(ValueError):
        test.get_data(raw, meta)
        
    raw = {"block 1": [(0., 0., 0.),
                       (1., 1., 1.)],
           "block 2": [(10., 10., 10.),
                       (11., 11., 11.)]
           }
        
    with pytest.raises(ValueError):
        test.get_data(raw, meta)


def test_get_None():
    
    test = PolygonDict()
    result = test.get_value(None)
    
    assert result is None
    

@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_PolygonDict_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raws = [{"block 1": [(0., 0.),
                         (1., 1.),
                         (2., 2.)],
             "block 2": [(10., 10.),
                         (11., 11.),
                         (12., 12.)]},
            {"block 1": [(0., 0., 0.),
                         (1., 1., 1.),
                         (2., 2., 2.)],
             "block 2": [(10., 10., 10.),
                         (11., 11., 11.),
                         (12., 12., 12.)]}
            ]
               
    ztests = [False, True]
    
    for raw, ztest in zip(raws, ztests):
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test"})
    
        test = PolygonDict()
        
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
        
        assert result["block 1"].exterior.coords[0][0] == 0.
        assert result["block 2"].exterior.coords[2][1] == 12.
        assert result["block 1"].has_z == ztest
        
        
def test_PolygonDict_auto_file_input_bad_header(mocker):

    df_dict = {"Wrong": [1],
               "Headers": [1]}
    df = pd.DataFrame(df_dict)
    
    mocker.patch('dtocean_core.data.definitions.pd.read_excel',
                 return_value=df,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})

    test = PolygonDict()
              
    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)
              
    fin = FInCls()
    fin._path = "file.xlsx"
    
    with pytest.raises(ValueError):
        fin.connect()


def test_PolygonDict_auto_file_output_bad_data(tmpdir):

    test_path = tmpdir.mkdir("sub").join("test{}".format(".csv"))
    test_path_str = str(test_path)
           
    raw = {"block 1": [(0., 0.),
                       (1., 1.),
                       (2., 2.)],
           "block 2": [(10., 10.),
                       (11., 11.),
                       (12., 12.)]}
        
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})

    test = PolygonDict()
    
    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, test)
    
    fout = FOutCls()
    fout._path = test_path_str
    fout.data.result = raw

    with pytest.raises(TypeError):
        fout.connect()


def test_PolygonDict_auto_plot(tmpdir):
        
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    raw = {"block 1": [(0., 0., 0.),
                       (1., 1., 1.),
                       (2., 2., 2.)],
           "block 2": [(10., 10., 10.),
                       (11., 11., 11.),
                       (12., 12., 12.)]
           }
    
    test = PolygonDict()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_PolygonDictColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PolygonDictColumn" in all_objs.keys()
    

def test_PolygonDictColumn_auto_db(mocker):
    
    names = ["block 1", "block 2"]
    raws = [[WKTElement("POLYGON ((0 0, 1 0, 1 1, 0 0))"),
             WKTElement("POLYGON ((10 10, 11 10, 11 11, 10 10))")],
            [WKTElement("POLYGON ((0 0 0, 1 0 0, 1 1 0, 0 0 0))"),
             WKTElement("POLYGON ((10 10 0, 11 10 0, 11 11 0, 10 10 0))")]]
    
    for raw in raws:
        
        mock_lists = [names, raw]
        
        mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                     return_value=mock_lists,
                     autospec=True)
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test",
                             "tables": ["mock.mock",
                                        "description",
                                        "boundary"]})
        
        test = PolygonDictColumn()
        
        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)
        
        query = QueryCls()
        query.meta.result = meta
        
        query.connect()
        result = test.get_data(query.data.result, meta)
            
        assert result["block 1"].exterior.coords[0][0] == 0.
        assert result["block 2"].exterior.coords[2][1] == 11.


def test_PolygonDictColumn_auto_db_empty(mocker):
    
    mock_lists = [[], []]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock",
                                    "description",
                                    "boundary"]})

    test = PolygonDictColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_PolygonDictColumn_auto_db_none(mocker):
    
    mock_lists = [[None, None], [None, None]]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock",
                                    "description",
                                    "boundary"]})
    
    test = PolygonDictColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None
    
    
def test_PolygonDictColumn_auto_db_no_tables(mocker):
    
    mock_lists = [[None, None], [None, None]]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PolygonDictColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    with pytest.raises(ValueError):
        query.connect()
