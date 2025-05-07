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

import pytest
import pandas as pd

from dtocean_app.widgets.output import OutputDataTable


def test_OutputDataTable(qtbot):
        
    window = OutputDataTable(None,
                             ["Test1", "Test2"],
                             units=["test", "test"])
    window.show()
    qtbot.addWidget(window)
    
    assert True


def test_OutputDataTable_set_value(qtbot):
    
    raw_dict = {"Test1": [0, 1, 2, 3],
                "Test2": [0, 1, 4, 9]}
                
    vals_df = pd.DataFrame(raw_dict)
    
    window = OutputDataTable(None,
                             ["Test1", "Test2"],
                             units=["test", "test"])
    window._set_value(vals_df)
    window.show()
    qtbot.addWidget(window)
    
    assert True



def test_OutputDataTable_set_value_None(qtbot):
    
    window = OutputDataTable(None,
                             ["Test1", "Test2"],
                             units=["test", "test"])
    window._set_value(None)
    window.show()
    qtbot.addWidget(window)
    
    assert True


def test_OutputDataTable_set_value_missing_cols(qtbot):
    
    raw_dict = {"Test1": [0, 1, 2, 3]}
                
    vals_df = pd.DataFrame(raw_dict)
    
    window = OutputDataTable(None,
                             ["Test1", "Test2"],
                             units=["test", "test"])
    window._set_value(vals_df)
    window.show()
    qtbot.addWidget(window)
    
    assert True


def test_OutputDataTable_set_value_extra_cols(qtbot):
    
    raw_dict = {"Test1": [0, 1, 2, 3],
                "Test2": [0, 1, 4, 9],
                "Test3": [0, 1, 8, 27]}
                
    vals_df = pd.DataFrame(raw_dict)
    
    window = OutputDataTable(None,
                             ["Test1", "Test2"],
                             units=["test", "test"])
    
    with pytest.raises(ValueError):
        window._set_value(vals_df)
