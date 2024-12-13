
from copy import deepcopy

import pytest
import numpy as np
import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import (NumpyLineDict,
                                           NumpyLineDictArrayColumn)


def test_NumpyLineDict_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "NumpyLineDict" in all_objs.keys()


def test_NumpyLineDict():
    
    coarse_sample = np.linspace(0., 2*np.pi, num=5)
    fine_sample = np.linspace(0., 2*np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    raw = {"Sin(x)": coarse_sin,
           "Cos(x)": fine_cos,
           1: coarse_sin}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x"],
                         "types": ["str"]})
    
    test = NumpyLineDict()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "Sin(x)" in b
    assert max(b["Sin(x)"][:,1]) == 1
    assert b["Cos(x)"][0,1] == b["Cos(x)"][-1,1]
    assert "1" in b


def test_get_None():
    
    test = NumpyLineDict()
    result = test.get_value(None)
    
    assert result is None


def test_NumpyLineDict_equals():
    
    coarse_sample = np.linspace(0., 2*np.pi, num=5)
    fine_sample = np.linspace(0., 2*np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    raw = {"Sin(x)" : np.array(coarse_sin),
           "Cos(x)" : np.array(fine_cos)}
    
    left = deepcopy(raw)
    right = deepcopy(raw)
    
    assert NumpyLineDict.equals(left, right)


def test_NumpyLineDict_not_equal_values():
    
    coarse_sample = np.linspace(0., 2*np.pi, num=5)
    fine_sample = np.linspace(0., 2*np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    left = {"Sin(x)" : np.array(coarse_sin),
            "Cos(x)" : np.array(fine_cos)}
    right = {"Sin(x)" : np.array(fine_cos),
             "Cos(x)" : np.array(coarse_sin)}
    
    assert not NumpyLineDict.equals(left, right)


def test_NumpyLineDict_not_equal_keys():
    
    coarse_sample = np.linspace(0., 2*np.pi, num=5)
    fine_sample = np.linspace(0., 2*np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    left = {"Sin(x)" : np.array(coarse_sin),
            "Cos(x)" : np.array(fine_cos)}
    right = {"Sin(x)" : np.array(coarse_sin),
             "Cosh(x)" : np.array(fine_cos)}
    
    assert not NumpyLineDict.equals(left, right)


@pytest.mark.parametrize("fext", [".xls", ".xlsx"])
def test_NumpyLine_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
        
    coarse_sample = np.linspace(0., 2 * np.pi, num=5)
    fine_sample = np.linspace(0., 2 * np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    raw = {"Sin(x)": coarse_sin,
           "Cos(x)": fine_cos}
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"]})
    
    test = NumpyLineDict()
    
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
    
    assert "Sin(x)" in result
    assert max(result["Sin(x)"][:, 1]) == 1
    assert result["Cos(x)"][0, 1] == result["Cos(x)"][-1, 1]


def test_NumpyLineDict_auto_plot(tmpdir):
        
    coarse_sample = np.linspace(0., 2 * np.pi, num=5)
    fine_sample = np.linspace(0., 2 * np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    raw = {"Sin(x)": coarse_sin,
           "Cos(x)": fine_cos}
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["x", "f(x)"],
                         "units": ["m", "m^{2}"]})
    
    test = NumpyLineDict()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
    

def test_NumpyLineDictArrayColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "NumpyLineDictArrayColumn" in all_objs.keys()
    

def test_NumpyLineDictArrayColumn_auto_db(mocker):
    
    coarse_sample = np.linspace(0., 2 * np.pi, num=5)
    fine_sample = np.linspace(0., 2 * np.pi, num=9)
    
    coarse_sin = zip(coarse_sample, np.sin(coarse_sample))
    fine_cos = zip(fine_sample, np.cos(fine_sample))
    
    mock_lists = [["Sin(x)", "Cos(x)"], [coarse_sin, fine_cos]]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Name", "f(x)"],
                         "tables": ["mock.mock", "name", "f"]})
    
    test = NumpyLineDictArrayColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
    result = test.get_data(query.data.result, meta)
        
    assert "Sin(x)" in result
    assert max(result["Sin(x)"][:, 1]) == 1
    assert result["Cos(x)"][0, 1] == result["Cos(x)"][-1, 1]


def test_NumpyLineDictArrayColumn_auto_db_empty(mocker):
    
    mock_lists = [[], []]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Name", "f(x)"],
                         "tables": ["mock.mock", "name", "f"]})
    
    test = NumpyLineDictArrayColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_NumpyLineDictArrayColumn_auto_db_none(mocker):
    
    mock_lists = [[None, None], [None, None]]
    
    mocker.patch('dtocean_core.data.definitions.get_all_from_columns',
                 return_value=mock_lists,
                 autospec=True)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Name", "f(x)"],
                         "tables": ["mock.mock", "name", "f"]})
    
    test = NumpyLineDictArrayColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None

