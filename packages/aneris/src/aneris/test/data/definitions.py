
import pandas as pd

from aneris.boundary import Structure


class SeriesData(Structure):
    
    '''Structure represented in a series of some sort'''
    
    def get_data(self, raw, meta_data):
        
        series = pd.Series(raw)
        
        return series
    
    def get_value(self, data):
        
        return data.copy()
    
    @classmethod
    def equals(cls, left, right):
        
        return left.equals(right)
