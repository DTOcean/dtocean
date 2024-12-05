# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 15:11:50 2018

@author: Mathew Topper
"""

from aneris.boundary.data import Structure


class ConcreteStructure(Structure):
    
    def get_data(self, raw, meta_data):
        
        return
    
    def get_value(self, data):
        
        return


def test_structure_load_data_importerror(monkeypatch):
    
    def mockerror(path):
        raise ImportError
    
    def mockreturn(path):
        return True
    
    monkeypatch.setattr("pickle.load", mockerror)
    monkeypatch.setattr("pandas.read_pickle", mockreturn)
    
    test = ConcreteStructure()
    x = test.load_data(__file__)
    
    assert x


def test_structure_equals():
    
    test = ConcreteStructure()
    x = test.equals(1, 1)
    
    assert x


def test_structure_not_equals():
    
    test = ConcreteStructure()
    x = test.equals(1, 2)
    
    assert not x
