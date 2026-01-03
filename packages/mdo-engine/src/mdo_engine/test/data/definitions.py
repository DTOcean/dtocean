import pandas as pd

from mdo_engine.boundary import Structure


class SeriesData(Structure):
    """Structure represented in a series of some sort"""

    @property
    def version(self):
        return 1

    def get_data(self, raw, meta_data):
        series = pd.Series(raw)

        return series

    def get_value(self, data):
        return data.copy()

    @classmethod
    def equals(cls, left, right):
        return left.equals(right)

    @staticmethod
    def toText(value: pd.Series):
        return value.to_json()

    @staticmethod
    def fromText(data, version) -> pd.Series:
        if version != 1:
            raise RuntimeError("Data version not recognised")

        return pd.read_json(data, typ="series")


class AnotherStructure(Structure):
    @property
    def version(self):
        return 1

    def get_data(self, raw, meta_data):
        pass

    def get_value(self, data):
        pass

    @staticmethod
    def toText(value):
        return ""

    @staticmethod
    def fromText(data, version):
        if version != 1:
            raise RuntimeError("Data version not recognised")


class AnotherStructureSubClass(AnotherStructure):
    pass
