# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 09:57:15 2016

@author: Mathew Topper
"""

#pylint: disable=C0103,W0622,R0903
class abstractclassmethod(classmethod):
    
    """Not that to make this work, you should place cls() in the abstract
    definition"""

    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)

