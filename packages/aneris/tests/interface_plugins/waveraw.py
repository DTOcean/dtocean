# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:44:44 2014

@author: Mathew Topper
"""

from aneris.boundary.interface import RawInterface

class OtherRaw(RawInterface):
    
    def __init__(self):
        
        super(OtherRaw, self).__init__()
        
        return
        
    @classmethod
    def get_name(cls):
        
        return "Other Raw Interface"
        
    @classmethod
    def declare_outputs(cls):
        
        '''Declare all the variables required as inputs by this interface.
        '''
        
        output_list =  ['not:a:variable',
                        ]
        
        return output_list
        

class WaveRaw(RawInterface):
    
    def __init__(self):
        
        super(WaveRaw, self).__init__()
        
        return
        
    @classmethod
    def get_name(cls):
        
        return "Wave Data Raw Interface"
        
    @classmethod
    def declare_outputs(cls):
        
        '''Declare all the variables required as inputs by this interface.
        '''
        
        output_list =  ['site:wave:dir',
                        'site:wave:spread',
                        'site:wave:skewness',
                        'site:wave:kurtosis',
                        'site:wave:freqs',
                        'site:wave:PSD1D',
                        'site:wave:Hm0',
                        'site:wave:Tz',
                         ]
        
        return output_list
        
    