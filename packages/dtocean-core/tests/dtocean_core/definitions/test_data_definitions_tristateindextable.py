import random
import uuid
from pathlib import Path

import pandas as pd
import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import AutoFileInput, AutoFileOutput, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import TriStateIndexTable

VALID_ENTRIES = ["true", "false", "unknown"]


def test_TriStateIndexTable_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "TriStateIndexTable" in all_objs.keys()


def test_TriStateIndexTable():
    k = 100
    labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(k)]))
    values = random.choices(VALID_ENTRIES, k=k)

    raw = {"Label": labels, "a": values, "b": values}
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["Label", "a", "b"],
        }
    )

    test = TriStateIndexTable()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert "a" in b
    assert len(b) == k
    assert b.index.name == "Label"


def test_get_None():
    test = TriStateIndexTable()
    result = test.get_value(None)

    assert result is None


def test_TriStateIndexTable_error():
    k = 100
    labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(k)]))
    idx = range(k)
    values = random.choices(VALID_ENTRIES, k=k)

    raw = {"Label": labels, "idx": idx, "a": values, "b": values}
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["Label", "idx", "a", "b"],
        }
    )

    test = TriStateIndexTable()

    with pytest.raises(ValueError) as e:
        test.get_data(raw, meta)

    assert "Given raw value is incorrectly formatted" in str(e)


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_TriStateIndexTable_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    k = 100
    labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(k)]))
    values = random.choices(VALID_ENTRIES, k=k)

    raw = {"Label": labels, "a": values, "b": values}
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["Label", "a", "b"],
        }
    )

    test = TriStateIndexTable()

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
    assert len(result) == k


def test_TriStateIndexTable_equals():
    k = 100
    labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(k)]))
    values = random.choices(VALID_ENTRIES, k=k)

    raw = {"Label": labels, "a": values, "b": values}

    a = pd.DataFrame(raw)
    b = pd.DataFrame(raw)

    assert TriStateIndexTable.equals(a, b)


def test_TriStateIndexTable_not_equals():
    k = 100

    labels1 = list(set([uuid.uuid4().hex[:6].upper() for _ in range(k)]))
    labels2 = list(set([uuid.uuid4().hex[:6].upper() for _ in range(k)]))

    values1 = random.choices(VALID_ENTRIES, k=k)
    values2 = random.choices(VALID_ENTRIES, k=k)

    raw1 = {"Label": labels1, "a": values1, "b": values1}
    raw2 = {"Label": labels2, "c": values2, "d": values2}

    a = pd.DataFrame(raw1)
    b = pd.DataFrame(raw2)

    assert not TriStateIndexTable.equals(a, b)


def test_toText_fromText():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["Label", "a", "b"],
        }
    )
    structure = TriStateIndexTable()

    k = 100
    labels = list(set([uuid.uuid4().hex[:6].upper() for _ in range(k)]))
    values = random.choices(VALID_ENTRIES, k=k)
    raw = {"Label": labels, "a": values, "b": values}

    a = structure.get_data(raw, meta)
    b = structure.get_value(a)
    c = structure.toText(b)

    test = structure.fromText(c, structure.version)

    assert test is not None
    assert test.round(15).equals(a.round(15))


def test_toText_fromText_none():
    structure = TriStateIndexTable()
    c = structure.toText(None)

    assert structure.fromText(c, structure.version) is None
