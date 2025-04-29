# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Rui Duarte
#    Copyright (C) 2016-2022 Mathew Topper
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

# pylint: disable=protected-access

import numpy as np
import pandas as pd

from dtocean_core.data.definitions import  (UnknownData,
                                            SeriesData,
                                            TimeSeries,
                                            TimeSeriesColumn,
                                            TableData,
                                            TableDataColumn,
                                            LineTable,
                                            LineTableExpand,
                                            LineTableColumn,
                                            TimeTable,
                                            TimeTableColumn,
                                            IndexTable,
                                            IndexTableColumn,
                                            TriStateTable,
                                            TriStateIndexTable,
                                            NumpyND,
                                            Numpy2D,
                                            Numpy2DColumn,
                                            Numpy3D,
                                            Numpy3DColumn,
                                            NumpyLine,
                                            NumpyLineDict,
                                            NumpyLineDictArrayColumn,
                                            NumpyBar,
                                            NumpyLineArray,
                                            NumpyLineColumn,
                                            Histogram,
                                            HistogramColumn,
                                            HistogramDict,
                                            CartesianData,
                                            CartesianDataColumn,
                                            CartesianList,
                                            CartesianListColumn,
                                            CartesianDict,
                                            CartesianDictColumn,
                                            CartesianListDict,
                                            CartesianListDictColumn,
                                            SimpleData,
                                            PathData,
                                            DirectoryData,
                                            SimpleList,
                                            SimpleDict,
                                            SimplePie,
                                            SimpleDataColumn,
                                            SimpleDataForeignColumn,
                                            DirectoryDataColumn,
                                            SimpleListColumn,
                                            SimpleDictColumn,
                                            DateTimeData,
                                            DateTimeDict,
                                            TriStateData,
                                            PointData,
                                            PointList,
                                            PointDict,
                                            PointDataColumn,
                                            PointDictColumn,
                                            PolygonData,
                                            PolygonDataColumn,
                                            PolygonList,
                                            PolygonListColumn,
                                            PolygonDict,
                                            PolygonDictColumn,
                                            XGrid2D,
                                            XGrid3D,
                                            XSet2D,
                                            XSet3D,
                                            Strata,
                                            Network,
                                            EIADict,
                                            RecommendationDict)

from ..widgets.input import (ListSelect,
                             FloatSelect,
                             IntSelect,
                             StringSelect,
                             DirectorySelect,
                             BoolSelect,
                             DateSelect,
                             CoordSelect,
                             PointSelect,
                             InputHistogram,
                             InputDataTable,
                             InputDictTable,
                             InputPointTable,
                             InputPointDictTable,
                             InputLineTable,
                             InputTimeTable,
                             InputTimeSeries,
                             InputTriStateTable)
from ..widgets.output import (LabelOutput,
                              TextOutput,
                              OutputDataTable)
                                            

class GUIStructure(object):
    """Dummy class for plugin detection"""


class UnknownData(GUIStructure, UnknownData):
    """Overloading UnknownData class"""


class SeriesData(GUIStructure, SeriesData):
    """Overloading SeriesData class"""
    
    @staticmethod
    def auto_output(self):
        
        df = self.data.result.to_frame()
        
        if self.meta.result.labels is None:
            labels = ["Data"]
        else:
            labels = [self.meta.result.labels[0]]

        if self.meta.result.units is None:
            units = [None]
        else:
            units = [self.meta.result.units[0]]

        widget = OutputDataTable(self.parent,
                                 labels,
                                 units)
        widget._set_value(df)
        
        self.data.result = widget

        return


class TimeSeries(GUIStructure, TimeSeries):
    """Overloading TimeSeries class"""
    
    @staticmethod
    def auto_input(self):
        
        if self.meta.result.labels is None:
            labels = ["Data"]
        else:
            labels = self.meta.result.labels
        
        widget = InputTimeSeries(self.parent,
                                 labels,
                                 self.meta.result.units)
        widget._set_value(self.data.result)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):
        
        SeriesData.auto_output(self)
        
        return
    
    
class TimeSeriesColumn(GUIStructure, TimeSeriesColumn):
    """Overloading TimeSeriesColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        TimeSeries.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        TimeSeries.auto_output(self)
        
        return


class TableData(GUIStructure, TableData):
    """Overloading TableData class"""
    
    @staticmethod
    def auto_input(self):
        
        widget = InputDataTable(self.parent,
                                self.meta.result.labels,
                                self.meta.result.units)
        widget._set_value(self.data.result, self.meta.result.types)
        
        self.data.result = widget
        
        return
    
    @staticmethod
    def auto_output(self):
        
        widget = OutputDataTable(self.parent,
                                 self.meta.result.labels,
                                 self.meta.result.units)
        widget._set_value(self.data.result)
        
        self.data.result = widget
        
        return


class TableDataColumn(GUIStructure, TableDataColumn):
    """Overloading TableDataColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        TableData.auto_input(self)
        
        return
        
    @staticmethod
    def auto_output(self):
        
        TableData.auto_output(self)
        
        return
        
        
class IndexTable(GUIStructure, IndexTable):
    """Overloading IndexTable class"""

    @staticmethod
    def auto_input(self):
        
        widget = InputDataTable(self.parent,
                                self.meta.result.labels,
                                self.meta.result.units,
                                self.meta.result.labels[0],
                                self.meta.result.valid_values)

        if self.data.result is not None:
            df = self.data.result.reset_index()
        else:
            df = None
        
        widget._set_value(df)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):
        
        widget = OutputDataTable(self.parent,
                                 self.meta.result.labels,
                                 self.meta.result.units)
        
        if self.data.result is not None:
            df = self.data.result.reset_index()
        else:
            df = None
            
        widget._set_value(df)
        
        self.data.result = widget

        return


class IndexTableColumn(GUIStructure, IndexTableColumn):
    """Overloading IndexTableColumn class"""

    @staticmethod
    def auto_input(self):
        
        IndexTable.auto_input(self)
        
        return
        
    @staticmethod
    def auto_output(self):
        
        IndexTable.auto_output(self)

        return


class LineTable(GUIStructure, LineTable):
    """Overloading LineTable class"""

    @staticmethod
    def auto_input(self):

        IndexTable.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        IndexTable.auto_output(self)
        
        return
    
    
class LineTableExpand(GUIStructure, LineTableExpand):
    """Overloading LineTableExpand class"""
    
    @staticmethod
    def auto_input(self):
        
        if self.data.result is not None:
            
            df = self.data.result.reset_index()
            labels = df.columns
            
        else:
            
            df = None
            labels = self.meta.result.labels
            
        if self.meta.result.units is not None:
            
            units = list(self.meta.result.units[:1])
            n_extra = len(labels) - 1
            
            if len(self.meta.result.units) > 1:
                add_units = [self.meta.result.units[1]] * n_extra
            else:
                add_units = [None] *  n_extra
                
            units += add_units
            
        else:
            
            units = None
        
        widget = InputDataTable(self.parent,
                                labels,
                                units,
                                self.meta.result.labels[0],
                                self.meta.result.valid_values,
                                True)
        
        widget._set_value(df)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):
        
        if self.data.result is not None:
            
            df = self.data.result.reset_index()
            labels = df.columns
            
        else:
            
            df = None
            labels = self.meta.result.labels
            
        if self.meta.result.units is not None:
            
            units = list(self.meta.result.units[:1])
            n_extra = len(labels) - 1
            
            if len(self.meta.result.units) > 1:
                add_units = [self.meta.result.units[1]] * n_extra
            else:
                add_units = [None] *  n_extra
                
            units += add_units
            
        else:

            units = None
            
        widget = OutputDataTable(self.parent,
                                 labels,
                                 units)
            
        widget._set_value(df)
        
        self.data.result = widget
        
        return


class LineTableColumn(GUIStructure, LineTableColumn):
    """Overloading LineTableColumn class"""

    @staticmethod
    def auto_input(self):
        
        LineTable.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        LineTable.auto_output(self)
        
        return


class TimeTable(GUIStructure, TimeTable):
    """Overloading TimeTable class"""

    @staticmethod
    def auto_input(self):

        widget = InputTimeTable(self.parent,
                                self.meta.result.labels,
                                self.meta.result.units)


        if self.data.result is not None:
            df = self.data.result.reset_index()
        else:
            df = None
        
        widget._set_value(df)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):
        
        widget = OutputDataTable(self.parent,
                                 self.meta.result.labels,
                                 self.meta.result.units)
        widget._set_value(self.data.result)
        
        self.data.result = widget

        return


class TimeTableColumn(GUIStructure, TimeTableColumn):
    """Overloading TimeTableColumn class"""

    @staticmethod
    def auto_input(self):
        
        TimeTable.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        TimeTable.auto_output(self)
        
        return
        

class TriStateTable(GUIStructure, TriStateTable):
    """Overloading TriStateTable class"""

    @staticmethod
    def auto_input(self):
        
        widget = InputTriStateTable(self.parent,
                                    self.meta.result.labels,
                                    self.meta.result.units)
        widget._set_value(self.data.result)
        
        self.data.result = widget
        
        return
        
    @staticmethod
    def auto_output(self):
        
        TableData.auto_output(self)
        
        return
    
    
class TriStateIndexTable(GUIStructure, TriStateIndexTable):
    """Overloading TriStateIndexTable class"""

    @staticmethod
    def auto_input(self):
        
        widget = InputTriStateTable(self.parent,
                                    self.meta.result.labels,
                                    self.meta.result.units,
                                    self.meta.result.labels[0],
                                    self.meta.result.valid_values)

        if self.data.result is not None:
            df = self.data.result.reset_index()
        else:
            df = None
        
        widget._set_value(df)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):
        
        IndexTable.auto_output(self)
        
        return


class NumpyND(GUIStructure, NumpyND):
    """Overloading NumpyND class"""


class Numpy2D(GUIStructure, Numpy2D):
    """Overloading Numpy2D class"""


class Numpy2DColumn(GUIStructure, Numpy2DColumn):
    """Overloading Numpy2DColumn class"""


class Numpy3D(GUIStructure, Numpy3D):
    """Overloading Numpy3D class"""


class Numpy3DColumn(GUIStructure, Numpy3DColumn):
    """Overloading Numpy3DColumn class"""


class NumpyLine(GUIStructure, NumpyLine):
    """Overloading NumpyLine class"""

    @staticmethod
    def auto_input(self):
        
        vals = self.data.result
        
        vals_df = None
                    
        if vals is not None:
                    
            val1 = vals[:,0]
            val2 = vals[:,1]
                        
            raw_dict = {"val1": val1,
                        "val2": val2}
                        
            vals_df = pd.DataFrame(raw_dict)
        
        widget = InputLineTable(self.parent,
                                self.meta.result.units)
        widget._set_value(vals_df)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):

        labels = ["val1", "val2"]        
        vals = self.data.result
                    
        if vals is None:
            
            vals_df = None

        else:
                                
            val1 = vals[:,0]
            val2 = vals[:,1]
                        
            raw_dict = {"val1": val1,
                        "val2": val2}
                        
            vals_df = pd.DataFrame(raw_dict)
        
        widget = OutputDataTable(self.parent, labels)
        widget._set_value(vals_df)
        
        self.data.result = widget

        return


class NumpyLineDict(GUIStructure, NumpyLineDict):
    """Overloading NumpyLineDict class"""
    
    
class NumpyLineDictArrayColumn(GUIStructure, NumpyLineDictArrayColumn):
    """Overloading NumpyLineDictArrayColumn class"""


class NumpyBar(GUIStructure, NumpyBar):
    """Overloading NumpyBar class"""
    

class NumpyLineArray(GUIStructure, NumpyLineArray):
    """Overloading NumpyLineArray class"""
    
    @staticmethod
    def auto_input(self):
        
        NumpyLine.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        NumpyLine.auto_output(self)
        
        return

    
class NumpyLineColumn(GUIStructure, NumpyLineColumn):
    """Overloading NumpyLineColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        NumpyLine.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        NumpyLine.auto_output(self)
        
        return


class Histogram(GUIStructure, Histogram):
    """Overloading Histogram class"""

    @staticmethod
    def auto_input(self):
        
        hist = self.data.result
        
        hist_df = None
                    
        if hist is not None:
                    
            bins = hist['bins']
            values = hist['values']

            raw_dict = {"Bin Separators": bins,
                        "Values": values + [None],
                        }
                        
            hist_df = pd.DataFrame(raw_dict)
        
        widget = InputHistogram(self.parent)
        widget._set_value(hist_df)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):
        
        hist = self.data.result
        
        if hist is None:

            hist_df = None
                    
        else:
                    
            bins = hist['bins']
            values = hist['values']

                        
            raw_dict = {"bins": bins[1:],
                        "values": values,
                        }
                        
            hist_df = pd.DataFrame(raw_dict)
        
        widget = OutputDataTable(self.parent)
        widget._set_value(hist_df)
        
        self.data.result = widget
        
        return

    
class HistogramColumn(GUIStructure, HistogramColumn):
    """Overloading HistogramColumn class"""


class HistogramDict(GUIStructure, HistogramDict):
    """Overloading HistogramDict class"""


class CartesianData(GUIStructure, CartesianData):
    """Overloading CartesianData class"""

    @staticmethod
    def auto_input(self):

        if self.meta.result.units is not None:
            unit = self.meta.result.units[0]
        else:
            unit = None
       
        input_widget = CoordSelect(self.parent,
                                   unit)
        
        input_widget._set_value(self.data.result)
            
        self.data.result = input_widget

        return

    @staticmethod
    def auto_output(self):
        
        unit = "m"
        
        output_widget = LabelOutput(self.parent,
                                   unit)
        
        coords = tuple(self.data.result)
        output_widget._set_value(coords)
            
        self.data.result = output_widget

        return

class CartesianDataColumn(GUIStructure, CartesianDataColumn):
    """Overloading CartesianDataColumn class"""

    @staticmethod
    def auto_input(self):
        
        CartesianData.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        CartesianData.auto_output(self)
        
        return
    
    
class CartesianList(GUIStructure, CartesianList):
    """Overloading CartesianList class"""
    
    @staticmethod
    def auto_input(self):
        
        coords = self.data.result
        
        coords_df = None
                    
        if coords is not None:
                    
            x_vals = coords[:,0]
            y_vals = coords[:,1]
        
            if coords.shape[1] == 3:
                z_vals = coords[:,2]
            else:
                z_vals = [None] * len(x_vals)
                
            raw_dict = {"x": x_vals,
                        "y": y_vals,
                        "z": z_vals}
                        
            coords_df = pd.DataFrame(raw_dict)
        
        widget = InputPointTable(self.parent)
        widget._set_value(coords_df)
        
        self.data.result = widget
        
        return

    @staticmethod
    def auto_output(self):
        
        coords = self.data.result
        
        coords_df = None
        labels = ["x", "y"]
            
        if coords is not None:

            x_vals = [x[0] for x in coords]
            y_vals = [x[1] for x in coords]
        
            if len(coords) == 3:
                z_vals = [x[2] for x in coords]
            else:
                z_vals = [None] * len(x_vals)
                
            raw_dict = {"x": x_vals,
                        "y": y_vals,
                        "z": z_vals}
                        
            coords_df = pd.DataFrame(raw_dict)
            
            labels.append("z")
        
        widget = OutputDataTable(self.parent,
                                 labels)
        widget._set_value(coords_df)
        
        self.data.result = widget

        return

    
class CartesianListColumn(GUIStructure, CartesianListColumn):
    """Overloading CartesianListColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        CartesianList.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        CartesianList.auto_output(self)
        
        return


class CartesianDict(GUIStructure, CartesianDict):
    """Overloading CartesianDict class"""
    
    
class CartesianDictColumn(GUIStructure, CartesianDictColumn):
    """Overloading CartesianDictColumn class"""


class CartesianListDict(GUIStructure, CartesianListDict):
    """Overloading CartesianListDict class"""
    
    
class CartesianListDictColumn(GUIStructure, CartesianListDictColumn):
    """Overloading CartesianListDictColumn class"""


class SimpleData(GUIStructure, SimpleData):
    """Overloading SimpleData class"""
    
    @staticmethod
    def auto_input(self):
        
        if self.meta.result.valid_values is not None:
            
            unit = None
            
            if self.meta.result.units is not None:
                unit = self.meta.result.units[0]
            
            input_widget = ListSelect(
                                    self.parent,
                                    self.meta.result.valid_values,
                                    unit=unit,
                                    experimental=self.meta.result.experimental)
            input_widget._set_value(self.data.result)
        
        elif self.meta.result.types is None:
            
            input_widget = None
        
        elif self.meta.result.types[0] == "float":
            
            unit = None
            minimum = None
            maximum = None
            
            if self.meta.result.units is not None:
                unit = self.meta.result.units[0]
            
            if self.meta.result.minimum_equals is not None:
                minimum = self.meta.result.minimum_equals[0]
            elif self.meta.result.minimums is not None:
                minimum = np.nextafter(self.meta.result.minimums[0], np.inf)
            
            if self.meta.result.maximum_equals is not None:
                maximum = self.meta.result.maximum_equals[0]
            elif self.meta.result.maximums is not None:
                maximum = np.nextafter(self.meta.result.maximums[0], -np.inf)
            
            input_widget = FloatSelect(self.parent, unit, minimum, maximum)
            input_widget._set_value(self.data.result)
        
        elif self.meta.result.types[0] == "int":
            
            unit = None
            minimum = None
            maximum = None
            
            if self.meta.result.units is not None:
                unit = self.meta.result.units[0]
            
            if self.meta.result.minimum_equals is not None:
                minimum = self.meta.result.minimum_equals[0]
            elif self.meta.result.minimums is not None:
                minimum = self.meta.result.minimums[0] + 1
            
            if self.meta.result.maximum_equals is not None:
                maximum = self.meta.result.maximum_equals[0]
            elif self.meta.result.maximums is not None:
                maximum = self.meta.result.maximums[0] - 1
            
            input_widget = IntSelect(self.parent, unit, minimum, maximum)
            input_widget._set_value(self.data.result)
        
        elif self.meta.result.types[0] == "str":
            
            unit = None
            
            if self.meta.result.units is not None:
                unit = self.meta.result.units[0]
            
            input_widget = StringSelect(self.parent,
                                        unit)
            input_widget._set_value(self.data.result)
        
        elif self.meta.result.types[0] == "bool":
            
            input_widget = BoolSelect(self.parent)
            input_widget._set_value(self.data.result)
        
        else:
            
            input_widget = None
        
        self.data.result = input_widget
        
        return
    
    @staticmethod
    def auto_output(self):
        
        if (self.meta.result.types[0] != "bool" and 
            self.meta.result.units is not None):
            unit = self.meta.result.units[0]
        else:
            unit = None
        
        output_widget = LabelOutput(self.parent,
                                    unit)
        output_widget._set_value(self.data.result)
            
        self.data.result = output_widget
        
        return


class PathData(GUIStructure, PathData):
    """Overloading PathData class"""

        
class DirectoryData(GUIStructure, DirectoryData):
    """Overloading DirectoryData class"""
    
    @staticmethod
    def auto_input(self):
        
        input_widget = DirectorySelect(self.parent)
        input_widget._set_value(self.data.result)
    
        self.data.result = input_widget
        
        return
        
    @staticmethod
    def auto_output(self):
        
        SimpleData.auto_output(self)
        
        return


class SimpleList(GUIStructure, SimpleList):
    """Overloading SimpleList class"""
    
    @staticmethod
    def auto_output(self):
        
        labels = ["Value"]
        
        if self.meta.result.units is not None:
            units = self.meta.result.units[0]
        else:
            units = None
        
        widget = OutputDataTable(self.parent,
                                 labels,
                                 units)
        
        df = None
        
        if self.data.result is not None:
            raw_dict = {"Value": self.data.result}
            df = pd.DataFrame(raw_dict)
        
        widget._set_value(df)
        
        self.data.result = widget

        return


class SimpleDict(GUIStructure, SimpleDict):
    """Overloading SimpleDict class"""
    
    @staticmethod
    def auto_input(self):
        
        widget = InputDictTable(self.parent,
                                self.meta.result.units,
                                self.meta.result.valid_values)
        
        val_types = [object, self.meta.result.types[0]]
        
        if self.data.result is not None:
            var_dict = self.data.result
            df_dict = {"Key": var_dict.keys(),
                       "Value": var_dict.values()}
            value = pd.DataFrame(df_dict)
            value = value.sort_values(by="Key")
        else:
            value = None
        
        widget._set_value(value, dtypes=val_types)
        
        self.data.result = widget
        
        return
    
    @staticmethod
    def auto_output(self):
        
        labels = ["Key", "Value"]
        
        if self.meta.result.units is not None:
            units = [None, self.meta.result.units[0]]
        else:
            units = None
        
        widget = OutputDataTable(self.parent,
                                 labels,
                                 units)
        
        df = None
        
        if self.data.result is not None:
            raw_dict = {"Key": self.data.result.keys(),
                        "Value": self.data.result.values()}
            df = pd.DataFrame(raw_dict)
            df = df.sort_values(by="Key")
        
        widget._set_value(df)
        
        self.data.result = widget

        return

        
class SimplePie(GUIStructure, SimplePie):
    """Overloading SimplePie class"""
    
    @staticmethod
    def auto_output(self):
        
        SimpleDict.auto_output(self)
        
        return


class SimpleDataColumn(GUIStructure, SimpleDataColumn):
    """Overloading SimpleColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        SimpleData.auto_input(self)
        
        return
        
    @staticmethod
    def auto_output(self):
        
        SimpleData.auto_output(self)
        
        return
        
        
class SimpleDataForeignColumn(GUIStructure, SimpleDataForeignColumn):
    """Overloading SimpleDataForeignColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        SimpleData.auto_input(self)
        
        return
        
    @staticmethod
    def auto_output(self):
        
        SimpleData.auto_output(self)
        
        return
        
        
class DirectoryDataColumn(GUIStructure, DirectoryDataColumn):
    """Overloading DirectoryDataColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        DirectoryData.auto_input(self)
        
        return
        
    @staticmethod
    def auto_output(self):
        
        DirectoryData.auto_output(self)
        
        return


class SimpleListColumn(GUIStructure, SimpleListColumn):
    """Overloading SimpleListColumn class"""
    
    @staticmethod
    def auto_output(self):
        
        SimpleList.auto_output(self)
        
        return


class SimpleDictColumn(GUIStructure, SimpleDictColumn):
    """Overloading SimpleDictColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        SimpleDict.auto_input(self)
        
        return
        
    @staticmethod
    def auto_output(self):
        
        SimpleDict.auto_output(self)
        
        return

    
class DateTimeData(GUIStructure, DateTimeData):
    """Overloading DateTimeData class"""

    @staticmethod
    def auto_input(self):
    
        input_widget = DateSelect(self.parent)
        input_widget._set_value(self.data.result)
            
        self.data.result = input_widget
    
        return
        
    @staticmethod
    def auto_output(self):
        
        output_widget = LabelOutput(self.parent,
                                    None)
        output_widget._set_value(self.data.result)
            
        self.data.result = output_widget

        return
    

class DateTimeDict(GUIStructure, DateTimeDict):
    """Overloading DateTimeDict class"""
    
    @staticmethod
    def auto_output(self):
        
        labels = ["Key", "DateTime"]
        
        widget = OutputDataTable(self.parent,
                                 labels)
        
        df = None
        
        if self.data.result is not None:
            raw_dict = {"Key": self.data.result.keys(),
                        "DateTime": self.data.result.values()}
            df = pd.DataFrame(raw_dict)
            df = df.sort_values(by="Key")
            df = df[["Key", "DateTime"]]
        
        widget._set_value(df)
        
        self.data.result = widget
    

class TriStateData(GUIStructure, TriStateData):
    """Overloading TriStateData class"""
    

class PointData(GUIStructure, PointData):
    """Overloading PointData class"""

    @staticmethod
    def auto_input(self):

        if self.meta.result.units is not None:
            unit = self.meta.result.units[0]
        else:
            unit = None
       
        input_widget = PointSelect(self.parent,
                                   unit)
        
        if self.data.result is None:
            coords = None
        else:
            coords = list(self.data.result.coords)[0]
        
        input_widget._set_value(coords)
            
        self.data.result = input_widget

        return

    @staticmethod
    def auto_output(self):
        
        unit = "m"
        
        output_widget = LabelOutput(self.parent,
                                   unit)
        
        coords = list(self.data.result.coords)[0]
        output_widget._set_value(coords)
            
        self.data.result = output_widget

        return


class PointList(GUIStructure, PointList):
    """Overloading PointList class"""
    
    @staticmethod
    def auto_input(self):
        
        points = self.data.result
        
        point_df = None
            
        if points is not None:
        
            coords = [x.coords[0] for x in points]
            
            x_vals = [x[0] for x in coords]
            y_vals = [x[1] for x in coords]
            
            z_vals = []
            
            for x in coords:
                
                if len(x) == 3:
                    z_vals.append(x[2])
                else:
                    z_vals.append(None)
                
            raw_dict = {"x": x_vals,
                        "y": y_vals,
                        "z": z_vals}
                        
            point_df = pd.DataFrame(raw_dict)
        
        widget = InputPointTable(self.parent)
        widget._set_value(point_df)
        
        self.data.result = widget
        
        return


class PointDict(GUIStructure, PointDict):
    """Overloading PointDict class"""
    
    @staticmethod
    def auto_input(self):
        
        point_dict = self.data.result
        
        point_df = None
            
        if point_dict is not None:
        
            coord_dict = {k: v.coords[0] for k, v in point_dict.items()}
            
            x_vals = [x[0] for x in coord_dict.values()]
            y_vals = [x[1] for x in coord_dict.values()]
            
            z_vals = []
            
            for x in coord_dict.values():
                
                if len(x) == 3:
                    z_vals.append(x[2])
                else:
                    z_vals.append(None)
                
            raw_dict = {"Key": coord_dict.keys(),
                        "x": x_vals,
                        "y": y_vals,
                        "z": z_vals}
                        
            point_df = pd.DataFrame(raw_dict)
            point_df = point_df.sort_values(by="Key")
        
        widget = InputPointDictTable(self.parent,
                                     self.meta.result.valid_values)
        
        val_types = [object, float, float, float]
        widget._set_value(point_df, dtypes=val_types)
        
        self.data.result = widget
        
        return
    
    @staticmethod
    def auto_output(self):
        
        labels = ["Key", "x", "y", "z"]
        
        widget = OutputDataTable(self.parent,
                                 labels)
        
        df = None
        
        if self.data.result is not None:
            
            point_array = np.array([np.array(el) for el in
                                                  self.data.result.values()])

            data = {"Key": self.data.result.keys(),
                    "x": point_array[:, 0],
                    "y": point_array[:, 1]}
                              
            if point_array.shape[1] == 3:
                data["z"] = point_array[:, 2]
            else:
                data["z"] = [None] * len(self.data.result)
        
            df = pd.DataFrame(data)
            df = df.sort_values(by="Key")
        
        widget._set_value(df)
        
        self.data.result = widget

        return


class PointDataColumn(GUIStructure, PointDataColumn):
    """Overloading PointDataColumn class"""

    @staticmethod
    def auto_input(self):
        
        PointData.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        PointData.auto_output(self)
        
        return
        
        
class PointDictColumn(GUIStructure, PointDictColumn):
    """Overloading PointDictColumn class"""


class PolygonData(GUIStructure, PolygonData):
    """Overloading PolygonData class"""
    
    @staticmethod
    def auto_input(self):
        
        polygon = self.data.result
        
        poly_df = None
            
        if polygon is not None:
        
            coords = list(polygon.exterior.coords)[:-1]
            
            x_vals = [x[0] for x in coords]
            y_vals = [x[1] for x in coords]
        
            if polygon.has_z:
                z_vals = [x[2] for x in coords]
            else:
                z_vals = [None] * len(x_vals)
                
            raw_dict = {"x": x_vals,
                        "y": y_vals,
                        "z": z_vals}
                        
            poly_df = pd.DataFrame(raw_dict)
        
        widget = InputPointTable(self.parent)
        widget._set_value(poly_df)
        
        self.data.result = widget
        
        return
        
    @staticmethod
    def auto_output(self):
        
        labels = ["x", "y", "z"]
        polygon = self.data.result
        
        if polygon is None:
            
            poly_df = None
            
        else: 
        
            coords = list(polygon.exterior.coords)[:-1]
            
            x_vals = [x[0] for x in coords]
            y_vals = [x[1] for x in coords]
        
            if polygon.has_z:
                z_vals = [x[2] for x in coords]
            else:
                z_vals = [None] * len(x_vals)
                
            raw_dict = {"x": x_vals,
                        "y": y_vals,
                        "z": z_vals}
                        
            poly_df = pd.DataFrame(raw_dict)
        
        widget = OutputDataTable(self.parent,
                                 labels)
        widget._set_value(poly_df)
        
        self.data.result = widget

        return


class PolygonDataColumn(GUIStructure, PolygonDataColumn):
    """Overloading PolygonDataColumn class"""
    
    @staticmethod
    def auto_input(self):
        
        PolygonData.auto_input(self)
        
        return

    @staticmethod
    def auto_output(self):
        
        PolygonData.auto_output(self)
        
        return


class PolygonList(GUIStructure, PolygonList):
    """Overloading PolygonList class"""
    
    
class PolygonListColumn(GUIStructure, PolygonListColumn):
    """Overloading PolygonListColumn class"""


class PolygonDict(GUIStructure, PolygonDict):
    """Overloading PolygonDict class"""


class PolygonDictColumn(GUIStructure, PolygonDictColumn):
    """Overloading PolygonDictColumn class"""


class XGrid2D(GUIStructure, XGrid2D):
    """Overloading XGrid2D class"""


class XGrid3D(GUIStructure, XGrid3D):
    """Overloading XGrid3D class"""


class XSet2D(GUIStructure, XSet2D):
    """Overloading XSet2D class"""


class XSet3D(GUIStructure, XSet3D):
    """Overloading XSet3D class"""


class Strata(GUIStructure, Strata):
    """Overloading Strata class"""


class Network(GUIStructure, Network):
    """Overloading Network class"""

    
class EIADict(GUIStructure, EIADict):
    """Overloading EIADict class"""
    
    @staticmethod
    def auto_output(self):
        
        labels = ["Key", "Value"]
        
        if self.meta.result.units is not None:
            units = [None] + self.meta.result.units[:1]
        else:
            units = None
        
        widget = OutputDataTable(self.parent,
                                 labels,
                                 units)
        
        raw_dict = {"Key": self.data.result.keys(),
                    "Value": self.data.result.values()}
        df = pd.DataFrame(raw_dict)
        
        widget._set_value(df)
        
        self.data.result = widget

        return


class RecommendationDict(GUIStructure, RecommendationDict):
    """Overloading RecommendationDict class"""

    @staticmethod
    def auto_output(self):
        
        rec = self.data.result

        env_impacts = ["Energy Modification",
                       "Footprint",
                       "Collision Risk",
                       "Collision Risk Vessel",
                       "Chemical Pollution",
                       "Turbidity",
                       "Underwater Noise",
                       "Electric Fields",
                       "Magnetic Fields",
                       "Temperature Modification",
                       "Reef Effect",
                       "Reserve Effect",
                       "Resting Place"]

        text  = ''

        for key in env_impacts:
            if key in rec and rec[key] is not None:
                text = text + str(key) + ': '
                text = text + str(rec[key]['Generic Explanation']) + ', '
                text = text + str(rec[key]['General Recommendation']) + ', '
                text = text + str(rec[key]['Detailed Recommendation']) + '.\n\n'

        widget = TextOutput(self.parent)
        widget._set_value(text)
        
        self.data.result = widget
        
        return