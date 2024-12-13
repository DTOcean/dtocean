# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2018 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pandas as pd


def installation_phase_cost_output(input_dict):

    '''Collect installation phase cost results in dict for output.

    Args:
        input_dict (dict [-]: Dictionary of installation phase cost data.

    Returns:
        data (dict) [-]: Formatted dictionary for output.

    '''

    data = {"Equipment": input_dict['COST']['Equipment Cost [EUR]'],
            "Fuel": input_dict['COST']['Fuel Cost [EUR]'],
            "Port": input_dict['COST']['Port Cost [EUR]'],
            "Vessel": input_dict['COST']['Vessel Cost [EUR]']}

    return data


def installation_phase_time_result(input_dict):

    '''Collect installation phase time results in dict for output.

    Args:
        input_dict (dict) [-]: Dictionary of installation phase time data.

    Returns:
        data (dict) [-]: Formatted dictionary for output.

    '''

    data = {"Prep": input_dict['TIME']['Preparation Time [h]'],
            "Sea": input_dict['TIME']['Sea Operation Time [h]'],
            "Transit": input_dict['TIME']['Sea Transit Time [h]'],
            "Wait": input_dict['TIME']['Waiting Time [h]'],
            "Total": input_dict['TIME']['Total Time [h]']}

    return data


def installation_phase_date_result(input_dict):
    
    '''Collect installation phase date results in dict for output.

    Args:
        input_dict (dict) [-]: Dictionary of installation phase time data.

    Returns:
        data (dict) [-]: Formatted dictionary for output.

    '''

    data = {"Start": pd.to_datetime(input_dict['DATE']['Start Date']),
            "Depart": pd.to_datetime(input_dict['DATE']['Depart Date']),
            "End": pd.to_datetime(input_dict['DATE']['End Date'])}

    return data


def find_marker_key_mf(nodes_dict, marker, component_type):
    
    '''Locate the parent key of a marker in the a network nodes dictionary.

    Args:
        nodes_dict (dict) [-]: Network nodes dictionary.
        marker (int) [-]: Marker to be found.
        component_type (str) [-]: To focus search, valid values are 'mooring'
                or 'foundation'.

    Returns:
        result (str) [-]: Parent key of marker.
        
    Note:
        This shoud never be allowed to return None. Raise error instead.

    '''

    result = None

    for key, value in nodes_dict.iteritems():

        for system in value:

            if component_type in system.lower():

                local_markers = value[system]["marker"]
                all_markers = \
                        [item for sublist in local_markers for item in sublist]

                if marker in all_markers:

                    result = key

                    return result

    return result
