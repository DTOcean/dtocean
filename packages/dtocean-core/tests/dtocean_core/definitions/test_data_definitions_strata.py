from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput, AutoPlot, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Strata


def test_Strata_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "Strata" in all_objs.keys()


def test_Strata():
    x = np.linspace(0.0, 1000.0, 101)
    y = np.linspace(0.0, 300.0, 31)
    nx = len(x)
    ny = len(y)

    X, Y = np.meshgrid(x, y)
    Z = -X * 0.1 - 1
    depths = Z.T[:, :, np.newaxis]
    sediments = np.full((nx, ny, 1), "rock")

    raw = {
        "values": {"depth": depths, "sediment": sediments},
        "coords": [x, y, ["layer 1"]],
    }

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "layer", "depth", "sediment"],
        }
    )

    test = Strata()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b["depth"].values.shape == (101, 31, 1)
    assert (b["sediment"].values == "rock").all()


def test_get_None():
    test = Strata()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".nc"])
def test_Strata_auto_file(tmpdir, fext):
    test_dir = tmpdir.mkdir("sub")

    test_path_out = test_dir.join("test{}".format(fext))
    test_path_out_path = Path(test_path_out)

    test_path_in = test_dir.join("test_depth{}".format(fext))
    test_path_in_path = Path(test_path_in)

    x = np.linspace(0.0, 1000.0, 101)
    y = np.linspace(0.0, 300.0, 31)
    nx = len(x)
    ny = len(y)

    X, Y = np.meshgrid(x, y)
    Z = -X * 0.1 - 1
    depths = Z.T[:, :, np.newaxis]
    sediments = np.full((nx, ny, 1), "rock")

    raw = {
        "values": {"depth": depths, "sediment": sediments},
        "coords": [x, y, ["layer 1"]],
    }

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "layer", "depth", "sediment"],
        }
    )

    test = Strata()

    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, test)

    fout = FOutCls()
    fout._path = test_path_out_path
    fout.data.result = test.get_data(raw, meta)

    fout.connect()

    assert len(tmpdir.listdir()) == 1

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin.meta.result = meta
    fin._path = test_path_in_path

    fin.connect()
    result = test.get_data(fin.data.result, meta)

    assert result["depth"].values.shape == (101, 31, 1)
    assert (result["sediment"].values == "rock").all()


def test_Strata_auto_plot(tmpdir):
    x = np.linspace(0.0, 1000.0, 101)
    y = np.linspace(0.0, 300.0, 31)
    nx = len(x)
    ny = len(y)

    X, Y = np.meshgrid(x, y)
    Z = -X * 0.1 - 1
    depths = Z.T[:, :, np.newaxis]
    sediments = np.full((nx, ny, 1), "rock")

    raw = {
        "values": {"depth": depths, "sediment": sediments},
        "coords": [x, y, ["layer 1"]],
    }

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "layer", "depth", "sediment"],
        }
    )

    test = Strata()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")
    plt.close("all")
