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


def sanitise_network(raw_dict=None):

    """Make device names lower case"""

    if raw_dict is None: return None

    sane_dict = {}

    for key, value in raw_dict.iteritems():

        if (isinstance(key, basestring) and 
            "device" in key.lower()): key = key.lower()

        elif isinstance(value, list):
            
            no_embed = False

            if not isinstance(value[0], list): 
                value = [value]
                no_embed = True
                
            new_value = []
                
            for embedded in value:
                
                new_embedded = []
    
                for item in embedded:
    
                    if (isinstance(item, basestring) and 
                        "device" in item.lower()): item = item.lower()
                    
                    new_embedded.append(item)
                    
                new_value.append(new_embedded)
                
            if no_embed:
                value = new_value[0]
            else:
                value = new_value

        elif isinstance(value, dict):

            value = sanitise_network(value)

        sane_dict[key] = value

    return sane_dict


