from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput, AutoPlot, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import SimplePie


def test_SimplePie_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "SimplePie" in all_objs.keys()


def test_SimplePie():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["int"],
        }
    )

    test = SimplePie()

    raw = {"a": 0, "b": 1}
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b["a"] == 0
    assert b["b"] == 1


def test_get_None():
    test = SimplePie()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_SimplePie_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    raw = {"a": 0, "b": 1}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["int"],
        }
    )

    test = SimplePie()

    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, test)

    fout = FOutCls()
    fout._path = test_path_path
    fout.data.result = test.get_data(raw, meta)

    fout.connect()

    assert len(tmpdir.listdir()) == 1

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = test_path_path
    fin.meta.result = meta

    fin.connect()
    result = test.get_data(fin.data.result, meta)

    assert result["a"] == 0
    assert result["b"] == 1


def test_SimplePie_auto_plot():
    raw = {"a": 0, "b": 1}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["int"],
        }
    )

    test = SimplePie()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")
