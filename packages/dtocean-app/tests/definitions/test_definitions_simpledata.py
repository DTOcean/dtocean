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


import pytest
from dtocean_core.data import CoreMetaData
from mdo_engine.boundary.interface import Box

from dtocean_app.data.definitions import SimpleData


class DummyMixin:
    def __init__(self):
        self._data = Box()
        self._meta = Box()

    @property
    def data(self) -> Box:
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def meta(self) -> Box:
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = value

    @property
    def parent(self):
        return None


@pytest.fixture
def structure():
    return SimpleData()


@pytest.fixture
def mixin():
    return DummyMixin()


def test_SimpleData_input_valid_values(mocker, structure, mixin):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "valid_values": ["a", "b"],
            "units": ["kg"],
        }
    )
    assert meta.units is not None

    test_data = "a"
    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.ListSelect")
    structure.auto_input(mixin)

    assert widget.call_args.args == (mixin.parent, meta.valid_values)
    assert widget.call_args.kwargs == {
        "unit": meta.units[0],
        "experimental": None,
    }
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_no_type(structure, mixin):
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": "a"})
    structure.auto_input(mixin)

    assert mixin.data.result is None


@pytest.mark.parametrize(
    "ttype, input_widget", [("float", "FloatSelect"), ("int", "IntSelect")]
)
def test_SimpleData_input_number_closed(
    mocker,
    structure,
    ttype,
    input_widget,
    mixin,
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
    assert meta.units is not None

    test_data = 1.0
    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": test_data})

    patch = "dtocean_app.data.definitions.{}".format(input_widget)
    widget = mocker.patch(patch)
    structure.auto_input(mixin)

    assert widget.call_args.args[:2] == (mixin.parent, meta.units[0])
    assert widget.call_args.args[2] > minimum
    assert widget.call_args.args[3] < maximum
    assert widget.return_value._set_value.call_args.args == (test_data,)


@pytest.mark.parametrize(
    "ttype, input_widget", [("float", "FloatSelect"), ("int", "IntSelect")]
)
def test_SimpleData_input_number_open(
    mocker,
    structure,
    ttype,
    input_widget,
    mixin,
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
    assert meta.units is not None

    test_data = 1.0
    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": test_data})

    patch = "dtocean_app.data.definitions.{}".format(input_widget)
    widget = mocker.patch(patch)
    structure.auto_input(mixin)

    assert widget.call_args.args == (
        mixin.parent,
        meta.units[0],
        minimum,
        maximum,
    )
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_str(mocker, structure, mixin):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["str"],
            "units": ["kg"],
        }
    )
    assert meta.units is not None

    test_data = "a"
    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.StringSelect")
    structure.auto_input(mixin)

    assert widget.call_args.args == (mixin.parent, meta.units[0])
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_bool(mocker, structure, mixin):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["bool"],
        }
    )

    test_data = False
    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.BoolSelect")
    structure.auto_input(mixin)

    assert widget.call_args.args == (mixin.parent,)
    assert widget.return_value._set_value.call_args.args == (test_data,)


def test_SimpleData_input_unknown(structure, mixin):
    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "types": ["unknown"],
        }
    )

    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": "a"})
    structure.auto_input(mixin)

    assert mixin.data.result is None


@pytest.mark.parametrize(
    "ttype, units, test_data, expected",
    [
        ("int", None, 1, None),
        ("bool", ["kg"], False, None),
        ("int", ["kg"], 1, "kg"),
    ],
)
def test_SimpleData_output(
    mocker,
    structure,
    ttype,
    units,
    test_data,
    expected,
    mixin,
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

    mixin.meta = Box({"result": meta})
    mixin.data = Box({"result": test_data})

    widget = mocker.patch("dtocean_app.data.definitions.LabelOutput")
    structure.auto_output(mixin)

    assert widget.call_args.args == (mixin.parent, expected)
    assert widget.return_value._set_value.call_args.args == (test_data,)
