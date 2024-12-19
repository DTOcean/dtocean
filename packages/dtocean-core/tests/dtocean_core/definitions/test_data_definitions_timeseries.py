from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import (
    AutoFileInput,
    AutoFileOutput,
    AutoPlot,
    AutoQuery,
    Core,
)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import TimeSeries, TimeSeriesColumn


def test_TimeSeries_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TimeSeries" in all_objs.keys()


def test_TimeSeries():
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    raw = [(d, v) for d, v in zip(dates, values)]

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["mass"],
            "units": ["kg"],
        }
    )

    test = TimeSeries()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert len(b) == len(dates)
    assert len(b.resample("D").mean()) == 2


def test_get_None():
    test = TimeSeries()
    result = test.get_value(None)

    assert result is None


def test_TimeSeries_equals():
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    dt_index = pd.DatetimeIndex(dates)

    a = pd.Series(values, index=dt_index)
    b = pd.Series(values, index=dt_index)

    assert TimeSeries.equals(a, b)


def test_TimeSeries_not_equals():
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    dt_index = pd.DatetimeIndex(dates)

    values = np.random.rand(len(dates))
    a = pd.Series(values, index=dt_index)

    values = np.random.rand(len(dates))
    b = pd.Series(values, index=dt_index)

    assert not TimeSeries.equals(a, b)


def test_TimeSeries_auto_file(tmpdir):
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    raw = [(d, v) for d, v in zip(dates, values)]

    test_path = tmpdir.mkdir("sub").join("test.csv")
    test_path_str = str(test_path)

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["mass"],
            "units": ["kg"],
        }
    )

    test = TimeSeries()

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

    assert len(result) == len(dates)
    assert len(result.resample("D").mean()) == 2


def test_TimeSeries_auto_plot(tmpdir):
    dates = []
    dt = datetime(2010, 12, 1)
    end = datetime(2010, 12, 2, 23, 59, 59)
    step = timedelta(seconds=3600)

    while dt < end:
        dates.append(dt)
        dt += step

    values = np.random.rand(len(dates))
    raw = [(d, v) for d, v in zip(dates, values)]

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["mass"],
            "units": ["kg"],
        }
    )

    test = TimeSeries()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_TimeSeriesColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TimeSeriesColumn" in all_objs.keys()


def test_TimeSeriesColumn_auto_db(mocker):
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
        "mass": values,
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
            "labels": ["mass"],
            "units": ["kg"],
            "tables": ["mock.mock", "date", "time", "mass"],
        }
    )

    test = TimeSeriesColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()
    result = test.get_data(query.data.result, meta)

    assert len(result) == len(dates)
    assert len(result.resample("D").mean()) == 2


def test_TimeSeriesColumn_auto_db_empty(mocker):
    mock_dict = {"date": [], "time": [], "mass": []}
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
            "labels": ["mass"],
            "units": ["kg"],
            "tables": ["mock.mock", "date", "time", "mass"],
        }
    )

    test = TimeSeriesColumn()

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
        "mass": values,
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
            "labels": ["mass"],
            "units": ["kg"],
            "tables": ["mock.mock", "date", "time", "mass"],
        }
    )

    test = TimeSeriesColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
