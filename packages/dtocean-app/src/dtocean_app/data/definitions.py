# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Rui Duarte
#    Copyright (C) 2016-2025 Mathew Topper
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


from typing import Optional, Protocol

import dtocean_core.data.definitions as definitions
import numpy as np
import pandas as pd
from mdo_engine.boundary.interface import Box
from PySide6.QtWidgets import QWidget

from ..widgets.input import (
    BoolSelect,
    CoordSelect,
    DateSelect,
    DirectorySelect,
    FloatSelect,
    InputDataTable,
    InputDictTable,
    InputHistogram,
    InputLineTable,
    InputPointDictTable,
    InputPointTable,
    InputTimeSeries,
    InputTimeTable,
    InputTriStateTable,
    IntSelect,
    ListSelect,
    PointSelect,
    StringSelect,
)
from ..widgets.output import LabelOutput, OutputDataTable, TextOutput


class WidgetMixin(Protocol):
    @property
    def data(self) -> Box: ...

    @property
    def meta(self) -> Box: ...

    @property
    def parent(self) -> Optional[QWidget]: ...


class GUIStructure:
    """Dummy class for plugin detection"""


class UnknownData(GUIStructure, definitions.UnknownData):
    """Overloading UnknownData class"""


class SeriesData(GUIStructure, definitions.SeriesData):
    """Overloading SeriesData class"""

    @staticmethod
    def auto_output(auto: WidgetMixin):
        df = auto.data.result.to_frame()

        if auto.meta.result.labels is None:
            labels = ["Data"]
        else:
            labels = [auto.meta.result.labels[0]]

        if auto.meta.result.units is None:
            units = [None]
        else:
            units = [auto.meta.result.units[0]]

        widget = OutputDataTable(auto.parent, labels, units)
        widget._set_value(df)

        auto.data.result = widget


class TimeSeries(GUIStructure, definitions.TimeSeries):
    """Overloading TimeSeries class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        if auto.meta.result.labels is None:
            labels = ["Data"]
        else:
            labels = auto.meta.result.labels

        widget = InputTimeSeries(auto.parent, labels, auto.meta.result.units)
        widget._set_value(auto.data.result)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        SeriesData.auto_output(auto)


class TimeSeriesColumn(GUIStructure, definitions.TimeSeriesColumn):
    """Overloading TimeSeriesColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        TimeSeries.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        TimeSeries.auto_output(auto)


class TableData(GUIStructure, definitions.TableData):
    """Overloading TableData class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        widget = InputDataTable(
            auto.parent, auto.meta.result.labels, auto.meta.result.units
        )
        widget._set_value(auto.data.result, auto.meta.result.types)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        widget = OutputDataTable(
            auto.parent, auto.meta.result.labels, auto.meta.result.units
        )
        widget._set_value(auto.data.result)

        auto.data.result = widget


class TableDataColumn(GUIStructure, definitions.TableDataColumn):
    """Overloading TableDataColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        TableData.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        TableData.auto_output(auto)


class IndexTable(GUIStructure, definitions.IndexTable):
    """Overloading IndexTable class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        widget = InputDataTable(
            auto.parent,
            auto.meta.result.labels,
            auto.meta.result.units,
            auto.meta.result.labels[0],
            auto.meta.result.valid_values,
        )

        if auto.data.result is not None:
            df = auto.data.result.reset_index()
        else:
            df = None

        widget._set_value(df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        widget = OutputDataTable(
            auto.parent, auto.meta.result.labels, auto.meta.result.units
        )

        if auto.data.result is not None:
            df = auto.data.result.reset_index()
        else:
            df = None

        widget._set_value(df)

        auto.data.result = widget


class IndexTableColumn(GUIStructure, definitions.IndexTableColumn):
    """Overloading IndexTableColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        IndexTable.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        IndexTable.auto_output(auto)


class LineTable(GUIStructure, definitions.LineTable):
    """Overloading LineTable class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        IndexTable.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        IndexTable.auto_output(auto)


class LineTableExpand(GUIStructure, definitions.LineTableExpand):
    """Overloading LineTableExpand class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        if auto.data.result is not None:
            df = auto.data.result.reset_index()
            labels = df.columns

        else:
            df = None
            labels = auto.meta.result.labels

        if auto.meta.result.units is not None:
            units = list(auto.meta.result.units[:1])
            n_extra = len(labels) - 1

            if len(auto.meta.result.units) > 1:
                add_units = [auto.meta.result.units[1]] * n_extra
            else:
                add_units = [None] * n_extra

            units += add_units

        else:
            units = None

        widget = InputDataTable(
            auto.parent,
            labels,
            units,
            auto.meta.result.labels[0],
            auto.meta.result.valid_values,
            True,
        )

        widget._set_value(df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        if auto.data.result is not None:
            df = auto.data.result.reset_index()
            labels = df.columns

        else:
            df = None
            labels = auto.meta.result.labels

        if auto.meta.result.units is not None:
            units = list(auto.meta.result.units[:1])
            n_extra = len(labels) - 1

            if len(auto.meta.result.units) > 1:
                add_units = [auto.meta.result.units[1]] * n_extra
            else:
                add_units = [None] * n_extra

            units += add_units

        else:
            units = None

        widget = OutputDataTable(auto.parent, labels, units)

        widget._set_value(df)

        auto.data.result = widget


class LineTableColumn(GUIStructure, definitions.LineTableColumn):
    """Overloading LineTableColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        LineTable.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        LineTable.auto_output(auto)


class TimeTable(GUIStructure, definitions.TimeTable):
    """Overloading TimeTable class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        widget = InputTimeTable(
            auto.parent, auto.meta.result.labels, auto.meta.result.units
        )

        if auto.data.result is not None:
            df = auto.data.result.reset_index()
        else:
            df = None

        widget._set_value(df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        widget = OutputDataTable(
            auto.parent, auto.meta.result.labels, auto.meta.result.units
        )
        widget._set_value(auto.data.result)

        auto.data.result = widget


class TimeTableColumn(GUIStructure, definitions.TimeTableColumn):
    """Overloading TimeTableColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        TimeTable.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        TimeTable.auto_output(auto)


class TriStateTable(GUIStructure, definitions.TriStateTable):
    """Overloading TriStateTable class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        widget = InputTriStateTable(
            auto.parent, auto.meta.result.labels, auto.meta.result.units
        )
        widget._set_value(auto.data.result)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        TableData.auto_output(auto)


class TriStateIndexTable(GUIStructure, definitions.TriStateIndexTable):
    """Overloading TriStateIndexTable class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        widget = InputTriStateTable(
            auto.parent,
            auto.meta.result.labels,
            auto.meta.result.units,
            auto.meta.result.labels[0],
            auto.meta.result.valid_values,
        )

        if auto.data.result is not None:
            df = auto.data.result.reset_index()
        else:
            df = None

        widget._set_value(df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        IndexTable.auto_output(auto)


class NumpyND(GUIStructure, definitions.NumpyND):
    """Overloading NumpyND class"""


class Numpy2D(GUIStructure, definitions.Numpy2D):
    """Overloading Numpy2D class"""


class Numpy2DColumn(GUIStructure, definitions.Numpy2DColumn):
    """Overloading Numpy2DColumn class"""


class Numpy3D(GUIStructure, definitions.Numpy3D):
    """Overloading Numpy3D class"""


class Numpy3DColumn(GUIStructure, definitions.Numpy3DColumn):
    """Overloading Numpy3DColumn class"""


class NumpyLine(GUIStructure, definitions.NumpyLine):
    """Overloading NumpyLine class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        vals = auto.data.result

        vals_df = None

        if vals is not None:
            val1 = vals[:, 0]
            val2 = vals[:, 1]

            raw_dict = {"val1": val1, "val2": val2}

            vals_df = pd.DataFrame(raw_dict)

        widget = InputLineTable(auto.parent, auto.meta.result.units)
        widget._set_value(vals_df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["val1", "val2"]
        vals = auto.data.result

        if vals is None:
            vals_df = None

        else:
            val1 = vals[:, 0]
            val2 = vals[:, 1]

            raw_dict = {"val1": val1, "val2": val2}

            vals_df = pd.DataFrame(raw_dict)

        widget = OutputDataTable(auto.parent, labels)
        widget._set_value(vals_df)

        auto.data.result = widget


class NumpyLineDict(GUIStructure, definitions.NumpyLineDict):
    """Overloading NumpyLineDict class"""


class NumpyLineDictArrayColumn(
    GUIStructure, definitions.NumpyLineDictArrayColumn
):
    """Overloading NumpyLineDictArrayColumn class"""


class NumpyBar(GUIStructure, definitions.NumpyBar):
    """Overloading NumpyBar class"""


class NumpyLineArray(GUIStructure, definitions.NumpyLineArray):
    """Overloading NumpyLineArray class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        NumpyLine.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        NumpyLine.auto_output(auto)


class NumpyLineColumn(GUIStructure, definitions.NumpyLineColumn):
    """Overloading NumpyLineColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        NumpyLine.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        NumpyLine.auto_output(auto)


class Histogram(GUIStructure, definitions.Histogram):
    """Overloading Histogram class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        hist = auto.data.result

        hist_df = None

        if hist is not None:
            bins = hist["bins"]
            values = hist["values"]

            raw_dict = {
                "Bin Separators": bins,
                "Values": values + [None],
            }

            hist_df = pd.DataFrame(raw_dict)

        widget = InputHistogram(auto.parent)
        widget._set_value(hist_df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["bins", "values"]
        hist = auto.data.result

        if hist is None:
            hist_df = None

        else:
            bins = hist["bins"]
            values = hist["values"]

            raw_dict = {
                "bins": bins[1:],
                "values": values,
            }

            hist_df = pd.DataFrame(raw_dict)

        widget = OutputDataTable(auto.parent, labels)
        widget._set_value(hist_df)

        auto.data.result = widget


class HistogramColumn(GUIStructure, definitions.HistogramColumn):
    """Overloading HistogramColumn class"""


class HistogramDict(GUIStructure, definitions.HistogramDict):
    """Overloading HistogramDict class"""


class CartesianData(GUIStructure, definitions.CartesianData):
    """Overloading CartesianData class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        if auto.meta.result.units is not None:
            unit = auto.meta.result.units[0]
        else:
            unit = None

        input_widget = CoordSelect(auto.parent, unit)

        input_widget._set_value(auto.data.result)

        auto.data.result = input_widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        unit = "m"

        output_widget = LabelOutput(auto.parent, unit)

        coords = tuple(auto.data.result)
        output_widget._set_value(coords)

        auto.data.result = output_widget


class CartesianDataColumn(GUIStructure, definitions.CartesianDataColumn):
    """Overloading CartesianDataColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        CartesianData.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        CartesianData.auto_output(auto)


class CartesianList(GUIStructure, definitions.CartesianList):
    """Overloading CartesianList class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        coords = auto.data.result

        coords_df = None

        if coords is not None:
            x_vals = coords[:, 0]
            y_vals = coords[:, 1]

            if coords.shape[1] == 3:
                z_vals = coords[:, 2]
            else:
                z_vals = [None] * len(x_vals)

            raw_dict = {"x": x_vals, "y": y_vals, "z": z_vals}

            coords_df = pd.DataFrame(raw_dict)

        widget = InputPointTable(auto.parent)
        widget._set_value(coords_df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        coords = auto.data.result

        coords_df = None
        labels = ["x", "y"]

        if coords is not None:
            x_vals = [x[0] for x in coords]
            y_vals = [x[1] for x in coords]

            if len(coords) == 3:
                z_vals = [x[2] for x in coords]
            else:
                z_vals = [None] * len(x_vals)

            raw_dict = {"x": x_vals, "y": y_vals, "z": z_vals}

            coords_df = pd.DataFrame(raw_dict)

            labels.append("z")

        widget = OutputDataTable(auto.parent, labels)
        widget._set_value(coords_df)

        auto.data.result = widget


class CartesianListColumn(GUIStructure, definitions.CartesianListColumn):
    """Overloading CartesianListColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        CartesianList.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        CartesianList.auto_output(auto)


class CartesianDict(GUIStructure, definitions.CartesianDict):
    """Overloading CartesianDict class"""


class CartesianDictColumn(GUIStructure, definitions.CartesianDictColumn):
    """Overloading CartesianDictColumn class"""


class CartesianListDict(GUIStructure, definitions.CartesianListDict):
    """Overloading CartesianListDict class"""


class CartesianListDictColumn(
    GUIStructure, definitions.CartesianListDictColumn
):
    """Overloading CartesianListDictColumn class"""


class SimpleData(GUIStructure, definitions.SimpleData):
    """Overloading SimpleData class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        if auto.meta.result.valid_values is not None:
            unit = None

            if auto.meta.result.units is not None:
                unit = auto.meta.result.units[0]

            input_widget = ListSelect(
                auto.parent,
                auto.meta.result.valid_values,
                unit=unit,
                experimental=auto.meta.result.experimental,
            )
            input_widget._set_value(auto.data.result)

        elif auto.meta.result.types is None:
            input_widget = None

        elif auto.meta.result.types[0] == "float":
            unit = None
            minimum = None
            maximum = None

            if auto.meta.result.units is not None:
                unit = auto.meta.result.units[0]

            if auto.meta.result.minimum_equals is not None:
                minimum = auto.meta.result.minimum_equals[0]
            elif auto.meta.result.minimums is not None:
                minimum = np.nextafter(auto.meta.result.minimums[0], np.inf)

            if auto.meta.result.maximum_equals is not None:
                maximum = auto.meta.result.maximum_equals[0]
            elif auto.meta.result.maximums is not None:
                maximum = np.nextafter(auto.meta.result.maximums[0], -np.inf)

            input_widget = FloatSelect(auto.parent, unit, minimum, maximum)
            input_widget._set_value(auto.data.result)

        elif auto.meta.result.types[0] == "int":
            unit = None
            minimum = None
            maximum = None

            if auto.meta.result.units is not None:
                unit = auto.meta.result.units[0]

            if auto.meta.result.minimum_equals is not None:
                minimum = auto.meta.result.minimum_equals[0]
            elif auto.meta.result.minimums is not None:
                minimum = auto.meta.result.minimums[0] + 1

            if auto.meta.result.maximum_equals is not None:
                maximum = auto.meta.result.maximum_equals[0]
            elif auto.meta.result.maximums is not None:
                maximum = auto.meta.result.maximums[0] - 1

            input_widget = IntSelect(auto.parent, unit, minimum, maximum)
            input_widget._set_value(auto.data.result)

        elif auto.meta.result.types[0] == "str":
            unit = None

            if auto.meta.result.units is not None:
                unit = auto.meta.result.units[0]

            input_widget = StringSelect(auto.parent, unit)
            input_widget._set_value(auto.data.result)

        elif auto.meta.result.types[0] == "bool":
            input_widget = BoolSelect(auto.parent)
            input_widget._set_value(auto.data.result)

        else:
            input_widget = None

        auto.data.result = input_widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        if (
            auto.meta.result.types[0] != "bool"
            and auto.meta.result.units is not None
        ):
            unit = auto.meta.result.units[0]
        else:
            unit = None

        output_widget = LabelOutput(auto.parent, unit)
        output_widget._set_value(auto.data.result)

        auto.data.result = output_widget


class PathData(GUIStructure, definitions.PathData):
    """Overloading PathData class"""


class DirectoryData(GUIStructure, definitions.DirectoryData):
    """Overloading DirectoryData class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        input_widget = DirectorySelect(auto.parent)
        input_widget._set_value(auto.data.result)

        auto.data.result = input_widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        SimpleData.auto_output(auto)


class SimpleList(GUIStructure, definitions.SimpleList):
    """Overloading SimpleList class"""

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["Value"]

        if auto.meta.result.units is not None:
            units = auto.meta.result.units[0]
        else:
            units = None

        widget = OutputDataTable(auto.parent, labels, units)

        df = None

        if auto.data.result is not None:
            raw_dict = {"Value": auto.data.result}
            df = pd.DataFrame(raw_dict)

        widget._set_value(df)

        auto.data.result = widget


class SimpleDict(GUIStructure, definitions.SimpleDict):
    """Overloading SimpleDict class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        widget = InputDictTable(
            auto.parent, auto.meta.result.units, auto.meta.result.valid_values
        )

        val_types = [object, auto.meta.result.types[0]]

        if auto.data.result is not None:
            var_dict = auto.data.result
            df_dict = {"Key": var_dict.keys(), "Value": var_dict.values()}
            value = pd.DataFrame(df_dict)
            value = value.sort_values(by="Key")
        else:
            value = None

        widget._set_value(value, dtypes=val_types)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["Key", "Value"]

        if auto.meta.result.units is not None:
            units = [None, auto.meta.result.units[0]]
        else:
            units = None

        widget = OutputDataTable(auto.parent, labels, units)

        df = None

        if auto.data.result is not None:
            raw_dict = {
                "Key": auto.data.result.keys(),
                "Value": auto.data.result.values(),
            }
            df = pd.DataFrame(raw_dict)
            df = df.sort_values(by="Key")

        widget._set_value(df)

        auto.data.result = widget


class SimplePie(GUIStructure, definitions.SimplePie):
    """Overloading SimplePie class"""

    @staticmethod
    def auto_output(auto: WidgetMixin):
        SimpleDict.auto_output(auto)


class SimpleDataColumn(GUIStructure, definitions.SimpleDataColumn):
    """Overloading SimpleColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        SimpleData.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        SimpleData.auto_output(auto)


class SimpleDataForeignColumn(
    GUIStructure, definitions.SimpleDataForeignColumn
):
    """Overloading SimpleDataForeignColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        SimpleData.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        SimpleData.auto_output(auto)


class DirectoryDataColumn(GUIStructure, definitions.DirectoryDataColumn):
    """Overloading DirectoryDataColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        DirectoryData.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        DirectoryData.auto_output(auto)


class SimpleListColumn(GUIStructure, definitions.SimpleListColumn):
    """Overloading SimpleListColumn class"""

    @staticmethod
    def auto_output(auto: WidgetMixin):
        SimpleList.auto_output(auto)


class SimpleDictColumn(GUIStructure, definitions.SimpleDictColumn):
    """Overloading SimpleDictColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        SimpleDict.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        SimpleDict.auto_output(auto)


class DateTimeData(GUIStructure, definitions.DateTimeData):
    """Overloading DateTimeData class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        input_widget = DateSelect(auto.parent)
        input_widget._set_value(auto.data.result)

        auto.data.result = input_widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        output_widget = LabelOutput(auto.parent, None)
        output_widget._set_value(auto.data.result)

        auto.data.result = output_widget


class DateTimeDict(GUIStructure, definitions.DateTimeDict):
    """Overloading DateTimeDict class"""

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["Key", "DateTime"]

        widget = OutputDataTable(auto.parent, labels)

        df = None

        if auto.data.result is not None:
            raw_dict = {
                "Key": auto.data.result.keys(),
                "DateTime": auto.data.result.values(),
            }
            df = pd.DataFrame(raw_dict)
            df = df.sort_values(by="Key")
            df = df[["Key", "DateTime"]]

        widget._set_value(df)

        auto.data.result = widget


class TriStateData(GUIStructure, definitions.TriStateData):
    """Overloading TriStateData class"""


class PointData(GUIStructure, definitions.PointData):
    """Overloading PointData class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        if auto.meta.result.units is not None:
            unit = auto.meta.result.units[0]
        else:
            unit = None

        input_widget = PointSelect(auto.parent, unit)

        if auto.data.result is None:
            coords = None
        else:
            coords = list(auto.data.result.coords)[0]

        input_widget._set_value(coords)

        auto.data.result = input_widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        unit = "m"

        output_widget = LabelOutput(auto.parent, unit)

        coords = list(auto.data.result.coords)[0]
        output_widget._set_value(coords)

        auto.data.result = output_widget


class PointList(GUIStructure, definitions.PointList):
    """Overloading PointList class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        points = auto.data.result

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

            raw_dict = {"x": x_vals, "y": y_vals, "z": z_vals}

            point_df = pd.DataFrame(raw_dict)

        widget = InputPointTable(auto.parent)
        widget._set_value(point_df)

        auto.data.result = widget


class PointDict(GUIStructure, definitions.PointDict):
    """Overloading PointDict class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        point_dict = auto.data.result

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

            raw_dict = {
                "Key": coord_dict.keys(),
                "x": x_vals,
                "y": y_vals,
                "z": z_vals,
            }

            point_df = pd.DataFrame(raw_dict)
            point_df = point_df.sort_values(by="Key")

        widget = InputPointDictTable(auto.parent, auto.meta.result.valid_values)

        val_types = [object, float, float, float]
        widget._set_value(point_df, dtypes=val_types)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["Key", "x", "y", "z"]

        widget = OutputDataTable(auto.parent, labels)

        df = None

        if auto.data.result is not None:
            point_array = np.array(
                [np.array(el.coords[0]) for el in auto.data.result.values()]
            )

            data = {
                "Key": auto.data.result.keys(),
                "x": point_array[:, 0],
                "y": point_array[:, 1],
            }

            if point_array.shape[1] == 3:
                data["z"] = point_array[:, 2]
            else:
                data["z"] = [None] * len(auto.data.result)

            df = pd.DataFrame(data)
            df = df.sort_values(by="Key")

        widget._set_value(df)

        auto.data.result = widget


class PointDataColumn(GUIStructure, definitions.PointDataColumn):
    """Overloading PointDataColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        PointData.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        PointData.auto_output(auto)


class PointDictColumn(GUIStructure, definitions.PointDictColumn):
    """Overloading PointDictColumn class"""


class PolygonData(GUIStructure, definitions.PolygonData):
    """Overloading PolygonData class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        polygon = auto.data.result

        poly_df = None

        if polygon is not None:
            coords = list(polygon.exterior.coords)[:-1]

            x_vals = [x[0] for x in coords]
            y_vals = [x[1] for x in coords]

            if polygon.has_z:
                z_vals = [x[2] for x in coords]
            else:
                z_vals = [None] * len(x_vals)

            raw_dict = {"x": x_vals, "y": y_vals, "z": z_vals}

            poly_df = pd.DataFrame(raw_dict)

        widget = InputPointTable(auto.parent)
        widget._set_value(poly_df)

        auto.data.result = widget

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["x", "y", "z"]
        polygon = auto.data.result

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

            raw_dict = {"x": x_vals, "y": y_vals, "z": z_vals}

            poly_df = pd.DataFrame(raw_dict)

        widget = OutputDataTable(auto.parent, labels)
        widget._set_value(poly_df)

        auto.data.result = widget


class PolygonDataColumn(GUIStructure, definitions.PolygonDataColumn):
    """Overloading PolygonDataColumn class"""

    @staticmethod
    def auto_input(auto: WidgetMixin):
        PolygonData.auto_input(auto)

    @staticmethod
    def auto_output(auto: WidgetMixin):
        PolygonData.auto_output(auto)


class PolygonList(GUIStructure, definitions.PolygonList):
    """Overloading PolygonList class"""


class PolygonListColumn(GUIStructure, definitions.PolygonListColumn):
    """Overloading PolygonListColumn class"""


class PolygonDict(GUIStructure, definitions.PolygonDict):
    """Overloading PolygonDict class"""


class PolygonDictColumn(GUIStructure, definitions.PolygonDictColumn):
    """Overloading PolygonDictColumn class"""


class XGrid2D(GUIStructure, definitions.XGrid2D):
    """Overloading XGrid2D class"""


class XGrid3D(GUIStructure, definitions.XGrid3D):
    """Overloading XGrid3D class"""


class XSet2D(GUIStructure, definitions.XSet2D):
    """Overloading XSet2D class"""


class XSet3D(GUIStructure, definitions.XSet3D):
    """Overloading XSet3D class"""


class Strata(GUIStructure, definitions.Strata):
    """Overloading Strata class"""


class Network(GUIStructure, definitions.Network):
    """Overloading Network class"""


class EIADict(GUIStructure, definitions.EIADict):
    """Overloading EIADict class"""

    @staticmethod
    def auto_output(auto: WidgetMixin):
        labels = ["Key", "Value"]

        if auto.meta.result.units is not None:
            units = [None] + auto.meta.result.units[:1]
        else:
            units = None

        widget = OutputDataTable(auto.parent, labels, units)

        raw_dict = {
            "Key": auto.data.result.keys(),
            "Value": auto.data.result.values(),
        }
        df = pd.DataFrame(raw_dict)

        widget._set_value(df)

        auto.data.result = widget


class RecommendationDict(GUIStructure, definitions.RecommendationDict):
    """Overloading RecommendationDict class"""

    @staticmethod
    def auto_output(auto: WidgetMixin):
        rec = auto.data.result

        env_impacts = [
            "Energy Modification",
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
            "Resting Place",
        ]

        text = ""

        for key in env_impacts:
            if key in rec and rec[key] is not None:
                text = text + str(key) + ": "
                text = text + str(rec[key]["Generic Explanation"]) + ", "
                text = text + str(rec[key]["General Recommendation"]) + ", "
                text = text + str(rec[key]["Detailed Recommendation"]) + ".\n\n"

        widget = TextOutput(auto.parent)
        widget._set_value(text)

        auto.data.result = widget

        return
