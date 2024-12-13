# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Adam Collin
#    Copyright (C) 2017-2021 Mathew Topper
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


def set_cables(component_data_df, network_design, hierarchy, db, cable_type):
    
    '''Set cable values in the dataframe.
    
    Args:
    
    Attributes:
    
    Returns:
    
    
    '''
    
    if cable_type == 'static':

        types = ['array', 'export']
        
    elif cable_type == 'dynamic':
        
        types = ['umbilical']
        
    else:
        
        #cable type not recognised
        return

    cables = \
        component_data_df[component_data_df['Installation Type'].isin(types)]

    down_interface_data = control_logic_cables_down(cables,
                                                    network_design,
                                                    hierarchy,
                                                    component_data_df)

    up_interface_data = control_logic_cables_up(cables,
                                                network_design,
                                                component_data_df)

    up_interface_type = get_component_type(up_interface_data["up_marker"],
                                           component_data_df)

    down_interface_type = get_component_type(
            down_interface_data["down_marker"], component_data_df)

    ids = cables.Marker.tolist()
    types = cables['Installation Type'].tolist()
    length = cables.Quantity.tolist()

    mass = []
    diameter = []
    mbr = []
    mbl = []
    
    for _, electrical_component in cables.iterrows():
    
        index = electrical_component['Key Identifier']
        
        mass.append(
            db[db['Key Identifier'] == index][
                                        'Dry Mass per Unit Length'].item())

        diameter.append(
            db[db['Key Identifier'] == index]['Diameter'].item())

        mbr.append(
            db[db['Key Identifier'] == index]['Min Bend Radius'].item())

        mbl.append(
            db[db['Key Identifier'] == index]['Min Break Load'].item())

    total_mass = [None]*len(mass)

    cables_dict = {'Marker': ids,
                   'Type': types,
                   'Length': length,
                   'Upstream Interface Marker':
                       up_interface_data["up_marker"],
                   'Downstream Interface Marker':
                       down_interface_data["down_marker"],
                   'Upstream Interface Type': up_interface_type,
                   'Downstream Interface Type': down_interface_type,
                   'Upstream Component Type': up_interface_data["up_type"],
                   'Upstream Component Id': up_interface_data["up_id"],
                   'Downstream Component Type':
                       down_interface_data["down_type"],
                   'Downstream Component Id': down_interface_data["down_id"],
                   'Mass': mass,
                   'Diameter': diameter,
                   'MBR': mbr,
                   'MBL': mbl,
                   'Total Mass': total_mass}

    cables_df = pd.DataFrame(cables_dict)

    return cables_df


def set_collection_points(component_data_df,
                          network_design,
                          hierarchy,
                          supplementary_data):
    
    '''Define and collect all data to make collection point dataframe.
    
    Args:
        component_data_df
        network_design
        hierarchy

    Attributes:
    
    Returns:
    
    '''

    cp_types = ['substation', 'passive hub']

    collection_points = component_data_df[
            component_data_df['Installation Type'].isin(cp_types)]

    all_interfaces = get_collection_point_interfaces(collection_points,
                                                     network_design,
                                                     component_data_df,
                                                     hierarchy)

    ids = collection_points['Marker'].tolist()

    collection_points_dict = {}    
    mass = []
    x = []
    y = []
    length = []
    width = []
    height = []

    for _, electrical_component in collection_points.iterrows():

        mass.append(
            get_physical(electrical_component, supplementary_data, 'Mass'))

        height.append(
            get_physical(electrical_component, supplementary_data, 'Height')) 

        length.append(
            get_physical(electrical_component, supplementary_data, 'Length')) 

        width.append(
            get_physical(electrical_component, supplementary_data, 'Width'))

        x.append(electrical_component['UTM X'])
        y.append(electrical_component['UTM Y'])

    # convert cp types to wp5 requirements
    all_cp_types = convert_cp_types(collection_points, supplementary_data)

    # These are not active
    pigtail_n = [None]*len(mass)
    pigtail_length = [None]*len(mass)
    pigail_diameter = [None]*len(mass)
    pigtail_cable_mass = [None]*len(mass)
    pigtail_total_mass = [None]*len(mass)

    collection_points_dict = {'Marker': ids,
                              'Type': all_cp_types,
                              'Length': length,
                              'Upstream Interface Marker':
                                      all_interfaces['up_markers'],
                              'Downstream Interface Marker':
                                      all_interfaces['down_markers'],
                              'Upstream Interface Type':
                                      all_interfaces['up_type'],
                              'Downstream Interface Type':
                                      all_interfaces['down_type'],
                              'Mass': mass,
                              'X Coord': x,
                              'Y Coord': y,
                              'Length': length,
                              'Width': width,
                              'Height': height,
                              'N Pigtails': pigtail_n,
                              'Pigtail Length': pigtail_length,
                              'Pigail Diameter': pigail_diameter,
                              'Pigtail Cable Mass': pigtail_cable_mass,
                              'Pigtail Total Mass': pigtail_total_mass
                              }

    collection_points_df = pd.DataFrame(collection_points_dict)

    return collection_points_df


def set_connectors(component_data_df, db):
    
    '''Make connector DataFrame for installation module.
    
    Attributes:
        mass (list)
        length (list)
        width (list)
        height (list)
        mating_force (list)
        demating_force  (list)
    '''

    types = ['wet-mate', 'dry-mate']

    connectors = \
        component_data_df[component_data_df['Installation Type'].isin(types)]

    mass = []
    length = []
    width = []
    height = []
    mating_force = []
    demating_force = []
    markers = []

    for _, connector in connectors.iterrows():

        index = connector['Key Identifier']

        mass.append(
                db[db['Key Identifier'] == index]['Dry Mass'].item())
        
        length.append(
                db[db['Key Identifier'] == index]['Depth'].item())
        
        width.append(
                db[db['Key Identifier'] == index]['Width'].item())
        
        height.append(
                db[db['Key Identifier'] == index]['Height'].item())
        
        mating_force.append(
                db[db['Key Identifier'] == index]['Mating Force'].item())
        
        demating_force.append(
                db[db['Key Identifier'] == index]['Demating Force'].item())
        
        markers.append(connector.Marker)

    connectors_dict = {'Mass': mass,
                       'Length': length,
                       'Width': width,
                       'Height': height,
                       'Mating Force': mating_force,
                       'Demating Force': demating_force,
                       'Marker': markers}

    connector_df = pd.DataFrame(connectors_dict)
    connector_df.set_index('Marker', inplace = True)
    
    return connector_df


def get_physical(cp, cp_data_df, attribute):
    
    cp_marker = cp['Marker']
    val = cp_data_df[cp_data_df.Marker == cp_marker][attribute].item()
    
    return val


def convert_cp_types(all_cps, cp_type_df):
    
    '''Map cp types to wp5 types. Allowed: 'Surface piercing' or 'seabed'.
    
    Args:
        all_cps
        type_df
    
    Attributes:
        all_cp_types
    
    '''

    all_cp_types = []

    for _, electrical_component in all_cps.iterrows():

        cp_marker = electrical_component['Marker']

        local_type = cp_type_df[cp_type_df.Marker == cp_marker].Type.item()

        if local_type == 'subsea':

            all_cp_types.append('seabed')

        else:
            
            all_cp_types.append('surface piercing')
    
    return all_cp_types


def get_collection_point_interfaces(components,
                                    network_design,
                                    component_data_df,
                                    hierarchy):
                                 
    '''Get substation and subhub interfaces.
    
    Returns:
        interfaces (dict) [-]

    '''

    # what other data is needed
    up_interface_marker = []
    up_interface_type = []
    down_interface_marker = []
    down_interface_type = []
    
    for _, electrical_component in components.iterrows():

        marker = electrical_component['Marker']

        system_type = find_marker_key(network_design, marker)
        
        connected_components = get_connected_components(
            network_design, system_type)

        if connected_components is None:
            
            # This should never occur
            pass

        else:

            substation_connections_id = []
            substation_connections_type = []

            parent = find_marker_key(network_design, marker)

            if parent == 'Substation':

                neighbour_markers = \
                    network_design['array']['Export cable']['marker']

#                all_markers = \
#                    [item for sublist in neighbour_markers for item in sublist]
#                    
                all_markers = flatten_list(neighbour_markers)
#                    [item for sublist in neighbour_markers for item in sublist]

                neighbour_marker = all_markers[-1]
                neighbour_type = \
                    get_component_type([neighbour_marker], component_data_df)

                down_interface_type.append(neighbour_type)

                if neighbour_type != 'j-tube':

                    down_interface_marker.append([neighbour_marker])

                else:

                    down_interface_marker.append(None)
                
                local_sys = hierarchy['array']['layout']

            else:

                neighbour_markers = network_design[system_type]['marker']
#                all_markers = \
#                    [item for sublist in neighbour_markers for item in sublist]
                
                all_markers = flatten_list(neighbour_markers)
                
                neighbour_marker = all_markers[-2]
                down_interface_marker.append([neighbour_marker])
                down_interface_type.extend([
                    get_component_type([neighbour_marker], component_data_df)])
                local_sys = hierarchy[parent]['layout']

            for item in local_sys:

                # only want first item - may have to be nested list
                neighbour_markers = network_design[item[0]]['marker']
#                all_markers = \
#                    [item for sublist in neighbour_markers for item in sublist]
                    
                all_markers = flatten_list(neighbour_markers)

                neighbour_marker = all_markers[0]    
                neighbour_type = \
                    get_component_type([neighbour_marker], component_data_df)
                substation_connections_id.append(neighbour_marker)
                substation_connections_type.extend(neighbour_type)

#            if len(substation_connections_type) > 1:
#
#                substation_connections_type = \
#                    flatten_list(substation_connections_type)

            up_interface_type.append(substation_connections_type)       

            if neighbour_type != 'j-tube':

                up_interface_marker.append(substation_connections_id)

            else:

                up_interface_marker.append(None)

    # make dict to return
    interfaces = {"up_markers": up_interface_marker,
                  "up_type": list_as_string(up_interface_type),
                  "down_markers": down_interface_marker,
                  "down_type": list_as_string(down_interface_type)}

    return interfaces


def list_as_string(l):
    
    string_list = [str(item) for item in l]
    
    return string_list


def get_component_type(marker, component_list):
    
    '''Return component type from DataFrame.
    
    Note:
        Some logic to map 'export' and 'array' to cable. May not be needed.

    '''

    component_type = component_list[
            component_list.Marker.isin(marker)]['Installation Type'].tolist()

    if 'N/A' in marker:

        # this the onshore landing point - find location in list and insert
        locale = marker.index("N/A")
        component_type.insert(locale, "landing point")

    if any("hub" in s for s in component_type):

        component_type = 'collection point'

    if any("substation" in s.lower() for s in component_type):

        component_type = 'collection point'
        
    if 'umbilical' in component_type:
        
        component_type = 'dynamic cable'
        
    if 'array' in component_type:
        
        component_type = 'static cable'

    return component_type


def find_marker_key(nodes_dict, marker, return_top_key=False):

    """Locate the parent key of a given marker in a network nodes dictionary
    """
    
    result = None
     
    for key, value in reversed(sorted(nodes_dict.iteritems())):
        
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


def check_neighbour(hierarchy,
                    network_design,
                    system,
                    system_to_find,
                    direction,
                    key):

    '''Add description.
    
    '''
    
    connected_marker = None

    array_systems = ['array', 'export cable', 'substation', 'layout']

    # check down
    if direction ==  'down':

        if system in array_systems:

            if key == 'array':
                
                local_sys = hierarchy['array'][system]
                
            else:
                
                local_sys = hierarchy[key][system]
            
            for item in local_sys:
                
                if system_to_find in item:
                    
                    loc = item.index(system_to_find)
                    
                    if loc == 0:
                        
                        if key == 'array':
                            
                            connected_system = 'collection point'
                            connected_marker = find_collection_point_markers(
                                    'Substation', network_design)

                        else:

                            connected_system = tidy_component_type(key)
                            connected_marker = key + str(' marker')

                            if 'device' in connected_system:

                                connected_marker = int(connected_system[6:])

                            else:
                                
                                connected_marker = key + str(' marker')
                                connected_marker = \
                                    find_collection_point_markers(
                                            key, network_design)
                                        
                    else:

                        connected_system = item[loc - 1]

                        if 'device' in connected_system:

                                connected_marker = int(connected_system[6:])

                        else:
                                
                                connected_marker = key + str(' marker')
#                                find_collection_point_markers()

    if direction == 'up':

        if system in array_systems:

            for item in hierarchy['array'][system]:

                if system_to_find in item:

                    loc = item.index(system_to_find)

                    if len(item) == loc + 1:

                        connected_system = system_to_find

                    else:

                        connected_system = item[loc + 1]

    return connected_system, connected_marker


def find_collection_point_markers(cp, topology):
    
    '''Find collection point marker.

    '''

    if cp == 'Substation':

       marker =  topology['array']['Substation']['marker'][0][0]

    else:

        marker = topology[cp]['marker'][0][-1]

    return marker


def tidy_component_type(key):
    
    if 'subhub' in key:
        
        component = 'collection point'
        
    return component


def find_system_neighbour(hierarchy,
                          network_design,
                          system_to_find,
                          direction):

    if system_to_find.lower() not in ['export cable', 'substation', 'subhub']:

        for key, value in reversed(sorted(hierarchy.iteritems())): 

            if "layout" in value:

                for system in value['layout']:

                    if system_to_find in system:

                        neighbour, neighbour_marker = \
                                check_neighbour(hierarchy,
                                                network_design,
                                                'layout',
                                                system_to_find,
                                                direction,
                                                key)

    return neighbour, neighbour_marker


def flatten_list(i):
    
    return [item for sublist in i for item in sublist]

  
def get_connected_components(network, system):
    
    if system in ['Export cable', 'Substation']:

        connected = network['array'][system]['marker']

    else:
        
        connected = network[system]['marker']
    
    return flatten_list(connected)


def control_logic_cables_down(components,
                              network_design,
                              hierarchy,
                              component_data_df):

    # what other data is needed
    down_interface_marker = []
    down_component_type = []
    down_component_id = []

    for _, electrical_component in components.iterrows():

        marker = electrical_component['Marker']

        system_type = find_marker_key(network_design, marker)
        
        connected_components = get_connected_components(
            network_design, system_type)

        if connected_components is None:
            
            pass
    
        else:
            
            # try to find component in the up direction
            component_idx = connected_components.index(marker)

            # find component in shore direction (down)
            if system_type == 'Export cable':

                down_interface_marker.append('N/A')
                down_component_type.append('N/A')
                down_component_id.append('N/A')
            
            else:
                
                if component_idx == 0:
    
                    down_type, down_m =\
                        find_system_neighbour(
                            hierarchy, network_design, system_type, 'down')
                    down_component_type.append(down_type)
                    down_component_id.append(down_m)
                    
                    if down_type == 'collection point':
                        # get substation marker from substation table
                        down_marker = find_collection_point_markers(
                                        'Substation', network_design)
                        down_interface_marker.append(down_marker)
                        
                        continue
                    
                    # get last marker of system
                    for key, value in network_design.iteritems():
                        
                        if down_type in key:
                            
                            local_sys = value['marker']
                            # get last marker
                            flat_local_sys = flatten_list(local_sys)
                            down_marker = flat_local_sys[-1]
                            down_interface_marker.append(down_marker)
    
                else:
    
                    down = connected_components[component_idx-1]
                    down_type = get_component_type([down], component_data_df)
                    down_interface_marker.append(down)
    
                    if down_type[0] in ['wet-mate', 'dry-mate', 'j-tube']:
    
                        # find what this is connected to
                        connector_idx = connected_components.index(down)
                        
                        if connector_idx > 0:
                            
                            # this exists
                            down_component = \
                                connected_components[connector_idx - 1]

                            down_component_type.append(get_component_type(
                                    [down_component], component_data_df))

                            down_component_id.append(down_component)
                            
                        else:
                            
                            # get next system - cycle through array until valid
                            # marker is found
                            parent = find_marker_key(network_design,
                                                     marker,
                                                     False)
 
                            down_type, down_m = find_system_neighbour(
                                    hierarchy, network_design, parent, 'down')

                            down_component_type.append(down_type)
                            down_component_id.append(down_m)

    # tidy device reference
    clean_down_component_type = ['device' if 'device' in item else item for
                                 item in down_component_type]

    interfaces = {"down_marker": down_interface_marker,
                  "down_type": clean_down_component_type,
                  "down_id": down_component_id}

    return interfaces


def control_logic_cables_up(components, network_design, component_data_df):

    # what other data is needed
    up_interface_marker = []
    up_component_type = []
    up_component_id = []

    for _, electrical_component in components.iterrows():

        marker = electrical_component['Marker']

        system_type = find_marker_key(network_design, marker)
        
        connected_components = get_connected_components(
            network_design, system_type)

        if connected_components is None:
            
            pass
    
        else:

            # try to find component in the up direction
            component_idx = connected_components.index(marker)
            
            if len(connected_components) > component_idx + 1:

                # this exists
                up = connected_components[component_idx + 1]
                up_type = \
                    get_component_type([up], component_data_df)
                up_interface_marker.append(up)

                if up_type[0] in ['wet-mate', 'dry-mate', 'j-tube']:

                    # find what this is connected to
                    connector_idx = connected_components.index(up)
                    
                    if len(connected_components) > connector_idx + 1:

                        # this exists
                        up_component = \
                            connected_components[connector_idx + 1]

                        up_component_type.append(get_component_type(
                                [up_component], component_data_df))

                        up_component_id.append(up_component)

                    else:

                        # get next system
                        parent = find_marker_key(network_design, marker, True)

                        if parent == 'array':

                            parent = 'collection point'
                            
                            # get substation marker from substation table
                            up_m = find_collection_point_markers(
                                    'Substation', network_design)

                        elif 'device' in parent:
                            
                            up_m = int(parent[6:])
                            parent = 'device'
                            
                        up_component_type.append(parent)
                        up_component_id.append(up_m)

            else:

                # find next system in the array
                parent = find_marker_key(network_design, marker, True)

    interfaces = {"up_marker": up_interface_marker,
                  "up_type": up_component_type,
                  "up_id": up_component_id}
                  
    return interfaces


def get_umbilical_terminations(network_design,
                               umbilical_ends,
                               dynamic_cable_df,
                               layout):

    '''Get the upstream and downstream connection coordinates of all dyamic
    cables.

    Args:

    Attributes:

    Returns:

    '''

    markers = []
    upstream_x = []
    upstream_y = []
    downstream_x = []
    downstream_y = []

    for _, cable in dynamic_cable_df.iterrows():

        parent = find_marker_key(network_design, cable.Marker)
        upstream = layout[layout['device [-]'] == parent]
        downstream = umbilical_ends[parent]

        markers.append(cable.Marker)
        upstream_x.append(upstream['x coord [m]'].item())
        upstream_y.append(upstream['y coord [m]'].item())
        downstream_x.append(downstream.x)
        downstream_y.append(downstream.y)

    umbilical_terminations_dict = {'Marker': markers,
                                   'Upstream UTM X': upstream_x,
                                   'Upstream UTM Y': upstream_y,
                                   'Downstream UTM X': downstream_x,
                                   'Downstream UTM Y': downstream_y,}

    umbilical_terminations_df = pd.DataFrame(umbilical_terminations_dict)
    
    return umbilical_terminations_df

def set_cable_cp_references(cables, collection_points):
    
    '''Set static/dynamic cable to collection point references to index
    
    Note:
    
        could be tidied up by improving if/if statement - same op in both

    '''
    
    if collection_points.empty: return cables

    for idx, cable in cables.iterrows():

        if cable['Downstream Component Type'] == 'collection point':
            
            # get index and update component id
            local_marker = cable['Downstream Component Id']
            
            indexed_ref = collection_points[
                collection_points.Marker == local_marker].index.item()

            cables.loc[idx, 'Downstream Component Id'] = indexed_ref

        if cable['Upstream Component Type'] == 'collection point':
            
            # get index and update component id
            local_marker = cable['Upstream Component Id']

            indexed_ref = collection_points[
                    collection_points.Marker == local_marker].index.item()
                
            cables.loc[idx, 'Upstream Component Id'] = indexed_ref

    return cables
