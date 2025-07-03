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

import pytest
from mdo_engine.boundary.interface import Box

from dtocean_app.data.definitions import SimpleList, SimpleListColumn


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
            "result": Box(
                {
                    "identifier": "test",
                    "structure": "test",
                    "title": "test",
                    "types": ["str"],
                    "units": None,
                }
            )
        }
    )

    structure.data = Box({"result": None})


def setup_data(structure):
    structure.meta = Box(
        {
            "result": Box(
                {
                    "identifier": "test",
                    "structure": "test",
                    "title": "test",
                    "types": ["str"],
                    "units": None,
                }
            )
        }
    )

    test_data = ["a", "b", "c"]
    structure.data = Box({"result": test_data})


def setup_data_units(structure):
    structure.meta = Box(
        {
            "result": Box(
                {
                    "identifier": "test",
                    "structure": "test",
                    "title": "test",
                    "types": ["str"],
                    "units": ["m"],
                }
            )
        }
    )

    test_data = ["a", "b", "c"]
    structure.data = Box({"result": test_data})


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
def data_units_mixin():
    mixin = DummyMixin()
    setup_data_units(mixin)
    return mixin


def test_SimpleList_output(qtbot, data_mixin):
    test = SimpleList()
    test.auto_output(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_SimpleList_output_units(qtbot, data_units_mixin):
    test = SimpleList()
    test.auto_output(data_units_mixin)
    widget = data_units_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_SimpleList_output_none(qtbot, none_mixin):
    test = SimpleList()
    test.auto_output(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_SimpleListColumn_output(qtbot, data_mixin):
    test = SimpleListColumn()
    test.auto_output(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_SimpleListColumn_output_none(qtbot, none_mixin):
    test = SimpleListColumn()
    test.auto_output(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)
