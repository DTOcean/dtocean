# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2025 Mathew Topper
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

import pandas as pd
import pytest
from mdo_engine.boundary.interface import Box

from dtocean_app.data.definitions import LineTableExpand


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


def setup_none(structure):
    structure.meta = Box(
        {
            "result": {
                "identifier": "test",
                "structure": "test",
                "title": "test",
                "labels": ["Velocity", "Drag 1"],
                "units": ["a", "b"],
                "valid_values": None,
            }
        }
    )

    structure.data = Box({"result": None})


def setup_data(structure):
    structure.meta = Box(
        {
            "result": {
                "identifier": "test",
                "structure": "test",
                "title": "test",
                "labels": ["Velocity", "Drag"],
                "units": ["a", "b"],
                "valid_values": None,
            }
        }
    )

    velocity = [float(x) for x in range(10)]
    drag1 = [2 * float(x) for x in range(10)]
    drag2 = [3 * float(x) for x in range(10)]

    raw = {"Velocity": velocity, "Drag 1": drag1, "Drag 2": drag2}
    df = pd.DataFrame(raw)

    structure.data = Box({"result": df})


def setup_data_one_unit(structure):
    structure.meta = Box(
        {
            "result": Box(
                {
                    "identifier": "test",
                    "structure": "test",
                    "title": "test",
                    "labels": ["Velocity", "Drag"],
                    "units": ["a"],
                    "valid_values": None,
                }
            )
        }
    )

    velocity = [float(x) for x in range(10)]
    drag1 = [2 * float(x) for x in range(10)]
    drag2 = [3 * float(x) for x in range(10)]

    raw = {"Velocity": velocity, "Drag 1": drag1, "Drag 2": drag2}
    df = pd.DataFrame(raw)

    structure.data = Box({"result": df})


def setup_data_no_unit(structure):
    structure.meta = Box(
        {
            "result": Box(
                {
                    "identifier": "test",
                    "structure": "test",
                    "title": "test",
                    "labels": ["Velocity", "Drag"],
                    "units": None,
                    "valid_values": None,
                }
            )
        }
    )

    velocity = [float(x) for x in range(10)]
    drag1 = [2 * float(x) for x in range(10)]
    drag2 = [3 * float(x) for x in range(10)]

    raw = {"Velocity": velocity, "Drag 1": drag1, "Drag 2": drag2}
    df = pd.DataFrame(raw)

    structure.data = Box({"result": df})


@pytest.fixture
def none_mixin():
    mixin = DummyMixin()
    setup_none(mixin)
    return mixin


@pytest.fixture
def data_mixin():
    mixin = DummyMixin()
    setup_data(mixin)
    return mixin


@pytest.fixture
def data_one_unit_mixin():
    mixin = DummyMixin()
    setup_data_one_unit(mixin)
    return mixin


@pytest.fixture
def data_no_unit_mixin():
    mixin = DummyMixin()
    setup_data_one_unit(mixin)
    return mixin


def test_LineTableExpand_input(qtbot, data_mixin):
    test = LineTableExpand()
    test.auto_input(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_LineTableExpand_input_none(qtbot, none_mixin):
    test = LineTableExpand()
    test.auto_input(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_LineTableExpand_input_one_unit(qtbot, data_one_unit_mixin):
    test = LineTableExpand()
    test.auto_input(data_one_unit_mixin)
    widget = data_one_unit_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_LineTableExpand_input_no_unit(qtbot, data_no_unit_mixin):
    test = LineTableExpand()
    test.auto_input(data_no_unit_mixin)
    widget = data_no_unit_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_LineTableExpand_output(qtbot, data_mixin):
    test = LineTableExpand()
    test.auto_output(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_LineTableExpand_output_none(qtbot, none_mixin):
    test = LineTableExpand()
    test.auto_output(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_LineTableExpand_output_one_unit(qtbot, data_one_unit_mixin):
    test = LineTableExpand()
    test.auto_output(data_one_unit_mixin)
    widget = data_one_unit_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_LineTableExpand_output_no_unit(qtbot, data_no_unit_mixin):
    test = LineTableExpand()
    test.auto_output(data_no_unit_mixin)
    widget = data_no_unit_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)
