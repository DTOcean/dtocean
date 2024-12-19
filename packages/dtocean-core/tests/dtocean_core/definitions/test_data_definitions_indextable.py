import uuid

import pandas as pd
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput, AutoQuery, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import IndexTable, IndexTableColumn


def test_IndexTable_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "IndexTable" in all_objs.keys()


def test_IndexTable():
    labels = []
    while len(labels) != 10:
        labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(10)]))

    data = [2 * float(x) for x in range(10)]

    raw = {"Label": labels, "Data": data}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["Label", "Data"],
        }
    )

    test = IndexTable()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert "Data" in b
    assert len(b) == len(data)
    assert b.index.name == "Label"


def test_get_None():
    test = IndexTable()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_IndexTable_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)

    labels = []
    while len(labels) != 10:
        labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(10)]))

    data = [2 * float(x) for x in range(10)]

    raw = {"Label": labels, "Data": data}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["Label", "Data"],
        }
    )

    test = IndexTable()

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

    assert "Data" in result
    assert len(result) == len(data)
    assert result.index.name == "Label"


def test_IndexTableColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "IndexTableColumn" in all_objs.keys()


def test_IndexTableColumn_auto_db(mocker):
    labels = []
    while len(labels) != 10:
        labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(10)]))

    data = [2 * float(x) for x in range(10)]

    mock_dict = {"label": labels, "data": data}
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
            "labels": ["Label", "Data"],
            "tables": ["mock.mock", "label", "data"],
        }
    )

    test = IndexTableColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert "Data" in result
    assert len(result) == len(data)
    assert result.index.name == "Label"


def test_IndexTableColumn_auto_db_empty(mocker):
    mock_dict = {"label": [], "data": []}
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
            "labels": ["Label", "Data"],
            "tables": ["mock.mock", "label", "data"],
        }
    )

    test = IndexTableColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_IndexTableColumn_auto_db_none(mocker):
    mock_dict = {"label": [None, None], "data": [1, 2]}
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
            "labels": ["Label", "Data"],
            "tables": ["mock.mock", "label", "data"],
        }
    )

    test = IndexTableColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
