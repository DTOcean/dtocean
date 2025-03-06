# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Rui Duarte, Mathew Topper
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

"""
Created on Wed Apr 06 15:59:04 2016

.. moduleauthor:: Rui Duarte <rui.duarte@france-energies-marines.org>
.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

from typing import Literal, Sequence, cast

import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap, Normalize

from .plots import PlotInterface


class EISPlot_hydro(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Environmental Impact Score"

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

        input_list = ["project.hydro_eis", "project.hydro_confidence"]

        return input_list

    @classmethod
    def declare_id_map(cls):
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
            "eis": "project.hydro_eis",
            "confidence": "project.hydro_confidence",
        }

        return id_map

    def connect(self):
        eis = self.data.eis
        confidence_dict = self.data.confidence
        plot_title = "Hydrodynamics"

        self.fig_handle = eis_plot(eis, confidence_dict, plot_title)


class EISPlot_elec(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Environmental Impact Score"

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

        input_list = ["project.elec_eis", "project.elec_confidence"]

        return input_list

    @classmethod
    def declare_id_map(cls):
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
            "eis": "project.elec_eis",
            "confidence": "project.elec_confidence",
        }

        return id_map

    def connect(self):
        eis = self.data.eis
        confidence_dict = self.data.confidence
        plot_title = "Electrical Sub-Systems"

        self.fig_handle = eis_plot(eis, confidence_dict, plot_title)


class EISPlot_moor(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Environmental Impact Score"

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

        input_list = ["project.moor_eis", "project.moor_confidence"]

        return input_list

    @classmethod
    def declare_id_map(cls):
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
            "eis": "project.moor_eis",
            "confidence": "project.moor_confidence",
        }

        return id_map

    def connect(self):
        eis = self.data.eis
        confidence_dict = self.data.confidence
        plot_title = "Moorings and Foundations"

        self.fig_handle = eis_plot(eis, confidence_dict, plot_title)


class GEISPlot_hydro(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Global Environmental Impact Score"

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

        input_list = ["project.hydro_global_eis"]

        return input_list

    @classmethod
    def declare_id_map(cls):
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

        id_map = {"geis": "project.hydro_global_eis"}

        return id_map

    def connect(self):
        geis = self.data.geis

        self.fig_handle = geis_plot(geis)


class GEISPlot_elec(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Global Environmental Impact Score"

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

        input_list = ["project.elec_global_eis"]

        return input_list

    @classmethod
    def declare_id_map(cls):
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

        id_map = {"geis": "project.elec_global_eis"}

        return id_map

    def connect(self):
        geis = self.data.geis

        self.fig_handle = geis_plot(geis)


class GEISPlot_moor(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Global Environmental Impact Score"

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

        input_list = ["project.moor_global_eis"]

        return input_list

    @classmethod
    def declare_id_map(cls):
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

        id_map = {"geis": "project.moor_global_eis"}

        return id_map

    def connect(self):
        geis = self.data.geis

        self.fig_handle = geis_plot(geis)


def cmap_env(position=None, bit=True):
    """Colormap for the environmental package"""

    colors = [
        (128, 0, 128),
        (255, 0, 255),
        (255, 0, 0),
        (255, 64, 0),
        (255, 128, 0),
        (255, 178, 102),
        (255, 255, 51),
        (153, 255, 153),
        (255, 255, 255),
        (204, 229, 255),
        (102, 178, 255),
        (0, 128, 255),
        (0, 0, 255),
    ]

    bit_rgb = np.linspace(0, 1, 256)

    if position is None:
        position = np.linspace(0, 1, len(colors))
    else:
        if len(position) != len(colors):
            raise ValueError("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            raise ValueError("position must start with 0 and end with 1")

    if bit:
        for i in range(len(colors)):
            colors[i] = (
                bit_rgb[colors[i][0]],
                bit_rgb[colors[i][1]],
                bit_rgb[colors[i][2]],
            )

    cdict = {
        "red": [],
        "green": [],
        "blue": [],
    }

    for pos, color in zip(position, colors):
        cdict["red"].append((pos, color[0], color[0]))
        cdict["green"].append((pos, color[1], color[1]))
        cdict["blue"].append((pos, color[2], color[2]))

    cdict = cast(
        dict[
            Literal["red", "green", "blue", "alpha"],
            Sequence[tuple[float, ...]],
        ],
        cdict,
    )
    cmap = LinearSegmentedColormap("environment", cdict, 256)

    return cmap


def geis_plot(geis):
    value = []

    if geis["Positive Impact"] is not None:
        value.append(geis["Positive Impact"])
    else:
        value.append(np.nan)

    if geis["Negative Impact"] is not None:
        value.append(geis["Negative Impact"])
    else:
        value.append(np.nan)

    if np.isnan(value[0]):
        pos_impact = 0.0
        value[0] = 0.0
    else:
        pos_impact = int(np.around(value[0]))

    if np.isnan(value[1]):
        neg_impact = 0.0
        value[1] = 0.0
    else:
        neg_impact = int(np.around(value[1]))

    env_cmap = cmap_env()
    norm = Normalize(-100, 50)
    env_color = env_cmap(norm(value))

    fig = plt.figure()

    ax1 = fig.add_subplot(1, 1, 1)

    scalex = 1.0
    scaley = 1.0

    effects = [path_effects.withSimplePatchShadow(offset=(10, -10))]

    rectangles = {
        "Positive": patches.Rectangle(
            (0.2 * scalex, 0.2 * scaley),
            0.1 * scalex,
            0.2 * scaley,
            facecolor=env_color[0],
            edgecolor="k",
            picker=5,
            path_effects=effects,
        ),
        "Negative": patches.Rectangle(
            (0.2 * scalex, 0.6 * scaley),
            0.1 * scalex,
            0.2 * scaley,
            facecolor=env_color[1],
            edgecolor="k",
            picker=5,
            path_effects=effects,
        ),
    }

    score = {"Positive": pos_impact, "Negative": neg_impact}

    if np.isnan(geis["Min Negative Impact"]):
        min_neg = 0.0
    else:
        min_neg = int(np.around(geis["Min Negative Impact"]))

    if np.isnan(geis["Max Negative Impact"]):
        max_neg = 0.0
    else:
        max_neg = int(np.around(geis["Max Negative Impact"]))

    if np.isnan(geis["Min Positive Impact"]):
        min_pos = 0.0
    else:
        min_pos = int(np.around(geis["Min Positive Impact"]))

    if np.isnan(geis["Max Positive Impact"]):
        max_pos = 0.0
    else:
        max_pos = int(np.around(geis["Max Positive Impact"]))

    for r in rectangles:
        ax1.add_artist(rectangles[r])
        rx, ry = rectangles[r].get_xy()
        cx = rx + rectangles[r].get_width() / 2.0
        cy = ry + rectangles[r].get_height() / 2.0

        ax1.annotate(
            r,
            (cx - 0.1 * scalex, cy),
            color="k",
            weight="bold",
            fontsize=16,
            ha="center",
            va="center",
            rotation=90,
        )

        ax1.annotate(
            str(score[r]),
            (cx + 0.15 * scalex, cy),
            color="b",
            fontsize=64,
            ha="center",
            va="center",
        )

        if r == "Positive":
            ax1.annotate(
                str([min_pos, max_pos]),
                (cx + 0.5 * scalex, cy),
                color="k",
                weight="bold",
                fontsize=16,
                ha="center",
                va="center",
            )

        if r == "Negative":
            ax1.annotate(
                str([min_neg, max_neg]),
                (cx + 0.5 * scalex, cy),
                color="k",
                weight="bold",
                fontsize=16,
                ha="center",
                va="center",
            )

    ax1.set_xticks([])
    ax1.set_yticks([])

    plt.title("ENVIRONMENTAL IMPACT ASSESSMENT")

    pos1 = ax1.get_position()

    cbar_ax = fig.add_axes((pos1.x0, pos1.y0 - 0.1, pos1.width, 0.025))

    cmmapable = cm.ScalarMappable(norm, env_cmap)
    cmmapable.set_array(range(-100, 50))
    plt.colorbar(cmmapable, orientation="horizontal", cax=cbar_ax)

    plt.title(
        "(negative impact) --- SCORING SYSTEM SCALE --- " "(positive impact)"
    )

    fig_handle = plt.gcf()

    return fig_handle


def eis_plot(eis, confidence_dict, plot_title):
    # Environmental impacts

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

    value = []
    impact = []
    confidence = []

    for key in env_impacts:
        if key in eis and eis[key] is not None:
            value.append(eis[key])
            impact.append(key)
            confidence.append(confidence_dict[key])
        else:
            value.append(0)
            impact.append(key)
            confidence.append(0)

    # if we want to sort the values
    # value, impact, confidence = zip(*sorted(zip(value, impact, confidence)))

    env_cmap = cmap_env()
    norm = Normalize(-100, 50)
    env_color = env_cmap(norm(value))

    fig = plt.figure()

    ax1 = fig.add_subplot(1, 1, 1)
    x = np.arange(len(value))
    ax1.barh(x, value, align="center", color=env_color)
    ax1.set_xticklabels([])
    ax1.set_yticks(x)
    ax1.set_yticklabels(impact)
    ax1.axvline(0, color="grey")

    for i, v in zip(x, value):
        if v < 0:
            ax1.text(
                v - 4.0,
                i + 0.15,
                str(int(round(v))),
                color="black",
                weight="bold",
            )
        elif v > 0:
            ax1.text(
                v + 1.0,
                i + 0.15,
                str(int(round(v))),
                color="black",
                weight="bold",
            )

    plt.gca().invert_yaxis()

    ax2 = cast(Axes, ax1.twinx())
    ax2.barh(x, np.zeros(len(x)), align="center")
    ax2.yaxis.tick_right()
    ax2.set_yticks(x)
    ax2.set_yticklabels(confidence)
    ax2.set_ylabel("Level of confidence")

    plt.xlim([-100, 50])
    plt.title(plot_title)

    pos1 = ax1.get_position()

    cbar_ax = fig.add_axes((pos1.x0, pos1.y0 - 0.06, pos1.width, 0.025))

    cmmapable = cm.ScalarMappable(norm, env_cmap)
    cmmapable.set_array(range(-100, 50))
    plt.colorbar(cmmapable, orientation="horizontal", cax=cbar_ax)

    plt.title(
        "(negative impact) --- SCORING SYSTEM SCALE ---" "(positive impact)"
    )

    fig_handle = plt.gcf()

    return fig_handle
