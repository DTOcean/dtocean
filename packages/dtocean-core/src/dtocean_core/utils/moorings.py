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


def get_component_dict(component_type,
                       data_table,
                       rope_data=None,
                       sand_data=None,
                       soft_data=None,
                       check_keys=None):
    
    valid_components = ["cable",
                        "chain",
                        "drag anchor",
                        "forerunner assembly",
                        "pile",
                        "rope",
                        "shackle",
                        "swivel"]
        
    if component_type not in valid_components:
        
        valid_str = ", ".join(valid_components)
        errStr = ("Argument system_type must be one of '{}' not "
                  "'{}'").format(valid_str, component_type)
        raise ValueError(errStr)
        
    if component_type in ["drag anchor", "pile"]:
        system_type = "foundation system"
    else:
        system_type = "mooring system"
        
    compdict = {}
    if check_keys is None: check_keys = []
        
    key_ids = data_table["Key Identifier"]
    
    for key_id in key_ids:
        
        # Check for duplicates
        if key_id in check_keys:
            
            errStr = "Key identifier {} has been duplicated".format(key_id)
            raise KeyError(errStr)
        
        # Start building the value dictionary
        data_dict = {"item1": system_type,
                     "item2": component_type}
                     
        record = data_table.loc[data_table['Key Identifier'] == key_id]
    
        # Build shared items
        data_dict["item3"] = record.iloc[0]["Name"]
                              
        # Build component specific items
        if component_type in ["chain", "forerunner assembly"]:
            
            data_dict["item5"] = [record.iloc[0]["Min Break Load"],
                                  record.iloc[0]["Axial Stiffness"]]
            data_dict["item6"] = [record.iloc[0]["Diameter"],
                                  record.iloc[0]["Connecting Length"]]
            data_dict["item7"] = [record.iloc[0]["Dry Mass per Unit Length"],
                                  record.iloc[0]["Wet Mass per Unit Length"]]
            data_dict["item11"] = record.iloc[0]["Cost per Unit Length"]
                                  
        elif component_type in ["shackle", "swivel"]:
            
            data_dict["item5"] = [record.iloc[0]["Min Break Load"],
                                  record.iloc[0]["Axial Stiffness"]]
            data_dict["item6"] = [record.iloc[0]["Nominal Diameter"],
                                  record.iloc[0]["Connecting Length"]]        
            data_dict["item7"] = [record.iloc[0]["Dry Unit Mass"],
                                  record.iloc[0]["Wet Unit Mass"]]
            data_dict["item11"] = record.iloc[0]["Cost"]
                                  
        elif component_type == "pile":
            
            data_dict["item5"] = [record.iloc[0]["Yield Stress"],
                                  record.iloc[0]["Youngs Modulus"]]
            data_dict["item6"] = [record.iloc[0]["Diameter"],
                                  record.iloc[0]["Wall Thickness"]]
            data_dict["item7"] = [record.iloc[0]["Dry Mass per Unit Length"],
                                  record.iloc[0]["Wet Mass per Unit Length"]]
            data_dict["item11"] = record.iloc[0]["Cost per Unit Length"]
    
        elif component_type == "drag anchor":
            
            if sand_data is None or soft_data is None:
                errStr = ("Arguments 'sand_data' and 'soft_data' must be "
                          "supplied if component_type is 'drag anchor'")
                raise ValueError(errStr)
            
            data_dict["item5"] = [record.iloc[0]["Min Break Load"],
                                  record.iloc[0]["Axial Stiffness"]]
            data_dict["item6"] = [record.iloc[0]["Width"],
                                  record.iloc[0]["Depth"],
                                  record.iloc[0]["Height"],
                                  record.iloc[0]["Connecting Size"]]
            data_dict["item7"] = [record.iloc[0]["Dry Unit Mass"],
                                  record.iloc[0]["Wet Unit Mass"]]
            
            # Add anchor coefficients
            sand_coeffs = sand_data.loc[sand_data['Key Identifier'] == key_id]
            soft_coeffs = sand_data.loc[soft_data['Key Identifier'] == key_id]
            
            sand_df = sand_coeffs[['Holding Capacity Coefficient 1',
                                   'Holding Capacity Coefficient 2',
                                   'Penetration Coefficient 1',
                                   'Penetration Coefficient 2']]

            soft_df = soft_coeffs[['Holding Capacity Coefficient 1',
                                   'Holding Capacity Coefficient 2',
                                   'Penetration Coefficient 1',
                                   'Penetration Coefficient 2']]
                                                   
            data_dict["item9"] = {'sand': sand_df.values.tolist()[0],
                                  'soft': soft_df.values.tolist()[0]}
            data_dict["item11"] = record.iloc[0]["Cost"]
                                  
        elif component_type == "rope":
            
            # Build rope axial stiffness list
            if rope_data is None:
                errStr = ("Argument 'rope_data' must be supplied if "
                          "component_type is 'rope'")
                raise ValueError(errStr)
        
            rope_array = rope_data[key_id]
            
            data_dict["item4"] = [record.iloc[0]["Material"]]
            data_dict["item5"] = [record.iloc[0]["Min Break Load"],
                                  rope_array.tolist()]
            data_dict["item6"] = [record.iloc[0]["Diameter"]]
            data_dict["item7"] = [record.iloc[0]["Dry Mass per Unit Length"],
                                  record.iloc[0]["Wet Mass per Unit Length"]]
            data_dict["item11"] = record.iloc[0]["Cost per Unit Length"]
                                  
        elif component_type == "cable":
            
            data_dict["item5"] = [record.iloc[0]["Min Break Load"],
                                  record.iloc[0]["Min Bend Radius"]]
            data_dict["item6"] = [record.iloc[0]["Diameter"]]
            data_dict["item7"] = [record.iloc[0]["Dry Mass per Unit Length"],
                                  record.iloc[0]["Wet Mass per Unit Length"]]
            data_dict["item11"] = record.iloc[0]["Cost per Unit Length"]

        else:
            
            errStr = "RUN FOR THE HILLS!!!!1!!"
            raise RuntimeError(errStr)
        
        compdict[key_id] = data_dict
        check_keys.append(key_id)
    
    return compdict
    
def get_moorings_tables(compdict):
    
    cable_df = pd.DataFrame(columns=[
                            'Key Identifier',
                            'Name',
                            'Min Break Load',
                            'Min Bend Radius',
                            'Diameter',
                            'Dry Mass per Unit Length',
                            'Wet Mass per Unit Length',
                            'Cost per Unit Length',
                            'Environmental Impact'])
    
    chain_df = pd.DataFrame(columns=[
                            'Key Identifier',
                            'Name',
                            'Min Break Load',
                            'Axial Stiffness',
                            'Diameter',
                            'Connecting Length',
                            'Dry Mass per Unit Length',
                            'Wet Mass per Unit Length',
                            'Cost per Unit Length',
                            'Environmental Impact'])
                            
    forerunner_df = pd.DataFrame(columns=[
                            'Key Identifier',
                            'Name',
                            'Min Break Load',
                            'Axial Stiffness',
                            'Diameter',
                            'Connecting Length',
                            'Dry Mass per Unit Length',
                            'Wet Mass per Unit Length',
                            'Cost per Unit Length',
                            'Environmental Impact'])
                            
    shackle_df = pd.DataFrame(columns=[                             
                             'Key Identifier',
                             'Name',
                             'Min Break Load',
                             'Axial Stiffness',
                             'Width',
                             'Depth',
                             'Height',
                             'Nominal Diameter',
                             'Connecting Length',
                             'Dry Unit Mass',
                             'Wet Unit Mass',
                             'Cost',
                             'Environmental Impact'])
                             
    swivel_df = pd.DataFrame(columns=[                             
                             'Key Identifier',
                             'Name',
                             'Min Break Load',
                             'Axial Stiffness',
                             'Width',
                             'Depth',
                             'Height',
                             'Nominal Diameter',
                             'Connecting Length',
                             'Dry Unit Mass',
                             'Wet Unit Mass',
                             'Cost',
                             'Environmental Impact'])
                             
    pile_df = pd.DataFrame(columns=[ 
                             'Key Identifier',
                             'Name',
                             'Yield Stress',
                             'Youngs Modulus',
                             'Diameter',
                             'Wall Thickness',
                             'Dry Mass per Unit Length',
                             'Wet Mass per Unit Length',
                             'Cost per Unit Length',
                             'Environmental Impact'])
                             
    anchor_df = pd.DataFrame(columns=[
                             'Key Identifier',
                             'Name',
                             'Min Break Load',
                             'Axial Stiffness',
                             'Width',
                             'Depth',
                             'Height',
                             'Connecting Size',
                             'Dry Unit Mass',
                             'Wet Unit Mass',
                             'Cost',
                             'Environmental Impact'])
                             
    anchor_sand_df = pd.DataFrame(columns=[
                             'Key Identifier',
                             'Holding Capacity Coefficient 1',
                             'Holding Capacity Coefficient 2',
                             'Penetration Coefficient 1',
                             'Penetration Coefficient 2'])
                             
    anchor_soft_df = pd.DataFrame(columns=[
                             'Key Identifier',
                             'Holding Capacity Coefficient 1',
                             'Holding Capacity Coefficient 2',
                             'Penetration Coefficient 1',
                             'Penetration Coefficient 2'])
                             
    rope_df = pd.DataFrame(columns=[
                             'Key Identifier',
                             'Name',
                             'Material',
                             'Min Break Load',
                             'Diameter',
                             'Dry Mass per Unit Length',
                             'Wet Mass per Unit Length',
                             'Cost per Unit Length',
                             'Environmental Impact'])
                             
    rope_dict = {}
    
    for key_id, data_dict in compdict.iteritems():
        
        values = []
        columns = []
        
        # Get component type
        component_type = data_dict["item2"]

        # Build shared items
        columns.append("Key Identifier")
        values.append(key_id)

        columns.append("Name")
        values.append(data_dict["item3"])       
                              
        # Build component specific items
        if component_type in ["chain", "forerunner assembly"]:
            
            columns.append("Min Break Load")
            values.append(data_dict["item5"][0])
            
            columns.append("Axial Stiffness")
            values.append(data_dict["item5"][1])
            
            columns.append("Diameter")
            values.append(data_dict["item6"][0])
            
            columns.append("Connecting Length")
            values.append(data_dict["item6"][1])
            
            columns.append("Dry Mass per Unit Length")
            values.append(data_dict["item7"][0])
            
            columns.append("Wet Mass per Unit Length")
            values.append(data_dict["item7"][1])
            
            columns.append("Cost per Unit Length")
            values.append(data_dict["item11"])

            record = pd.Series(values, index=columns)
            
            if component_type == "chain":
                chain_df = chain_df.append(record, ignore_index=True)
            else:
                forerunner_df = forerunner_df.append(record, ignore_index=True)
                
        elif component_type in ["shackle", "swivel"]:
            
            columns.append("Min Break Load")
            values.append(data_dict["item5"][0])
            
            columns.append("Axial Stiffness")
            values.append(data_dict["item5"][1])
            
            columns.append("Width")
            values.append(data_dict["item6"][0])
            
            columns.append("Depth")
            values.append(data_dict["item6"][0])
            
            columns.append("Height")
            values.append(data_dict["item6"][0])
            
            columns.append("Nominal Diameter")
            values.append(data_dict["item6"][0])
            
            columns.append("Connecting Length")
            values.append(data_dict["item6"][1])
            
            columns.append("Dry Unit Mass")
            values.append(data_dict["item7"][0])
            
            columns.append("Wet Unit Mass")
            values.append(data_dict["item7"][1])
            
            columns.append("Cost")
            values.append(data_dict["item11"])
            
            record = pd.Series(values, index=columns)
            
            if component_type == "shackle":
                shackle_df = shackle_df.append(record, ignore_index=True)
            else:
                swivel_df = swivel_df.append(record, ignore_index=True)
                
        elif component_type == "pile":
            
            columns.append("Yield Stress")
            values.append(data_dict["item5"][0])
            
            columns.append("Youngs Modulus")
            values.append(data_dict["item5"][1])
            
            columns.append("Diameter")
            values.append(data_dict["item6"][0])
            
            columns.append("Wall Thickness")
            values.append(data_dict["item6"][1])
            
            columns.append("Dry Mass per Unit Length")
            values.append(data_dict["item7"][0])
            
            columns.append("Wet Mass per Unit Length")
            values.append(data_dict["item7"][1])
            
            columns.append("Cost per Unit Length")
            values.append(data_dict["item11"])
            
            record = pd.Series(values, index=columns)
            pile_df = pile_df.append(record, ignore_index=True)
            
        elif component_type == "drag anchor":
            
            columns.append("Min Break Load")
            values.append(data_dict["item5"][0])
            
            columns.append("Axial Stiffness")
            values.append(data_dict["item5"][1])
            
            columns.append("Width")
            values.append(data_dict["item6"][0])
            
            columns.append("Depth")
            values.append(data_dict["item6"][1])
            
            columns.append("Height")
            values.append(data_dict["item6"][2])
            
            columns.append("Connecting Size")
            values.append(data_dict["item6"][3])
            
            columns.append("Dry Unit Mass")
            values.append(data_dict["item7"][0])
            
            columns.append("Wet Unit Mass")
            values.append(data_dict["item7"][1])
            
            columns.append("Cost")
            values.append(data_dict["item11"])
            
            record = pd.Series(values, index=columns)
            anchor_df = anchor_df.append(record, ignore_index=True)

            # Anchor coefficients
            coef_cols = ['Key Identifier',
                         'Holding Capacity Coefficient 1',
                         'Holding Capacity Coefficient 2',
                         'Penetration Coefficient 1',
                         'Penetration Coefficient 2']
            
            sand_list = [key_id]
            soft_list = [key_id]

            sand_list.extend(data_dict["item9"]["sand"])
            soft_list.extend(data_dict["item9"]["soft"])
            
            # Fix error in data
            if len(sand_list) == 4: sand_list.append(0.)
            if len(soft_list) == 4: soft_list.append(0.)

            sand_record = pd.Series(sand_list, index=coef_cols)
            soft_record = pd.Series(soft_list, index=coef_cols)
            
            anchor_sand_df = anchor_sand_df.append(sand_record,
                                                   ignore_index=True)
            anchor_soft_df = anchor_sand_df.append(soft_record,
                                                   ignore_index=True)            

            
        elif component_type == "rope":
                        
            columns.append("Material")
            values.append(data_dict["item4"][0])
            
            columns.append("Min Break Load")
            values.append(data_dict["item5"][0])
            
            columns.append("Diameter")
            values.append(data_dict["item6"][0])
            
            columns.append("Dry Mass per Unit Length")
            values.append(data_dict["item7"][0])
            
            columns.append("Wet Mass per Unit Length")
            values.append(data_dict["item7"][1])
            
            columns.append("Cost per Unit Length")
            values.append(data_dict["item11"])
            
            record = pd.Series(values, index=columns)
            rope_df = rope_df.append(record, ignore_index=True)
            
            # Collect the rope axial stress data
            rope_dict[key_id] = data_dict["item5"][1]

        elif component_type == "cable":
            
            columns.append("Min Break Load")
            values.append(data_dict["item5"][0])
            
            columns.append("Min Bend Radius")
            values.append(data_dict["item5"][1])
            
            columns.append("Diameter")
            values.append(data_dict["item6"][0])
            
            columns.append("Dry Mass per Unit Length")
            values.append(data_dict["item7"][0])
            
            columns.append("Wet Mass per Unit Length")
            values.append(data_dict["item7"][1])
            
            columns.append("Cost per Unit Length")
            values.append(data_dict["item11"])
            
            record = pd.Series(values, index=columns)
            cable_df = cable_df.append(record, ignore_index=True)

        else:
            
            errStr = ("The blue meanies are coming! Or, there was an unknown "
                      "component type: {}").format(component_type)
            raise RuntimeError(errStr)
            

    tables = {"cable": cable_df,
              "chain": chain_df,
              "forerunner assembly": forerunner_df,
              "shackle": shackle_df,
              "swivel": swivel_df,
              "pile": pile_df,
              "drag anchor": anchor_df,
              "drag anchor sand": anchor_sand_df,
              "drag anchor soft": anchor_soft_df,
              "rope": rope_df,
              "rope axial stiffness": rope_dict}
            
    return tables

