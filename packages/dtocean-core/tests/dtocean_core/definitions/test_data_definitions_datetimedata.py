import datetime

import pytest

from dtocean_core.core import Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import DateTimeData


def test_DateTimeData_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "DateTimeData" in all_objs.keys()


def test_DateTimeData():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
        }
    )

    test = DateTimeData()

    raw = datetime.datetime.now()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert isinstance(b, datetime.datetime)


def test_DateTimeData_invalid():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
        }
    )

    test = DateTimeData()

    raw = 1.0

    with pytest.raises(TypeError):
        test.get_data(raw, meta)


def test_get_None():
    test = DateTimeData()
    result = test.get_value(None)

    assert result is None


def test_DateTimeData_equals():
    left = datetime.datetime(1979, 9, 25)
    right = datetime.datetime(1979, 9, 25)

    assert DateTimeData.equals(left, right)


def test_DateTimeData_not_equals():
    left = datetime.datetime(1979, 9, 25)
    right = datetime.datetime(1980, 8, 5)

    assert not DateTimeData.equals(left, right)


def test_toText_fromText():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
        }
    )
    structure = DateTimeData()

    raw = datetime.datetime.now()
    a = structure.get_data(raw, meta)
    b = structure.get_value(a)
    c = structure.toText(b)

    assert structure.fromText(c, structure.version) == a


def test_toText_fromText_none():
    structure = DateTimeData()
    c = structure.toText(None)

    assert structure.fromText(c, structure.version) is None
