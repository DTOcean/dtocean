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

from attrdict import AttrDict
from dtocean_app.data.definitions import (SimpleList,
                                          SimpleListColumn)


def setup_none(structure):

    structure.parent = None
    structure.meta = AttrDict({'result': AttrDict({"identifier": "test",
                                                   "structure": "test",
                                                   "title": "test",
                                                   "types": ["str"],
                                                   "units": None})})
    
    structure.data = AttrDict({'result': None})
    
    return

 
def setup_data(structure):

    structure.parent = None
    structure.meta = AttrDict({'result': AttrDict({"identifier": "test",
                                                   "structure": "test",
                                                   "title": "test",
                                                   "types": ["str"],
                                                   "units": None})})
    
    test_data = ["a", "b", "c"]
    structure.data = AttrDict({'result': test_data})
    
    return


def setup_data_units(structure):

    structure.parent = None
    structure.meta = AttrDict({'result': AttrDict({"identifier": "test",
                                                   "structure": "test",
                                                   "title": "test",
                                                   "types": ["str"],
                                                   "units": ["m"]})})
    
    test_data = ["a", "b", "c"]
    structure.data = AttrDict({'result': test_data})
    
    return
    
    
def test_SimpleList_output(qtbot):
    
    test = SimpleList()
    setup_data(test)
    
    test.auto_output(test)
    widget = test.data.result
    
    widget.show()
    qtbot.addWidget(widget)
    
    assert True
    
    
def test_SimpleList_output_units(qtbot):
    
    test = SimpleList()
    setup_data_units(test)
    
    test.auto_output(test)
    widget = test.data.result
    
    widget.show()
    qtbot.addWidget(widget)
    
    assert True
    
    
def test_SimpleList_output_none(qtbot):
    
    test = SimpleList()
    setup_none(test)

    test.auto_output(test)
    widget = test.data.result
    
    widget.show()
    qtbot.addWidget(widget)
    
    assert True
    
    
def test_SimpleListColumn_output(qtbot):
    
    test = SimpleListColumn()
    setup_data(test)
    
    test.auto_output(test)
    widget = test.data.result
    
    widget.show()
    qtbot.addWidget(widget)
    
    assert True
    
    
def test_SimpleListColumn_output_none(qtbot):
    
    test = SimpleListColumn()
    setup_none(test)

    test.auto_output(test)
    widget = test.data.result
    
    widget.show()
    qtbot.addWidget(widget)
    
    assert True
