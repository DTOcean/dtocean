# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 15:11:50 2018

@author: Mathew Topper
"""

from mdo_engine.boundary.data import Structure


class ConcreteStructure(Structure):
    @property
    def version(self):
        return 1

    def get_data(self, raw, meta_data):
        pass

    def get_value(self, data):
        pass

    @staticmethod
    def toText(data):
        return ""

    @staticmethod
    def fromText(data, version):
        if version != 1:
            raise RuntimeError(f"Version {version} not recognised")


def test_structure_equals():
    test = ConcreteStructure()
    x = test.equals(1, 1)

    assert x


def test_structure_not_equals():
    test = ConcreteStructure()
    x = test.equals(1, 2)

    assert not x
