from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import XSet3D


def test_XSet3D():
    raw = {
        "values": {
            "a": np.random.randn(2, 3, 1),
            "b": np.random.randn(2, 3, 1),
        },
        "coords": [["a", "b"], [-2, 0, 2], [datetime(2010, 12, 1)]],
    }

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "t", "a", "b"],
            "units": [None, "m", "s", "POWER!", None],
        }
    )

    test = XSet3D()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b["a"].shape == (2, 3, 1)
    assert b["a"].units == "POWER!"
    assert b.t.units == "s"


def test_get_None():
    test = XSet3D()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".nc"])
def test_XSet3D_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    raw = {
        "values": {
            "a": np.random.randn(2, 3, 1),
            "b": np.random.randn(2, 3, 1),
        },
        "coords": [["a", "b"], [-2, 0, 2], [datetime(2010, 12, 1)]],
    }
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "t", "a", "b"],
            "units": [None, "m", "s", "POWER!", None],
        }
    )
    test = XSet3D()

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
    fin.meta.result = meta
    fin._path = test_path_path

    fin.connect()
    a = test.get_data(fin.data.result, meta)
    b = test.get_value(a)

    assert b is not None
    assert b["a"].shape == (2, 3, 1)
    assert b["a"].units == "POWER!"
    assert b.t.units == "s"


def test_toText_fromText():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "t", "a", "b"],
            "units": [None, "m", "s", "POWER!", None],
        }
    )
    structure = XSet3D()

    raw = {
        "values": {
            "a": np.random.randn(2, 3, 1),
            "b": np.random.randn(2, 3, 1),
        },
        "coords": [["a", "b"], [-2, 0, 2], [datetime(2010, 12, 1)]],
    }

    a = structure.get_data(raw, meta)
    b = structure.get_value(a)
    c = structure.toText(b)
    test = structure.fromText(c, structure.version)

    assert test is not None
    assert test.equals(a)


def test_toText_fromText_none():
    structure = XSet3D()
    c = structure.toText(None)

    assert structure.fromText(c, structure.version) is None
