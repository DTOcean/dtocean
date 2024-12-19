import datetime
from pathlib import Path

import pandas as pd
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import DateTimeDict


def test_DateTimeDict_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "DateTimeDict" in all_objs.keys()


def test_DateTimeDict():
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = DateTimeDict()

    raw = {
        "a": datetime.datetime.now(),
        "b": datetime.datetime.now(datetime.UTC),
    }
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b["a"] == raw["a"]
    assert b["b"] == raw["b"]


def test_DateTimeDict_type_error():
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = DateTimeDict()

    raw = {"a": "wrong", "b": datetime.datetime.now(datetime.UTC)}

    with pytest.raises(TypeError):
        test.get_data(raw, meta)


def test_get_None():
    test = DateTimeDict()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_DateTimeDict_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    raw = {
        "a": datetime.datetime.now(),
        "b": datetime.datetime.now(datetime.UTC),
    }

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = DateTimeDict()

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

    # Microseconds are lost in xls case
    assert result["a"].replace(microsecond=0) == raw["a"].replace(microsecond=0)
    assert result["b"].replace(microsecond=0) == raw["b"].replace(microsecond=0)


def test_DateTimeDict_auto_file_input_bad_header(mocker):
    df_dict = {"Wrong": [1], "Headers": [1]}
    df = pd.DataFrame(df_dict)

    mocker.patch(
        "dtocean_core.data.definitions.pd.read_excel",
        return_value=df,
        autospec=True,
    )

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = DateTimeDict()

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = Path("file.xlsx")

    with pytest.raises(ValueError):
        fin.connect()


def test_DateTimeDict_auto_file_input_bad_ext():
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = DateTimeDict()

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = Path("file.bad")

    with pytest.raises(IOError):
        fin.connect()


def test_DateTimeDict_auto_file_output_bad_ext():
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = DateTimeDict()

    fin_factory = InterfaceFactory(AutoFileOutput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = Path("file.bad")

    with pytest.raises(IOError):
        fin.connect()
