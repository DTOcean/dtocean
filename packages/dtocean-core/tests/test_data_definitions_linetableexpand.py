import pytest

import pandas as pd
import matplotlib.pyplot as plt

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import LineTableExpand


def test_LineTableExpand_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "LineTableExpand" in all_objs.keys()


def test_LineTableExpand():
    
    velocity = [float(x) for x in range(10)]
    drag1 = [2 * float(x) for x in range(10)]
    drag2 = [3 * float(x) for x in range(10)]
    
    raw = {"Velocity": velocity,
           "Drag 1": drag1,
           "Drag 2": drag2}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity",
                                    "Drag"]})
    
    test = LineTableExpand()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert "Drag 1" in b
    assert len(b.columns) == 2
    assert len(b) == len(velocity)
    assert b.index.name == "Velocity"
    
    
def test_get_None():
    
    test = LineTableExpand()
    result = test.get_value(None)
    
    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_LineTableExpand_auto_file(tmpdir, fext):
    
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
        
    velocity = [float(x) for x in range(10)]
    drag1 = [2 * float(x) for x in range(10)]
    drag2 = [3 * float(x) for x in range(10)]
    
    raw = {"Velocity": velocity,
           "Drag 1": drag1,
           "Drag 2": drag2}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity",
                                    "Drag"]})
    
    test = LineTableExpand()
    
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

    assert "Drag 1" in result
    assert len(result.columns) == 2
    assert len(result) == len(velocity)
    assert result.index.name == "Velocity"


def test_LineTableExpand_auto_plot(tmpdir):
        
    velocity = [float(x) for x in range(10)]
    drag1 = [2 * float(x) for x in range(10)]
    drag2 = [3 * float(x) for x in range(10)]
    
    raw = {"Velocity": velocity,
           "Drag 1": drag1,
           "Drag 2": drag2}

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["Velocity",
                                    "Drag"],
                         "units": ["m/s", "N"]})
    
    test = LineTableExpand()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")
