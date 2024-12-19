from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput, AutoQuery, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import TableData, TableDataColumn


def test_TableData_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TableData" in all_objs.keys()


def test_TableData():
    idx = range(1000)

    values = np.random.rand(len(idx))
    raw = {"index": idx, "a": values, "b": values}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["index", "a", "b"],
            "units": [None, "kg", None],
        }
    )

    test = TableData()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert "a" in b
    assert len(b) == len(idx)


def test_get_None():
    test = TableData()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_TableData_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    idx = range(1000)

    values = np.random.rand(len(idx))
    raw = {"index": idx, "a": values, "b": values}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["index", "a", "b"],
            "units": [None, "kg", None],
        }
    )

    test = TableData()

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

    fin.connect()
    result = test.get_data(fin.data.result, meta)

    assert "a" in result
    assert len(result) == len(idx)


def test_TableDataData_equals():
    idx = range(1000)
    values = np.random.rand(len(idx))
    raw = {"index": idx, "a": values, "b": values}

    a = pd.DataFrame(raw)
    b = pd.DataFrame(raw)

    assert TableData.equals(a, b)


def test_TableDataData_not_equals():
    idx = range(1000)
    values1 = np.random.rand(len(idx))
    values2 = np.random.rand(len(idx))

    raw1 = {"index": idx, "a": values1, "b": values1}

    raw2 = {"index": idx, "c": values2, "d": values2}

    a = pd.DataFrame(raw1)
    b = pd.DataFrame(raw2)

    assert not TableData.equals(a, b)


def test_TableDataColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TableDataColumn" in all_objs.keys()


def test_TableDataColumn_auto_db(mocker):
    idx = range(1000)
    values = np.random.rand(len(idx))

    mock_dict = {"index": idx, "a": values, "b": values}
    mock_df = pd.DataFrame(mock_dict)

    mocker.patch(
        "dtocean_core.data.definitions.get_table_df",
        return_value=mock_df,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["index", "a", "b"],
            "tables": ["mock.mock", "index", "a", "b"],
        }
    )

    test = TableDataColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert "a" in result
    assert len(result) == len(idx)


def test_TableDataColumn_auto_db_empty(mocker):
    mock_dict = {"index": [], "a": [], "b": []}
    mock_df = pd.DataFrame(mock_dict)

    mocker.patch(
        "dtocean_core.data.definitions.get_table_df",
        return_value=mock_df,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["index", "a", "b"],
            "tables": ["mock.mock", "index", "a", "b"],
        }
    )

    test = TableDataColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_TableDataColumn_auto_db_none(mocker):
    mock_dict = {"index": [None, None], "a": [None, None], "b": [None, None]}
    mock_df = pd.DataFrame(mock_dict)

    mocker.patch(
        "dtocean_core.data.definitions.get_table_df",
        return_value=mock_df,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["index", "a", "b"],
            "tables": ["mock.mock", "index", "a", "b"],
        }
    )

    test = TableDataColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
