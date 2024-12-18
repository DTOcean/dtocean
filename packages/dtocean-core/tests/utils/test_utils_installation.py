# -*- coding: utf-8 -*-
"""
Created on Tue Oct 02 16:54:47 2018

@author: Mathew Topper
"""

from pandas import Timestamp

from dtocean_core.utils.installation import installation_phase_date_result


def test_installation_phase_date_result():

    input_dict = {'DATE': {'Start Date': '3/11/2000',
                           'Depart Date': '3/11/2000',
                           'End Date': '3/11/2000'}}
            
    result = installation_phase_date_result(input_dict)
    is_timestamps = [isinstance(x, Timestamp) for x in result.values()]
    
    assert set(result.keys()) == set(['Start', 'End', 'Depart'])
    assert all(is_timestamps)
