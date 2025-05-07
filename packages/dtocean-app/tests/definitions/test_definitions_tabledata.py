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

import numpy as np
import pytest
from attrdict import AttrDict
from dtocean_core.data import CoreMetaData

from dtocean_app.data.definitions import TableData


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
def structure_empty(meta):
    structure = TableData()
    structure.data = AttrDict({"result": None})
    structure.meta = AttrDict({"result": meta})
    structure.parent = None

    return structure


@pytest.fixture
def test_data(structure_empty):
    import random
    import string

    nrows = 100
    idx = range(nrows)
    a = np.random.rand(len(idx))
    letters = string.ascii_lowercase
    b = [random.choice(letters) + random.choice(letters) for _ in idx]
    raw = {"index": idx, "a": a, "b": b}

    return structure_empty.get_data(raw, structure_empty.meta.result)


@pytest.fixture
def structure_data(structure_empty, test_data):
    structure_empty.data = AttrDict({"result": test_data})
    return structure_empty


def test_TableData_input(mocker, qtbot, meta, test_data, structure_data):
    widget = mocker.patch("dtocean_app.data.definitions.InputDataTable")
    structure_data.auto_input(structure_data)

    assert widget.call_args.args == (
        structure_data.parent,
        meta.labels,
        meta.units,
    )
    assert widget.return_value._set_value.call_args.args == (
        test_data,
        meta.types,
    )


def test_TableData_output(mocker, qtbot, meta, test_data, structure_data):
    widget = mocker.patch("dtocean_app.data.definitions.OutputDataTable")
    structure_data.auto_output(structure_data)

    assert widget.call_args.args == (
        structure_data.parent,
        meta.labels,
        meta.units,
    )
    assert widget.return_value._set_value.call_args.args == (test_data,)
