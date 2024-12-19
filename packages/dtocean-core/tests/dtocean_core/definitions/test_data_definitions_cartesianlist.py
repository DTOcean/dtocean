from pathlib import Path

import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput, AutoQuery, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import CartesianList, CartesianListColumn


def test_CartesianList_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianList" in all_objs.keys()


def test_CartesianList():
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = CartesianList()

    raw = [(0, 1), (1, 2)]
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b[0][0] == 0
    assert b[0][1] == 1

    raw = [(0, 1, -1), (1, 2, -2)]
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b[0][0] == 0
    assert b[0][1] == 1
    assert b[0][2] == -1

    raw = [(0, 1, -1, 1)]

    with pytest.raises(ValueError):
        test.get_data(raw, meta)


def test_get_None():
    test = CartesianList()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_CartesianList_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    raws = [[(0, 1), (1, 2)], [(0, 1, -1), (1, 2, -2)]]

    for raw in raws:
        meta = CoreMetaData(
            {"identifier": "test", "structure": "test", "title": "test"}
        )

        test = CartesianList()

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

        assert result[0][0] == 0
        assert result[0][1] == 1


def test_CartesianListColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "CartesianListColumn" in all_objs.keys()


def test_CartesianListColumn_auto_db(mocker):
    raws = [[(0, 1), (1, 2)], [(0, 1, -1), (1, 2, -2)]]

    for raw in raws:
        mock_list = [raw]

        mocker.patch(
            "dtocean_core.data.definitions.get_one_from_column",
            return_value=mock_list,
        )

        meta = CoreMetaData(
            {
                "identifier": "test",
                "structure": "test",
                "title": "test",
                "tables": ["mock.mock", "position"],
            }
        )

        test = CartesianListColumn()

        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)

        query = QueryCls()
        query.meta.result = meta

        query.connect()
        result = test.get_data(query.data.result, meta)

        assert result[0][0] == 0
        assert result[0][1] == 1


def test_CartesianListColumn_auto_db_empty(mocker):
    mock_list = None

    mocker.patch(
        "dtocean_core.data.definitions.get_one_from_column",
        return_value=mock_list,
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

    test = CartesianListColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_CartesianListColumn_auto_db_none(mocker):
    mock_list = [None]

    mocker.patch(
        "dtocean_core.data.definitions.get_one_from_column",
        return_value=mock_list,
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

    test = CartesianListColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
