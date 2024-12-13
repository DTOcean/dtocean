# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2021 Mathew Topper
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

from collections import OrderedDict

import pandas as pd


def get_component_dict(component_type,
                       data_table_cfr,
                       data_table_ncfr,
                       check_keys=None):

    valid_components = ["chain",
                        "forerunner",
                        "shackle",
                        "swivel",
                        "anchor",
                        "pile",
                        "rope",
                        "static cable",
                        "dynamic cable",
                        "wet mate",
                        "dry mate",
                        "transformer",
                        "collection point",
                        'user-defined']
                         
    if component_type not in valid_components:
        
        valid_str = ", ".join(valid_components)
        errStr = ("Argument system_type must be one of '{}' not "
                  "'{}'").format(valid_str, component_type)
        raise ValueError(errStr)

    if component_type in ["static cable",
                          "dynamic cable",
                          "wet mate",
                          "dry mate",
                          "transformer",
                          "collection point"]:
                              
        system_type = "electrical system"

    elif component_type in ['user-defined']:
                                
        system_type = 'user-defined'
        
    elif component_type in ["drag anchor", "pile"]:
        
        system_type = "foundation system"
        
    else:
        
        system_type = "mooring system"
    
    compdict = {}
    
    if check_keys is None: check_keys = []
    
    key_ids = data_table_cfr["Key Identifier"]
    
    for key_id in key_ids:
        
        # Check for duplicates
        if key_id in check_keys:
            
            errStr = "Key identifier {} has been duplicated".format(key_id)
            raise KeyError(errStr)
        
        # Start building the value dictionary
        data_dict = {"item1": system_type,
                     "item2": component_type}
                     
        record_cfr = data_table_cfr.loc[
                                  data_table_cfr['Key Identifier'] == key_id]
        record_ncfr = data_table_ncfr.loc[
                                  data_table_ncfr['Key Identifier'] == key_id]
    
        # Build shared items

        data_dict["item10"] = {"failratecrit" : [
                                        record_cfr.iloc[0]["Lower Bound"],
                                        record_cfr.iloc[0]["Mean"],
                                        record_cfr.iloc[0]["Upper Bound"]],
                               "failratenoncrit" : [
                                        record_ncfr.iloc[0]["Lower Bound"],
                                        record_ncfr.iloc[0]["Mean"],
                                        record_ncfr.iloc[0]["Upper Bound"]]
                                }
                                
        compdict[key_id] = data_dict
        check_keys.append(key_id)

    return compdict


def get_reliability_tables(compdict):
    
    def key_to_int(df):
        key = 'Key Identifier'
        try:
            df[key] = df[key].astype(int)
        except:
            pass
    
    base_df = pd.DataFrame(columns=['Key Identifier',
                                    'Lower Bound',
                                    'Mean',
                                    'Upper Bound'])
    
    chain_CFR_df = base_df.copy()
    chain_NCFR_df = base_df.copy()
    
    forerunner_CFR_df = base_df.copy()
    forerunner_NCFR_df = base_df.copy()
    
    shackle_CFR_df = base_df.copy()
    shackle_NCFR_df = base_df.copy()
    
    swivel_CFR_df = base_df.copy()
    swivel_NCFR_df = base_df.copy()
    
    anchor_CFR_df = base_df.copy()
    anchor_NCFR_df = base_df.copy()
    
    pile_CFR_df = base_df.copy()
    pile_NCFR_df = base_df.copy()

    rope_CFR_df = base_df.copy()
    rope_NCFR_df = base_df.copy()
    
    static_cable_CFR_df = base_df.copy()
    static_cable_NCFR_df = base_df.copy()
                             
    dynamic_cable_CFR_df = base_df.copy()
    dynamic_cable_NCFR_df = base_df.copy()
    
    wet_mate_CFR_df = base_df.copy()
    wet_mate_NCFR_df = base_df.copy()
    
    dry_mate_CFR_df = base_df.copy()
    dry_mate_NCFR_df = base_df.copy()
    
    transformer_CFR_df = base_df.copy()
    transformer_NCFR_df = base_df.copy()
    
    collection_point_CFR_df = base_df.copy()
    collection_point_NCFR_df = base_df.copy()

    for key_id, data_dict in compdict.iteritems():
        
        # Get component type
        component_type = data_dict["item2"]
        
        values_CFR = []
        values_NCFR = []
        columns = []

        columns.append("Key Identifier")
        values_CFR.append(key_id)
        values_NCFR.append(key_id)
                
        columns.append("Lower Bound")
        values_CFR.append(data_dict["item10"]["failratecrit"][0])
        values_NCFR.append(data_dict["item10"]["failratenoncrit"][0])
        
        columns.append("Mean")
        values_CFR.append(data_dict["item10"]["failratecrit"][1])
        values_NCFR.append(data_dict["item10"]["failratenoncrit"][1])
        
        columns.append("Upper Bound")
        values_CFR.append(data_dict["item10"]["failratecrit"][2])
        values_NCFR.append(data_dict["item10"]["failratenoncrit"][2]) 
        
        record_CFR = pd.Series(values_CFR, index=columns)
        record_NCFR = pd.Series(values_NCFR, index=columns)
        
        # Build component specific items
        if component_type == 'chain':
            
            chain_CFR_df = chain_CFR_df.append(record_CFR,
                                               ignore_index=True)
            chain_NCFR_df = chain_NCFR_df.append(record_NCFR,
                                                 ignore_index=True)
        
        if component_type == 'forerunner assembly':
        
            forerunner_CFR_df = forerunner_CFR_df.append(record_CFR,
                                                         ignore_index=True)
            forerunner_NCFR_df = forerunner_NCFR_df.append(record_NCFR,
                                                           ignore_index=True)
        
        if component_type == 'shackle':
        
            shackle_CFR_df = shackle_CFR_df.append(record_CFR,
                                                   ignore_index=True)
            shackle_NCFR_df = shackle_NCFR_df.append(record_NCFR,
                                                     ignore_index=True)
        
        if component_type == 'swivel':
        
            swivel_CFR_df = swivel_CFR_df.append(record_CFR,
                                                 ignore_index=True)
            swivel_NCFR_df = swivel_NCFR_df.append(record_NCFR,
                                                   ignore_index=True)
        
        if component_type == 'anchor':
        
            anchor_CFR_df = anchor_CFR_df.append(record_CFR,
                                                 ignore_index=True)
            anchor_NCFR_df = anchor_NCFR_df.append(record_NCFR,
                                                   ignore_index=True)
        
        if component_type == 'pile':
        
            pile_CFR_df = pile_CFR_df.append(record_CFR,
                                             ignore_index=True)
            pile_NCFR_df = pile_NCFR_df.append(record_NCFR,
                                               ignore_index=True)
        
        if component_type == 'rope':
        
            rope_CFR_df = rope_CFR_df.append(record_CFR,
                                             ignore_index=True)
            rope_NCFR_df = rope_NCFR_df.append(record_NCFR,
                                               ignore_index=True)
        
        if component_type == 'static cable':
        
            static_cable_CFR_df = static_cable_CFR_df.append(record_CFR,
                                                             ignore_index=True)
            static_cable_NCFR_df = static_cable_NCFR_df.append(
                                                           record_NCFR,
                                                           ignore_index=True)
        
        if component_type == 'dynamic cable':
        
            dynamic_cable_CFR_df = dynamic_cable_CFR_df.append(
                                                        record_CFR,
                                                        ignore_index=True)
            dynamic_cable_NCFR_df = dynamic_cable_NCFR_df.append(
                                                        record_NCFR,
                                                        ignore_index=True)
        
        if component_type == 'wet mate':
        
            wet_mate_CFR_df = wet_mate_CFR_df.append(record_CFR,
                                                     ignore_index=True)
            wet_mate_NCFR_df = wet_mate_NCFR_df.append(record_NCFR,
                                                       ignore_index=True)
        
        if component_type == 'dry mate':
        
            dry_mate_CFR_df = dry_mate_CFR_df.append(record_CFR,
                                                     ignore_index=True)
            dry_mate_NCFR_df = dry_mate_NCFR_df.append(record_NCFR,
                                                       ignore_index=True)
        
        if component_type == 'transformer':
        
            transformer_CFR_df = transformer_CFR_df.append(record_CFR,
                                                           ignore_index=True)
            transformer_NCFR_df = transformer_NCFR_df.append(record_NCFR,
                                                             ignore_index=True)
        
        if component_type == 'collection point':
        
            collection_point_CFR_df = collection_point_CFR_df.append(
                                                            record_CFR,
                                                            ignore_index=True)
            collection_point_NCFR_df = collection_point_NCFR_df.append(
                                                            record_NCFR,
                                                            ignore_index=True)
    
    key_to_int(chain_CFR_df)
    key_to_int(chain_NCFR_df)
    
    key_to_int(forerunner_CFR_df)
    key_to_int(forerunner_NCFR_df)
    
    key_to_int(shackle_CFR_df)
    key_to_int(shackle_NCFR_df)
    
    key_to_int(swivel_CFR_df)
    key_to_int(swivel_NCFR_df)
    
    key_to_int(anchor_CFR_df)
    key_to_int(anchor_NCFR_df)
    
    key_to_int(pile_CFR_df)
    key_to_int(pile_NCFR_df)
    
    key_to_int(rope_CFR_df)
    key_to_int(rope_NCFR_df)
    
    key_to_int(static_cable_CFR_df)
    key_to_int(static_cable_NCFR_df)
    
    key_to_int(dynamic_cable_CFR_df)
    key_to_int(dynamic_cable_NCFR_df)
    
    key_to_int(wet_mate_CFR_df)
    key_to_int(wet_mate_NCFR_df)
    
    key_to_int(dry_mate_CFR_df)
    key_to_int(dry_mate_NCFR_df)
    
    key_to_int(transformer_CFR_df)
    key_to_int(transformer_NCFR_df)
    
    key_to_int(collection_point_CFR_df)
    key_to_int(collection_point_NCFR_df)
    
    tables = {
                'chain CFR': chain_CFR_df,
                'chain NCFR': chain_NCFR_df,
                
                'forerunner CFR': forerunner_CFR_df,
                'forerunner NCFR': forerunner_NCFR_df,
                
                'shackle CFR': shackle_CFR_df,
                'shackle NCFR': shackle_NCFR_df,
                
                'swivel CFR': swivel_CFR_df,
                'swivel NCFR': swivel_NCFR_df,
                
                'anchor CFR': anchor_CFR_df,
                'anchor NCFR': anchor_NCFR_df,
                
                'pile CFR': pile_CFR_df,
                'pile NCFR': pile_NCFR_df,
                
                'rope CFR': rope_CFR_df,
                'rope NCFR': rope_NCFR_df,
                
                'static_cable CFR': static_cable_CFR_df,
                'static_cable NCFR': static_cable_NCFR_df,
                
                'dynamic_cable CFR': dynamic_cable_CFR_df,
                'dynamic_cable NCFR': dynamic_cable_NCFR_df,
                
                'wet_mate CFR': wet_mate_CFR_df,
                'wet_mate NCFR': wet_mate_NCFR_df,
                
                'dry_mate CFR': dry_mate_CFR_df,
                'dry_mate NCFR': dry_mate_NCFR_df,
                
                'transformer CFR': transformer_CFR_df,
                'transformer NCFR': transformer_NCFR_df,
                
                'collection_point CFR': collection_point_CFR_df,
                'collection_point NCFR': collection_point_NCFR_df,
              }

    return tables


def compdict_from_mock(xls_file,
                       default_lower=1.,
                       default_mean=1.,
                       default_upper=1.):
    
    def key_to_int(df):
        key = 'Key Identifier'
        try:
            df[key] = df[key].astype(int)
        except:
            pass
    
    sheet_names = xls_file.sheet_names
    
    base_df = pd.DataFrame(columns=['Key Identifier',
                                    'Lower Bound',
                                    'Mean',
                                    'Upper Bound'])
    
    compdict = {}
    
    for comp_type in sheet_names:
        
        comp_df = xls_file.parse(comp_type)
        CFR_df = base_df.copy()
        NCFR_df = base_df.copy()
        
        for record in comp_df.itertuples():
            
            values_CFR = []
            values_NCFR = []
            columns = []
            
            columns.append("Key Identifier")
            values_CFR.append(record[1])
            values_NCFR.append(record[1])
            
            columns.append("Lower Bound")
            values_CFR.append(default_lower)
            values_NCFR.append(default_lower)
            
            columns.append("Mean")
            values_CFR.append(default_mean)
            values_NCFR.append(default_mean)
            
            columns.append("Upper Bound")
            values_CFR.append(default_upper)
            values_NCFR.append(default_upper) 
            
            record_CFR = pd.Series(values_CFR, index=columns)
            record_NCFR = pd.Series(values_NCFR, index=columns)
            
            CFR_df = CFR_df.append(record_CFR, ignore_index=True)
            NCFR_df = NCFR_df.append(record_NCFR, ignore_index=True)
        
        key_to_int(CFR_df)
        key_to_int(NCFR_df)
        
        comp_type_dict = get_component_dict(comp_type.replace("_", " "),
                                            CFR_df,
                                            NCFR_df,
                                            check_keys=compdict.keys())
        compdict.update(comp_type_dict)
    
    return compdict


def get_reliability_dict(reliability_network,
                         electrical_layout=None):
    
    """Borrows code / ideas from the dtocean-maintenance module, originally
    authored by Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>"""
    
    if electrical_layout is None: electrical_layout = 'radial'
    
    system_ids = []
    subsystem_ids = []
    reliability_metric = []

    # read the failure rates from reliability_network
    for system_group in reliability_network:
        
        if (system_group[0] not in ["PAR", "SER"] and
            system_group[0][1] in ['Substation', 'Export Cable'] and
            'array' in system_group[0][2]):

            reliability_metric.append(system_group[0][-1])
            system_ids.append("-")
            subsystem_ids.append(system_group[0][1])

            continue

        if (electrical_layout == 'radial' or
            electrical_layout == 'singlesidedstring' or
            electrical_layout == 'doublesidedstring'):

            # Groups of devices
            for device_group in system_group:
                
                flagMFSubSystem = False

                # Number of subsystems
                for subsystem in device_group:
                    
                    device_name = subsystem[2]
                    
                    if not 'device' in device_name:
        
                        msgStr = ("Device number not detected in subsystem "
                                  "data. Found '{}'").format(device_name)
                        raise RuntimeError(msgStr)

                    subsystem_name = subsystem[1]

                    # E-Mail of Sam
                    # The first one is for the mooring/Foundation
                    # (mooring line/anchor)
                    if ('M&F sub-system' in subsystem_name and
                        not flagMFSubSystem):

                        subsystem_name += ' mooring foundation'
                        flagMFSubSystem = True

                    #  The second one is for the the umbilical
                    # cable
                    elif ('M&F sub-system' in subsystem_name and
                          flagMFSubSystem):

                        subsystem_name += ' dynamic cable'

                    system_ids.append(device_name)
                    subsystem_ids.append(subsystem_name)

                    # In case of 'singlesidedstring' or
                    # 'doublesidedstring' failure rate is a list
                    subsystem_fr = subsystem[-1]

                    if (type(subsystem_fr) == list and
                        'Array elec sub-system' in subsystem_name):
                        reliability_metric.append(subsystem_fr[1])
                    else:
                        reliability_metric.append(subsystem_fr)

        elif electrical_layout == 'multiplehubs':

            if not 'subhub' in system_group[1][0][0][2]:

                msgStr = ("Subhub not detected in system hierarchy. Found "
                          "'{}'").format(system_group[1][0][0][2])
                raise RuntimeError(msgStr)
            
            # loop over subhubs
            for hub_group in system_group[1]:  

                if ('Substation' in hub_group[0][1] or
                    'Elec sub-system' in hub_group[0][1]):

                    reliability_metric.append(hub_group[0][-1])
                    subsystem_ids.append(hub_group[0][1])
                    system_ids.append(hub_group[0][2])
                    
                    continue

                # device_group
                for device_group in hub_group:

                    flagMFSubSystem = False
                    
                    # Number of subsystems
                    for subsystem in device_group:

                        device_name = subsystem[2]
                        
                        if not 'device' in device_name:
            
                            msgStr = ("Device number not detected in "
                                      "subsystem data. Found '{}'").format(
                                                                  device_name)
                            raise RuntimeError(msgStr)
    
                        subsystem_name = subsystem[1]
                        
                        # E-Mail of Sam
                        # The first one is for the mooring/Foundation
                        # (mooring line/anchor)
                        if ('M&F sub-system' in subsystem_name and
                            not flagMFSubSystem):
    
                            subsystem_name += ' mooring foundation'
                            flagMFSubSystem = True
    
                        #  The second one is for the the umbilical
                        # cable
                        elif ('M&F sub-system' in subsystem_name and
                              flagMFSubSystem):

                            subsystem_name += ' dynamic cable'

                        subsystem_ids.append(subsystem_name)
                        system_ids.append(device_name)
                        reliability_metric.append(subsystem[-1])

    ram_dict = OrderedDict([("system id [-]", system_ids),
                            ("subsystem id [-]", subsystem_ids),
                            ("reliability metric", reliability_metric)])
    
    return ram_dict
