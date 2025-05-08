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


import numpy as np
import pytest
from dtocean_core.data import CoreMetaData
from mdo_engine.boundary.interface import Box

from dtocean_app.data.definitions import TableData


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
def meta():
    return CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["index", "a", "b"],
            "units": [None, "kg", None],
            "types": ["int", "float", "str"],
        }
    )


@pytest.fixture
def structure():
    return TableData()


@pytest.fixture
def test_data(meta, structure):
    import random
    import string

    nrows = 100
    idx = range(nrows)
    a = np.random.rand(len(idx))
    letters = string.ascii_lowercase
    b = [random.choice(letters) + random.choice(letters) for _ in idx]
    raw = {"index": idx, "a": a, "b": b}

    return structure.get_data(raw, meta)


@pytest.fixture
def mixin_data(meta, test_data):
    mixin = DummyMixin()
    mixin.data = Box({"result": test_data})
    mixin.meta = Box({"result": meta})
    return mixin


def test_TableData_input(mocker, meta, test_data, structure, mixin_data):
    widget = mocker.patch("dtocean_app.data.definitions.InputDataTable")
    structure.auto_input(mixin_data)

    assert widget.call_args.args == (
        mixin_data.parent,
        meta.labels,
        meta.units,
    )
    assert widget.return_value._set_value.call_args.args == (
        test_data,
        meta.types,
    )


def test_TableData_output(mocker, meta, test_data, structure, mixin_data):
    widget = mocker.patch("dtocean_app.data.definitions.OutputDataTable")
    structure.auto_output(mixin_data)

    assert widget.call_args.args == (
        mixin_data.parent,
        meta.labels,
        meta.units,
    )
    assert widget.return_value._set_value.call_args.args == (test_data,)
