from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
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
from dtocean_core.data.definitions import TimeTable, TimeTableColumn


def test_TimeTable_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TimeTable" in all_objs.keys()


def test_TimeTable():
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    raw = {"DateTime": dates, "a": values, "b": values}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["a", "b"],
            "units": ["kg", None],
        }
    )

    test = TimeTable()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert "a" in b
    assert len(b) == len(dates)
    assert len(b.resample("D").mean()) == 2


def test_get_None():
    test = TimeTable()
    result = test.get_value(None)

    assert result is None


def test_TimeTable_not_dt():
    dates = []
    dt = 0
    end = 3600
    step = 60

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    raw = {"DateTime": dates, "a": values, "b": values}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["a", "b"],
            "units": ["kg", None],
        }
    )

    test = TimeTable()

    with pytest.raises(ValueError) as excinfo:
        test.get_data(raw, meta)

    assert "datetime.datetime objects" in str(excinfo.value)


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_TimeTable_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    raw = {"DateTime": dates, "a": values, "b": values}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["a", "b"],
            "units": ["kg", None],
        }
    )

    test = TimeTable()

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
    assert len(result) == len(dates)
    assert len(result.resample("D").mean()) == 2


def test_TimeTable_auto_plot(tmpdir):
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    raw = {"DateTime": dates, "a": values, "b": values}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["a", "b"],
            "units": ["kg", None],
        }
    )

    test = TimeTable()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_TimeTableColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TimeTableColumn" in all_objs.keys()


def test_TimeTableColumn_auto_db(mocker):
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))

    mock_dict = {
        "date": [x.date() for x in dates],
        "time": [x.time() for x in dates],
        "a": values,
        "b": values,
    }
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
            "labels": ["a", "b"],
            "units": ["kg", None],
            "tables": ["mock.mock", "date", "time", "a", "b"],
        }
    )

    test = TimeTableColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert "a" in result
    assert len(result) == len(dates)
    assert len(result.resample("D").mean()) == 2


def test_TimeSeriesColumn_auto_db_empty(mocker):
    mock_dict = {"date": [], "time": [], "a": [], "b": []}
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
            "labels": ["a", "b"],
            "units": ["kg", None],
            "tables": ["mock.mock", "date", "time", "a", "b"],
        }
    )

    test = TimeTableColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_TimeSeriesColumn_auto_db_none(mocker):
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))

    mock_dict = {
        "date": [None] * len(dates),
        "time": [x.time() for x in dates],
        "a": values,
        "b": values,
    }
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
            "labels": ["a", "b"],
            "units": ["kg", None],
            "tables": ["mock.mock", "date", "time", "a", "b"],
        }
    )

    test = TimeTableColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
