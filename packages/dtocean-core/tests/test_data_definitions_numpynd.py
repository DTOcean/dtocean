
# pylint: disable=protected-access

import numpy as np

from dtocean_core.core import Core
from dtocean_core.data.definitions import NumpyND


def test_NumpyND_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures
    
    assert "NumpyND" in all_objs.keys()


def test_NumpyND_equals():
    
    a = np.array([[1, 2, 3],
                  [4, 5, 6]])
    b = np.array([[1, 2, 3],
                  [4, 5, 6]])
    
    assert NumpyND.equals(a, b)


def test_NumpyND_not_equals():
    
    a = np.array([[1, 2, 3],
                  [4, 5, 6]])
    b = np.random.rand(100)
    
    assert not NumpyND.equals(a, b)
