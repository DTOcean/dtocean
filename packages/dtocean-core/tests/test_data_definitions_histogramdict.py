import pytest

import numpy as np
import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import HistogramDict


def test_HistogramDict_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "HistogramDict" in all_objs.keys()


def test_HistogramDict():
    
    test_data_one = np.random.random(10)
    test_data_two = np.random.random(10)
    
    values_one, bins_one = np.histogram(test_data_one)
    values_two, bins_two = np.histogram(test_data_two)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
                         
    values_dict = {"test_one": (values_one, bins_one),
                   "test_two": (values_two, bins_two)}
    
    test = HistogramDict()
    a = test.get_data(values_dict, meta)
    b = test.get_value(a)
    
    assert len(b["test_one"]["values"]) == len(values_one)
    assert len(b["test_two"]["bins"]) == len(b["test_two"]["values"]) + 1


def test_get_None():
    
    test = HistogramDict()
    result = test.get_value(None)
    
    assert result is None


def test_HistogramDict_equals():
    
    test_data_one = np.random.random(10)
    test_data_two = np.random.random(10)
    
    values_one, bins_one = np.histogram(test_data_one)
    values_two, bins_two = np.histogram(test_data_two)
    
    a = {"test_one": (values_one, bins_one),
         "test_two": (values_two, bins_two)}
    
    b = {"test_one": (values_one, bins_one),
         "test_two": (values_two, bins_two)}
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    test = HistogramDict()
    
    adata = test.get_data(a, meta)
    avalue = test.get_value(adata)
    
    bdata = test.get_data(b, meta)
    bvalue = test.get_value(bdata)
    
    assert HistogramDict.equals(avalue, bvalue)


def test_HistogramDict_not_equals_values():
    
    test_data_one = np.random.random(10)
    test_data_two = np.random.random(10)
    test_data_three = np.random.random(10)
    
    values_one, bins_one = np.histogram(test_data_one)
    values_two, bins_two = np.histogram(test_data_two)
    values_three, bins_three = np.histogram(test_data_three)
    
    a = {"test_one": (values_one, bins_one),
         "test_two": (values_two, bins_two)}
    
    b = {"test_one": (values_one, bins_one),
         "test_two": (values_three, bins_three)}
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    test = HistogramDict()
    
    adata = test.get_data(a, meta)
    avalue = test.get_value(adata)
    
    bdata = test.get_data(b, meta)
    bvalue = test.get_value(bdata)
    
    assert not HistogramDict.equals(avalue, bvalue)


def test_HistogramDict_not_equals_keys():
    
    test_data_one = np.random.random(10)
    test_data_two = np.random.random(10)
    
    values_one, bins_one = np.histogram(test_data_one)
    values_two, bins_two = np.histogram(test_data_two)
    
    a = {"test_one": (values_one, bins_one),
         "test_two": (values_two, bins_two)}
    
    b = {"test_one": (values_one, bins_one),
         "test_three": (values_two, bins_two)}
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    test = HistogramDict()
    
    adata = test.get_data(a, meta)
    avalue = test.get_value(adata)
    
    bdata = test.get_data(b, meta)
    bvalue = test.get_value(bdata)
    
    assert not HistogramDict.equals(avalue, bvalue)


@pytest.mark.parametrize("fext", [".xls", ".xlsx"])
def test_HistogramDict_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
        
    test_data_one = np.random.random(10)
    test_data_two = np.random.random(10)
    
    values_one, bins_one = np.histogram(test_data_one)
    values_two, bins_two = np.histogram(test_data_two)
                         
    values_dict = {"test_one": (values_one, bins_one),
                   "test_two": (values_two, bins_two)}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = HistogramDict()
    
    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, test)
    
    fout = FOutCls()
    fout._path = test_path_str
    fout.data.result = test.get_data(values_dict, meta)

    fout.connect()
    
    assert len(tmpdir.listdir()) == 1
              
    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)
              
    fin = FInCls()
    fin._path = test_path_str
    
    fin.connect()
    result = test.get_data(fin.data.result, meta)
        
    assert len(result["test_one"]["values"]) == len(values_one)
    assert len(result["test_two"]["bins"]) == \
                                      len(result["test_two"]["values"]) + 1


def test_HistogramDict_auto_plot(tmpdir):
    
    test_data_one = np.random.random(10)
    test_data_two = np.random.random(10)
    
    values_one, bins_one = np.histogram(test_data_one)
    values_two, bins_two = np.histogram(test_data_two)
        
    values_dict = {"test_one": (values_one, bins_one),
                   "test_two": (values_two, bins_two)}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = HistogramDict()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(values_dict, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
