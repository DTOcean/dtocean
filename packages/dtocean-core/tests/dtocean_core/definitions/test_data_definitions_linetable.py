import pytest

import pandas as pd
import matplotlib.pyplot as plt

from mdo_engine.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import LineTable, LineTableColumn


def test_LineTable_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "LineTable" in all_objs.keys()


def test_LineTable():
    
    velocity = [float(x) for x in range(10)]
    thrust = [2 * float(x) for x in range(10)]
    power = [3 * float(x) for x in range(10)]
    
    raw = {"Velocity": velocity,
           "Thrust": thrust,
           "Power": power}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity",
                                    "Thrust",
                                    "Power"]})
    
    test = LineTable()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "Thrust" in b
    assert len(b) == len(velocity)
    assert b.index.name == "Velocity"
    
    
def test_get_None():
    
    test = LineTable()
    result = test.get_value(None)
    
    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_LineTable_auto_file(tmpdir, fext):
    
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
        
    velocity = [float(x) for x in range(10)]
    thrust = [2 * float(x) for x in range(10)]
    power = [3 * float(x) for x in range(10)]
    
    raw = {"Velocity": velocity,
           "Thrust": thrust,
           "Power": power}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity",
                                    "Thrust",
                                    "Power"]})
    
    test = LineTable()
    
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
    
    assert "Thrust" in result
    assert len(result) == len(velocity)
    assert result.index.name == "Velocity"


def test_LineTable_auto_plot(tmpdir):
        
    velocity = [float(x) for x in range(10)]
    thrust = [2 * float(x) for x in range(10)]
    power = [3 * float(x) for x in range(10)]
    
    raw = {"Velocity": velocity,
           "Thrust": thrust,
           "Power": power}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity", "Thrust", "Power"],
                         "units": ["m/s", "N", "W"]})
    
    test = LineTable()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
    

def test_LineTableColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "LineTableColumn" in all_objs.keys()
    

def test_LineTableColumn_auto_db(mocker):
    
    velocity = [float(x) for x in range(10)]
    thrust = [2 * float(x) for x in range(10)]
    power = [3 * float(x) for x in range(10)]
    
    mock_dict = {"velocity": velocity,
                 "thrust": thrust,
                 "power": power}
    mock_df = pd.DataFrame(mock_dict)
    
    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity", "Thrust", "Power"],
                         "units": ["m/s", "N", "W"],
                         "tables": ["mock.mock",
                                    "velocity",
                                    "thrust",
                                    "power"]
                         })
    
    test = LineTableColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
    result = test.get_data(query.data.result, meta)
        
    assert "Thrust" in result
    assert len(result) == len(velocity)
    assert result.index.name == "Velocity"
    

def test_LineTableColumn_auto_db_empty(mocker):
    
    mock_dict = {"velocity": [],
                 "thrust": [],
                 "power": []}
    mock_df = pd.DataFrame(mock_dict)
    
    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity", "Thrust", "Power"],
                         "units": ["m/s", "N", "W"],
                         "tables": ["mock.mock",
                                    "velocity",
                                    "thrust",
                                    "power"]
                         })
    
    test = LineTableColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_LineTableColumn_auto_db_none(mocker):
    
    thrust = [2 * float(x) for x in range(10)]
    power = [3 * float(x) for x in range(10)]
    
    mock_dict = {"velocity": [None]*10,
                 "thrust": thrust,
                 "power": power}
    mock_df = pd.DataFrame(mock_dict)
    
    mocker.patch('dtocean_core.data.definitions.get_table_df',
                 return_value=mock_df,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity", "Thrust", "Power"],
                         "units": ["m/s", "N", "W"],
                         "tables": ["mock.mock",
                                    "velocity",
                                    "thrust",
                                    "power"]
                         })
    
    test = LineTableColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None
