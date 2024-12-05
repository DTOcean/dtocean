# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

from aneris.utilities.misc import safe_update

def test_safe_update():
    
    dst = {'a': 1, 'b': 2, 'd': 1}
    src = {'b': 3, 'c': 4, 'd': None}
    
    result = safe_update(dst, src)
    
    assert result.keys() == ['a', 'b', 'd']
    assert result['b'] == 3
    assert result['d'] == 1
    