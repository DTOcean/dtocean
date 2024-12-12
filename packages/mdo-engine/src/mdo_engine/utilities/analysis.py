# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 22:45:34 2016

@author: Mathew Topper
"""

import pandas as pd

def get_variable_network(controller,
                         pool,
                         simulation,
                         hub_id):
    
    all_interface_names = controller.get_sequenced_interfaces(simulation,
                                                              hub_id)
    
    required_intermediate_df = pd.DataFrame(columns=["Source",
                                                     "Destination",
                                                     "Identifier"])
                                                     
    optional_intermediate_df = pd.DataFrame(columns=["Source",
                                                     "Destination",
                                                     "Identifier"])
    
    required_input_df = pd.DataFrame(columns=["Type",
                                              "Interface",
                                              "Identifier"])
                                              
    optional_input_df = pd.DataFrame(columns=["Type",
                                              "Interface",
                                              "Identifier"])
                                              
    output_df = pd.DataFrame(columns=["Type", "Interface", "Identifier"])
    
    for interface_name in all_interface_names:
        
        required_intermediate_records = []
        optional_intermediate_records = []
        required_records = []
        optional_records = []
        output_records = []
    
        interface_obj = controller.get_interface_obj(simulation,
                                                     hub_id,
                                                     interface_name)
        
        (input_declaration,
         optional_inputs) = interface_obj.get_inputs()
        
        all_inputs = controller._get_active_inputs(pool,
                                                   simulation,
                                                   input_declaration)
                                                                                          
        for var_id in all_inputs:
            
            if var_id in optional_inputs:
                
                if output_df["Identifier"].isin([var_id]).any():
                    
                    all_interfaces = output_df.loc[
                                                output_df.Identifier == var_id,
                                                "Interface"]
                                                   
                    last_interface = all_interfaces.iloc[-1]
                    
                    optional_intermediate_records.append((last_interface,
                                                          interface_name,
                                                          var_id))
                
                elif optional_input_df["Identifier"].isin([var_id]).any():
                    
                    var_dexes = optional_input_df["Identifier"].isin([var_id])
                    optional_input_df.ix[var_dexes, "Type"] = "Shared"           
                    var_type = "Shared"
                    
                    optional_records.append((var_type,
                                             interface_name,
                                             var_id))
                    
                else:
                    
                    var_type = "Unique"
                    
                    optional_records.append((var_type,
                                             interface_name,
                                             var_id))
                    
            else:
                
                if output_df["Identifier"].isin([var_id]).any():
                    
                    all_interfaces = output_df.loc[
                                                output_df.Identifier == var_id,
                                                "Interface"]
                                                   
                    last_interface = all_interfaces.iloc[-1]
                    
                    required_intermediate_records.append((last_interface,
                                                          interface_name,
                                                          var_id))
                
                elif required_input_df["Identifier"].isin([var_id]).any():
                    
                    var_dexes = required_input_df["Identifier"].isin([var_id])
                    required_input_df.ix[var_dexes, "Type"] = "Shared"           
                    var_type = "Shared"
                    
                    required_records.append((var_type,
                                             interface_name,
                                             var_id))
                    
                else:
                    
                    var_type = "Unique"
                    
                    required_records.append((var_type,
                                             interface_name,
                                             var_id))
                                        
        all_outputs = interface_obj.get_outputs()
        
        for var_id in all_outputs:
            
            if output_df["Identifier"].isin([var_id]).any():
                
                var_dexes = output_df["Identifier"].isin([var_id])
                output_df.ix[var_dexes, "Type"] = "Shared"           
                var_type = "Shared"
                
            else:
                
                var_type = "Unique"
                    
            output_records.append((var_type,
                                   interface_name,
                                   var_id))
                    
        new_required_intermediate = pd.DataFrame.from_records(
                                    required_intermediate_records,
                                    columns=required_intermediate_df.columns)
        required_intermediate_df = required_intermediate_df.append(
                                                new_required_intermediate,
                                                ignore_index=True)
        
        new_required = pd.DataFrame.from_records(
                                            required_records,
                                            columns=required_input_df.columns)
        required_input_df = required_input_df.append(new_required,
                                                     ignore_index=True)
                                                     
        new_optional_intermediate = pd.DataFrame.from_records(
                                    optional_intermediate_records,
                                    columns=optional_intermediate_df.columns)
        optional_intermediate_df = optional_intermediate_df.append(
                                                new_optional_intermediate,
                                                ignore_index=True)
        
        new_optional = pd.DataFrame.from_records(
                                            optional_records,
                                            columns=optional_input_df.columns)
        optional_input_df = optional_input_df.append(new_optional,
                                                     ignore_index=True)
        
        new_output = pd.DataFrame.from_records(
                                            output_records,
                                            columns=output_df.columns)
        output_df = output_df.append(new_output, ignore_index=True)
        
    return (required_input_df,
            optional_input_df,
            output_df,
            required_intermediate_df,
            optional_intermediate_df)

def get_interface_variables(controller,
                            data_catalog,
                            simulation,
                            hub_id,
                            interface_name):

    interface_obj = controller.get_interface_obj(simulation,
                                                 hub_id,
                                                 interface_name)
    
    (input_declaration,
     optional_inputs) = interface_obj.get_inputs(True)
    
    all_outputs = interface_obj.get_outputs()
    
    inputs_raw = {"variable id": [],
                  "variable name": [],
                  "optional": []}

    for var_id in input_declaration:
        
        all_vars = data_catalog.get_variable_identifiers()
        
        if var_id not in all_vars:
            
            errStr = ("Given variable '{}' is not found in the given data "
                      "catalog").format(var_id)
            raise KeyError(errStr)
            
        metadata = data_catalog.get_metadata(var_id)
        
        inputs_raw["variable id"].append(var_id)
        inputs_raw["variable name"].append(metadata.title)
        
        optional = False
        
        if var_id in optional_inputs: optional = True
        
        inputs_raw["optional"].append(optional)
        
    outputs_raw = {"variable id": [],
                   "variable name": []}

    for var_id in all_outputs:
        
        all_vars = data_catalog.get_variable_identifiers()
        
        if var_id not in all_vars:
            
            errStr = ("Given variable '{}' is not found in the given data "
                      "catalog").format(var_id)
            raise KeyError(errStr)
            
        metadata = data_catalog.get_metadata(var_id)
        
        outputs_raw["variable id"].append(var_id)
        outputs_raw["variable name"].append(metadata.title)
        
    # Build pandas tables
    inputs_df = pd.DataFrame(inputs_raw)
    outputs_df = pd.DataFrame(outputs_raw)
    
    # Reset column order
    shared_cols = ["variable id", "variable name"]
    input_cols = shared_cols + ["optional"]
    inputs_df = inputs_df[input_cols]
    outputs_df = outputs_df[shared_cols]
    
    return inputs_df, outputs_df

def count_atomic_variables(variables, catalog, atomic_attr, atomic_structures):
    
    n_atomic = 0
    
    for var_id in variables:
        
        var_meta = catalog.get_metadata(var_id)
        
        if var_meta.structure in atomic_structures:
            
            n_atomic += len(getattr(var_meta, atomic_attr))
            
        else:
            
            n_atomic += 1
            
    return n_atomic
