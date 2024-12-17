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

"""
Created on Wed Apr 06 15:59:04 2016

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point, Polygon

from . import PlotInterface

BLUE = "#6699cc"
GREEN = "#32CD32"
RED = "#B20000"
GREY = "#999999"


class ArrayLeasePlot(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Lease Area Array Layout"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "site.lease_boundary",
            "project.layout",
            "options.boundary_padding",
        ]

        return input_list

    @classmethod
    def declare_optional(cls):
        option_list = ["options.boundary_padding"]

        return option_list

    @classmethod
    def declare_id_map(self):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "lease_poly": "site.lease_boundary",
            "layout": "project.layout",
            "padding": "options.boundary_padding",
        }

        return id_map

    def connect(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect="equal")

        short_layout = {
            key.replace("device", ""): value
            for key, value in self.data.layout.items()
        }

        plot_point_dict(ax1, short_layout, "k+")
        plot_lease_boundary(ax1, self.data.lease_poly, self.data.padding)

        ax1.margins(0.1, 0.1)
        ax1.autoscale_view()

        annotate_poly(ax1, self.data.lease_poly)

        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha="right")

        plt.title("Array Layout in Lease Area")
        plt.tight_layout()

        self.fig_handle = plt.gcf()

        return


class ArrayLeasePlotNumbers(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Lease Area Array Layout (With Device Numbers)"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "site.lease_boundary",
            "project.layout",
            "options.boundary_padding",
        ]

        return input_list

    @classmethod
    def declare_optional(cls):
        option_list = ["options.boundary_padding"]

        return option_list

    @classmethod
    def declare_id_map(self):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "lease_poly": "site.lease_boundary",
            "layout": "project.layout",
            "padding": "options.boundary_padding",
        }

        return id_map

    def connect(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect="equal")

        short_layout = {
            key.replace("device", ""): value
            for key, value in self.data.layout.items()
        }

        plot_point_dict(ax1, short_layout, "k+", annotate=True)
        plot_lease_boundary(ax1, self.data.lease_poly, self.data.padding)

        ax1.margins(0.1, 0.1)
        ax1.autoscale_view()

        annotate_poly(ax1, self.data.lease_poly)

        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha="right")

        plt.title("Array Layout in Lease Area")
        plt.tight_layout()

        self.fig_handle = plt.gcf()

        return


class ArrayCablesPlot(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Array Cable Layout"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "site.lease_boundary",
            "corridor.landing_point",
            "project.layout",
            "project.cable_routes",
            "project.substation_layout",
        ]

        return input_list

    @classmethod
    def declare_optional(cls):
        option_list = ["site.lease_boundary"]

        return option_list

    @classmethod
    def declare_id_map(self):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "lease_poly": "site.lease_boundary",
            "landing_point": "corridor.landing_point",
            "layout": "project.layout",
            "cable_routes": "project.cable_routes",
            "substation_layout": "project.substation_layout",
        }

        return id_map

    def connect(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect="equal")

        short_layout = {
            key.replace("device", ""): value
            for key, value in self.data.layout.items()
        }
        landing_dict = {"Export Cable Landing": self.data.landing_point}

        lplot = plot_point_dict(ax1, landing_dict, "or", "Export Cable Landing")
        dplot = plot_point_dict(ax1, short_layout, "k+", "Devices")
        splot = plot_point_dict(
            ax1, self.data.substation_layout, "gs", "Collection Points"
        )
        plot_cables(ax1, self.data.cable_routes)

        if self.data.lease_poly is not None:
            plot_lease_boundary(ax1, self.data.lease_poly)

        ax1.margins(0.1, 0.1)
        ax1.autoscale_view()

        if self.data.lease_poly is not None:
            annotate_poly(ax1, self.data.lease_poly)

        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha="right")
        plt.legend(
            handles=[dplot, splot, lplot],
            bbox_to_anchor=(1.05, 1),
            loc=2,
            borderaxespad=0.0,
            numpoints=1,
        )

        plt.title("Electrical Cable Layout")
        plt.tight_layout(rect=[0, 0.04, 0.84, 0.96])

        self.fig_handle = plt.gcf()

        return


class ArrayFoundationsPlot(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Array Foundations Layout"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "site.lease_boundary",
            "project.layout",
            "project.substation_layout",
            "project.foundations_component_data",
        ]

        return input_list

    @classmethod
    def declare_optional(cls):
        option_list = ["site.lease_boundary"]

        return option_list

    @classmethod
    def declare_id_map(self):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "lease_poly": "site.lease_boundary",
            "layout": "project.layout",
            "substation_layout": "project.substation_layout",
            "foundations_components": "project.foundations_component_data",
        }

        return id_map

    def connect(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect="equal")

        short_layout = {
            key.replace("device", ""): value
            for key, value in self.data.layout.items()
        }

        dplot = plot_point_dict(ax1, short_layout, "k+", "Devices")
        splot = plot_point_dict(
            ax1, self.data.substation_layout, "gs", "Collection Points"
        )

        foundation_marker = {
            "shallowfoundation": "b_",
            "gravity": "r^",
            "pile": "co",
            "suctioncaisson": "mp",
            "directembedment": "y|",
            "drag": "kv",
        }

        foundation_name = {
            "shallowfoundation": "Shallow",
            "gravity": "Gravity",
            "pile": "Pile",
            "suctioncaisson": "Suction Caisson",
            "directembedment": "Direct Embedment",
            "drag": "Drag",
        }

        foundations_locations = self.data.foundations_components[
            ["Type", "UTM X", "UTM Y"]
        ]

        locations_groups = foundations_locations.groupby("Type")
        foundations_handles = []

        for name, group in locations_groups:
            plot_marker = foundation_marker[name]
            plot_name = foundation_name[name]

            coords = group[["UTM X", "UTM Y"]].values
            plot_dict = {i: Point(xy) for i, xy in enumerate(coords)}
            fplot = plot_point_dict(
                ax1, plot_dict, plot_marker, plot_name, markersize=8
            )

            foundations_handles.append(fplot)

        if self.data.lease_poly is not None:
            plot_lease_boundary(ax1, self.data.lease_poly)

        ax1.margins(0.1, 0.1)
        ax1.autoscale_view()

        if self.data.lease_poly is not None:
            annotate_poly(ax1, self.data.lease_poly)

        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"

        all_handles = [dplot, splot] + foundations_handles

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha="right")
        plt.legend(
            handles=all_handles,
            bbox_to_anchor=(1.05, 1),
            loc=2,
            borderaxespad=0.0,
            numpoints=1,
        )

        plt.title("Foundations Layout")
        plt.tight_layout()

        self.fig_handle = plt.gcf()

        return


def plot_point_dict(
    ax,
    layout,
    marker,
    label=None,
    annotate=False,
    markersize=None,
    text_weight=None,
    text_size=None,
):
    if text_weight is None:
        text_weight = "normal"
    if text_size is None:
        text_size = "medium"

    x = []
    y = []

    for coords in layout.itervalues():
        x.append(coords.x)
        y.append(coords.y)

    kwargs = {"mew": 2, "markersize": 10}

    if label is not None:
        kwargs["label"] = label
    if markersize is not None:
        kwargs["markersize"] = markersize

    pplot = ax.plot(x, y, marker, **kwargs)

    if not annotate:
        return pplot[0]

    for key, point in layout.iteritems():
        coords = list(point.coords)[0]
        ax.annotate(
            str(key),
            xy=coords[:2],
            xytext=(0, 10),
            xycoords="data",
            textcoords="offset pixels",
            horizontalalignment="center",
            weight=text_weight,
            size=text_size,
        )

    return pplot[0]


def plot_lease_boundary(ax, lease_boundary, padding=None):
    outer_coords = list(lease_boundary.exterior.coords)

    if padding is None:
        lease_boundary = Polygon(outer_coords)
        # patch = PolygonPatch(lease_boundary, ec=GREY, fill=False)

    else:
        inner_boundary = lease_boundary.buffer(-padding)
        inner_coords = list(inner_boundary.exterior.coords)

        # Check if the orientation of the polygons are the same
        if clockwise(*zip(*inner_coords)) == clockwise(*zip(*outer_coords)):
            inner_coords = inner_coords[::-1]

        lease_boundary = Polygon(outer_coords, [inner_coords])
        # patch = PolygonPatch(
        #     lease_boundary, fc=RED, fill=True, alpha=0.3, ls=None
        # )

    # ax.add_patch(patch)

    return


def annotate_poly(ax, lease_poly):
    maxy = lease_poly.bounds[3] + 50.0
    centroid = np.array(lease_poly.centroid)

    ymin, ymax = ax.get_ylim()

    if maxy > ymax:
        maxy = ymin + 0.95 * (ymax - ymin)

    ax.annotate(
        "Lease Area",
        xy=(centroid[0], maxy),
        horizontalalignment="center",
        verticalalignment="bottom",
        weight="bold",
        size="large",
    )

    return


def plot_cables(ax, cable_routes):
    cables = cable_routes.groupby("Marker")

    xmax = -np.inf
    ymax = -np.inf
    xmin = np.inf
    ymin = np.inf

    for name, cable in cables:
        x = cable["UTM X"]
        y = cable["UTM Y"]

        xmax = max(list(x) + [xmax])
        ymax = max(list(y) + [ymax])
        xmin = min(list(x) + [xmin])
        ymin = min(list(y) + [ymin])

        line = plt.Line2D(x, y)
        ax.add_line(line)

    return


def clockwise(x, y):
    """Use the shoelace formula to determine whether the polygon points are
    defined in a clockwise direction"""
    # https://stackoverflow.com/a/1165943/3215152
    # https://stackoverflow.com/a/19875560/3215152
    if sum(x[i] * (y[i + 1] - y[i - 1]) for i in range(-1, len(x) - 1)) < 0:
        return True
    return False
