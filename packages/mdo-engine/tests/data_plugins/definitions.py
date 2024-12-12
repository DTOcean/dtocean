import builtins
from copy import deepcopy

import pandas as pd

from mdo_engine.boundary import Structure


class UnitData(Structure):
    """A single item of data"""

    def get_data(self, raw, meta_data):
        return raw

    def get_value(self, data):
        return deepcopy(data)


class Simple(Structure):
    """Simple single value data such as a bool, str, int or float"""

    def get_data(self, raw, meta_data):
        simple = raw

        if meta_data._types:
            try:
                simple_type = getattr(builtins, meta_data._types[0])
                simple = simple_type(simple)
            except TypeError:
                errStr = (
                    "Raw data is of incorrect type. Should be " "{}, but is {}."
                ).format(meta_data._types, type(simple))
                raise TypeError(errStr)

        return simple

    def get_value(self, data):
        return data


class SimpleList(Structure):
    """Simple list of value data such as a bool, str, int or float"""

    def get_data(self, raw, meta_data):
        raw_list = raw

        if meta_data._types:
            simple_list = []

            for item in raw_list:
                try:
                    simple_type = getattr(builtins, meta_data._types[0])
                    simple_item = simple_type(item)
                except TypeError:
                    errStr = (
                        "Raw data is of incorrect type. Should be "
                        "{}, but is {}."
                    ).format(meta_data._types[0], type(item))
                    raise TypeError(errStr)

                simple_list.append(simple_item)

        else:
            simple_list = raw_list

        return simple_list

    def get_value(self, data):
        return data[:]


class TableData(Structure):
    """Structure represented in a pandas dataframe"""

    def get_data(self, raw, meta_data):
        dataframe = pd.DataFrame(raw)

        return dataframe

    def get_value(self, data):
        return data.copy()

    @classmethod
    def equals(cls, left, right):
        return left.equals(right)
