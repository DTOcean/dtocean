# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:44:44 2014

@author: Mathew Topper
"""

from ..modules.datawell import SPT
from ...boundary.interface import FileInterface, MaskVariable


class SPTInterface(FileInterface):
    
    def __init__(self):
        
        super(SPTInterface, self).__init__()
        
    @classmethod
    def get_valid_extensions(cls):
        
        return [".spt"]
        
    @classmethod
    def declare_id_map(cls):
        
        id_map = {'bearingsDegrees': 'site:wave:dir',
                  'spreadingDegrees': 'site:wave:spread',
                  'skewness': 'site:wave:skewness',
                  'kurtosis': 'site:wave:kurtosis',
                  'frequencies': 'site:wave:freqs',
                  'PSD1D': 'site:wave:PSD1D',
                  'Hm0': 'site:wave:Hm0',
                  'Tz': 'site:wave:Tz',
                  'masked': "masked.variable"
                  }
                  
        return id_map
        
    @classmethod
    def get_name(cls):
        
        return "Datawell SPT File"
        
    @classmethod
    def declare_inputs(cls):
        
        '''Declare all the variables required as inputs by this interface.
        '''
        
        input_list =  [MaskVariable("masked.variable")]
        
        return input_list
        
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
        
    @classmethod        
    def declare_optional(cls):
        
        return None
         
    def connect(self):
        
        super(SPTInterface, self).connect()
        
        # Load the SPT File
        readSPT = SPT()
        readSPT.read(self._path)
        readSPT.make_normalised()
        
        for output in self.declare_outputs():
            
            spt_name = self.valid_id_map.get(output)
            self.data[spt_name] = readSPT.normalised[spt_name]
        
        return

    def put_data(self, *args, **kwargs):
        
        errStr = 'SPT file interface is read-only.'
        
        raise NotImplementedError(errStr)

