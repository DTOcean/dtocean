from pathlib import Path

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
from dtocean_core.data.definitions import (
    NumpyLine,
    NumpyLineArray,
    NumpyLineColumn,
)


def test_NumpyLine_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "NumpyLine" in all_objs.keys()


def test_NumpyLine():
    coarse_sample = np.linspace(0.0, 2 * np.pi, num=5)
    raw = list(zip(coarse_sample, np.sin(coarse_sample)))

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "f(x)"],
        }
    )

    test = NumpyLine()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert max(b[:, 1]) == 1


def test_get_None():
    test = NumpyLine()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_NumpyLine_auto_file(tmpdir, fext):
    coarse_sample = np.linspace(0.0, 2 * np.pi, num=5)
    raw = list(zip(coarse_sample, np.sin(coarse_sample)))

    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "f(x)"],
        }
    )

    test = NumpyLine()

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

    assert max(result[:, 1]) == 1


def test_NumpyLine_auto_plot(tmpdir):
    coarse_sample = np.linspace(0.0, 2 * np.pi, num=5)
    raw = list(zip(coarse_sample, np.sin(coarse_sample)))

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "f(x)"],
            "units": ["m", "m^{2}"],
        }
    )

    test = NumpyLine()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_NumpyLineArray_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "NumpyLineArray" in all_objs.keys()


def test_NumpyLineArray_auto_db(mocker):
    coarse_sample = np.linspace(0.0, 2 * np.pi, num=5)
    mock_list = [list(zip(coarse_sample, np.sin(coarse_sample)))]

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
            "labels": ["x", "f(x)"],
            "units": ["m", "m^{2}"],
            "tables": ["mock.mock", "f_x"],
        }
    )

    test = NumpyLineArray()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert max(result[:, 1]) == 1


def test_NumpyLineArray_auto_db_empty(mocker):
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
            "labels": ["x", "f(x)"],
            "units": ["m", "m^{2}"],
            "tables": ["mock.mock", "f_x"],
        }
    )

    test = NumpyLineArray()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_NumpyLineArray_auto_db_none(mocker):
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
            "labels": ["x", "f(x)"],
            "units": ["m", "m^{2}"],
            "tables": ["mock.mock", "f_x"],
        }
    )

    test = NumpyLineArray()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_NumpyLineColumn_auto_db(mocker):
    coarse_sample = np.linspace(0.0, 2 * np.pi, num=5)
    mock_lists = [coarse_sample, list(np.sin(coarse_sample))]

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
            "labels": ["x", "f(x)"],
            "units": ["m", "m^{2}"],
            "tables": ["mock.mock", "x", "f_x"],
        }
    )

    test = NumpyLineColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert max(result[:, 1]) == 1


def test_NumpyLineColumn_auto_db_empty(mocker):
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
            "labels": ["x", "f(x)"],
            "units": ["m", "m^{2}"],
            "tables": ["mock.mock", "x", "f_x"],
        }
    )

    test = NumpyLineColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_NumpyLineColumn_auto_db_none(mocker):
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
            "labels": ["x", "f(x)"],
            "units": ["m", "m^{2}"],
            "tables": ["mock.mock", "x", "f_x"],
        }
    )

    test = NumpyLineColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
