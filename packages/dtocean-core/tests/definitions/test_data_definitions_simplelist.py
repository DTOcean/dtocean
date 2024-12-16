# pylint: disable=protected-access

import matplotlib.pyplot as plt
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
from dtocean_core.data.definitions import SimpleList, SimpleListColumn


def test_SimpleList_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "SimpleList" in all_objs.keys()


@pytest.mark.parametrize(
    "tinput, ttype",
    [
        ([1, 2], "int"),
        (["hello", "world"], "str"),
        ([True, False], "bool"),
        ([0.5, 0.6], "float"),
    ],
)
def test_SimpleList(tinput, ttype):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
        }
    )

    test = SimpleList()

    a = test.get_data(tinput, meta)
    b = test.get_value(a)

    assert b == tinput


@pytest.mark.parametrize(
    "tinput, ttype",
    [
        ([1, 2.1], "int"),
        (["hello", True], "str"),
        ([True, "False"], "bool"),
        ([0.5, 1], "float"),
    ],
)
def test_SimpleList_get_data_coerce(tinput, ttype):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
        }
    )

    test = SimpleList()
    a = test.get_data(tinput, meta)

    assert type(a[0]).__name__ == ttype


def test_SimpleList_get_value_None():
    test = SimpleList()
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
def test_SimpleList_equals(left, right):
    assert SimpleList.equals(left, right)


@pytest.mark.parametrize(
    "left, right",
    [
        ([1, 2], [1, 3]),
        (["hello", "world"], ["world", "hello"]),
        ([True, False], [True, True]),
        ([0.5, 0.6], [0.5, -0.6]),
    ],
)
def test_SimpleList_not_equals(left, right):
    assert not SimpleList.equals(left, right)


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_SimpleList_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)

    raw = [1.0, 2.0, 3.0]

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["float"],
        }
    )

    test = SimpleList()

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
    fin.meta.result = meta

    fin.connect()
    result = test.get_data(fin.data.result, meta)

    assert result == raw


def test_SimpleList_auto_plot():
    raw = [1.0, 2.0, 3.0]

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["float"],
        }
    )

    test = SimpleList()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_SimpleListColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "SimpleListColumn" in all_objs.keys()


def test_SimpleListColumn_auto_db(mocker):
    raw = [1.0, 2.0, 3.0]
    mock_lists = [raw]

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
            "types": ["float"],
        }
    )

    test = SimpleListColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert result == raw


def test_SimpleListColumn_auto_db_empty(mocker):
    mock_lists = [[]]

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

    test = SimpleListColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_SimpleListColumn_auto_db_none(mocker):
    mock_lists = [[None, None]]

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

    test = SimpleListColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
