import pytest

import numpy as np
import matplotlib.pyplot as plt

from mdo_engine.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import XGrid2D


def test_XGrid2D_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "XGrid2D" in all_objs.keys()


def test_XGrid2D():

    raw = {"values": np.random.randn(2, 3),
           "coords": [['a', 'b'], [-2, 0, 2]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['x', 'y'],
                         "units": [None, 'm', 'POWER!']})
    
    test = XGrid2D()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b.values.shape == (2,3)
    assert b.units == 'POWER!'
    assert b.y.units == 'm'
    

def test_get_None():
    
    test = XGrid2D()
    result = test.get_value(None)
    
    assert result is None


@pytest.mark.parametrize("fext", [".nc"])
def test_XGrid2D_auto_file(tmpdir, fext):

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
           
    raw = {"values": np.random.randn(2, 3),
           "coords": [['a', 'b'], [-2, 0, 2]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['x', 'y'],
                         "units": [None, 'm', 'POWER!']})
    
    test = XGrid2D()
    
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
    fin.meta.result = meta
    fin._path = test_path_str
    
    fin.connect()
    result = test.get_data(fin.data.result, meta)
    
    assert result.values.shape == (2,3)
    assert result.units == 'POWER!'
    assert result.y.units == 'm'
        

def test_XGrid2D_auto_plot(tmpdir):
        
    raw = {"values": np.random.randn(2, 3),
           "coords": [['a', 'b'], [-2, 0, 2]]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['x', 'y'],
                         "units": ['\sum_{n=1}^{\infty} 2^{-n} = 1',
                                   'm', 
                                   'POWER!']})
    
    test = XGrid2D()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_XGrid2D_auto_plot_reverse(tmpdir):
        
    raw = {"values": np.random.randn(3, 2),
           "coords": [[-2, 0, 2], ['a', 'b']]}
           
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ['x', 'y'],
                         "units": ['\sum_{n=1}^{\infty} 2^{-n} = 1',
                                   'm', 
                                   'POWER!']})
    
    test = XGrid2D()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
