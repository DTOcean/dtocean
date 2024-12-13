
# pylint: disable=protected-access

import numpy as np
import pandas as pd
import xarray as xr

from dtocean_core.core import Core
from dtocean_core.data.definitions import XGridND


def test_XGridND_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures
    
    assert "XGridND" in all_objs.keys()


def test_XGridND_equals():
    
    data = np.random.rand(4, 3)
    locs = ['IA', 'IL', 'IN']
    times = pd.date_range('2000-01-01', periods=4)
    
    a = xr.DataArray(data, coords=[times, locs], dims=['time', 'space'])
    b = xr.DataArray(data, coords=[times, locs], dims=['time', 'space'])
    
    assert XGridND.equals(a, b)


def test_XGridND_not_equals():
    
    data = np.random.rand(4, 3)
    locs = ['IA', 'IL', 'IN']
    times = pd.date_range('2000-01-01', periods=4)
    
    a = xr.DataArray(data, coords=[times, locs], dims=['time', 'space'])
    
    locs = ['IA', 'IN', 'IL']
    times = pd.date_range('2001-01-01', periods=4)
    
    b = xr.DataArray(data, coords=[times, locs], dims=['time', 'space'])
    
    assert not XGridND.equals(a, b)
