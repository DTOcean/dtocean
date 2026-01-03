import builtins
import json
from copy import deepcopy

import pandas as pd

from mdo_engine.boundary import Structure


class UnitData(Structure):
    """A single item of data"""

    @property
    def version(self):
        return 1

    def get_data(self, raw, meta_data):
        return raw

    def get_value(self, data):
        return deepcopy(data)

    @staticmethod
    def toText(value):
        return json.dumps(value)

    @staticmethod
    def fromText(data, version):
        if version != 1:
            raise RuntimeError("Data version not recognised")

        return json.loads(data)


class Simple(Structure):
    """Simple single value data such as a bool, str, int or float"""

    @property
    def version(self):
        return 1

    def get_data(self, raw, meta_data):
        simple = raw

        if meta_data._types:
            try:
                simple_type = getattr(builtins, meta_data._types[0])
                simple = simple_type(simple)
            except TypeError:
                errStr = (
                    "Raw data is of incorrect type. Should be {}, but is {}."
                ).format(meta_data._types, type(simple))
                raise TypeError(errStr)

        return simple

    def get_value(self, data):
        return data

    @staticmethod
    def toText(value):
        return json.dumps(value)

    @staticmethod
    def fromText(data, version):
        if version != 1:
            raise RuntimeError("Data version not recognised")

        return json.loads(data)


class SimpleList(Structure):
    """Simple list of value data such as a bool, str, int or float"""

    @property
    def version(self):
        return 1

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

    @staticmethod
    def toText(value):
        return json.dumps(value)

    @staticmethod
    def fromText(data, version):
        if version != 1:
            raise RuntimeError("Data version not recognised")

        return json.loads(data)


class TableData(Structure):
    """Structure represented in a pandas dataframe"""

    @property
    def version(self):
        return 1

    def get_data(self, raw, meta_data):
        dataframe = pd.DataFrame(raw)

        return dataframe

    def get_value(self, data):
        return data.copy()

    @classmethod
    def equals(cls, left, right):
        return left.equals(right)

    @staticmethod
    def toText(value: pd.DataFrame):
        return value.to_json()

    @staticmethod
    def fromText(data, version):
        if version != 1:
            raise RuntimeError("Data version not recognised")

        return pd.read_json(data)
