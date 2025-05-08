# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2018 Mathew Topper
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

import numpy as np
import pytest
from mdo_engine.boundary.interface import Box

from dtocean_app.data.definitions import (
    CartesianList,
    CartesianListColumn,
)


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
    structure.parent = None
    structure.meta = Box(
        {"result": {"identifier": "test", "structure": "test", "title": "test"}}
    )

    structure.data = Box({"result": None})


def setup_data(structure):
    structure.parent = None
    structure.meta = Box(
        {"result": {"identifier": "test", "structure": "test", "title": "test"}}
    )

    test_data = np.array([(0, 1), (1, 2)])
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


def test_CartesianList_input(qtbot, data_mixin):
    test = CartesianList()
    test.auto_input(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_CartesianList_input_none(qtbot, none_mixin):
    test = CartesianList()
    test.auto_input(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_CartesianList_output(qtbot, data_mixin):
    test = CartesianList()
    test.auto_output(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_CartesianList_output_none(qtbot, none_mixin):
    test = CartesianList()
    test.auto_output(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_CartesianListColumn_input(qtbot, data_mixin):
    test = CartesianListColumn()
    test.auto_input(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_CartesianListColumn_input_none(qtbot, none_mixin):
    test = CartesianListColumn()
    test.auto_input(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_CartesianListColumn_output(qtbot, data_mixin):
    test = CartesianListColumn()
    test.auto_output(data_mixin)
    widget = data_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_CartesianListColumn_output_none(qtbot, none_mixin):
    test = CartesianListColumn()
    test.auto_output(none_mixin)
    widget = none_mixin.data.result

    widget.show()
    qtbot.addWidget(widget)
