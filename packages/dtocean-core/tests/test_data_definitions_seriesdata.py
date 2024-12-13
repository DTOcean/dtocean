
# pylint: disable=protected-access

import numpy as np
import pandas as pd

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import AutoFileInput, AutoFileOutput, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import SeriesData


def test_SeriesData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "SeriesData" in all_objs.keys()


def test_SeriesData():
    
    raw = np.random.rand(100)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['mass'],
                         "units": ["kg"]})
    
    test = SeriesData()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert len(b) == len(raw)
    
    
def test_get_None():
    
    test = SeriesData()
    result = test.get_value(None)
    
    assert result is None


def test_SeriesData_equals():
    
    a = pd.Series([1, 2, 3])
    b = pd.Series([1, 2, 3])
    
    assert SeriesData.equals(a, b)


def test_SeriesData_not_equals():
    
    a = pd.Series([1, 2, 3])
    b = pd.Series()
    
    assert not SeriesData.equals(a, b)


def test_SeriesData_auto_file(tmpdir):
        
    raw = np.random.rand(100)
    test_path = tmpdir.mkdir("sub").join("test.csv")
    test_path_str = str(test_path)
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['mass'],
                         "units": ["kg"]})
    
    test = SeriesData()
    
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
    
    assert len(result) == len(raw)
