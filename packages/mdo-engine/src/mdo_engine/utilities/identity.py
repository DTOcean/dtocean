# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 16:45:19 2015

@author: Mathew Topper
"""

import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    
    '''Generate a random id'''
    
    id_str = ''.join(random.choice(chars) for _ in range(size))
    
    return id_str
    
def get_unique_id(id_list):
        
        '''Get an id unique to the given list of ids.'''
        
        # Keep trying for a unique id.
        while True:
            
            unique_id = id_generator()
            
            if id_list is None:
                
                break
            
            if unique_id not in id_list:
                
                break
            
        return unique_id
