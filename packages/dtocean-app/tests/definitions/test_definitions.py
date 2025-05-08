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


import datetime
from typing import Optional

import numpy as np
import pandas as pd
from mdo_engine.boundary.interface import Box
from PySide6.QtWidgets import QWidget
from shapely.geometry import Point

from dtocean_app.data.definitions import (
    DateTimeDict,
    Histogram,
    NumpyLine,
    PointDict,
    SimpleDict,
    TimeSeries,
)


class DummyMixin:
    def __init__(self):
        self._data = Box()
        self._meta = Box()
        self._parent: Optional[QWidget] = None

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
    def parent(self) -> Optional[QWidget]:
        return self._parent


def test_TimeSeries_input(qtbot):
    test = TimeSeries()
    mixin = DummyMixin()

    rng = pd.date_range("1/1/2011", periods=72, freq="H")
    ts = pd.Series(np.random.randn(len(rng)), index=rng)
    mixin.data = Box({"result": ts})
    mixin.meta = Box({"result": {"labels": None, "units": None}})

    test.auto_input(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_NumpyLine_input(qtbot):
    test = NumpyLine()
    mixin = DummyMixin()

    line = np.array([[0, 0], [1, 2], [2, 2], [3, 3], [4, 4]])
    mixin.data = Box({"result": line})
    mixin.meta = Box({"result": {"labels": None, "units": [None, "m"]}})

    test.auto_input(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_Histogram_input(qtbot):
    test = Histogram()
    mixin = DummyMixin()

    hist = {}
    hist["bins"] = [0, 1, 2, 3, 4, 5]
    hist["values"] = [1, 1, 2, 1, 1]
    mixin.data = Box({"result": hist})
    mixin.meta = Box({"result": {"labels": None, "units": [None, "kg"]}})

    test.auto_input(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_SimpleDict_input(qtbot):
    test = SimpleDict()
    mixin = DummyMixin()

    test_dict = {"a": 1, "b": 2, "c": 3}
    mixin.data = Box({"result": test_dict})
    mixin.meta = Box(
        {
            "result": {
                "labels": None,
                "types": [float],
                "units": ["kg"],
                "valid_values": ["a", "b", "c"],
            }
        }
    )

    test.auto_input(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_SimpleDict_output(qtbot):
    test = SimpleDict()
    mixin = DummyMixin()

    test_dict = {"a": 1, "b": 2, "c": 3}
    mixin.data = Box({"result": test_dict})
    mixin.meta = Box(
        {
            "result": {
                "labels": None,
                "types": [float],
                "units": ["kg"],
                "valid_values": ["a", "b", "c"],
            }
        }
    )

    test.auto_output(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_DateTimeDict_output(qtbot):
    test = DateTimeDict()
    mixin = DummyMixin()

    mydict = {"test": datetime.date(1943, 3, 13)}
    mixin.data = Box({"result": mydict})

    test.auto_output(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_PointDict_input(qtbot):
    test = PointDict()
    mixin = DummyMixin()

    test_dict = {"a": Point([0, 0]), "b": Point([1, 1]), "c": Point([2, 2])}
    mixin.data = Box({"result": test_dict})
    mixin.meta = Box({"result": {"valid_values": ["a", "b", "c"]}})

    test.auto_input(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_PointDict_output(qtbot):
    test = PointDict()
    mixin = DummyMixin()

    test_dict = {"a": Point([0, 0]), "b": Point([1, 1]), "c": Point([2, 2])}
    mixin.data = Box({"result": test_dict})
    mixin.meta = Box({"result": {"valid_values": ["a", "b", "c"]}})

    test.auto_output(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_PointDict3D_input(qtbot):
    test = PointDict()
    mixin = DummyMixin()

    test_dict = {
        "a": Point([0, 0, 0]),
        "b": Point([1, 1, 1]),
        "c": Point([2, 2, 2]),
    }
    mixin.data = Box({"result": test_dict})
    mixin.meta = Box({"result": {"valid_values": ["a", "b", "c"]}})

    test.auto_input(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)


def test_PointDict3D_output(qtbot):
    test = PointDict()
    mixin = DummyMixin()

    test_dict = {
        "a": Point([0, 0, 0]),
        "b": Point([1, 1, 1]),
        "c": Point([2, 2, 2]),
    }
    mixin.data = Box({"result": test_dict})
    mixin.meta = Box({"result": {"valid_values": ["a", "b", "c"]}})

    test.auto_output(mixin)
    widget = mixin.data.result

    widget.show()
    qtbot.addWidget(widget)
