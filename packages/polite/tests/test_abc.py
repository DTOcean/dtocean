# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:24:33 2016

@author: Mathew Topper
"""

#pylint: disable=C0103,C0111

import abc
import pytest

from polite.abc import abstractclassmethod

#pylint: disable=C0111,R0903
class ClassBase(object, metaclass=abc.ABCMeta):

    @abstractclassmethod
    def test(cls):
        """Test method"""
        return cls()

#pylint: disable=C0111,R0903
class ClassRegistered(ClassBase):
    
    @classmethod
    def test(cls):
        return True

        
def test_abstractclassmethod_base():
    
    with pytest.raises(TypeError):
        ClassBase.test()


def test_abstractclassmethod_register():
        
    assert ClassRegistered.test()
