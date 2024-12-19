from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
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
from dtocean_core.data.definitions import SimpleDict, SimpleDictColumn


def test_SimpleDict_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "SimpleDict" in all_objs.keys()


@pytest.mark.parametrize(
    "tinput, ttype",
    [
        ([1, 2], "int"),
        (["hello", "world"], "str"),
        ([True, False], "bool"),
        ([0.5, 0.6], "float"),
    ],
)
def test_SimpleDict(tinput, ttype):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
        }
    )

    test = SimpleDict()

    raw = {"a": tinput[0], "b": tinput[1]}
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b["a"] == tinput[0]
    assert b["b"] == tinput[1]


def test_SimpleDict_get_value_None():
    test = SimpleDict()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize(
    "left, right",
    [
        ([1, 2], [1, 2]),
        (["hello", "world"], ["hello", "world"]),
        ([True, False], [True, False]),
        ([0.5, 0.6], [0.5, 0.6]),
    ],
)
def test_SimpleDict_equals(left, right):
    left_dict = {"a": left[0], "b": left[1]}
    right_dict = {"a": right[0], "b": right[1]}

    assert SimpleDict.equals(left_dict, right_dict)


@pytest.mark.parametrize(
    "left, right",
    [
        ([1, 2], [1, 3]),
        (["hello", "world"], ["world", "hello"]),
        ([True, False], [True, True]),
        ([0.5, 0.6], [0.5, -0.6]),
    ],
)
def test_SimpleDict_not_equals(left, right):
    left_dict = {"a": left[0], "b": left[1]}
    right_dict = {"a": right[0], "b": right[1]}

    assert not SimpleDict.equals(left_dict, right_dict)


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_SimpleDict_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    raw = {"a": 0.0, "b": 1.0}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["float"],
        }
    )

    test = SimpleDict()

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

    assert result["a"] == 0.0
    assert result["b"] == 1.0


def test_SimpleDict_auto_file_input_bad_header(mocker):
    df_dict = {"Wrong": [1], "Headers": [1]}
    df = pd.DataFrame(df_dict)

    mocker.patch(
        "dtocean_core.data.definitions.pd.read_excel",
        return_value=df,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["int"],
        }
    )

    test = SimpleDict()

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = Path("file.xlsx")
    fin.meta.result = meta

    with pytest.raises(ValueError):
        fin.connect()


def test_SimpleDict_auto_plot():
    raw = {"a": 0, "b": 1}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["int"],
        }
    )

    test = SimpleDict()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_SimpleDictColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "SimpleDictColumn" in all_objs.keys()


def test_SimpleDictColumn_auto_db(mocker):
    raw = {"a": 0, "b": 1}

    mock_lists = [raw.keys(), raw.values()]

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
            "tables": ["mock.mock", "name", "position"],
            "types": ["int"],
        }
    )

    test = SimpleDictColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert result["a"] == 0
    assert result["b"] == 1


def test_SimpleDictColumn_auto_db_empty(mocker):
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
            "types": ["float"],
        }
    )

    test = SimpleDictColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_SimpleDictColumn_auto_db_none(mocker):
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
            "types": ["float"],
        }
    )

    test = SimpleDictColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
