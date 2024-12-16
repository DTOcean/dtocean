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

from __future__ import division, print_function

import argparse
import datetime as dt
import logging

# Standard Library
import os
import re
import shutil
import string
import time

import numpy as np
import pandas as pd

# External modules
import yaml

# DTOcean modules
from mdo_engine.utilities.database import PostgreSQL
from polite_config.configuration import ReadYAML
from polite_config.paths import ModPath, UserDataPath
from shapely import geos, wkb
from win32com.client import Dispatch

# Local modules
from . import SmartFormatter
from .files import onerror

# Set up logging
module_logger = logging.getLogger(__name__)


def bathy_records_to_strata(bathy_records=None, pre_bathy=None):
    """Convert the bathymetry layers table returned by the database into
    Strata structure raw input"""

    loop_start_time = time.clock()

    # Allow a predefined bathymetry table and grid dimensions to be passed
    # instead of the DB records.
    if bathy_records is None and pre_bathy is None:
        errStr = "One of arguments bathy_records or pre_bathy must be given"
        raise ValueError(errStr)

    elif bathy_records is not None:
        bathy_table, xi, yj = init_bathy_records(bathy_records)

    elif pre_bathy is not None:
        bathy_table, xi, yj = pre_bathy

    else:
        return None

    msg = "Building layers..."
    module_logger.debug(msg)

    layers = list(set(bathy_table["layer_order"]))
    layers.sort()

    bathy_layer_groups = bathy_table.groupby("layer_order")

    layer_depths = []
    layer_sediments = []

    for layer in layers:
        layer_table = bathy_layer_groups.get_group(layer)
        layer_depth, layer_sediment = build_bathy_layer(layer_table, xi, yj)

        layer_depths.append(layer_depth)
        layer_sediments.append(layer_sediment)

    depth_array = np.dstack(layer_depths)
    sediment_array = np.dstack(layer_sediments)

    layer_names = ["layer {}".format(x) for x in layers]

    raw_strata = {
        "values": {"depth": depth_array, "sediment": sediment_array},
        "coords": [xi, yj, layer_names],
    }

    loop_end_time = time.clock()
    loop_time = loop_end_time - loop_start_time

    msg = ("Time elapsed building {} layer(s) was " "{} seconds").format(
        len(layers), loop_time
    )
    module_logger.debug(msg)

    return raw_strata


def tidal_series_records_to_xset(tidal_records):
    """Convert the bathymetry layers table returned by the database into
    tidal time series structure raw input"""

    loop_start_time = time.clock()

    msg = "Building DataFrame from {} records".format(len(tidal_records))
    module_logger.debug(msg)

    tidal_table = pd.DataFrame.from_records(
        tidal_records,
        columns=[
            "utm_point",
            "measure_date",
            "measure_time",
            "u",
            "v",
            "turbulence_intensity",
            "ssh",
        ],
    )

    if tidal_table.empty:
        return None

    msg = "Converting PostGIS Point types to coordinates..."
    module_logger.debug(msg)

    tidal_table = point_to_xy(tidal_table)

    msg = "Getting grid extents..."
    module_logger.debug(msg)

    xi, yj = get_grid_coords(tidal_table)

    msg = "Joining dates and times..."
    module_logger.debug(msg)

    tidal_table["datetime"] = [
        dt.datetime.combine(d, t)
        for d, t in zip(
            tidal_table["measure_date"], tidal_table["measure_time"]
        )
    ]

    tidal_table = tidal_table.drop("measure_date", 1)
    tidal_table = tidal_table.drop("measure_time", 1)

    msg = "Building time steps..."
    module_logger.debug(msg)

    steps = list(set(tidal_table["datetime"]))
    steps.sort()

    tidal_table_groups = tidal_table.groupby("datetime")

    u_steps = []
    v_steps = []
    ssh_steps = []
    ti_steps = []

    for step in steps:
        step_table = tidal_table_groups.get_group(step)
        (u_step, v_step, ssh_step, ti_step) = build_tidal_series_step(
            step_table, xi, yj
        )

        u_steps.append(u_step)
        v_steps.append(v_step)
        ssh_steps.append(ssh_step)
        ti_steps.append(ti_step)

    u_array = np.dstack(u_steps)
    v_array = np.dstack(v_steps)
    ssh_array = np.dstack(ssh_steps)
    ti_array = np.dstack(ti_steps)

    raw = {
        "values": {
            "U": u_array,
            "V": v_array,
            "SSH": ssh_array,
            "TI": ti_array,
        },
        "coords": [xi, yj, steps],
    }

    loop_end_time = time.clock()
    loop_time = loop_end_time - loop_start_time

    msg = ("Time elapsed building {} step(s) was " "{} seconds").format(
        len(steps), loop_time
    )
    module_logger.debug(msg)

    return raw


def init_bathy_records(bathy_records):
    msg = "Building DataFrame from {} records".format(len(bathy_records))
    module_logger.debug(msg)

    bathy_cols = ["utm_point", "depth"]
    bathy_cols.extend(["layer_order", "initial_depth", "sediment_type"])

    bathy_table = pd.DataFrame.from_records(bathy_records, columns=bathy_cols)

    if bathy_table.empty:
        return None

    msg = "Converting PostGIS Point types to coordinates..."
    module_logger.debug(msg)

    bathy_table = point_to_xy(bathy_table)

    msg = "Getting grid extents..."
    module_logger.debug(msg)

    xi, yj = get_grid_coords(bathy_table)

    return bathy_table, xi, yj


def point_to_xy(
    df, point_column="utm_point", decimals=2, drop_point_column=True
):
    x = []
    y = []

    for point_hex in df[point_column]:
        point = wkb.loads(point_hex, hex=True)
        coords = list(point.coords)[0]
        x.append(coords[0])
        y.append(coords[1])

    x = np.array(x)
    x = x.round(decimals)

    y = np.array(y)
    y = y.round(decimals)

    df["x"] = x
    df["y"] = y

    if drop_point_column:
        df = df.drop(point_column, 1)

    return df


def get_grid_coords(df, xlabel="x", ylabel="y"):
    xi = np.unique(df[xlabel])
    xdist = xi[1:] - xi[:-1]

    if len(np.unique(xdist)) != 1:
        safe_dist = [str(x) for x in np.unique(xdist)]
        dist_str = ", ".join(safe_dist)
        errStr = (
            "Distances in x-direction are not equal. Unique lengths " "are: {}"
        ).format(dist_str)
        raise ValueError(errStr)

    yj = np.unique(df[ylabel])
    ydist = yj[1:] - yj[:-1]

    if len(np.unique(ydist)) != 1:
        safe_dist = [str(y) for y in np.unique(ydist)]
        dist_str = ", ".join(safe_dist)
        errStr = (
            "Distances in y-direction are not equal. Unique lengths " "are: {}"
        ).format(dist_str)
        raise ValueError(errStr)

    return xi, yj


def build_bathy_layer(layer_table, xi, yj):
    depth_array = np.zeros([len(xi), len(yj)]) * np.nan
    sediment_array = np.full([len(xi), len(yj)], None, dtype="object")

    for record in layer_table.itertuples():
        xidxs = np.where(xi == record.x)[0]
        assert len(xidxs) == 1
        xidx = xidxs[0]

        yidxs = np.where(yj == record.y)[0]
        assert len(yidxs) == 1
        yidx = yidxs[0]

        depth = record.depth - record.initial_depth
        sediment = record.sediment_type

        depth_array[xidx, yidx] = depth
        sediment_array[xidx, yidx] = sediment

    return depth_array, sediment_array


def build_tidal_series_step(step_table, xi, yj):
    u_array = np.zeros([len(xi), len(yj)]) * np.nan
    v_array = np.zeros([len(xi), len(yj)]) * np.nan
    ssh_array = np.zeros([len(xi), len(yj)]) * np.nan
    ti_array = np.zeros([len(xi), len(yj)]) * np.nan

    for record in step_table.itertuples():
        xidxs = np.where(xi == record.x)[0]
        assert len(xidxs) == 1
        xidx = xidxs[0]

        yidxs = np.where(yj == record.y)[0]
        assert len(yidxs) == 1
        yidx = yidxs[0]

        u_array[xidx, yidx] = record.u
        v_array[xidx, yidx] = record.v
        ssh_array[xidx, yidx] = record.ssh
        ti_array[xidx, yidx] = record.turbulence_intensity

    return u_array, v_array, ssh_array, ti_array


def get_table_df(db, schema, table, columns):
    df = pd.read_sql_table(table, db._engine, schema=schema, columns=columns)

    return df


def get_one_from_column(db, schema, table, column):
    Table = db.safe_reflect_table(table, schema)
    result = db.session.query(Table.columns[column]).one_or_none()

    return result


def filter_one_from_column(
    db, schema, table, result_column, filter_column, filter_value
):
    TableTwo = db.safe_reflect_table(table, schema)
    query = db.session.query(TableTwo.columns[result_column])
    result = query.filter(
        TableTwo.columns[filter_column] == filter_value
    ).one_or_none()

    return result


def get_all_from_columns(db, schema, table, columns):
    Table = db.safe_reflect_table(table, schema)

    col_lists = []

    for column in columns:
        col_all = db.session.query(Table.columns[column]).all()
        trim_col = [item[0] for item in col_all]

        col_lists.append(trim_col)

    return col_lists


def database_to_files(
    root_path,
    table_list,
    database,
    schema=None,
    table_name_list=None,
    pid_list=None,
    fid_list=None,
    where_list=None,
    auto_child=False,
    print_function=None,
):
    if print_function is None:
        print_function = print

    def _dump_child(
        root_path,
        table_dict,
        engine,
        schema,
        table_name_list=None,
        pid_list=None,
        fid_list=None,
        where_list=None,
        auto_val=None,
    ):
        child_path = os.path.join(root_path, table_dict["table"])
        if auto_val is not None:
            child_path += str(auto_val)
            auto_child = True
        else:
            auto_child = False

        # dump a directory
        if os.path.exists(child_path):
            shutil.rmtree(child_path, onerror=onerror)

        os.makedirs(child_path)

        # Recurse for the children
        database_to_files(
            child_path,
            table_dict["children"],
            engine,
            schema,
            table_name_list,
            pid_list,
            fid_list,
            where_list,
            auto_child,
            print_function,
        )

        return

    def _autofit_columns(xlpath):
        excel = Dispatch("Excel.Application")
        wb = excel.Workbooks.Open(os.path.abspath(xlpath))

        # Activate second sheet
        excel.Worksheets(1).Activate()

        # Autofit column in active sheet
        excel.ActiveSheet.Columns.AutoFit()

        # Or simply save changes in a current file
        wb.Save()

        wb.Close()

        return

    for table_dict in table_list:
        table_df = None
        new_name_list = None
        new_pid_list = None
        new_fid_list = None
        new_where_list = None

        full_dict = check_dict(table_dict)

        # Set the schema
        if schema is None:
            var_schema = full_dict["schema"]
        else:
            var_schema = schema

        msg_str = "Dumping table: {}.{}".format(var_schema, table_dict["table"])
        print_function(msg_str)

        if not full_dict["dummy"]:
            if table_name_list is None:
                table_idx = 0
                new_name_list = [full_dict["table"]]

            else:
                table_idx = len(table_name_list)
                new_name_list = table_name_list + [full_dict["table"]]

                if fid_list is None:
                    new_fid_list = [full_dict["fkey"]]
                else:
                    new_fid_list = fid_list + [full_dict["fkey"]]

            # Filter by the parent table if required
            query_str = query_builder(
                new_name_list, pid_list, new_fid_list, where_list, var_schema
            )

            msg_str = "Executing query: {}".format(query_str)
            print_function(msg_str)

            # Read the table first
            table_df = pd.read_sql(query_str, database._engine)

            if full_dict["stripf"] and auto_child:
                msg_str = "Stripping column: {}".format(full_dict["fkey"])
                print_function(msg_str)

                table_df = table_df.drop(full_dict["fkey"], 1)

            if full_dict["array"] is not None:
                array_str = ", ".join(full_dict["array"])
                msg_str = "Coverting array columns: {}".format(array_str)
                print_function(msg_str)

                table_df = convert_array(table_df, full_dict["array"])

            if full_dict["bool"] is not None:
                bool_str = ", ".join(full_dict["bool"])
                msg_str = "Coverting boolean columns: {}".format(bool_str)
                print_function(msg_str)

                table_df = convert_bool(table_df, full_dict["bool"])

            if full_dict["geo"] is not None:
                geo_str = ", ".join(full_dict["geo"])
                msg_str = "Coverting Geometry columns: {}".format(geo_str)
                print_function(msg_str)

                table_df = convert_geo(table_df, full_dict["geo"])

            if full_dict["time"] is not None:
                time_str = ", ".join(full_dict["time"])
                msg_str = "Coverting Time columns: {}".format(time_str)
                print_function(msg_str)

                table_df = convert_time(table_df, full_dict["time"])

            if len(table_df) < 1e6:
                table_fname = full_dict["table"] + ".xlsx"
                tab_path = os.path.join(root_path, table_fname)

                msg_str = "Writing to: {}".format(tab_path)
                print_function(msg_str)

                # Create a Pandas Excel writer using XlsxWriter as the engine.
                writer = pd.ExcelWriter(tab_path, engine="xlsxwriter")

                # Convert the dataframe to an XlsxWriter Excel object.
                table_df.to_excel(writer, index=False)

                # Close the Pandas Excel writer and output the Excel file.
                writer.save()

                # Fit the column widths (don't let failure be catastrophic)
                try:
                    _autofit_columns(tab_path)
                except:
                    print_function("*** Column adjust failed. Skipping. ***")
                    pass

            else:
                table_fname = full_dict["table"] + ".csv"
                tab_path = os.path.join(root_path, table_fname)

                msg_str = "Writing to: {}".format(tab_path)
                print_function(msg_str)

                table_df.to_csv(tab_path, index=False)

        if full_dict["children"] is not None:
            # Include pid in iteration
            if full_dict["pkey"] is not None:
                if pid_list is None:
                    new_pid_list = [full_dict["pkey"]]
                else:
                    new_pid_list = pid_list + [full_dict["pkey"]]

            # Check autokey
            if full_dict["autokey"]:
                pkids = table_df[full_dict["pkey"]]
                del table_df

                for pkid in pkids:
                    # Add a where
                    new_where = {"table#": table_idx, "value": pkid}

                    if where_list is None:
                        new_where_list = [new_where]
                    else:
                        new_where_list = where_list + [new_where]

                    _dump_child(
                        root_path,
                        table_dict,
                        database,
                        var_schema,
                        new_name_list,
                        new_pid_list,
                        new_fid_list,
                        new_where_list,
                        pkid,
                    )

            else:
                del table_df

                if where_list is None:
                    new_where_list = None
                else:
                    new_where_list = where_list[:]

                _dump_child(
                    root_path,
                    table_dict,
                    database,
                    var_schema,
                    new_name_list,
                    new_pid_list,
                    new_fid_list,
                    new_where_list,
                )

    return


def database_from_files(
    root_path,
    table_list,
    database,
    schema=None,
    add_fid=None,
    truncate=True,
    drop_missing=True,
    print_function=None,
):
    if print_function is None:
        print_function = print

    def _list_dirs(path, tab_match):
        dir_list = [
            item
            for item in os.listdir(path)
            if os.path.isdir(os.path.join(path, item))
        ]

        match_str = r"^{}[0-9]+".format(tab_match)
        dir_list = [s for s in dir_list if re.search(match_str, s)]
        dir_list.sort()

        return dir_list

    for table_dict in table_list:
        full_dict = check_dict(table_dict)

        # Set the schema
        if schema is None:
            var_schema = full_dict["schema"]
        else:
            var_schema = schema

        if not full_dict["dummy"]:
            xlname = "{}.xlsx".format(full_dict["table"])
            xlpath = os.path.join(root_path, xlname)

            csvname = "{}.csv".format(full_dict["table"])
            csvpath = os.path.join(root_path, csvname)

            # Try to read the table as xl or csv
            if os.path.isfile(xlpath):
                msg_str = "Reading file: {}".format(xlpath)
                print_function(msg_str)

                xl = pd.ExcelFile(xlpath)
                df = xl.parse("Sheet1")

            elif os.path.isfile(csvpath):
                msg_str = "Reading file: {}".format(csvpath)
                print_function(msg_str)

                df = pd.read_csv(csvpath)

            else:
                errStr = (
                    "Table {} could not be found in directory " "{}"
                ).format(full_dict["table"], root_path)
                raise IOError(errStr)

            if add_fid is not None:
                msg_str = ("Adding foreign key '{}' with value: " "{}").format(
                    full_dict["fkey"], add_fid
                )
                print_function(msg_str)

                df[full_dict["fkey"]] = add_fid

            # Get the table name
            dbname = "{}.{}".format(var_schema, full_dict["table"])

            # Clean the table
            if truncate:
                msg_str = "Truncating table: {}".format(dbname)
                print_function(msg_str)

                query_str = "TRUNCATE TABLE {} CASCADE".format(dbname)
                database.execute_transaction(query_str)

            # Drop columns not in the recepting table
            if drop_missing:
                actual_tables = database.get_column_names(
                    full_dict["table"], var_schema
                )
                missing_set = set(df.columns) - set(actual_tables)

                if missing_set:
                    cols_str = ", ".join(missing_set)
                    msg_str = ("Dropping extraneous columns: " "{}").format(
                        cols_str
                    )
                    print_function(msg_str)

                    df = df.drop(missing_set, 1)

            msg_str = "Writing to table: {}".format(dbname)
            print_function(msg_str)

            df.to_sql(
                full_dict["table"],
                database._engine,
                schema=var_schema,
                if_exists="append",
                index=False,
                chunksize=50000,
            )

            del df

        if full_dict["children"] is not None:
            if full_dict["autokey"]:
                tab_dirs = _list_dirs(root_path, full_dict["table"])
                fids = [int(x.split(full_dict["table"])[1]) for x in tab_dirs]

                if not tab_dirs:
                    continue

                first_dir = tab_dirs.pop(0)
                first_fid = fids.pop(0)

                child_path = os.path.join(root_path, first_dir)

                database_from_files(
                    child_path,
                    full_dict["children"],
                    database,
                    var_schema,
                    first_fid,
                    print_function=print_function,
                )

                for next_tab_dir, next_fid in zip(tab_dirs, fids):
                    child_path = os.path.join(root_path, next_tab_dir)

                    database_from_files(
                        child_path,
                        full_dict["children"],
                        database,
                        var_schema,
                        next_fid,
                        False,
                        print_function=print_function,
                    )

            else:
                child_path = os.path.join(root_path, full_dict["table"])

                database_from_files(
                    child_path,
                    full_dict["children"],
                    database,
                    var_schema,
                    truncate=truncate,
                    print_function=print_function,
                )

    return


def query_builder(
    table_list, pid_list=None, fid_list=None, where_list=None, schema=None
):
    def _add_schema(table_name, schema=None):
        if schema is None:
            dbname = table_name
        else:
            dbname = "{}.{}".format(schema, table_name)

        return dbname

    consume_list = table_list[:]
    table_name = _add_schema(consume_list.pop(), schema)

    # No joins or wheres
    if pid_list is None:
        query_str = "SELECT * FROM {};".format(table_name)
        return query_str

    table_shorts = ["t{}".format(i) for i in xrange(len(table_list))]
    consume_shorts = table_shorts[:]
    table_short = consume_shorts.pop()

    query_str = "SELECT {0}.*\nFROM {1} {0}".format(table_short, table_name)

    consume_pid = pid_list[:]

    # Add joins
    if fid_list is not None:
        consume_fid = fid_list[:]

        while consume_list:
            table_fid = consume_fid.pop()
            join_table_pid = consume_pid.pop()
            join_table_name = _add_schema(consume_list.pop(), schema)
            join_table_short = consume_shorts.pop()

            query_str += ("\nJOIN {0} {1} ON {1}.{2} = " "{3}.{4}").format(
                join_table_name,
                join_table_short,
                join_table_pid,
                table_short,
                table_fid,
            )

            table_short = join_table_short

    # Add wheres
    if where_list is not None:
        where_str = None

        for where_dict in where_list:
            table_short = table_shorts[where_dict["table#"]]
            table_pid = pid_list[where_dict["table#"]]
            pid_value = where_dict["value"]

            eq_str = "{}.{} = {}".format(table_short, table_pid, pid_value)

            if where_str is None:
                where_str = "\nWHERE " + eq_str
            else:
                where_str += " AND " + eq_str

        query_str += where_str

    query_str += ";"

    return query_str


def convert_array(table_df, array_cols):
    brackets = string.maketrans("[]", "{}")

    def _safe_square2curly(x):
        if x is None:
            return
        else:
            y = str(x).translate(brackets)
            return y

    for array_col in array_cols:
        table_df[array_col] = table_df[array_col].apply(_safe_square2curly)

    return table_df


def convert_bool(table_df, bool_cols):
    def _safe_bool2str(x):
        if x is None:
            y = None
        elif x:
            y = "yes"
        else:
            y = "no"

        return y

    for bool_col in bool_cols:
        table_df[bool_col] = table_df[bool_col].apply(_safe_bool2str)

    return table_df


def convert_geo(table_df, geo_cols):
    def _safe_to_wkt(x):
        if x is None:
            return
        else:
            geo_shape = wkb.loads(x, hex=True)
            srid = geos.lgeos.GEOSGetSRID(geo_shape._geom)
            if srid > 0:
                result = "SRID={};{}".format(srid, geo_shape.wkt)
            else:
                result = geo_shape.wkt
            return result

    for geo_col in geo_cols:
        table_df[geo_col] = table_df[geo_col].apply(_safe_to_wkt)

    return table_df


def convert_time(table_df, time_cols):
    def _safe_time2str(x):
        if x is None:
            return
        else:
            return x.strftime("%H:%M:%S")

    for time_col in time_cols:
        table_df[time_col] = table_df[time_col].apply(_safe_time2str)

    return table_df


def check_dict(table_dict):
    full_dict = {
        "array": None,
        "autokey": False,
        "bool": None,
        "children": None,
        "dummy": False,
        "fkey": None,
        "geo": None,
        "pkey": None,
        "schema": None,
        "stripf": False,
        "time": None,
    }

    full_dict.update(table_dict)

    if "table" not in full_dict.keys():
        errStr = (
            "Each definition requires a table name under the " "'table' key."
        )
        raise KeyError(errStr)

    return full_dict


def get_table_map(map_name="table_map.yaml"):
    # Load the yaml files
    objdir = ModPath(__name__, "..", "config")
    table_yaml = objdir.get_path(map_name)

    with open(table_yaml, "r") as f:
        table_list = yaml.load(f, Loader=yaml.FullLoader)

    return table_list


def filter_map(table_list, filter_name, parent=None):
    copy_list = table_list[:]

    for table_dict in copy_list:
        full_dict = check_dict(table_dict)

        table_name = full_dict["table"]

        if filter_name == table_name:
            if parent is not None:
                parent["children"] = [full_dict]
                return parent
            else:
                return table_dict

        elif full_dict["children"] is not None:
            result = filter_map(full_dict["children"], filter_name, table_dict)

            if result is not None:
                if parent is not None:
                    parent["children"] = [result]
                    return parent
                else:
                    return result

    return None


def draw_map(table_list, level=0):
    map_str = ""

    for table_dict in table_list:
        full_dict = check_dict(table_dict)

        if level > 0:
            n_spaces = 2 * level - 1
            level_marks = " " + " " * n_spaces + "|"
        else:
            level_marks = "|"

        level_marks += "-"

        map_str += "{} {}\n".format(level_marks, full_dict["table"])

        if full_dict["children"] is not None:
            map_str += draw_map(full_dict["children"], level + 1)

    return map_str


def get_database_config(db_config_name="database.yaml"):
    userconfigdir = UserDataPath("dtocean_core", "DTOcean", "config")
    useryaml = ReadYAML(userconfigdir, db_config_name)

    if userconfigdir.isfile(db_config_name):
        configdir = userconfigdir
    else:
        configdir = ModPath("dtocean_core", "config")

    configyaml = ReadYAML(configdir, db_config_name)
    config = configyaml.read()

    return useryaml, config


def get_database(credentials, echo=False, timeout=None, db_adapter="psycopg2"):
    database = PostgreSQL(db_adapter)
    database.set_credentials(credentials)
    database.set_echo(echo)
    database.set_timeout(timeout)
    database.configure()

    return database


def database_convert_parser():
    """Command line parser for database_to_files and database_from_files."""

    desStr = "Convert DTOcean database to and from structured files"
    epiStr = "Mathew Topper, Data Only Greater, (c) 2018"

    parser = argparse.ArgumentParser(
        description=desStr, epilog=epiStr, formatter_class=SmartFormatter
    )

    parser.add_argument(
        "action",
        choices=["dump", "load", "list", "view", "dir"],
        help="R|Select an action, where\n"
        " dump = export database to files\n"
        " load = import files into database\n"
        " list = print stored credentials identifiers\n"
        " view = print stored credentials (using -i "
        "option)\n"
        "  dir = print table structure",
    )

    parser.add_argument(
        "-d",
        "--directory",
        help=("directory to add or read files from. " "Defaults to '.'"),
        type=str,
        default=".",
    )

    parser.add_argument(
        "-s",
        "--section",
        choices=["device", "site", "other"],
        help="R|Only operate on section from\n"
        " device = tables related to the OEC\n"
        " site = tables related to the deployment site\n"
        " other = tables related to the reference data",
    )

    parser.add_argument(
        "-i", "--identifier", help=("stored credentials identifier"), type=str
    )

    parser.add_argument("--host", help=("override database host"), type=str)

    parser.add_argument("--name", help=("override database name"), type=str)

    parser.add_argument("--user", help=("override database username"), type=str)

    parser.add_argument(
        "-p", "--pwd", help=("override database password"), type=str
    )

    args = parser.parse_args()

    result = {
        "action": args.action,
        "root_path": args.directory,
        "filter_table": args.section,
        "db_id": args.identifier,
        "db_host": args.host,
        "db_name": args.name,
        "db_user": args.user,
        "db_pwd": args.pwd,
    }

    return result


def database_convert_interface():
    """Command line interface for database_to_files and database_from_files.

    Example:

        To get help::

            $ dtocean-database -h

    """

    request = database_convert_parser()

    _, config = get_database_config()

    # List the available database configurations
    if request["action"] == "list":
        id_str = ", ".join(config.keys())

        if id_str:
            msg_str = (
                "Available database configuration identifiers are: " "{}"
            ).format(id_str)
        else:
            msg_str = "No database configurations are stored"

        print(msg_str)

        return

    if request["action"] == "view":
        if request["db_id"] is None:
            err_msg = "Option '-i' must be specified with 'view' action"
            raise ValueError(err_msg)

        cred = config[request["db_id"]]

        for k, v in cred.iteritems():
            print("{:>8} ::  {}".format(k, v))

        return

    table_list = get_table_map()

    # Filter the table if required
    if request["filter_table"] is not None:
        filtered_dict = filter_map(table_list, request["filter_table"])
        table_list = [filtered_dict]

    if request["action"] == "dir":
        print("\n" + draw_map(table_list))
        return

    # Set up the DB
    if request["db_id"] is not None:
        cred = config[request["db_id"]]
    else:
        cred = {"host": None, "dbname": None, "user": None, "pwd": None}

    if request["db_host"] is not None:
        cred["host"] = request["db_host"]

    if request["db_name"] is not None:
        cred["dbname"] = request["db_name"]

    if request["db_user"] is not None:
        cred["user"] = request["db_user"]

    if request["db_pwd"] is not None:
        cred["pwd"] = "postgres"

    db = get_database(cred, timeout=60)

    if request["action"] == "dump":
        # make a directory if required
        if not os.path.exists(request["root_path"]):
            os.makedirs(request["root_path"])

        database_to_files(request["root_path"], table_list, db)

        return

    if request["action"] == "load":
        database_from_files(request["root_path"], table_list, db)

        return

    raise RuntimeError("Highly illogical...")

    return
