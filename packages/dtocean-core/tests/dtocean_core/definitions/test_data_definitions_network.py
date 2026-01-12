from collections import Counter
from pathlib import Path

import pytest
from mdo_engine.control.factory import InterfaceFactory

from dtocean_core.core import (
    AutoFileInput,
    AutoFileOutput,
    Core,
)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Network

NETWORK = {
    "nodes": {
        "array": {
            "Export cable": {
                "marker": [[0, 1]],
                "quantity": Counter({"6": 1, "17": 1}),
            },
            "Substation": {"marker": [[2]], "quantity": Counter({"12": 1})},
        },
        "device001": {
            "marker": [[35, 8, 9, 32, 33]],
            "quantity": Counter({"2": 1, "6": 3, "id743": 1}),
        },
        "device002": {
            "marker": [[36, 6, 7, 73, 34]],
            "quantity": Counter({"2": 1, "6": 3, "id743": 1}),
        },
    },
    "topology": {
        "array": {
            "Export cable": [["17", "6"]],
            "Substation": [["12"]],
            "layout": [["device002", "device001"]],
        },
        "device001": {"Elec sub-system": [["6", "2", "6", "id743", "6"]]},
        "device002": {"Elec sub-system": [["6", "2", "6", "id743", "6"]]},
    },
}


def test_Network_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "Network" in all_objs.keys()


def test_Network():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
        }
    )

    test = Network()
    a = test.get_data(NETWORK, meta)
    b = test.get_value(a)

    assert "topology" in b
    assert "nodes" in b


def test_get_None():
    test = Network()
    result = test.get_value(None)

    assert result is None


def test_Network_equals():
    assert Network.equals(NETWORK, NETWORK)


def test_Network_not_equals():
    a = NETWORK
    b = {
        "nodes": {
            "array": {
                "Export cable": {
                    "marker": [[0, 1]],
                    "quantity": Counter({"6": 1, "17": 1}),
                },
            }
        },
        "topology": {
            "array": {
                "Export cable": [["17", "6"]],
            }
        },
    }

    assert not Network.equals(a, b)


@pytest.mark.parametrize("fext", [".yaml"])
def test_Network_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_path = Path(test_path)

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
        }
    )

    test = Network()

    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, test)

    fout = FOutCls()
    fout._path = test_path_path
    expected = test.get_data(NETWORK, meta)
    fout.data.result = expected

    fout.connect()

    assert len(tmpdir.listdir()) == 1

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = test_path_path

    fin.connect()
    result = test.get_data(fin.data.result, meta)

    assert expected == result


def test_toText_fromText():
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
        }
    )
    structure = Network()

    a = structure.get_data(NETWORK, meta)
    b = structure.get_value(a)
    c = structure.toText(b)

    assert structure.fromText(c, structure.version) == a


def test_toText_fromText_none():
    structure = Network()
    c = structure.toText(None)

    assert structure.fromText(c, structure.version) is None
