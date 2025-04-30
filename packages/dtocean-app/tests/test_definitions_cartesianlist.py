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
from attrdict import AttrDict

from dtocean_app.data.definitions import CartesianList, CartesianListColumn


def setup_none(structure):
    structure.parent = None
    structure.meta = AttrDict(
        {
            "result": AttrDict(
                {"identifier": "test", "structure": "test", "title": "test"}
            )
        }
    )

    structure.data = AttrDict({"result": None})


def setup_data(structure):
    structure.parent = None
    structure.meta = AttrDict(
        {
            "result": AttrDict(
                {"identifier": "test", "structure": "test", "title": "test"}
            )
        }
    )

    test_data = np.array([(0, 1), (1, 2)])
    structure.data = AttrDict({"result": test_data})


def test_CartesianList_input(qtbot):
    test = CartesianList()
    setup_data(test)

    test.auto_input(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True


def test_CartesianList_input_none(qtbot):
    test = CartesianList()
    setup_none(test)

    test.auto_input(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True


def test_CartesianList_output(qtbot):
    test = CartesianList()
    setup_data(test)

    test.auto_output(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True


def test_CartesianList_output_none(qtbot):
    test = CartesianList()
    setup_none(test)

    test.auto_output(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True


def test_CartesianListColumn_input(qtbot):
    test = CartesianListColumn()
    setup_data(test)

    test.auto_input(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True


def test_CartesianListColumn_input_none(qtbot):
    test = CartesianListColumn()
    setup_none(test)

    test.auto_input(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True


def test_CartesianListColumn_output(qtbot):
    test = CartesianListColumn()
    setup_data(test)

    test.auto_output(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True


def test_CartesianListColumn_output_none(qtbot):
    test = CartesianListColumn()
    setup_none(test)

    test.auto_output(test)
    widget = test.data.result

    widget.show()
    qtbot.addWidget(widget)

    assert True
