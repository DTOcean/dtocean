# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es archivo temporal
"""

import os
import glob
import errno
import argparse
import platform

from copy import deepcopy
from collections import Counter, OrderedDict

import numpy as np
import pandas as pd

from yaml import load, safe_dump

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def yaml_to_py(yaml_path):
    
    '''Return the python object interpretation of a yaml file'''
    
    with open(yaml_path, 'r') as yaml_stream:
        
        try:
            pyfmt = load(yaml_stream, Loader=Loader)
        except Exception as e:
            errStr = "File {} produced error:\n{}".format(yaml_path, e)
            raise Exception(errStr)
    
    return pyfmt


def xl_to_dds(xl_path,
              ignore_column=None,
              ignore_missing=True,
              sanitise_keys=True):
    
    '''Read an XL file and produce a dds list of the form expected by
    the DataDefinition boundary class'''
    
    sheets = pd.read_excel(xl_path, sheet_name=None, index_col=0)
    root_sheet = sheets.pop("ROOT", None)
    
    # Drop a column if ignore_column is given
    if ignore_column is not None and ignore_column in root_sheet.columns:
        root_sheet = root_sheet.drop(ignore_column, axis=1)
    
    # Fix the columns if necessary
    if sanitise_keys:
        
        root_cols = root_sheet.columns
        sane_cols = []
        
        for header in root_cols:
            
            sane_header = header.lower()
            sane_header = sane_header.replace(" ", "_")
            
            sane_cols.append(sane_header)
            
        root_sheet.columns = sane_cols
    
    # Test for duplicate indexes
    root_indices = root_sheet.index.tolist()
    
    if len(root_indices) != len(set(root_indices)):
        _raise_dupes_error(xl_path, "root", root_indices)
    
    data = []
    
    for identifier, row in root_sheet.iterrows():
        
        if ignore_missing: row = row.dropna()
        
        member_dict = {"identifier": identifier}
        member_dict.update(row.to_dict())
        
        for key, df in sheets.items():
            
            # Drop a column if ignore_column is given
            if ignore_column is not None and ignore_column in df.columns:
                df = df.drop(ignore_column, 1)
            
            # Fix the key if you need to
            if sanitise_keys:
                
                sane_key = key.lower()
                sane_key = sane_key.replace(" ", "_")
            
            else:
                
                sane_key = key
            
            # Test for duplicate indexes
            sheet_indices = df.index.tolist()
            
            if len(sheet_indices) != len(set(sheet_indices)):
                _raise_dupes_error(xl_path, key, sheet_indices)
            
            # Test for erroneous indexes
            erroneous_indices = set(sheet_indices) - set(root_indices)
            
            if erroneous_indices:
                
                safe_indices = [str(x) for x in erroneous_indices]
                erroneous_str = ", ".join(safe_indices)
                
                errStr = ("The following erroneous indentifiers were found in "
                          "the {} sheet of file {}: {}").format(key,
                                                                xl_path,
                                                                erroneous_str)
                raise KeyError(errStr)
            
            if identifier in df.index:
                
                keyseries = df.loc[identifier].dropna()
                keyseries = keyseries.replace("-", np.nan)
                keyseries = keyseries.where(pd.notnull(keyseries), None)
                
                if keyseries.empty:
                    
                    errStr = ("No values are set for variable {} in sheet "
                              "{}").format(identifier, key)
                    raise ValueError(errStr)
                
                # Catch AttributeErrors here
                try:
                    
                    member_dict[sane_key] = keyseries.tolist()
                
                except AttributeError as e:
                    
                    errStr = ("The following AttributeError occurred reading "
                              'file {}, sheet "{}", indentifier "{}":'
                              '\n{}').format(xl_path, key, identifier, e)
                    raise AttributeError(errStr)
        
        data.append(member_dict)
    
    return data


def dds_merge(original_list, update_list, verbose=False):
    
    original_dict = {}
    update_dict = {}
    merged_list = []
    
    for original in original_list:
        original_dict[original['identifier']] = deepcopy(original)
    
    for update in update_list:
        update_dict[update['identifier']] = deepcopy(update)
    
    for identifier, update in update_dict.items():
        
        merged = {}
        
        if identifier in original_dict:
            
            original = original_dict.pop(identifier)
            
            for key, update_value in update.items():
                
                merged[key] = update_value
                
                if key in original:
                    
                    original_value = original[key]
                    
                    if update_value != original_value and verbose:
                        
                        print("Modified field {} for indentifier "
                              "{}".format(key, identifier))
                    
                    original.pop(key)
                
                elif verbose:
                    
                    print("Added field {} for indentifier "
                          "{}".format(key, identifier))
            
            for key, original_value in original.items():
                
                merged[key] = original_value
            
            merged_list.append(merged)
        
        else:
            
            if verbose: print("Added indentifier {}".format(identifier))
            
            merged_list.append(update)
    
    for identifier, original in original_dict.items():
        
        if verbose: print("Indentifier {} is missing".format(identifier))
        
        merged_list.append(original)
    
    return merged_list


def xl_to_data_yaml(xl_path,
                    yaml_path,
                    ignore_column=None,
                    ignore_missing=True,
                    sanitise_keys=True):
    
    '''Read an XL file and produce a yaml file of the form expected by
    the DataDefinition boundary class'''
    
    data = xl_to_dds(xl_path,
                     ignore_column,
                     ignore_missing,
                     sanitise_keys)
    
    with open(yaml_path, 'w') as outfile:
        safe_dump(data,
                  outfile,
                  default_flow_style=False,
                  encoding='utf-8',
                  allow_unicode=True,
                  explicit_start=True)
    
    return


def dds_to_xl(dds_list,
              xl_path,
              root_cols=None):
    
    '''1. Find all keys with string or list values
       2. Iterate through the dds_list populating dictionaries for each string
          key using none if the data does not exist
       3. List keys for their own sheets with dummy column headers
       4. Build pandas tables
       5. Write the tables to an XL file
    '''
    
    root_keys = set()
    list_keys = set()
    
    for definition in dds_list:
        
        for key, value in definition.items():
            
            if isinstance(value, list):
                
                list_keys = list_keys | {key}
                
            else:
                
                root_keys = root_keys | {key}
    
    root_dict = {}
    
    for key in root_keys:
        
        value_list = []
        
        for definition in dds_list:
            
            if key in definition:
                
                value = definition[key]
            
            else:
                
                value = None
            
            value_list.append(value)
            
        root_dict[key.capitalize()] = value_list
    
    df_dict = OrderedDict()
    df_dict["ROOT"] = root_dict
    
    for key in list_keys:
        
        temp_dict = {}
        max_length = 0
        
        for definition in dds_list:
            
            if key in definition:
                
                temp_dict[definition["identifier"]] = definition[key]
                
                if len(definition[key]) > max_length:
                    max_length = len(definition[key])
        
        list_dict = {}
        list_dict["Identifier"] = []
        dummy_cols = []
        
        for i in range(max_length):
            
            col_name = "{} {}".format(key.capitalize(), i + 1)
            dummy_cols.append(col_name)
            list_dict[col_name] = []
        
        for identifier, value in temp_dict.items():
            
            list_dict["Identifier"].append(identifier)
            new_value = value[:]
            
            for col in dummy_cols:
                
                if len(new_value) > 0:
                    
                    col_value = new_value.pop(0)
                    
                else:
                    
                    col_value = None
                
                list_dict[col].append(col_value)
        
        df_dict[key.capitalize()] = list_dict
    
    writer = pd.ExcelWriter(xl_path)
    
    for sheet, df_dict in df_dict.items():
        
        if sheet == "ROOT" and root_cols is not None:
                        
            df = pd.DataFrame(df_dict,
                              columns=root_cols)
        
        else:
            
            df = pd.DataFrame(df_dict)
        
        df = df.set_index(["Identifier"])
        df = df.sort_index()
        
        df.to_excel(writer, sheet_name=sheet)
    
    writer.close()
    
    # Fit the columns (Windows only)
    if platform.system() == "Windows":
    
        from win32com.client import Dispatch
        
        excel = Dispatch('Excel.Application')
        wb = excel.Workbooks.Open(os.path.abspath(xl_path))
        
        for i in range(wb.Sheets.Count):
        
            #Activate each sheet
            excel.Worksheets(i + 1).Activate()
            
            #Autofit column in active sheet
            excel.ActiveSheet.Columns.AutoFit()
        
        #Save changes
        wb.Save()
        wb.Close()
    
    return


def xl_merge(original_xl_path,
             updated_xl_path,
             merged_xl_path=None,
             verbose=False,
             dry_run=False,
             preserve_order=True):
    
    if dry_run: verbose = True
    
    if preserve_order:
        
        root_df = pd.read_excel(original_xl_path,
                                sheet_name="ROOT")
        root_cols = root_df.columns.tolist()
        
    else:
        
        root_cols = None
    
    original_dds = xl_to_dds(original_xl_path)
    updated_dds = xl_to_dds(updated_xl_path)
    
    merged_dds = dds_merge(original_dds, updated_dds, verbose)
        
    if dry_run: return
    
    if merged_xl_path is None:
        
         original_root, ext = os.path.splitext(original_xl_path)
         merged_xl_path = original_root + "_merge" + ext
    
    dds_to_xl(merged_dds, merged_xl_path, root_cols)
    
    return


def bootstrap_dds(xl_dir,
                  yaml_dir=None,
                  ignore_column=None,
                  ignore_missing=True,
                  verbose=False):
    
    '''Convert a set of DDS xl files in the first given directory to DDS yaml
    files in the second given directory'''
    
    xl_exts = ('*.xls', '*.xlsx')
    xl_paths = []
    
    # Get all the xl DDS file
    for ext in xl_exts:
        
        search_xl = os.path.join(xl_dir, ext)
        xl_paths.extend(glob.glob(search_xl))
    
    # Filter out temporary buffer files.
    xl_paths = [path for path in xl_paths if "~$" not in path]
    
    for xl_path in xl_paths:
        
        # Construct the path to the yaml DDS
        xl_name = os.path.split(xl_path)[1]
        name = os.path.splitext(xl_name)[0]
        yaml_name = "{}.yaml".format(name)
        
        if yaml_dir is None: yaml_dir = xl_dir
        
        yaml_path = os.path.join(yaml_dir, yaml_name)
        
        if verbose:
            msg = "create DDS file: {}".format(yaml_path)
            print(msg)
        
        # Convert the files
        xl_to_data_yaml(xl_path, yaml_path, ignore_column, ignore_missing)
    
    return


def mkdir_p(path):
    
    '''Create a directory structure based on path. Analagous to mkdir -p.
    
    Args:
      path (str): directory tree to create.
    
    '''
    
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
    
    return


def bootstrap_dds_interface():
    '''Command line interface for bootstrap_dds.
    
    Example:
    
        To get help::
            
            $ bootstrap_dds -h
    
    '''
    
    epiStr = ('''Mathew Topper, Tecnalia (c) 2015.''')
              
    desStr = "Convert XL DDS files to YAML DDS files."

    parser = argparse.ArgumentParser(description=desStr,
                                     epilog=epiStr)
    
    parser.add_argument("xldir",
                        help=("path to directory containing XL files"),
                        type=str)
                        
    parser.add_argument("-o", "--out",
                        help=("alternative directory path for YAML files"),
                        type=str,
                        default=None)
                        
    parser.add_argument("-i", "--ignore",
                        help=("ignore given column name in XL files"),
                        type=str,
                        default=None)
                        
    parser.add_argument("-v", "--verbose",
                        help=("print verbose output"),
                        action='store_true')
    
    args = parser.parse_args()
    
    xldir       = args.xldir
    yamldir     = args.out
    ignorecol   = args.ignore
    verbose     = args.verbose
            
    bootstrap_dds(xldir, yamldir, ignorecol, verbose=verbose)
    
    return


def xl_merge_interface():
    '''Command line interface for xl_merge.
    
    Example:
    
        To get help::
            
            $ xl_merge -h
    
    '''
    
    epiStr = ('''Mathew Topper, Tecnalia (c) 2015.''')
              
    desStr = "Merge two XL DDS files."

    parser = argparse.ArgumentParser(description=desStr,
                                     epilog=epiStr)
    
    parser.add_argument("original",
                        help=("the path to the original XL DDS file"),
                        type=str)
                        
    parser.add_argument("updated",
                        help=("the path to the updated XL DDS file"),
                        type=str)
                        
    parser.add_argument("-o", "--out",
                        help=("alternative path for merged XL DDS file"),
                        type=str,
                        default=None)
                        
    parser.add_argument("-v", "--verbose",
                        help=("print verbose output"),
                        action='store_true')
                        
    parser.add_argument("-d", "--dry-run",
                        help=("print verbose output, without creating a file"),
                        action='store_true')
    
    args = parser.parse_args()
    
    original_path = args.original
    updated_path  = args.updated
    merged_path   = args.out
    verbose       = args.verbose
    dry_run       = args.dry_run
        
    xl_merge(original_path,
             updated_path,
             merged_xl_path=merged_path,
             verbose=verbose,
             dry_run=dry_run)
    
    return


def _raise_dupes_error(file_name, sheet_name, duped_list):
    
    dupes = [item for item, count in Counter(duped_list).items()
                                                            if count > 1]
    dupes_str = "\n".join(format(x) for x in dupes)           
    errStr = ("The following duplicates were found in the {} sheet of "
              "file {}:\n").format(sheet_name, file_name) + dupes_str
              
    raise KeyError(errStr)
