# -*- coding: utf-8 -*-

#    Copyright (C) 2025 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=redefined-outer-name,protected-access,unused-argument

import pytest
from attrdict import AttrDict
from dtocean_core.data import CoreMetaData

from dtocean_app.data.definitions import SimpleData


@pytest.fixture
def structure():
    structure = SimpleData()
    structure.parent = None

    return structure


def test_SimpleData_input_valid_values(mocker, qtbot, structure):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "valid_values": ["a", "b"],
            "units": ["kg"],
        }
    )

    test_data = "a"
    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.ListSelect")
    structure.auto_input(structure)

    assert widget.call_args.args == (structure.parent, meta.valid_values)
    assert widget.call_args.kwargs == {
        "unit": meta.units[0],
        "experimental": None,
    }
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_no_type(qtbot, structure):
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": "a"})
    structure.auto_input(structure)

    assert structure.data.result is None


@pytest.mark.parametrize(
    "ttype, input_widget", [("float", "FloatSelect"), ("int", "IntSelect")]
)
def test_SimpleData_input_number_closed(
    mocker, qtbot, structure, ttype, input_widget
):
    minimum = -10.0
    maximum = 10.0
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
            "units": ["kg"],
            "minimums": [minimum],
            "maximums": [maximum],
        }
    )

    test_data = 1.0
    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": test_data})

    patch = "dtocean_app.data.definitions.{}".format(input_widget)
    widget = mocker.patch(patch)
    structure.auto_input(structure)

    assert widget.call_args.args[:2] == (structure.parent, meta.units[0])
    assert widget.call_args.args[2] > minimum
    assert widget.call_args.args[3] < maximum
    assert widget.return_value._set_value.call_args.args == (test_data,)


@pytest.mark.parametrize(
    "ttype, input_widget", [("float", "FloatSelect"), ("int", "IntSelect")]
)
def test_SimpleData_input_number_open(
    mocker, qtbot, structure, ttype, input_widget
):
    minimum = -10.0
    maximum = 10.0
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
            "units": ["kg"],
            "minimum_equals": [minimum],
            "maximum_equals": [maximum],
        }
    )

    test_data = 1.0
    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": test_data})

    patch = "dtocean_app.data.definitions.{}".format(input_widget)
    widget = mocker.patch(patch)
    structure.auto_input(structure)

    assert widget.call_args.args == (
        structure.parent,
        meta.units[0],
        minimum,
        maximum,
    )
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_str(mocker, qtbot, structure):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["str"],
            "units": ["kg"],
        }
    )

    test_data = "a"
    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.StringSelect")
    structure.auto_input(structure)

    assert widget.call_args.args == (structure.parent, meta.units[0])
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_bool(mocker, qtbot, structure):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["bool"],
        }
    )

    test_data = False
    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.BoolSelect")
    structure.auto_input(structure)

    assert widget.call_args.args == (structure.parent,)
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_unknown(qtbot, structure):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["unknown"],
        }
    )

    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": "a"})
    structure.auto_input(structure)

    assert structure.data.result is None


@pytest.mark.parametrize(
    "ttype, units, test_data, expected",
    [
        ("int", None, 1, None),
        ("bool", ["kg"], False, None),
        ("int", ["kg"], 1, "kg"),
    ],
)
def test_SimpleData_output(
    mocker, qtbot, structure, ttype, units, test_data, expected
):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": [ttype],
            "units": units,
        }
    )

    structure.meta = AttrDict({"result": meta})
    structure.data = AttrDict({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.LabelOutput")
    structure.auto_output(structure)

    assert widget.call_args.args == (structure.parent, expected)
    assert widget.return_value._set_value.call_args.args == (test_data,)
