import matplotlib.pyplot as plt
import numpy as np
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import (
    AutoFileInput,
    AutoFileOutput,
    AutoPlot,
    AutoQuery,
    Core,
)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import CartesianDict, CartesianDictColumn


def test_CartesianDict_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianDict" in all_objs.keys()


def test_CartesianDict():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["str"],
        }
    )

    test = CartesianDict()

    raw = {"a": (0, 1), "b": (1, 2), 1: (2, 3)}
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b["a"] is not None
    assert b["a"][0] == 0
    assert b["a"][1] == 1
    assert "1" in b

    raw = {"a": (0, 1, -1), "b": (1, 2, -2)}
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b["a"] is not None
    assert b["a"][0] == 0
    assert b["a"][1] == 1
    assert b["a"][2] == -1

    raw = {"a": (0, 1, -1, 1)}

    with pytest.raises(ValueError):
        test.get_data(raw, meta)


def test_get_None():
    test = CartesianDict()
    result = test.get_value(None)

    assert result is None


def test_CartesianDict_equals():
    left = {"a": np.array([0, 1, -1]), "b": np.array([1, 2, -2])}
    right = {"a": np.array([0, 1, -1]), "b": np.array([1, 2, -2])}

    assert CartesianDict.equals(left, right)


def test_CartesianDict_not_equal_values():
    left = {"a": np.array([0, 1, -1]), "b": np.array([1, 2, -2])}
    right = {"a": np.array([0, 1, -1]), "b": np.array([1, 2, 2])}

    assert not CartesianDict.equals(left, right)


def test_CartesianDict_not_equal_keys():
    left = {"a": np.array([0, 1, -1]), "b": np.array([1, 2, -2])}
    right = {"a": np.array([0, 1, -1]), "c": np.array([1, 2, -2])}

    assert not CartesianDict.equals(left, right)


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_CartesianDict_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)

    raws = [{"a": (0, 1), "b": (1, 2)}, {"a": (0, 1, -1), "b": (1, 2, -2)}]

    for raw in raws:
        meta = CoreMetaData(
            {"identifier": "test", "structure": "test", "title": "test"}
        )

        test = CartesianDict()

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

        assert result["a"][0] == 0
        assert result["a"][1] == 1


@pytest.mark.parametrize(
    "raw", [{"a": (0, 1), "b": (1, 2)}, {"a": (0, 1, -1), "b": (1, 2, -2)}]
)
def test_CartesianDict_auto_plot(raw):
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = CartesianDict()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_CartesianDictColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianDictColumn" in all_objs.keys()


def test_CartesianDictColumn_auto_db(mocker):
    raws = [{"a": (0, 1), "b": (1, 2)}, {"a": (0, 1, -1), "b": (1, 2, -2)}]

    for raw in raws:
        mock_lists = [raw.keys(), raw.values()]

        mocker.patch(
            "dtocean_core.data.definitions.get_all_from_columns",
            return_value=mock_lists,
        )

        meta = CoreMetaData(
            {
                "identifier": "test",
                "structure": "test",
                "title": "test",
                "tables": ["mock.mock", "name", "position"],
            }
        )

        test = CartesianDictColumn()

        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)

        query = QueryCls()
        query.meta.result = meta

        query.connect()
        result = test.get_data(query.data.result, meta)

        assert result["a"][0] == 0
        assert result["a"][1] == 1


def test_CartesianDictColumn_auto_db_empty(mocker):
    mock_lists = [[], []]

    mocker.patch(
        "dtocean_core.data.definitions.get_all_from_columns",
        return_value=mock_lists,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "tables": ["mock.mock", "position"],
        }
    )

    test = CartesianDictColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_CartesianDictColumn_auto_db_none(mocker):
    mock_lists = [[None, None], [None, None]]

    mocker.patch(
        "dtocean_core.data.definitions.get_all_from_columns",
        return_value=mock_lists,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "tables": ["mock.mock", "position"],
        }
    )

    test = CartesianDictColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
