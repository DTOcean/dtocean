from pathlib import Path

import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import (
    AutoFileInput,
    AutoFileOutput,
    Core,
)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import RecommendationDict


def test_RecommendationDict_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "RecommendationDict" in all_objs.keys()


@pytest.mark.parametrize(
    "tinput, ttype",
    [
        ([1, 2], "int"),
        (["hello", "world"], "str"),
        ([True, False], "bool"),
        ([0.5, 0.6], "float"),
    ],
)
def test_RecommendationDict(tinput, ttype):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
        }
    )

    test = RecommendationDict()

    raw = {"a": tinput[0], "b": tinput[1]}
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b["a"] == tinput[0]
    assert b["b"] == tinput[1]


def test_RecommendationDict_get_value_None():
    test = RecommendationDict()
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
def test_RecommendationDict_equals(left, right):
    left_dict = {"a": left[0], "b": left[1]}
    right_dict = {"a": right[0], "b": right[1]}

    assert RecommendationDict.equals(left_dict, right_dict)


@pytest.mark.parametrize(
    "left, right",
    [
        ([1, 2], [1, 3]),
        (["hello", "world"], ["world", "hello"]),
        ([True, False], [True, True]),
        ([0.5, 0.6], [0.5, -0.6]),
    ],
)
def test_RecommendationDict_not_equals(left, right):
    left_dict = {"a": left[0], "b": left[1]}
    right_dict = {"a": right[0], "b": right[1]}

    assert not RecommendationDict.equals(left_dict, right_dict)


@pytest.mark.parametrize("fext", [".csv", ".xls", ".xlsx"])
def test_RecommendationDict_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    raw = {"a": 0.0, "b": 1.0}

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["float"],
        }
    )

    test = RecommendationDict()

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
    fin.meta.result = meta

    fin.connect()
    result = test.get_data(fin.data.result, meta)

    assert result["a"] == 0.0
    assert result["b"] == 1.0


@pytest.mark.parametrize(
    "tinput, ttype",
    [
        ([1, 2], "int"),
        (["hello", "world"], "str"),
        ([True, False], "bool"),
        ([0.5, 0.6], "float"),
    ],
)
def test_toText_fromText(tinput, ttype):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
        }
    )
    structure = RecommendationDict()

    raw = {"a": tinput[0], "b": tinput[1]}
    a = structure.get_data(raw, meta)
    b = structure.get_value(a)
    c = structure.toText(b)

    test = structure.fromText(c, structure.version)
    assert test is not None

    for k, v in a.items():
        assert k in test
        assert test[k] == v


def test_toText_fromText_none():
    structure = RecommendationDict()
    c = structure.toText(None)

    assert structure.fromText(c, structure.version) is None
