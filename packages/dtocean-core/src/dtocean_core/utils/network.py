# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2024 Mathew Topper
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

def find_marker_key(nodes_dict, marker, return_top_key=False):
    
    """Locate the parent key of a given marker in a network nodes dictionary
    """
    
    result = None
    
    for key, value in nodes_dict.iteritems():
        
        top_key = key
        
        if "marker" in value:
            
            all_markers = value["marker"]
            all_markers = [item for sublist in all_markers for item in sublist]

            if marker in all_markers:
                result = key
                break
        else:
            
            result = find_marker_key(value, marker)
            break
        
    if result is not None and return_top_key: result = top_key
        
    return result
