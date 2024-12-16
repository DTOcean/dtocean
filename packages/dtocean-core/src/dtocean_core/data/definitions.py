
#    Copyright (C) 2016 Mathew Topper, David Bould, Rui Duarte, Francesco Ferri
#    Copyright (C) 2017-2024 Mathew Topper
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

import __builtin__

import os
from copy import deepcopy
from cycler import cycler
from datetime import datetime
from itertools import product

import yaml
import numpy as np
import pandas as pd
import xarray as xr
import shapefile
from scipy import interpolate
from natsort import natsorted
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

from shapely.geometry import Polygon, Point
from descartes import PolygonPatch
from geoalchemy2.shape import to_shape

from aneris.boundary import Structure
from ..utils.database import (get_table_df,
                              get_one_from_column,
                              filter_one_from_column,
                              get_all_from_columns)

BLUE = '#6699cc'


class UnknownData(Structure):

    '''An item of data whose structrue is not understood'''

    def get_data(self, raw, meta_data):

        return raw

    def get_value(self, data):

        return deepcopy(data)


class SeriesData(Structure):
    
    '''Structure represented in a series of some sort'''
    
    def get_data(self, raw, meta_data):
        
        series = pd.Series(raw)
        
        return series
    
    def get_value(self, data):
        
        result = None
        
        if data is not None:
            result = data.copy()
            
        return result
    
    @classmethod
    def equals(cls, left, right): 
        
        return left.equals(right)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".csv" in self._path:
            series = pd.read_csv(self._path,
                                 header=None,
                                 index_col=0,
                                 squeeze=True)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format is .csv")
        
        self.data.result = series
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        s = self.data.result
        
        if ".csv" in self._path:
            s.to_csv(self._path)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format is .csv")
        
        return
        
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv"]


class TimeSeries(SeriesData):
    
    '''List of tuples expected with the first entries being datetime.datetime
    objects.'''
    
    def get_data(self, raw, meta_data):
        
        if isinstance(raw, pd.Series):
            
            if not isinstance(raw.index, pd.DatetimeIndex):
                
                errStr = ("TimeSeries requires a DatetimeIndex as the index "
                          "of any given series. Current index type is "
                          "{}".format(type(raw.index)))
                raise ValueError(errStr)
            
            return raw
        
        dates, values = zip(*raw)
        
        if not all(isinstance(x, datetime) for x in dates):
            
            errStr = ("TimeSeries requires a datetime.datetime object as first"
                      "index of all given tuples.")
            raise ValueError(errStr)
        
        dt_index = pd.DatetimeIndex(dates)
        time_series = pd.Series(values, index=dt_index)
        time_series = time_series.sort_index()
        
        return time_series
    
    @staticmethod
    def auto_plot(self):

        fig = plt.figure()
        ax = fig.gca()
        self.data.result.plot(ax=ax)
        
        # Pad the y-axis slightly
        ymin, ymax = ax.get_ylim()
        ylength = ymax - ymin
        ymargin = (0.05 * ylength) / ylength
                
        ax.margins(y=ymargin)

        if self.meta.result.labels is not None:
            ylabel = self.meta.result.labels[0]
        else:
            ylabel = ""

        if self.meta.result.units is not None:
            ylabel = "{} [${}$]".format(ylabel, self.meta.result.units[0])

        plt.ylabel(ylabel.strip())
        
        plt.title(self.meta.result.title)

        self.fig_handle = plt.gcf()

        return
        
    @staticmethod
    def auto_file_input(self):
        
        fmtStr = "%Y-%m-%d %H:%M:%S.%f"
        
        SeriesData.auto_file_input(self)
        
        s = self.data.result
        
        try:
        
            s.index = s.index.map(lambda x: pd.to_datetime(x, format=fmtStr))
               
        except ValueError:  # wrong datetime object format
            
            errStr = ("TimeSeries requires a datetime.datetime object "
                      "as first index of all given entries. "
                      "The accepted format is: {}").format(fmtStr)
            raise ValueError(errStr)
            
        self.data.result = s
        
        return


class TimeSeriesColumn(TimeSeries):
    
    """The first two entries of the tables key of the DDS entry should refer
    to the date and time columns within the database. These do not need to be
    specified in the labels key, but all other columns should be labelled."""
    
    @staticmethod
    def auto_db(self):
        
        schema, table = self.meta.result.tables[0].split(".")
        
        df = get_table_df(self._db,
                          schema,
                          table,
                          self.meta.result.tables[1:])
        
        if df.empty:
            
            result = None
            
        else:
            
            dt_labels = ["Date", "Time"]
            dt_labels.extend(self.meta.result.labels)
            
            name_map = {k: v for k, v in zip(self.meta.result.tables[1:],
                                             dt_labels)}
                                         
            df = df.rename(columns=name_map)
            
            # Don't allow Date to have any null
            if pd.isnull(df["Date"]).any(): return
            
            dtstrs = [datetime.combine(date, time) for
                        date, time in zip(df["Date"], df["Time"])]
            
            df["DateTime"] = dtstrs
            df = df.drop("Date", 1)
            df = df.drop("Time", 1)
            df = df.set_index("DateTime")
            
            result = df.to_records(convert_datetime64=True)
        
        self.data.result = result
        
        return


class TableData(Structure):
    
    '''Structure represented in a pandas dataframe. Note the labels are 
    order sensitive, so care should be taken when defining them. When adding
    labels using the argument 'add_labels' to pass a list, by default they are
    added to the back of the meta data labels. They can be added to the front
    of the labels if the argument 'add_labels_pos' is set to "front".
    '''
    
    def get_data(self, raw,
                       meta_data,
                       add_labels=None,
                       add_labels_pos="back",
                       relax_cols=False):
        
        if meta_data.labels is None:
            
            errStr = "Labels must be set for TableData column names"
            raise ValueError(errStr)
            
        if (meta_data.units is not None and
            len(meta_data.units) != len(meta_data.labels)):
            
            errStr = ("Meta data inconsistent. There are {} units defined "
                      "but {} labels").format(len(meta_data.units),
                                              len(meta_data.labels))
            raise ValueError(errStr)
        
        req_cols = meta_data.labels[:]
        
        if add_labels is not None:
            
            if add_labels_pos == "front":
                
                add_labels.extend(req_cols)
                req_cols = add_labels
            
            elif add_labels_pos == "back":
                
                req_cols.extend(add_labels)
            
            else:
                
                errStr = ("Argument add_labels_pos may only have value "
                          "'back' or 'front' not '{}'").format(add_labels_pos)
                raise ValueError(errStr)
        
        if isinstance(raw, dict):
            
            raw_cols = raw.keys()
            columns = None
        
        elif isinstance(raw, pd.DataFrame):
            
            raw_cols = raw.columns.values
            columns = None
        
        else:
            
            raw_cols = req_cols
            columns = req_cols
        
        # Covert req_cols and raw_cols into sets
        req_set = set(req_cols)
        raw_set = set(raw_cols)
        
        if not relax_cols and raw_set != req_set:
            
            missing = req_set - raw_set
            extra = raw_set - req_set
            
            errStr = "Columns in raw data are incorrectly labelled."
            
            if missing:
                safe_missing = [str(x) for x in missing]
                missing_str = ", ".join(safe_missing)
                errStr += " Missing are '{}'.".format(missing_str)
            
            if extra:
                safe_extra = [str(x) for x in extra]
                extra_str = ", ".join(safe_extra)
                errStr += " Erroneous are '{}'.".format(extra_str)
            
            raise ValueError(errStr)
        
        dataframe = pd.DataFrame(raw, columns=columns)
        
        # Order the columns
        if relax_cols:
            dataframe = dataframe[natsorted(dataframe.columns)]
        else:
            dataframe = dataframe[req_cols]
        
        # Assign types
        if meta_data.types is not None:
            
            if len(meta_data.types) == len(req_cols) + 1:
                types = meta_data.types[1:]
            else:
                types = meta_data.types
            
            for c, t in zip(req_cols, types):
                
                ## TODO: Deal with this better
                try:
                    dataframe[c] = dataframe[c].astype(t)
                except: # pylint: disable=bare-except
                    pass
        
        return dataframe
    
    def get_value(self, data):
        
        result = None
        
        if data is not None:
            result = data.copy()
            
        return result
    
    @classmethod
    def equals(cls, left, right): 
        
        return left.equals(right)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))
        
        self.data.result = df
        
        return
    
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        df = self.data.result
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
        
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]


class TableDataColumn(TableData):

    @staticmethod
    def auto_db(self):
        
        schema, table = self.meta.result.tables[0].split(".")

        df = get_table_df(self._db,
                          schema,
                          table,
                          self.meta.result.tables[1:])
                               
        if df.empty:
            
            df = None
            
        else:
            
            name_map = {k: v for k, v in zip(self.meta.result.tables[1:],
                                             self.meta.result.labels)}
            df = df.rename(columns=name_map)
            
            # Don't allow all null values
            if pd.isnull(df).all().all(): df = None

        self.data.result = df

        return

        
class IndexTable(TableData):

    '''Structure represented in a pandas dataframe with a defined index.
    The first label will identify which dictionary key to use as the index.

    The index column is then considered invariant from the users persepective.
    '''

    def get_data(self, raw, meta_data):

        if meta_data.labels is None:

            errStr = ("The first label of a variable with IndexTable  "
                      "structure must indicate the key to be used as the "
                      "index.")
            raise ValueError(errStr)

        index_key = meta_data.labels[0]

        dataframe = super(IndexTable, self).get_data(raw, meta_data)
        
        if index_key not in dataframe.columns:

            errStr = ("IndexTable structure requires one column "
                      "to have value '{}'").format(index_key)
            raise ValueError(errStr)
            
        if meta_data.valid_values is not None:
            
            index_series = dataframe[index_key]
            has_indexes = index_series.isin(meta_data.valid_values)
            
            if not has_indexes.all():
                
                errStr = ("The indices of the given raw data do not match the "
                          "valid variables meta data")
                raise ValueError(errStr)

        dataframe = dataframe.set_index(index_key)
        
        if meta_data.valid_values is not None:
            dataframe.reindex(index=meta_data.valid_values)
        
        return dataframe
        
    @staticmethod
    def auto_file_output(self):
        
        self.data.result = self.data.result.reset_index()
        
        TableData.auto_file_output(self)
        
        return


class IndexTableColumn(IndexTable):

    @staticmethod
    def auto_db(self):
        
        schema, table = self.meta.result.tables[0].split(".")

        df = get_table_df(self._db,
                          schema,
                          table,
                          self.meta.result.tables[1:])
                               
        if df.empty:
            
            df = None
            
        else:
            
            name_map = {k: v for k, v in zip(self.meta.result.tables[1:],
                                             self.meta.result.labels)}
            df = df.rename(columns=name_map)
            
            # Don't allow null values in the keys
            if pd.isnull(df[self.meta.result.labels[0]]).any(): df = None

        self.data.result = df

        return


class LineTable(TableData):

    '''Structure represented in a pandas dataframe with free variable data on
    the index. The first label will identify which dictionary key to use as
    the index.

    Each column of the table then represents a line using identical abscissae
    values.'''

    def get_data(self, raw, meta_data, relax_cols=False):

        if meta_data.labels is None:

            errStr = ("The first label of a variable with LineTable structure "
                      "must indicate the key to be used as the index.")
            raise ValueError(errStr)

        index_key = meta_data.labels[0]

        dataframe = super(LineTable, self).get_data(raw,
                                                    meta_data,
                                                    relax_cols=relax_cols)
        
        if index_key not in dataframe.columns:

            errStr = ("LineTable structure requires one column "
                      "to have value '{}'").format(index_key)
            raise ValueError(errStr)

        dataframe = dataframe.set_index(index_key)

        return dataframe
    
    @staticmethod
    def auto_plot(self):
        
        # Get number of columns for legend
        ncol = len(self.data.result.columns) / 20 + 1
        
        fig = plt.figure()
        ax = fig.gca()
        
        self.data.result.plot(ax=ax)
        lgd = ax.legend(bbox_to_anchor=(1.04, 1),
                        loc="upper left",
                        ncol=ncol)
        
        xlabel = self.meta.result.labels[0]
        
        if (self.meta.result.units is not None and
            self.meta.result.units[0] is not None):
            
            xlabel = "{} [${}$]".format(xlabel, self.meta.result.units[0])
        
        plt.xlabel(xlabel)
        plt.title(self.meta.result.title)
        
        # Auto adjust canvas for legend
        # https://stackoverflow.com/a/45846024
        plt.gcf().canvas.draw()
        invFigure = plt.gcf().transFigure.inverted()
        
        lgd_pos = lgd.get_window_extent()
        lgd_coord = invFigure.transform(lgd_pos)
        lgd_xmax = lgd_coord[1, 0]
        
        ax_pos = plt.gca().get_window_extent()
        ax_coord = invFigure.transform(ax_pos)
        ax_xmax = ax_coord[1, 0]
        
        shift = ax_xmax / lgd_xmax
        plt.gcf().tight_layout(rect=(0, 0, shift, 1))
        
        self.fig_handle = plt.gcf()
        
        return
    
    @staticmethod
    def auto_file_output(self):
        
        IndexTable.auto_file_output(self)
        
        return
    
    
class LineTableExpand(LineTable):

    '''Structure represented in a pandas dataframe with free variable data on
    the index. The first label will identify which dictionary key to use as
    the index. The input data keys/columns will be included in the final table.

    Each column of the table then represents a line using identical abscissae
    values.'''

    def get_data(self, raw, meta_data):

        dataframe = super(LineTableExpand, self).get_data(raw,
                                                          meta_data,
                                                          relax_cols=True)

        return dataframe


class LineTableColumn(LineTable):

    @staticmethod
    def auto_db(self):
        
        schema, table = self.meta.result.tables[0].split(".")

        df = get_table_df(self._db,
                          schema,
                          table,
                          self.meta.result.tables[1:])
                               
        if df.empty:
            
            df = None
            
        else:
        
            name_map = {k: v for k, v in zip(self.meta.result.tables[1:],
                                             self.meta.result.labels)}
                                         
            df = df.rename(columns=name_map)
            
            # Don't allow null values in the keys
            if pd.isnull(df[self.meta.result.labels[0]]).any(): df = None

        self.data.result = df

        return
        

class TimeTable(TableData):
    
    '''Structure represented in a pandas dataframe with a datetime index. One
    key in the raw data should be named "DateTime". If non-indexed raw data
    is given then the datetimes should be in the first column.'''
    
    def get_data(self, raw, meta_data):
        
        if not all(isinstance(x, datetime) for x in raw["DateTime"]):
            
            errStr = ("TimeTable requires 'DateTime' key to be all "
                      "datetime.datetime objects")
            raise ValueError(errStr)
                
        dataframe = super(TimeTable, self).get_data(raw,
                                                    meta_data,
                                                    add_labels=["DateTime"],
                                                    add_labels_pos="front")
        
        if "DateTime" not in dataframe.columns:
            
            errStr = ("TimeTable structure requires one column "
                      "to have value 'DateTime'")
            raise ValueError(errStr)
        
        dataframe = dataframe.set_index(["DateTime"])
        dataframe = dataframe.sort_index()
        
        return dataframe
    
    @staticmethod
    def auto_plot(self):
        
        fig = plt.figure()
        self.data.result.plot(ax=fig.gca())
        
        plt.title(self.meta.result.title)
        
        self.fig_handle = plt.gcf()
        
        return
        
    @staticmethod
    def auto_file_input(self):
        
        fmtStr = "%Y-%m-%d %H:%M:%S.%f"
        
        TableData.auto_file_input(self)
        
        df = self.data.result
                
        try:
        
            df = df.set_index("DateTime")
            df.index = df.index.map(
                                lambda x: pd.to_datetime(x, format=fmtStr))
            df.index.name = "DateTime"
            df = df.reset_index()
                           
        except ValueError:  # wrong datetime object format
            
            errStr = ("TimeTable requires a datetime.datetime object "
                      "as first index of all given entries. "
                      "The accepted format is: {}").format(fmtStr)
            raise ValueError(errStr)
            
        self.data.result = df
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        IndexTable.auto_file_output(self)
        
        return


class TimeTableColumn(TimeTable):
    
    """The first two entries of the tables key of the DDS entry should refer
    to the date and time columns within the database. These do not need to be
    specified in the labels key. The remaining colums of the tables key should
    match to values in the labels key."""

    @staticmethod
    def auto_db(self):
        
        schema, table = self.meta.result.tables[0].split(".")

        df = get_table_df(self._db,
                          schema,
                          table,
                          self.meta.result.tables[1:])
                               
        if df.empty:
            
            df = None
            
        else:
            
            dt_labels = ["Date", "Time"]
            dt_labels.extend(self.meta.result.labels)
            
            name_map = {k: v for k, v in zip(self.meta.result.tables[1:],
                                             dt_labels)}
                                         
            df = df.rename(columns=name_map)
            
            # Don't allow Date to have any null
            if pd.isnull(df["Date"]).any(): return
            
            dtstrs = [datetime.combine(date, time) for
                        date, time in zip(df["Date"], df["Time"])]
    
            df["DateTime"] = dtstrs
            df = df.drop("Date", 1)
            df = df.drop("Time", 1)

        self.data.result = df

        return
        
        
class TriStateTable(TableData):

    '''Structure represented in a pandas dataframe with tri-state values.'''

    def get_data(self, raw, meta_data):
        
        df = super(TriStateTable, self).get_data(raw, meta_data)
        
        if not np.all(df.isin(["true", "false", "unknown"])):
            
            errStr = ('Given raw value is incorrectly formatted. It must be '
                      'a string with value "true", "false" or "unknown".')
            raise ValueError(errStr)
            
        return df
        
        
class TriStateIndexTable(IndexTable):

    '''Structure represented in a pandas dataframe with tri-state values and
    a predefined index column.'''

    def get_data(self, raw, meta_data):
        
        df = super(TriStateIndexTable, self).get_data(raw, meta_data)
        
        if not np.all(df.isin(["true", "false", "unknown"])):
            
            errStr = ('Given raw value is incorrectly formatted. It must be '
                      'a string with value "true", "false" or "unknown".')
            raise ValueError(errStr)
            
        return df
        

class NumpyND(Structure):
    
    '''Numpy array. This structure is too general for most applications and so
    the get_value method deliberately raises an error. Subclasses of this class
    should be used instead.'''
    
    def get_data(self, raw, meta_data):
        
        array = np.array(raw)
        
        return array
    
    def get_value(self, data):
        
        errStr = "Only subclasses of NumpyND may be used."
        
        raise NotImplementedError(errStr)
    
    @classmethod
    def equals(cls, left, right):
        
        return np.array_equal(left, right)


class Numpy2D(NumpyND):

    '''Numpy2D array.'''

    def get_data(self, raw, meta_data):

        data = super(Numpy2D, self).get_data(raw, meta_data)

        if len(data.shape) != 2:

            errStr = ("Numpy2D class requires 2 dimensions  "
                      "supplied data has {}").format(
                                                  len(data.shape))
            raise ValueError(errStr)

        return data

    def get_value(self, data):

        result = None
        
        if data is not None:
            result = data.copy()
            
        return result


class Numpy2DColumn(Numpy2D):
    '''Numpy2DColumn array.'''

    @staticmethod
    def auto_db(self):
        
        schema, table = self.meta.result.tables[0].split(".")

        df = get_table_df(self._db,
                          schema,
                          table,
                          self.meta.result.tables[1:4])
                               
        if df.empty:
            
            result = None
            
        else:
            
            # Don't allow first two columns to have any null
            if pd.isnull(df[self.meta.result.tables[1:3]]).any().any(): return

            df = df.set_index(self.meta.result.tables[1:3])
            groups = df.groupby(level=df.index.names)
    
            df = groups.first()
            levels = map(tuple, df.index.levels)
            index = list(product(*levels))
    
            df = df.reindex(index)
            shape = map(len, df.index.levels)
            
            result = df.values.reshape(shape)

        self.data.result = result

        return


class Numpy3D(NumpyND):

    '''Numpy3D array.'''

    def get_data(self, raw, meta_data):

        data = super(Numpy3D, self).get_data(raw, meta_data)

        if len(data.shape) != 3:

            errStr = ("Numpy3D class requires 3 dimensions  "
                      "supplied data has {}").format(
                                                  len(data.shape))
            raise ValueError(errStr)

        return data

    def get_value(self, data):

        result = None
        
        if data is not None:
            result = data.copy()
            
        return result


class Numpy3DColumn(Numpy3D):
    '''Numpy3DColumn array.'''

    @staticmethod
    def auto_db(self):
        
        schema, table = self.meta.result.tables[0].split(".")

        df = get_table_df(self._db,
                          schema,
                          table,
                          self.meta.result.tables[1:5])
                               
        if df.empty:
            
            result = None
            
        else:
            
            # Don't allow first three columns to have any null
            if pd.isnull(df[self.meta.result.tables[1:4]]).any().any(): return
    
            df = df.set_index(self.meta.result.tables[1:4])
            groups = df.groupby(level=df.index.names)
    
            df = groups.first()
            levels = map(tuple, df.index.levels)
            index = list(product(*levels))
    
            df = df.reindex(index)
            shape = map(len, df.index.levels)
                        
            result = df.values.reshape(shape)
            
        self.data.result = result

        return


class NumpyLine(NumpyND):

    '''2D Numpy array with the first dimension having value 2'''

    def get_data(self, raw, meta_data):

        data = super(NumpyLine, self).get_data(raw, meta_data)

        if data.shape[1] != 2:


            errStr = ("Second dimension must have value 2. The second "
                      "dimension of the given data has value {}").format(
                                                          data.shape[1])
            raise ValueError(errStr)

        # Sort on the zero axis
        data = data[np.argsort(data[:, 0])]

        return data

    def get_value(self, data):

        result = None
        
        if data is not None:
            result = data.copy()
            
        return result
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))
        if "x" in df.columns and "y" in df.columns:
            data = np.c_[df.x,df.y]
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "x, y)")
        
        # Sort on the zero axis
        data = data[np.argsort(data[:, 0])]
        self.data.result = data
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        if isinstance(self.data.result, np.ndarray):
            data_ = self.data.result
        else:
            raise TypeError("Data type not understood: possible type for a "
                            "NumpyND subclass is: numpy.ndarray")
        
        data = {"x": data_[:,0],
                "y": data_[:,1]}
                
        
        df = pd.DataFrame(data)
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
                
        return
                
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]

    @staticmethod
    def auto_plot(self):

        plt.figure()
        plt.plot(*zip(*self.data.result))
        plt.title(self.meta.result.title)

        xlabel = ""
        ylabel = ""

        if self.meta.result.labels is not None:

            xlabel = self.meta.result.labels[0]
            ylabel = self.meta.result.labels[1]

            if xlabel is None: xlabel = ""
            if ylabel is None: ylabel = ""

        if self.meta.result.units is not None:

            xunit = self.meta.result.units[0]
            yunit = self.meta.result.units[1]

            if xunit is not None: xlabel = "{} [${}$]".format(xlabel, xunit)
            if yunit is not None: ylabel = "{} [${}$]".format(ylabel, yunit)

            xlabel = xlabel.lstrip()
            ylabel = ylabel.lstrip()

        if xlabel: plt.xlabel(xlabel)
        if ylabel: plt.ylabel(ylabel)

        self.fig_handle = plt.gcf()

        return


class NumpyLineArray(NumpyLine):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)
            
        schema, table = self.meta.result.tables[0].split(".")

        result = get_one_from_column(self._db,
                                     schema,
                                     table,
                                     self.meta.result.tables[1])

        if result is not None and result[0] is not None:
            self.data.result = result[0]
        
        return


class NumpyLineColumn(NumpyLine):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:3])
                
        line = zip(col_lists[0], col_lists[1])
        
        # Filter out None in first column
        line = [(x, y) for (x, y) in line if x is not None]
        
        if line: self.data.result = line
        
        return


class NumpyLineDict(NumpyLine):
    
    """Collection of NumpyLine structures on matching axes."""
    
    def get_data(self, raw, meta_data):
        
        valid_dict = {}
        
        for key, value in raw.items():
        
            value = super(NumpyLineDict, self).get_data(value, meta_data)
            
            if meta_data.types:
                key = _assign_type(key, meta_data.types)
            
            valid_dict[key] = value
        
        return valid_dict
    
    def get_value(self, data):
        
        copy_dict = None
        
        if data is not None:
            copy_dict = {k: super(NumpyLineDict, self).get_value(v) for
                                                        k, v in data.items()}
        
        return copy_dict
    
    @classmethod
    def equals(cls, left, right):
        
        if set(left.keys()) != set(right.keys()): return False
        
        value_check = []
        
        for lkey, lvalue in left.iteritems():
            
            rvalue = right[lkey]
            value_check.append(np.array_equal(lvalue, rvalue))
        
        return all(value_check)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            xl = pd.ExcelFile(self._path)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {}, {}".format('.xls',
                                                                 '.xlsx'))
             
        result = {}
             
        for sheet_name in xl.sheet_names:
            
            df = xl.parse(sheet_name)
            
            if "x" in df.columns and "y" in df.columns:
                
                data = np.c_[df.x, df.y]
                
            else:
                
                errStr = ("The specified file structure is not supported, "
                          "the columns' headers shuld be defined as: (x, y)")
                raise ValueError(errStr)
            
            # Sort on the zero axis
            data = data[np.argsort(data[:, 0])]
            
            result[sheet_name] = data
            
        self.data.result = result
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data_dict = self.data.result
        
        if ".xls" in self._path:
            xl = pd.ExcelWriter(self._path)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are "
                            "{}, {}".format('.xls', '.xlsx'))
        
        # Sort the keys
        keys = data_dict.keys()
        keys = natsorted(keys)
        
        for key in keys:
            
            value = data_dict[key]

            data = {"x": value[:, 0],
                    "y": value[:, 1]}
            df = pd.DataFrame(data)
        
            df.to_excel(xl, sheet_name=key, index=False)
            
        xl.save()
                
        return
                
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".xls", ".xlsx"]

    @staticmethod
    def auto_plot(self):
        
        plt.figure()
        
        kwargs = {}
        
        if len(self.data.result) < 10:
            kwargs["label"] = self.data.result.keys()
        else:
            kwargs["color"] = '0.5'

        for line in self.data.result:
            plt.plot(*zip(*self.data.result[line]), **kwargs)
            
        if len(self.data.result) < 10:
            plt.legend(bbox_to_anchor=(1.05, 1),
                       loc=2,
                       borderaxespad=0.)

        xlabel = ''

        if self.meta.result.labels is not None:
            xlabel = self.meta.result.labels[0]

        if self.meta.result.units is not None:
            xlabel = "{} [${}$]".format(xlabel, self.meta.result.units[0])

        plt.xlabel(xlabel)

        plt.title(self.meta.result.title)

        self.fig_handle = plt.gcf()

        return
        
        
class NumpyLineDictArrayColumn(NumpyLineDict):
    
    """Collect a column with keys and a second column containing 2D arrays"""

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:3])
        
        all_keys = col_lists[0]
        all_lines = col_lists[1]
    
        # Don't allow any None keys
        result_dict = {key: line for key, line in zip(all_keys, all_lines)
                                                            if key is not None}
        
        if result_dict: self.data.result = result_dict
        
        return


class NumpyBar(NumpyLine):

    '''2D Numpy array with the first dimension having value 2 for binned
    data'''

    @staticmethod
    def _auto_plot(self):
        
        return


class Histogram(Structure):
    
    """Structure to store histogram data. The input is a tuple of bin values
    and the bins separators. The final structure is a dictionary with keys
    "values" and "bins".
    """
    
    def get_data(self, raw, meta_data):
        
        if len(raw[1]) != len(raw[0]) + 1:
            
            errStr = ("The bin separators must contain one more item than the "
                      "bin values. Given data contains {} values and {} "
                      "bin separators").format(len(raw[0]),
                                               len(raw[1]))
            raise ValueError(errStr)
        
        histogram = {"values": raw[0],
                     "bins"  : raw[1]}
        
        return histogram
    
    def get_value(self, data):
        
        return deepcopy(data)
    
    @classmethod
    def equals(cls, left, right):
        
        vals_equal = np.array_equal(left["values"], right["values"])
        bins_equal = np.array_equal(left["bins"], right["bins"])
        
        return vals_equal and bins_equal
    
    @staticmethod
    def auto_file_input(self):
        column_requirements = ("bin start", "bin end", "bin value")
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))
        if all([x in df.columns for x in column_requirements]):
            data = np.c_[df["bin start"],df["bin end"], df["bin value"]]
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "bin start, bin end, bin value)")
        
        # Sort on the zero axis
        data = data[np.argsort(data[:, 0])]  # is this needed?
        #check bin consistency
        n_bins = data.shape[0]
        
        for ib in range(1, n_bins):
            if not data[ib-1,1] == data[ib,0]:
                raise ValueError("The data format is incorrect. ",
                                 "The relation\nbin_end(i) == bin_start(i+1)",
                                 "\nis not satisfied ")
        
        self.data.result = ( 
                            data[:,2],
                            np.unique(data[:,[0,1]].flatten())
                           )
        
        return
    
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data_ = self.data.result
        
        data = {"bin start": data_["bins"][:-1],
                "bin end": data_["bins"][1:],
                "bin value": data_["values"]}
        
        df = pd.DataFrame(data)
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
        
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]
    
    @staticmethod
    def auto_plot(self):
        
        hist = self.data.result
        bins = hist['bins']
        values = hist['values']
        nvalues = len(values)
        width = np.ediff1d(bins)
        x = bins[:nvalues]
        
        plt.figure()
        plt.bar(x, values, width, align = 'edge')
        
        plt.title(self.meta.result.title)
        
        self.fig_handle = plt.gcf()
        
        return


class HistogramColumn(Histogram):

    """Assumes the first column contains bin values (Frequency) and next two
    columns contain bin separators.
    """

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:4])

        all_bin_values = col_lists[0]
        all_bin_lowers = col_lists[1]
        all_bin_uppers = col_lists[2]
        
        if not all_bin_values or not all_bin_lowers or not all_bin_uppers:
            return
        
        # Don't allow None in the bin separators
        if None in all_bin_lowers or None in all_bin_uppers: return
        
        lowest_val = min(all_bin_lowers)
        bin_separators = [lowest_val] + all_bin_uppers
        
        result = (all_bin_values, bin_separators)
                  
        self.data.result = result
        
        return
        

class HistogramDict(Histogram):

    """Dictionary containing histogram dictionaries for a related quantity.
    The raw data should be a dictionary with values as
    (bin values, bin separators)
    """

    def get_data(self, raw, meta_data):
        
        hist_dict = {k: super(HistogramDict, self).get_data(v, meta_data)
                                                    for k, v in raw.items()}
        
        return hist_dict
    
    @classmethod
    def equals(cls, left, right):
        
        if set(left.keys()) != set(right.keys()): return False
        
        for key in left.keys():
            
            left_val = left[key]
            right_val = right[key]
            
            vals_equal = np.array_equal(left_val["values"],
                                        right_val["values"])
            bins_equal = np.array_equal(left_val["bins"], right_val["bins"])
            
            if not (vals_equal and bins_equal): return False
        
        return True
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()

        column_requirements = ("bin start", "bin end", "bin value")
        
        if ".xls" in self._path:
            xl = pd.ExcelFile(self._path)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {}, {}".format('.xls',
                                                                 '.xlsx'))
             
        result = {}
             
        for sheet_name in xl.sheet_names:
            
            df = xl.parse(sheet_name)
             
            if all([x in df.columns for x in column_requirements]):
                
                data = np.c_[df["bin start"], df["bin end"], df["bin value"]]
                
            else:
                
                errStr = ("The specified file structure is not supported "
                          "the columns' headers should be defined as: "
                          "(bin start, bin end, bin value)")
                raise ValueError(errStr)
            
            # Sort on the zero axis
            data = data[np.argsort(data[:, 0])]  # is this needed?
            
            # Check bin consistency
            n_bins = data.shape[0]
    
            for ib in range(1, n_bins):
                if not data[ib - 1, 1] == data[ib, 0]:
                    errStr = ("The data format is incorrect. ",
                              "The relation 'bin_end(i) == bin_start(i+1)' ",
                              "is not satisfied ")
                    raise ValueError(errStr)
            
            result[sheet_name] = (data[:, 2],
                                  np.unique(data[:, [0, 1]].flatten())
                                  )
            
        self.data.result = result
        
        return
    
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data_dict = self.data.result
        
        if ".xls" in self._path:
            xl = pd.ExcelWriter(self._path)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are "
                            "{}, {}".format('.xls', '.xlsx'))
        
        # Sort the keys
        keys = data_dict.keys()
        keys = natsorted(keys)
        
        for key in keys:
            
            value = data_dict[key]
        
            data = {"bin start": value["bins"][:-1],
                    "bin end": value["bins"][1:],
                    "bin value": value["values"]}
            df = pd.DataFrame(data)
            
            df.to_excel(xl, sheet_name=key, index=False)
            
        xl.save()
        
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".xls", ".xlsx"]

    @staticmethod
    def auto_plot(self):

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_prop_cycle(cycler('color', ['c', 'm', 'y', 'k']))

        for i, hist in enumerate(self.data.result):
            bins = self.data.result[hist]['bins']
            values = self.data.result[hist]['values']
            nvalues = len(values)
            width = np.ediff1d(bins)
            x = bins[:nvalues]

            ax.bar(x,
                   values,
                   zs=len(self.data.result) - i,
                   zdir="y",
                   width=width,
                   align='edge',
                   alpha=0.6)

        plt.yticks(range(len(self.data.result)),
                   self.data.result.keys(),
                   rotation=-15,
                   va='center',
                   ha='left')
        plt.title(self.meta.result.title)

        self.fig_handle = plt.gcf()

        return


class CartesianData(NumpyND):

    '''Array with single dimension of length 2 or 3.'''

    def get_data(self, raw, meta_data):

        data = super(CartesianData, self).get_data(raw, meta_data)

        if not (data.shape == (3,) or data.shape == (2,)):

            errStr = ("Data must be single dimension vector "
                      "of length 2 or 3. The shape of the "
                      "given data is {}").format(data.shape)
            raise ValueError(errStr)

        return data

    def get_value(self, data):

        result = None
        
        if data is not None:
            result = data.copy()
            
        return result
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))
        if "x" in df.columns and "y" in df.columns:
            if not len(df.x) > 1:      
                data = np.r_[df.x,df.y]
                if "z" in df.columns: data = np.r_[data, df.z]
            else:
                raise ValueError("The CartesianData structure only support",
                                 " x, y and z(optional) columns with lenght 1")
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "x, y, z(optional))")
                             
        self.data.result = data
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        if isinstance(self.data.result, np.ndarray):
            data_ = self.data.result
        else:
            raise TypeError("Data type not understood: possible type for a "
                            "CartesianList subclass is: numpy.ndarray")
        
        data = {"x": data_[0],
                "y": data_[1]}
                
        if data_.shape[0] == 3:
            data["z"] = data_[2]
        
        df = pd.DataFrame(data, index=[0])
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
                
        return
                
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]
        

class CartesianDataColumn(CartesianData):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        result = get_one_from_column(self._db,
                                     schema,
                                     table,
                                     self.meta.result.tables[1])

        if result is not None and result[0] is not None:
            self.data.result = result[0]

        return
        

class CartesianList(Numpy2D):

    '''2D array with second dimension of length 2 or 3.'''

    def get_data(self, raw, meta_data):

        data = super(CartesianList, self).get_data(raw, meta_data)
        
        if not (data.shape[1] == 3 or data.shape[1] == 2):

            errStr = ("Second dimension must be of length 2 or 3. The length "
                      "for the given data is {}").format(data.shape[1])
            raise ValueError(errStr)

        return data

    def get_value(self, data):

        result = None
        
        if data is not None:
            result = data.copy()
            
        return result
        
    @staticmethod
    def auto_plot(self):

        x = []
        y = []

        for coords in self.data.result:
            x.append(coords[0])
            y.append(coords[1])

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1,aspect='equal')
        ax1.plot(x,y,'k+', mew=2, markersize=10)
        ax1.margins(0.1,0.1)
        ax1.autoscale_view()

        xlabel=''
        ylabel=''

        if self.meta.result.labels is not None:
            xlabel = self.meta.result.labels[0]
            ylabel = self.meta.result.labels[1]

        if self.meta.result.units is not None:
            xlabel = "{} [${}$]".format(xlabel, self.meta.result.units[0])
            ylabel = "{} [${}$]".format(ylabel, self.meta.result.units[1])
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.title(self.meta.result.title)
        
        self.fig_handle = plt.gcf()
       
        return

    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))
        if "x" in df.columns and "y" in df.columns:
            
            data = np.c_[df.x,df.y]
            if "z" in df.columns: data = np.c_[data, df.z]

        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "x, y, z(optional))")
                             
        self.data.result = data
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        if isinstance(self.data.result, np.ndarray):
            data_ = self.data.result
        else:
            raise TypeError("Data type not understood: possible type for a "
                            "CartesianList subclass is: numpy.ndarray")
                                
        data = {"x": data_[:,0],
                "y": data_[:,1]}
                
        if data_.shape[1] == 3:
            data["z"] = data_[:,2]
        
        df = pd.DataFrame(data)
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
                
        return
                
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]


class CartesianListColumn(CartesianList):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        result = get_one_from_column(self._db,
                                     schema,
                                     table,
                                     self.meta.result.tables[1])

        if result is not None and result[0] is not None:
            self.data.result = result[0]
        
        return


class CartesianDict(CartesianData):
    
    '''Dictionary of arrays with single dimension of length 2 or 3.'''
    
    def get_data(self, raw, meta_data):
        
        safe_data = {}
        
        for key, value in raw.iteritems():
            
            safe_value = super(CartesianDict, self).get_data(value, meta_data)
            
            if meta_data.types:
                key = _assign_type(key, meta_data.types)
            
            safe_data[key] = safe_value
        
        return safe_data
    
    def get_value(self, data):
        
        new_dict = None
        
        if data is not None:
            new_dict = {k: super(CartesianDict, self).get_value(v)
                                                    for k, v in data.items()}
        
        return new_dict
    
    @classmethod
    def equals(cls, left, right):
        
        if set(left.keys()) != set(right.keys()): return False
        
        value_check = []
        
        for lkey, lvalue in left.iteritems():
            
            rvalue = right[lkey]
            value_check.append(np.array_equal(lvalue, rvalue))
        
        return all(value_check)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))
            
        if all([el in df.columns for el in ["x", "y", "ID"]]):
            data = np.c_[df.x,df.y]
            if "z" in df.columns: data = np.c_[data, df.z]
        
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "ID, x, y, z(optional))")
        
        if len(np.unique(df.ID)) != data.shape[0]:
            raise ValueError("The ID columns can not contains multiple",
                             " instance of the same data.")
        data_ = {}
        for k, v in zip(df.ID, data):
            data_[k] = v
            
        self.data.result = data_
        
        return 
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data_ = self.data.result
        
        columns = ["ID", "x", "y"]

        if data_.itervalues().next().shape[0] == 3:
            columns += ["z"]
        
        df = pd.DataFrame(columns=columns)
        
        for k, v in data_.iteritems():
            
            df2 = pd.DataFrame(v.reshape((1,len(columns)-1)),
                               columns=columns[1:])
            df2["ID"] = k
            
            df = df.append(df2,
                           ignore_index=True,
                           sort=False)
                   
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
                
        return
                
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]
        
    @staticmethod
    def auto_plot(self):

        x = []
        y = []
        n = []

        for key, coords in self.data.result.iteritems():
            x.append(coords[0])
            y.append(coords[1])
            n.append(key)

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1,aspect='equal')
        ax1.plot(x,y,'k+', mew=2, markersize=10)
        for i, txt in enumerate(n):
            ax1.annotate(txt, (x[i],y[i]))
        ax1.margins(0.1,0.1)
        ax1.autoscale_view()

        xlabel=''
        ylabel=''


        ''' not working
        if self.meta.result.labels is not None:
            xlabel = self.meta.result.labels[0]
            ylabel = self.meta.result.labels[1]

        if self.meta.result.units is not None:
            xlabel = "{} {}".format(xlabel, self.meta.result.units[0])
            ylabel = "{} {}".format(ylabel, self.meta.result.units[1])
        '''
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.title(self.meta.result.title)
        
        self.fig_handle = plt.gcf()
       
        return


class CartesianDictColumn(CartesianDict):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:3])
        
        result_dict = {k: v for k, v in zip(col_lists[0], col_lists[1])
                                        if k is not None and v is not None}
        
        if result_dict: self.data.result = result_dict
        
        return


class CartesianListDict(CartesianList):
    
    '''Dictionary of 2D arrays with second dimension of length 2 or 3.'''
    
    def get_data(self, raw, meta_data):
        
        safe_data = {}
        
        for key, value in raw.iteritems():
            
            safe_value = super(CartesianListDict, self).get_data(value,
                                                                 meta_data)
            
            if meta_data.types:
                key = _assign_type(key, meta_data.types)
            
            safe_data[key] = safe_value
            
        return safe_data
    
    def get_value(self, data):
        
        new_dict = None
        
        if data is not None:
            new_dict = {k: super(CartesianListDict, self).get_value(v)
                                                    for k, v in data.items()}
            
        return new_dict
    
    @classmethod
    def equals(cls, left, right):
        
        if set(left.keys()) != set(right.keys()): return False
        
        value_check = []
        
        for lkey, lvalue in left.iteritems():
            
            rvalue = right[lkey]
            value_check.append(np.array_equal(lvalue, rvalue))
        
        return all(value_check)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))
            
        if ("x" in df.columns and 
            "y" in df.columns and 
            "ID" in df.columns):
            dim=2
            if "z" in df.columns: dim=3

        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "x, y, z(optional))")
        
        ks = np.unique(df.ID)
        data = {}
        
        for k in ks:
            
            t = df[df["ID"]==k]
            
            if dim==2:
                data[k] = np.c_[t.x, t.y]
            else:
                data[k] = np.c_[t.x, t.y, t.z]
            
        self.data.result = data
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data_ = self.data.result
        
        columns = ["ID", "x", "y"]

        if data_.itervalues().next().shape[1] == 3:
            columns += ["z"]
            
        df = pd.DataFrame(columns=columns)
        for k, v in data_.iteritems():
            df2 = pd.DataFrame(v, columns=columns[1:])
            df2["ID"] = [k]*v.shape[0]
            
            df = df.append(df2,
                           ignore_index=True,
                           sort=False)
                   
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
                
        return
                
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]

    @staticmethod
    def _auto_plot(self):
        
        return

#    @staticmethod
#    def auto_plot(self):
#
#    # TODO: INSUFFICIENT IMPLENENTATION: ONLY PLOTS ONE POINT PER KEY
#
#        x = []
#        y = []
#        n = []
#
#        for key, coords in self.data.result.iteritems():
#            x.append(coords[0][0])
#            y.append(coords[0][1])
#            n.append(key)
#
#        fig = plt.figure()
#        ax1 = fig.add_subplot(1,1,1,aspect='equal')
#        ax1.plot(x,y,'k+', mew=2, markersize=10)
#        for i, txt in enumerate(n):
#            ax1.annotate(txt, (x[i],y[i]))
#        ax1.margins(0.1,0.1)
#        ax1.autoscale_view()
#
#        xlabel=''
#        ylabel=''
#
#
#        ''' not working
#        if self.meta.result.labels is not None:
#            xlabel = self.meta.result.labels[0]
#            ylabel = self.meta.result.labels[1]
#
#        if self.meta.result.units is not None:
#            xlabel = "{} {}".format(xlabel, self.meta.result.units[0])
#            ylabel = "{} {}".format(ylabel, self.meta.result.units[1])
#        '''
#        
#        plt.xlabel(xlabel)
#        plt.ylabel(ylabel)
#
#        plt.title(self.meta.result.title)
#        
#        self.fig_handle = plt.gcf()
#       
#        return


class CartesianListDictColumn(CartesianListDict):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:3])
        
        result_dict = {k: v for k, v in zip(col_lists[0], col_lists[1])
                                        if k is not None and v is not None}
        
        if result_dict: self.data.result = result_dict
        
        return


class SimpleData(Structure):
    
    '''Simple single value data such as a bool, str, int or float'''
    
    def get_data(self, raw, meta_data):
        
        typed = self._assign_type(raw, meta_data.types)
        
        if meta_data.valid_values is not None:
            
            if typed not in meta_data.valid_values:
                
                valid_str = ", ".join(meta_data.valid_values)
                errStr = ("Given data '{}' does not match any valid value "
                          "from: {}").format(typed, valid_str)
                raise ValueError(errStr)
        
        if (meta_data.types[0] in ["int", "float"] and
            meta_data.minimum_equals is not None):
            
            test = self._assign_type(meta_data.minimum_equals[0],
                                     meta_data.types)
            
            if typed < test:
                errStr = ("Given data '{}' is less than minimum value: "
                          "{}").format(typed, meta_data.minimum_equals[0])
                raise ValueError(errStr)
        
        if (meta_data.types[0] in ["int", "float"] and
            meta_data.minimums is not None):
            
            test = self._assign_type(meta_data.minimums[0],
                                     meta_data.types)
            
            if typed <= test:
                errStr = ("Given data '{}' is less than or equal to minimum "
                          "value: {}").format(typed, meta_data.minimums[0])
                raise ValueError(errStr)
        
        if (meta_data.types[0] in ["int", "float"] and
            meta_data.maximum_equals is not None):
            
            test = self._assign_type(meta_data.maximum_equals[0],
                                     meta_data.types)
            
            if typed > test:
                errStr = ("Given data '{}' is greater than maximum value: "
                          "{}").format(typed, meta_data.maximum_equals[0])
                raise ValueError(errStr)
        
        if (meta_data.types[0] in ["int", "float"] and
            meta_data.maximums is not None):
            
            test = self._assign_type(meta_data.maximums[0],
                                     meta_data.types)
            
            if typed >= test:
                errStr = ("Given data '{}' is greater than or equal to "
                          "maximum value: {}").format(typed,
                                                      meta_data.maximums[0])
                raise ValueError(errStr)
        
        return typed
    
    def get_value(self, data):
        
        return deepcopy(data)
    
    def _assign_type(self, raw, type_list): # pylint: disable=no-self-use
        
        if type_list is not None:
        
            typed = _assign_type(raw, type_list)
        
        else:
            
            errStr = "SimpleData structures require types meta data to be set"
            raise ValueError(errStr)
        
        return typed


class PathData(SimpleData):
    
    """A SimpleData subclass for retrieving path strings. Should be used as
    a super class for file or directory paths"""
    
    def _assign_type(self, raw, type_list):
        
        typed = super(PathData, self)._assign_type(raw, ["str"])
        
        return typed


class DirectoryData(PathData):
    
    """A PathData subclass for retrieving path strings to directories."""


class SimpleList(Structure):
    
    '''Simple list of value data such as a bool, str, int or float'''
    
    def get_data(self, raw, meta_data):
        
        raw_list = raw
        
        if meta_data.types is not None:
            
            simple_list = []
            
            for item in raw_list:
                
                typed = _assign_type(item, meta_data.types)
                simple_list.append(typed)
        
        else:
            
            errStr = "SimpleList structures require types meta data to be set"
            raise ValueError(errStr)
        
        if meta_data.valid_values is not None:
            
            for simple_item in simple_list:
                
                if simple_item not in meta_data.valid_values:
                    
                    valid_str = ", ".join(meta_data.valid_values)
                    errStr = ("Raw data '{}' does not match any valid "
                              "value from: {}").format(simple_item,
                                                       valid_str)
                    raise ValueError(errStr)
        
        return simple_list
    
    def get_value(self, data):
        
        result = None
        
        if data is not None:
            result = data[:]
        
        return result
    
    @staticmethod
    def auto_plot(self):

        if self.meta.result.types[0] not in ["float", "int"]: return

        plt.figure()
        plt.plot(self.data.result)
        plt.title(self.meta.result.title)

        if self.meta.result.units is not None:
            plt.ylabel("${}$".format(self.meta.result.units[0]))

        self.fig_handle = plt.gcf()

        return
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        # Disable integer conversion for float types
        convert_float = True
        
        if (self.meta.result.types is not None and
            self.meta.result.types[0] == "float"): convert_float = False
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path, convert_float=convert_float)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported.",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))  
        if not "data" in df.columns:
            raise TypeError("The file does not contain the correct header.",
                            "The data column needs to have the header: 'data'")
        
        self.data.result = list(df.data)
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data = self.data.result
        df = pd.DataFrame(data, columns=["data"])
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
        
        return
        
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]


class SimpleDict(Structure):
    
    '''Dictionary containing a named variable as a key and a simple
    single valued str, float, int, bool as the value.'''
    
    def get_data(self, raw, meta_data):
        
        raw_dict = raw
        
        if meta_data.types is not None:
            
            typed_dict = {}
            
            try:
                
                for key, value in raw_dict.iteritems():
                    
                    typed_value = _assign_type(value, meta_data.types)
                    typed_dict[key] = typed_value
            
            except AttributeError:
                
                errStr = ("Raw data may not be a dictionary. Type is actually "
                          "{}.").format(type(raw_dict))
                raise AttributeError(errStr)
        
        else:
            
            errStr = "SimpleDict structures require types meta data to be set"
            raise ValueError(errStr)
        
        # Test keys against valid values
        if meta_data.valid_values is not None:
            
            for key in typed_dict.iterkeys():
                
                if key not in meta_data.valid_values:
                    
                    valid_str = ", ".join(meta_data.valid_values)
                    errStr = ("Raw data key '{}' does not match any valid "
                              "value from: {}").format(key,
                                                       valid_str)
                    raise ValueError(errStr)
        
        return typed_dict
    
    def get_value(self, data):
        
        return deepcopy(data)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        # Disable integer conversion for float types
        convert_float = True
        
        if self.meta.result.types[0] == "float": convert_float = False
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path, convert_float=convert_float)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        
        if not ("data" in df.columns 
                and "ID" in df.columns):
            raise ValueError("The file does not contain the correct header.",
                            "The data column needs to have the header: 'data'",
                            "and the key colum needs to have the header: 'ID'")
                            
        self.data.result = dict(zip(df.ID, df.data))
        
        return
    
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        dc = self.data.result
        data = [[k,v] for k,v in dc.iteritems()]
        df = pd.DataFrame(data, columns=["ID", "data"])
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]
    
    @staticmethod
    def auto_plot(self):
        
        if not self.meta.result.types[0] in ["int", "float"]: return
        
        num_dict = self.data.result
        
        labels = num_dict.keys()
        labels = natsorted(labels)
        
        sizes = np.array([num_dict[x] for x in labels])
        
        plt.figure()
        plt.bar(range(len(sizes)),
                sizes,
                align='center')
        plt.xticks(range(len(sizes)),
                   labels,
                   rotation=30,
                   ha="right")
        
        if self.meta.result.units is not None:
            plt.ylabel("[${}$]".format(self.meta.result.units[0]))
        
        plt.title(self.meta.result.title)
        
        plt.tight_layout()
        
        self.fig_handle = plt.gcf()
        
        return


class SimplePie(SimpleDict):

    @staticmethod
    def auto_plot(self):
        
        if not self.meta.result.types[0] in ["int", "float"]: return

        num_dict = self.data.result
        labels = num_dict.keys()
        sizes = num_dict.values()
        
        filter_sizes = []
        filter_labels = []
        
        for label, size in zip(labels, sizes):
            
            if size > 0.:
                filter_sizes.append(size)
                filter_labels.append(label)
        
        labels = filter_labels
        sizes = np.array(filter_sizes)
        
        # Don't allow negative values
        if (sizes < 0).any(): return

        plt.figure()
        
        _, _, autotexts = plt.pie(sizes,
                                  labels=labels,
                                  autopct='%1.1f%%',
                                  shadow=True, 
                                  startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                              foreground='k')])
        
        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
        plt.title(self.meta.result.title, y=1.08)
        plt.tight_layout()

        self.fig_handle = plt.gcf()
        
        return


class SimpleDataColumn(SimpleData):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        result = get_one_from_column(self._db,
                                     schema,
                                     table,
                                     self.meta.result.tables[1])

        if result is not None and result[0] is not None:
            self.data.result = result[0]

        return
        

class SimpleDataForeignColumn(SimpleData):
    
    """Table meta data keys are as follows:
    
    1. The primary table with the foreign key column
    2. The secondary table to retrieve the data from
    3. The column to extract the value of the foreign key in the primary table
    4. The column to filter the key value against in the secondary table
    5. The column to retrieve as the result in the secondary table.
    
    """

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)
            
        schema, table = self.meta.result.tables[0].split(".")
        
        table_two_id = get_one_from_column(self._db,
                                           schema,
                                           table,
                                           self.meta.result.tables[2])

        if table_two_id is None or table_two_id[0] is None: return
                                               
        schema, table = self.meta.result.tables[1].split(".")

        result = filter_one_from_column(self._db,
                                        schema,
                                        table,
                                        self.meta.result.tables[4],
                                        self.meta.result.tables[3],
                                        table_two_id[0])
                
        if result is not None and result[0] is not None:
            self.data.result = result[0]

        return
        
        
class DirectoryDataColumn(DirectoryData):

    @staticmethod
    def auto_db(self):

        SimpleDataColumn.auto_db(self)

        return


class SimpleListColumn(SimpleList):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         [self.meta.result.tables[1]])
        
        result = col_lists[0]
        
        if result and set(result) != set([None]):
            self.data.result = result

        return
    
    @staticmethod
    def _auto_file_input(self):
        
        return
     
    @staticmethod
    def _auto_file_output(self):
        
        return


class SimpleDictColumn(SimpleDict):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:3])
        
        result = {k: v for k, v in zip(col_lists[0], col_lists[1])
                                        if k is not None and v is not None}
        
        if result: self.data.result = result

        return
    
    
class DateTimeData(Structure):

    '''A datetime.dateime data object'''

    def get_data(self, raw, meta_data):

        if not isinstance(raw, datetime):

            errStr = ("DateTimeData requires a datetime.datetime object as "
                      "raw data.")
            raise TypeError(errStr)

        return raw

    def get_value(self, data):

        return data


class DateTimeDict(DateTimeData):

    '''Dictionary containing a named variable as a key and a datatime as the
    value.'''

    def get_data(self, raw, meta_data):

        raw_dict = raw
        checked_dict = {}

        try:

            for key, value in raw_dict.iteritems():
                            
                date_item = super(DateTimeDict, self).get_data(value,
                                                               meta_data)
                checked_dict[key] = date_item

        except AttributeError:

            errStr = ("Raw data may not be a dictionary. Type is actually "
                      "{}.").format(type(raw_dict))
            raise AttributeError(errStr)

        except TypeError:

            errStr = ("Raw data is of incorrect type. Should be "
                      "datetime.datetime, but is {}.").format(type(value))
            raise TypeError(errStr)

        return checked_dict

    def get_value(self, data):

        return deepcopy(data)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        
        if not ("data" in df.columns 
                and "ID" in df.columns):
            raise ValueError("The file does not contain the correct ",
                             "header. The data column needs to have the ",
                             "header: 'data' and the key colum needs to have "
                             "the header: 'ID'")
        
        result = {}
        
        for key, data in zip(df.ID, df.data):
            
            ts = pd.to_datetime(data)
            dt = ts.to_pydatetime()
            
            result[key] = dt
            
        if not result: result = None
            
        self.data.result = result
        
        return
        
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        dc = self.data.result
        data = [[k,v] for k,v in dc.iteritems()]
        df = pd.DataFrame(data, columns=["ID", "data"])
        
        if ".xls" in self._path:
            writer = pd.ExcelWriter(self._path, engine='xlsxwriter')
            df.to_excel(writer, index=False)
            writer.save()
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        
        return
        
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]


class TriStateData(Structure):
    
    '''Data that can be "true", "false" or "unknown". Must be provided as
    a string'''
    
    def get_data(self, raw, meta_data):
        
        if isinstance(raw, basestring):
            
            if raw in ["true", "false", "unknown"]:
                
                return raw
        
        errStr = ('Given raw value is incorrectly formatted. It must be '
                  'a string with value "true", "false" or "unknown". '
                  'Given was: {}').format(raw)
        raise ValueError(errStr)
    
    def get_value(self, data):
        
        return deepcopy(data)


class PointData(Structure):

    '''A shapely Point variable. These are expected to be georeferenced.'''

    def get_data(self, raw, meta_data):
        
        if isinstance (raw, Point):
            
            point = raw
            
        else:
            
            # Don't allow misshapen data
            if not 1 < len(raw) < 4:
                errStr = ("Raw data must contain 2 or 3 coordinates. "
                          "Given data has {}").format(len(raw))
                raise ValueError(errStr)
            
            point = Point(*[float(x) for x in raw])

        return point

    def get_value(self, data):
        
        result = None
        
        if data is not None:
            result = Point(data)
        
        return result
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path or ".csv" in self._path:
            data = PointData._read_table(self._path)
        elif ".shp" in self._path:
            data = PointData._read_shapefile(self._path)
        else:
             raise TypeError("The specified file format is not supported. ",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.shp',
                                                                    '.xls',
                                                                    '.xlsx'))
        
        self.data.result = data
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        points = [self.data.result]
        
        if ".xls" in self._path or ".csv" in self._path:
            PointData._write_table(self._path, points)
        elif ".shp" in self._path:
            PointData._write_shapefile(self._path, points)
        else:
             raise TypeError("The specified file format is not supported. ",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.shp',
                                                                    '.xls',
                                                                    '.xlsx'))
        
        return
    
    @staticmethod
    def _read_table(path):
        
        if ".xls" in path:
            df = pd.read_excel(path)
        elif ".csv" in path:
            df = pd.read_csv(path) 
        
        if "x" in df.columns and "y" in df.columns:
            
            data = np.c_[df.x,df.y]
            if "z" in df.columns: data = np.c_[data, df.z]
        
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "x, y, z(optional))")
        
        result = Point(data[0])
        
        return result
    
    @staticmethod
    def _write_table(path, points):
        
        point = points[0]
        
        if isinstance(point, Point):
            data_ = np.array(point).reshape((1, -1))
        else:
            raise TypeError("Data type not understood: type for a "
                            "PointData subclass is shapely Point")
        
        data = {"x": data_[:,0],
                "y": data_[:,1]}
        
        if data_.shape[1] == 3:
            data["z"] = data_[:,2]
        
        df = pd.DataFrame(data)
        
        if ".xls" in path:
            df.to_excel(path, index=False)
        elif ".csv" in path:
            df.to_csv(path, index=False)
        
        return
    
    @staticmethod
    def _read_shapefile(path):
        
        with shapefile.Reader(path) as shp:
        
            if shp.shapeType not in [shapefile.POINT, shapefile.POINTZ]:
                
                err_str = ("The imported shapefile must have POINT or POINTZ "
                           "type. Given file has {} "
                           "type").format(shp.shapeTypeName)
                raise ValueError(err_str)
            
            shapes = shp.shapes()
            
            if len(shapes) != 1:
                
                err_str = ("Only one shape may be defined in the imported "
                           "shapefile. Given file has {} "
                           "shapes").format(len(shapes))
                raise ValueError(err_str)
            
            s = shapes[0]
            point = s.points[0]
            
            if shp.shapeType == shapefile.POINTZ:
                point.append(s.z[0])
        
        data = Point(point)
        
        return data
    
    @staticmethod
    def _write_shapefile(path, points):
        
        point = points[0]
        
        if isinstance(point, Point):
            data = np.array(point)
        else:
            raise TypeError("Data is not a valid Point object.")
            
        with shapefile.Writer(path) as shp:
            
            shp.field('name', 'C')
            
            if len(data) == 3: 
                shp.pointz(*data)
            else:
                shp.point(*data)
            
            shp.record('point1')
        
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".shp", ".xls", ".xlsx"]

    @staticmethod
    def auto_plot(self):

        x = self.data.result.x
        y = self.data.result.y

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1,aspect='equal')
        ax1.plot(x,y,'k+', mew=2, markersize=10)
        ax1.margins(0.1,0.1)
        ax1.autoscale_view()

        xlabel=''
        ylabel=''

        if self.meta.result.labels is not None:
            xlabel = self.meta.result.labels[0]
            ylabel = self.meta.result.labels[1]

        if self.meta.result.units is not None:
            xlabel = "{} [${}$]".format(xlabel, self.meta.result.units[0])
            ylabel = "{} [${}$]".format(ylabel, self.meta.result.units[1])

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)

        plt.title(self.meta.result.title)

        self.fig_handle = plt.gcf()
        
        return


class PointList(PointData):
    
    '''A list containing shapely Point variables as values'''
    
    def get_data(self, raw, meta_data):
        
        point_list = [super(PointList, self).get_data(xy, meta_data)
                                                            for xy in raw]
        
        return point_list
    
    def get_value(self, data):
        
        new_point_list = None
        
        if data is not None:
            new_point_list = [
                            super(PointList, self).get_value(p) for p in data]
        
        return new_point_list
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path or ".csv" in self._path:
            data = PointList._read_table(self._path)
        elif ".shp" in self._path:
            data = PointList._read_shapefile(self._path)
        else:
             raise TypeError("The specified file format is not supported. ",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.shp',
                                                                    '.xls',
                                                                    '.xlsx'))
        
        self.data.result = data
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        points = self.data.result
        
        if ".xls" in self._path or ".csv" in self._path:
            PointList._write_table(self._path, points)
        elif ".shp" in self._path:
            PointList._write_shapefile(self._path, points)
        else:
             raise TypeError("The specified file format is not supported. ",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.shp',
                                                                    '.xls',
                                                                    '.xlsx'))
        
        return
    
    @staticmethod
    def _read_table(path):
        
        if ".xls" in path:
            df = pd.read_excel(path)
        elif ".csv" in path:
            df = pd.read_csv(path) 
        
        if "x" in df.columns and "y" in df.columns:
            
            data = np.c_[df.x,df.y]
            if "z" in df.columns: data = np.c_[data, df.z]
        
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "x, y, z(optional))")
        
        result = [Point(coord) for coord in data]
        
        return result
    
    @staticmethod
    def _write_table(path, points):
        
        for point in points:
            if not isinstance(point, Point):
                raise TypeError("Data type not understood: type for a "
                                "PointData subclass is shapely Point")
        
        data_ = np.array([np.array(point) for point in points])
        
        data = {"x": data_[:, 0],
                "y": data_[:, 1]}
        
        if data_.shape[1] == 3:
            data["z"] = data_[:, 2]
        
        df = pd.DataFrame(data)
        
        if ".xls" in path:
            df.to_excel(path, index=False)
        elif ".csv" in path:
            df.to_csv(path, index=False)
        
        return
    
    @staticmethod
    def _read_shapefile(path):
        
        with shapefile.Reader(path) as shp:
        
            if shp.shapeType not in [shapefile.MULTIPOINT,
                                     shapefile.MULTIPOINTZ]:
                
                err_str = ("The imported shapefile must have MULTIPOINT or "
                           "MULTIPOINTZ type. Given file has {} "
                           "type").format(shp.shapeTypeName)
                raise ValueError(err_str)
            
            shapes = shp.shapes()
            
            if len(shapes) != 1:
                
                err_str = ("Only one shape may be defined in the imported "
                           "shapefile. Given file has {} "
                           "shapes").format(len(shapes))
                raise ValueError(err_str)
            
            s = shapes[0]
        
        if shp.shapeType == shapefile.MULTIPOINTZ:
            result = [Point(point + (z,)) for point, z in zip(s.points, s.z)]
        else:
            result = [Point(point) for point in s.points]
        
        return result
    
    @staticmethod
    def _write_shapefile(path, points):
        
        for point in points:
            if not isinstance(point, Point):
                raise TypeError("Data type not understood: type for a "
                                "PointData subclass is shapely Point")
        
        data = np.array([np.array(point) for point in points])
        
        with shapefile.Writer(path) as shp:
            
            shp.field('name', 'C')
            
            if data.shape[1] == 3:
                shp.multipointz(data)
            else:
                shp.multipoint(data)
            
            shp.record('multipoint1')
        
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".shp", ".xls", ".xlsx"]
    
    @staticmethod
    def auto_plot(self):

        x = []
        y = []

        for coords in self.data.result:
            x.append(coords.x)
            y.append(coords.y)

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1,aspect='equal')
        ax1.plot(x,y,'k+', mew=2, markersize=10)
        ax1.margins(0.1,0.1)
        ax1.autoscale_view()

        xlabel=''
        ylabel=''

        if self.meta.result.labels is not None:
            xlabel = self.meta.result.labels[0]
            ylabel = self.meta.result.labels[1]

        if self.meta.result.units is not None:
            xlabel = "{} [${}$]".format(xlabel, self.meta.result.units[0])
            ylabel = "{} [${}$]".format(ylabel, self.meta.result.units[1])

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)

        plt.title(self.meta.result.title)

        self.fig_handle = plt.gcf()
        
        return


class PointDict(PointData):

    '''A dictionary containing shapely Point variables as values'''

    def get_data(self, raw, meta_data):

        points_dict = {k: super(PointDict, self).get_data(v, meta_data)
                                                for k, v in raw.items()}

        return points_dict

    def get_value(self, data):
        
        new_points_dict = None

        if data is not None:
            new_points_dict = {k: super(PointDict, self).get_value(v)
                                                for k, v in data.items()}

        return new_points_dict
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        else:
             raise TypeError("The specified file format is not supported. ",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.xls',
                                                                    '.xlsx'))  
        
        if all([el in df.columns for el in ["x", "y", "ID"]]):
            data = np.c_[df.x,df.y]
            if "z" in df.columns: data = np.c_[data, df.z]

        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers shuld be defined as: "
                             "ID, x, y, z(optional))")
        
        self.data.result = dict(zip(df.ID, [Point(xyz) for xyz in data]))
        
        return
    
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        if isinstance(self.data.result, dict):
            data_ = np.array([[k]+list(np.array(el)) for k, el in
                                                  self.data.result.items()])
        else:
            raise TypeError("Data type not understood: possible type for a "
                            "PointData subclass are: Point, list, dictionary")
                                
        data = {"x": data_[:,1],
                "y": data_[:,2],
                "ID": data_[:,0]}
                
        if data_.shape[1]-1 == 3:
            data["z"] = data_[:,3]
        
        df = pd.DataFrame(data)
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        else:
            raise TypeError("The specified file format is not supported.",
                            "Supported format are {},{},{}".format('.csv',
                                                                   '.xls',
                                                                   '.xlsx'))
                
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]
    
    @staticmethod
    def auto_plot(self):

        x = []
        y = []

        for coords in self.data.result.itervalues():
            x.append(coords.x)
            y.append(coords.y)

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
        ax1.plot(x, y, 'k+', mew=2, markersize=10)
        ax1.margins(0.1, 0.1)
        ax1.autoscale_view()
        
        for key, point in self.data.result.iteritems():
            
            coords = list(point.coords)[0]
            ax1.annotate(str(key),
                         xy=coords[:2],
                         xytext=(0, 10),
                         xycoords='data',
                         textcoords='offset pixels',
                         horizontalalignment='center',
                         weight="bold",
                         size='large')

        xlabel = ''
        ylabel = ''

        if self.meta.result.labels is not None:
            xlabel = self.meta.result.labels[0]
            ylabel = self.meta.result.labels[1]

        if self.meta.result.units is not None:
            xlabel = "{} [${}$]".format(xlabel, self.meta.result.units[0])
            ylabel = "{} [${}$]".format(ylabel, self.meta.result.units[1])

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)

        plt.title(self.meta.result.title)

        '''
        xlabel = self.meta.result.labels[0]
        ylabel = self.meta.result.labels[1]

        if self.meta.result.units[0] is not None:
            xlabel = "{} {}".format(xlabel, self.meta.result.units[0])

        plt.xlabel(xlabel)

        if self.meta.result.units[1] is not None:
            xlabel = "{} {}".format(ylabel, self.meta.result.units[1])

        plt.ylabel(ylabel)
        '''
        
        self.fig_handle = plt.gcf()
       
        return
        
        
class PointDataColumn(PointData):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        result = get_one_from_column(self._db,
                                     schema,
                                     table,
                                     self.meta.result.tables[1])
                     
        if result is not None and result[0] is not None:
            self.data.result = to_shape(result[0])

        return
        
        
class PointDictColumn(PointDict):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")
        
        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:3])
        
        filter_dict = {k: v for k, v in zip(col_lists[0], col_lists[1])
                                        if k is not None and v is not None}
        
        point_dict = {key: to_shape(wkb_point)
                                    for key, wkb_point in filter_dict.items()}
        
        if point_dict: self.data.result = point_dict

        return


class PolygonData(Structure):

    def get_data(self, raw, meta_data):
        
        if isinstance (raw, Polygon):
            
            ring = raw
            
        else:
            
            np_raw = np.array(raw)
            
            if len(np_raw.shape) != 2:
                errStr = ("Raw data must have exactly 2 dimensions. Given "
                          "data has {}").format(len(np_raw))
                raise ValueError(errStr)
            
            # Don't allow misshapen data
            if not 1 < np_raw.shape[1] < 4:
                errStr = ("Raw data must contain 2 or 3 dimensional "
                          "coordinates. Given data has {}").format(len(raw))
                raise ValueError(errStr)
            
            ring = Polygon(np_raw)
        
        return ring

    def get_value(self, data):
        
        result = None
        
        if data is not None:
            result = Polygon(data)

        return result
        
    @staticmethod
    def auto_plot(self):

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1,aspect='equal')

        patch = PolygonPatch(self.data.result,
                             fc=BLUE,
                             ec=BLUE,
                             fill=False,
                             linewidth=2)
        ax1.add_patch(patch)
        
        coords = list(self.data.result.exterior.coords)
        
        for i, xy in enumerate(coords[:-1]):
            
            ax1.annotate("({:.1f}, {:.1f})".format(*xy[:2]),
                         xy=xy[:2],
                         horizontalalignment='center',
                         weight="bold",
                         size='large')

        ax1.margins(0.1,0.1)
        ax1.autoscale_view()

        xlabel = 'UTM x [$m$]'
        ylabel = 'UTM y [$m$]'

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha='right')

        plt.title(self.meta.result.title)
        plt.tight_layout()

        self.fig_handle = plt.gcf()
        
        return
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path or ".csv" in self._path:
            data = PolygonData._read_table(self._path)
        elif ".shp" in self._path:
            data = PolygonData._read_shapefile(self._path)
        else:
             raise TypeError("The specified file format is not supported. ",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.shp',
                                                                    '.xls',
                                                                    '.xlsx'))
        
        self.data.result = data
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        poly = self.data.result
        
        if ".xls" in self._path or ".csv" in self._path:
            PolygonData._write_table(self._path, poly)
        elif ".shp" in self._path:
            PolygonData._write_shapefile(self._path, poly)
        else:
             raise TypeError("The specified file format is not supported. ",
                             "Supported format are {},{},{}".format('.csv',
                                                                    '.shp',
                                                                    '.xls',
                                                                    '.xlsx'))
        
        return
    
    @staticmethod
    def _read_table(path):
        
        if ".xls" in path:
            df = pd.read_excel(path)
        elif ".csv" in path:
            df = pd.read_csv(path) 
             
        if len(df) < 3:
            raise ValueError("PolygonError: A LinearRing must have ",
                             "at least 3 coordinate tuples")
        
        
        if "x" in df.columns and "y" in df.columns and "z" in df.columns:
            
            data = Polygon(np.c_[df.x, df.y, df.z])
            
        elif "x" in df.columns and "y" in df.columns:
            
            data = Polygon(np.c_[df.x, df.y])
            
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers should be defined as: "
                             "x, y, z(optional)")
            
        return data
    
    @staticmethod
    def _write_table(path, polygon):
        
        if isinstance(polygon, Polygon):
            data = np.array(polygon.exterior.coords[:])[:-1]
        else:
            raise TypeError("The result does not contain valid",
                            " Polygon object.")
            
        if data.shape[1] == 2:
            columns = ["x", "y"]
        elif data.shape[1] == 3:
            columns = ["x", "y", "z"]
        else:
            errStr = "Look, I'm a doctor, not an escalator."
            raise SystemError(errStr)
        
        df = pd.DataFrame(data, columns=columns)
        
        if ".xls" in path:
            df.to_excel(path, index=False)
        elif ".csv" in path:
            df.to_csv(path, index=False)
        
        return
    
    @staticmethod
    def _read_shapefile(path):
        
        with shapefile.Reader(path) as shp:
        
            if shp.shapeType not in [shapefile.POLYGON, shapefile.POLYGONZ]:
                
                err_str = ("The imported shapefile must have POLYGON or "
                           "POLYGONZ type. Given file has {} "
                           "type").format(shp.shapeTypeName)
                raise ValueError(err_str)
            
            shapes = shp.shapes()
            
            if len(shapes) != 1:
                
                err_str = ("Only one shape may be defined in the imported "
                           "shapefile. Given file has {} "
                           "shapes").format(len(shapes))
                raise ValueError(err_str)
            
            s = shapes[0]
            
            if len(s.parts) != 1:
                
                err_str = ("Only polygons with exterior coordinates may be "
                           "defined in the imported shapefile. Given file has "
                           "{} parts").format(len(s.parts))
                raise ValueError(err_str)
        
        if shp.shapeType == shapefile.POLYGONZ:
            points = [point + (z,) for point, z in zip(s.points, s.z)]
        else:
            points = s.points
        
        data = Polygon(points)
        
        return data
    
    @staticmethod
    def _write_shapefile(path, polygon):
        
        if isinstance(polygon, Polygon):
            data = np.array(polygon.exterior.coords)
        else:
            raise TypeError("Data is not a valid Polygon object.")
            
        with shapefile.Writer(path) as shp:
            
            shp.field('name', 'C')
            
            if data.shape[1] == 3:
                shp.polyz([data.tolist()])
            else:
                shp.poly([data.tolist()])
            
            shp.record('polygon1')
        
        return
    
    @staticmethod
    def get_valid_extensions(cls):
        
        return [".csv", ".shp", ".xls", ".xlsx"]

    
class PolygonDataColumn(PolygonData):
    
    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        result = get_one_from_column(self._db,
                                     schema,
                                     table,
                                     self.meta.result.tables[1])

        if result is not None and result[0] is not None:
            self.data.result = to_shape(result[0])

        return


class PolygonList(PolygonData):

    def get_data(self, raw, meta_data):

        ring_list = [super(PolygonList, self).get_data(x, meta_data)
                                                            for x in raw]

        return ring_list

    def get_value(self, data):
        
        ring_list = None
        
        if data is not None:
            ring_list = [super(PolygonList, self).get_value(x) for x in data]

        return ring_list
        
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)
        
        if ("ID" in df.columns and
            "x" in df.columns and
            "y" in df.columns and
            "z" in df.columns):
            
            ks = np.unique(df.ID)
            data = []
            
            for k in ks:
                
                t = df[df["ID"]==k]
                data.append(Polygon(np.c_[t.x, t.y, t.z]))

        elif "ID" in df.columns and "x" in df.columns and "y" in df.columns:
            
            ks = np.unique(df.ID)
            data = []
            
            for k in ks:
                
                t = df[df["ID"]==k]
                data.append(Polygon(np.c_[t.x, t.y]))
                
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers should be defined as: "
                             "ID, x, y, z(optional)")
                             
        self.data.result = data
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        polys = self.data.result
        data = []
        for ip, poly in enumerate(polys):
            if isinstance(poly, Polygon):
                data.append(("polygon-{}".format(ip),
                               np.array(poly.exterior.coords[:])[:-1]))
            else:
                raise TypeError("The result list does not contain valid",
                                " Polygon objects.")
                                        
        if data[0][1].shape[1] == 2:
            columns = ["ID", "x", "y"]
        elif data[0][1].shape[1] == 3:
            columns = ["ID", "x", "y", "z"]
        else:
            errStr = "I'm a doctor, not a bricklayer."
            raise SystemError(errStr)
        
        df = pd.DataFrame(columns=columns)
        for k, v in data:
            df2 = pd.DataFrame(v, columns=columns[1:])
            df2["ID"] = [k]*v.shape[0]
            
            df = df.append(df2,
                           ignore_index=True,
                           sort=False)
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
                
        return
    
    @staticmethod        
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]

    @staticmethod
    def auto_plot(self):

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1,aspect='equal')

        for polygon in self.data.result:
            patch = PolygonPatch(polygon,
                                 fc=BLUE,
                                 ec=BLUE,
                                 fill=False,
                                 linewidth=2)
            ax1.add_patch(patch)

        ax1.margins(0.1,0.1)
        ax1.autoscale_view()

        xlabel = 'UTM x [$m$]'
        ylabel = 'UTM y [$m$]'

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha='right')

        plt.title(self.meta.result.title)
        plt.tight_layout()

        self.fig_handle = plt.gcf()
        
        return
        

class PolygonListColumn(PolygonList):

    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")
        
        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         [self.meta.result.tables[1]])
                             
        all_entries = col_lists[0]
                
        if all_entries and set(all_entries) != set([None]):
            self.data.result = [to_shape(wkb_poly)
                                                for wkb_poly in all_entries]

        return
        
        
class PolygonDict(PolygonData):

    def get_data(self, raw, meta_data):

        ring_dict = {k: super(PolygonDict, self).get_data(v, meta_data)
                                                    for k, v in raw.items()}
                                                        
        return ring_dict

    def get_value(self, data):
        
        ring_dict = None

        if data is not None:
            ring_dict = {k: super(PolygonDict, self).get_value(v)
                                                    for k, v in data.items()}
                                                        
        return ring_dict
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path()
        
        if ".xls" in self._path:
            df = pd.read_excel(self._path)
        elif ".csv" in self._path:
            df = pd.read_csv(self._path)

        data = {}

        if ("ID" in df.columns and
            "x" in df.columns and
            "y" in df.columns and
            "z" in df.columns):
            
            ks = np.unique(df.ID)

            for k in ks:
                
                t = df[df["ID"] == k]
                data[k] = Polygon(np.c_[t.x, t.y, t.z])

        elif "ID" in df.columns and "x" in df.columns and "y" in df.columns:
            
            ks = np.unique(df.ID)
            
            for k in ks:
                
                t = df[df["ID"] == k]
                data[k] = Polygon(np.c_[t.x, t.y])
                
        else:
            
            raise ValueError("The specified file structure is not supported, "
                             "the columns' headers should be defined as: "
                             "ID, x, y, z(optional)")
                             
        self.data.result = data
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        polys = self.data.result
        data = []
        
        for name, poly in polys.iteritems():
            
            if isinstance(poly, Polygon):
                data.append((name, np.array(poly.exterior.coords[:])[:-1]))
            else:
                raise TypeError("The result list does not contain valid",
                                " Polygon objects.")
                                        
        if data[0][1].shape[1] == 2:
            columns = ["ID", "x", "y"]
        elif data[0][1].shape[1] == 3:
            columns = ["ID", "x", "y", "z"]
        else:
            errStr = "I'm a doctor, not a coal miner."
            raise SystemError(errStr)
        
        df = pd.DataFrame(columns=columns)
        
        for k, v in data:
            
            df2 = pd.DataFrame(v, columns=columns[1:])
            df2["ID"] = [k]*v.shape[0]
            
            df = df.append(df2,
                           ignore_index=True,
                           sort=False)
        
        if ".xls" in self._path:
            df.to_excel(self._path, index=False)
        elif ".csv" in self._path:
            df.to_csv(self._path, index=False)
        
        return
    
    @staticmethod        
    def get_valid_extensions(cls):
        
        return [".csv", ".xls", ".xlsx"]

    @staticmethod
    def auto_plot(self):

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
            
        for key, polygon in self.data.result.iteritems():
            
            patch = PolygonPatch(polygon,
                                 fc=BLUE,
                                 ec=BLUE,
                                 fill=False,
                                 linewidth=2)
            ax1.add_patch(patch)
            
            centroid = np.array(polygon.centroid)
            ax1.annotate(str(key),
                         xy=centroid[:2],
                         xytext=(0, 0),
                         xycoords='data',
                         textcoords='offset pixels',
                         horizontalalignment='center',
                         weight="bold",
                         size='large')

        ax1.margins(0.1, 0.1)
        ax1.autoscale_view()

        xlabel = 'UTM x [$m$]'
        ylabel = 'UTM y [$m$]'

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha='right')

        plt.title(self.meta.result.title)
        plt.tight_layout()

        self.fig_handle = plt.gcf()
        
        return

class PolygonDictColumn(PolygonDict):
    
    @staticmethod
    def auto_db(self):

        if self.meta.result.tables is None:

            errStr = ("Tables not defined for variable "
                      "'{}'.").format(self.meta.result.identifier)
            raise ValueError(errStr)

        schema, table = self.meta.result.tables[0].split(".")

        col_lists = get_all_from_columns(self._db,
                                         schema,
                                         table,
                                         self.meta.result.tables[1:3])

        filter_dict = {k: v for k, v in zip(col_lists[0], col_lists[1])
                                        if k is not None and v is not None}
        
        poly_dict = {key: to_shape(wkb_poly)
                                    for key, wkb_poly in filter_dict.items()}
        
        if poly_dict: self.data.result = poly_dict

        return


class XGridND(Structure):
    
    '''xrarray DataArray object. See xarray.pydata.org
    
    Note: This class should not be used directly, subclass and set get_n_dims
    to an integer value.'''
    
    def get_n_dims(self):
        
        errStr = "Only subclasses of XGridND may be used."
        
        raise NotImplementedError(errStr)
    
    def get_data(self, raw, meta_data):
        
        """
        Add raw data.
        
        Args:
            data (dict): dictionary with following keys:
                values (numpy.ndarray): The data to store.
                coords (list): List of arrays or lists with the coordinates for
                    each dimension. They are ordered by the dimensions of the
                    array.
        
        Note:
            The "labels" key in the DDS files is used to provide dimension
                and data dimension names. The number of labels should match
                the number of dimensions in the data
            The "units" key in the DDS files is used to add units attributes
                to the dimensions and the data. The first n entries matches
                the dimesnions and the last matches the data.
        """
        
        coords = raw["coords"]
        n_dims = self.get_n_dims()
        
        if meta_data.labels is None:
            
            errStr = ("Labels metadata must be set for {} data "
                      "structures").format(self.__class__.__name__)
            raise ValueError(errStr)
        
        dims = meta_data.labels[:]
        
        if len(dims) != n_dims:
            
            errStr = ("Given number of labels is incorrect. The data has {} "
                      "dimensions but {} labels are given").format(len(dims),
                                                                   n_dims)
            raise ValueError(errStr)
        
        if meta_data.units is not None:
            units = meta_data.units[:]
        else:
            units = None
        
        coords, attrs = self._get_coords_attrs(dims,
                                               coords,
                                               units)
        
        data_array = xr.DataArray(raw["values"],
                                  coords=coords,
                                  attrs=attrs)
        
        return data_array
    
    def _get_coords_attrs(self, dims, coords, units):
        
        if len(dims) != len(coords):
            
            errStr = ("The number of coordinate lists must match the number "
                      "of labels.")
            raise ValueError(errStr)
        
        if units is not None and len(units) != len(dims) + 1:
            
            errStr = ("The number of units must match the number "
                      "of labels plus one.")
            raise ValueError(errStr)
        
        attrs = None
        coord_tuples = []
        
        for dim, coord_list in zip(dims, coords):
            coord_tuples.append((dim, coord_list))
        
        if units is not None:
            
            data_unit = units.pop()
            
            if data_unit is not None:
                attrs = {'units': data_unit}
            
            new_tuples = []
            
            for coord_item, unit in zip(coord_tuples, units):
                
                if unit is not None:
                    
                    coord_attrs = {'units': unit}
                    new_coord_item = (coord_item[0],
                                      coord_item[1],
                                      coord_attrs)
                
                else:
                    
                    new_coord_item = coord_item
                
                new_tuples.append(new_coord_item)
            
            coord_tuples = new_tuples
        
        return coord_tuples, attrs
    
    def get_value(self, data):
        
        result = None
        
        if data is not None:
            result = data.copy(deep=True)
        
        return result
    
    @classmethod
    def equals(cls, left, right):
        
        return left.identical(right)
    
    @staticmethod
    def auto_file_input(self):
        
        self.check_path(True)
                             
        dataset = xr.open_dataset(self._path)
        
        coord_list = []
            
        for coord in self.meta.result.labels:
                               
            coord_list.append(dataset.coords[coord])
            
        raw_dict = {"values": dataset["data"].values,
                    "coords": coord_list}
        
        self.data.result = raw_dict
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data = self.data.result
        
        data = data.to_dataset(name="data")
        data.to_netcdf(self._path, format="NETCDF4")
        
        return
    
    @staticmethod        
    def get_valid_extensions(cls):
        
        return [".nc"]


class XGrid2D(XGridND):

    '''xrarray DataArray object with 2 dimensions and arbitrary number of
    values. See xarray.pydata.org'''

    def get_n_dims(self):

        return 2

    @staticmethod
    def auto_plot(self):
        
        xcoord = self.data.result.coords[self.meta.result.labels[0]]
        ycoord = self.data.result.coords[self.meta.result.labels[1]]
        
        if xcoord.values.dtype.kind in {'U', 'S'}:
            xuniques = xcoord.values
            x = range(len(xuniques))
        else:
            xuniques, x = np.unique(xcoord, return_inverse=True)
            
        if ycoord.values.dtype.kind in {'U', 'S'}:
            yuniques = ycoord.values
            y = range(len(yuniques))
        else:
            yuniques, y = np.unique(ycoord, return_inverse=True)
        
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
        plt.contourf(x, y, self.data.result.T)
        clb = plt.colorbar()
        
        xlabel = self.meta.result.labels[0]
        ylabel = self.meta.result.labels[1]
        
        if self.meta.result.units is not None:
            
            if self.meta.result.units[0] is not None:
                xlabel = "{} [${}$]".format(xlabel, self.meta.result.units[0])
                
            if self.meta.result.units[1] is not None:
                ylabel = "{} [${}$]".format(ylabel, self.meta.result.units[1])
            
            if self.meta.result.units[2] is not None:
                clb.set_label("${}$".format(self.meta.result.units[2]))
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        if xcoord.values.dtype.kind in {'U', 'S'}:
            plt.xticks(x, xuniques)
        else:
            locs, _ = plt.xticks()
            f = interpolate.interp1d(x, xuniques, fill_value="extrapolate")
            new_labels = ['{0:.8g}'.format(tick) for tick in f(locs)]
            plt.xticks(locs, new_labels)
        
        if ycoord.values.dtype.kind in {'U', 'S'}:
            plt.yticks(y, yuniques)
        else:
            locs, _ = plt.yticks()
            f = interpolate.interp1d(y, yuniques, fill_value="extrapolate")
            new_labels = ['{0:.8g}'.format(tick) for tick in f(locs)]
            plt.yticks(locs, new_labels)
        
        plt.title(self.meta.result.title)
        
        self.fig_handle = plt.gcf()
        
        return


class XGrid3D(XGridND):

    '''xrarray DataArray object with 3 dimensions and arbitrary number of
    values. See xarray.pydata.org'''

    def get_n_dims(self):

        return 3


class XSetND(XGridND):

    '''xrarray Dataset object with n_dims dimensions and arbitrary number of
    values. See xarray.pydata.org

    Note: This class should not be used directly, subclass and set get_n_dims
    to an integer value.'''

    def get_data(self, raw, meta_data):

        """
        Add raw data.

        Args:
            data (dict): dictionary with following keys:
                values (dict): keys: dataset name
                               values (numpy.ndarray): The data to store.
                coords (list): List of arrays or lists with the coordinates for
                    each dimension. They are ordered by the dimensions of the
                    array.

        Note:
            The "labels" key in the DDS files is used to provide dimension
                and data dimension names. The first n labels will be used
                to define the dimension names, the remaining should match
                to the name of each data item stored in the set.
            The "units" key in the DDS files is used to add units attributes
                to the dimensions and the data. The first n entries matches
                the dimesnions and the last matches the data.
        """

        n_dims = self.get_n_dims()

        if meta_data.labels is None:

            errStr = ("Labels metadata must be set for {} data "
                      "structures").format(self.__class__.__name__)
            raise ValueError(errStr)
            
        if len(meta_data.labels) < n_dims:
            
            errStr = "Insufficent entries in labels metadata to set dimensions"
            raise ValueError(errStr)

        dims = meta_data.labels[:n_dims]
        set_names = meta_data.labels[n_dims:]
        
        if not set_names:
            
            errStr = "No data labels are set in labels metadata."
            raise ValueError(errStr)
        
        missing_values = set(set_names) - set(raw["values"])
        
        if missing_values:
            
            errStr = "Data labels '{}' are missing from raw data".format(
                                                    ", ".join(missing_values))
            raise ValueError(errStr)

        if meta_data.units is not None:
            all_units = meta_data.units[:]
            coord_units = meta_data.units[:n_dims]
        else:
            all_units = None
            coord_units = None

        set_dict = {}

        for k in raw["values"]:
            
            if k not in set_names:
                
                errStr = ("Data label '{}' is not valid for this structure "
                          "defintion. Must be one of: "
                          "{}").format(k, ", ".join(set_names))
                raise ValueError(errStr)

            if all_units is not None:
                unit_idx = set_names.index(k)
                local_units = coord_units[:]
                local_units.append(all_units[unit_idx + n_dims])
            else:
                local_units = None

            coords, attrs = self._get_coords_attrs(dims,
                                                   raw["coords"],
                                                   local_units)

            data_array = xr.DataArray(raw["values"][k],
                                      coords=coords,
                                      attrs=attrs)

            set_dict[k] = data_array

        data_set = xr.Dataset(set_dict)

        return data_set
        
    @staticmethod
    def auto_file_input(self):
        
        self.check_path(True)
                             
        dataset = xr.open_dataset(self._path)
        
        values_dict = {}
        
        for key, dataarray in dataset.data_vars.iteritems():
        
            values_dict[key] = dataarray.values
            
        n_vars = len(values_dict)
        
        coord_list = []
            
        for coord in self.meta.result.labels[:-n_vars]:
                               
            coord_list.append(dataset.coords[coord])
            
        raw_dict = {"values": values_dict,
                    "coords": coord_list}
        
        self.data.result = raw_dict

        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        data = self.data.result
        data.to_netcdf(self._path, format="NETCDF4")
        
        return
    
    @staticmethod        
    def get_valid_extensions(cls):
        
        return [".nc"]


class XSet2D(XSetND):

    '''xrarray Dataset object with 2 dimensions and arbitrary number of
    values. See xarray.pydata.org'''

    def get_n_dims(self):

        return 2


class XSet3D(XSetND):

    '''xrarray Dataset object with 3 dimensions and arbitrary number of
    values. See xarray.pydata.org'''

    def get_n_dims(self):

        return 3

   
class Strata(XSet3D):

    '''xrarray Dataset object with 3 dimensions and arbitrary number of
    values. This is a bespoke class for sediment layer retrieval.'''
    
    @staticmethod
    def auto_plot(self):
        
        bathy = self.data.result["depth"].sel(layer="layer 1")

        x = bathy.coords[self.meta.result.labels[0]]
        y = bathy.coords[self.meta.result.labels[1]]

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1,aspect='equal')
        plt.contourf(x, y, bathy.T)
        clb = plt.colorbar()
        
        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"
        zlabel = "Depth [$m$]"

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        clb.set_label(zlabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha='right')

        plt.title(self.meta.result.title)
        plt.tight_layout()

        self.fig_handle = plt.gcf()
        
        return
        
    @staticmethod
    def auto_file_input(self):
        
        self.check_path(True)
                             
        strata = xr.open_dataset(self._path)
                
        sediment_path = self._path.replace("depth", "sediment")
        sediment_data = xr.open_dataset(sediment_path)
        sediment_data = sediment_data.where(
                                        sediment_data["sediment"] != 'None')
        sediment_data = sediment_data.fillna(None)
        
        strata["sediment"] = sediment_data["sediment"]
        
        values_dict = {"depth": strata["depth"].values,
                       "sediment": strata["sediment"].values}
                               
        coord_list = [strata.coords[self.meta.result.labels[0]],
                      strata.coords[self.meta.result.labels[1]],
                      strata.coords["layer"]]
        
        raw_dict = {"values": values_dict,
                    "coords": coord_list}
        
        self.data.result = raw_dict
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        root_path = os.path.splitext(self._path)[0]
        
        depth_data = self.data.result["depth"]
        depth_set = depth_data.to_dataset()
        data_path = "{}_depth.nc".format(root_path)
        depth_set.to_netcdf(data_path, format="NETCDF4")
        
        sediment_data = self.data.result["sediment"]
        sediment_data = sediment_data.astype(str)
                
        sediment_set = sediment_data.to_dataset()
        data_path = "{}_sediment.nc".format(root_path)
        sediment_set.to_netcdf(data_path, format="NETCDF4")
        
        return


class Network(Structure): 

    '''Structure which describes the networked elements of the electrical and
    moorings / foundations outputs
    
    Note:
        A the highest level a dictionary is expected with two keys: topology
        and nodes. The topology key contains the connectivity of the network
        and the nodes key contains labels for the nodes, in particularly the
        quantity of components used at each node and a unique marker that can
        be used to assosiate external data to the node labels.'''

    def get_data(self, raw, meta_data):
        
        if set(raw.keys()) != set(["topology", "nodes"]):
            
            errStr = ("The two top level keys 'topology' and 'nodes' must "
                      "be set for a valid network.")
            raise KeyError(errStr)                      
                     
        # Need to test more of the network details here. Keys could be checked
        # along with counting the number of items vs the number of markers.

        return raw

    def get_value(self, data):

        return deepcopy(data)
        
    @staticmethod
    def auto_file_input(self):
        
        self.check_path(True)
        
        with open(self._path, 'r') as stream:
            data = yaml.load(stream, Loader=yaml.FullLoader)

        self.data.result = data
        
        return
     
    @staticmethod
    def auto_file_output(self):
        
        self.check_path()
        
        network_dict = self.data.result

        with open(self._path, 'w') as stream:
            yaml.dump(network_dict, stream, default_flow_style=False)
            
        return
    
    @staticmethod        
    def get_valid_extensions(cls):
        
        return [".yaml"]


class EIADict(Structure):

    '''Structure for storing environmental recommendations'''

    def get_data(self, raw, meta_data):

        return raw

    def get_value(self, data):

        return deepcopy(data)
        
    @staticmethod
    def auto_file_output(self):
        
        SimpleDict.auto_file_output(self)
        
        return
        
    @staticmethod
    def get_valid_extensions(cls):
        
        return SimpleDict.get_valid_extensions(cls)




class RecommendationDict(Structure):

    '''Structure for storing environmental recommendations'''

    def get_data(self, raw, meta_data):

        return raw

    def get_value(self, data):

        return deepcopy(data)
        
    @staticmethod
    def auto_file_output(self):
        
        SimpleDict.auto_file_output(self)
        
        return
        
    @staticmethod
    def get_valid_extensions(cls):
        
        return SimpleDict.get_valid_extensions(cls)


def _assign_type(raw, type_list):
    
    TypeCls = getattr(__builtin__, type_list[0])
    
    return TypeCls(raw)
