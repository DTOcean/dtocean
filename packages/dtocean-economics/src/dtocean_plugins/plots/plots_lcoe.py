#    Copyright (C) 2026 Mathew Topper
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

import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from dtocean_plugins.plots.base import PlotInterface


class LCOEPDFPlot(PlotInterface):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "LCOE PDF Plot"

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
            "project.economics_metrics",
            "project.lcoe_pdf",
            "project.confidence_density",
        ]

        return input_list

    @classmethod
    def declare_optional(cls):
        return []

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
            "economics_metrics": "project.economics_metrics",
            "confidence_density": "project.confidence_density",
            "lcoe_pdf": "project.lcoe_pdf",
        }

        return id_map

    def connect(self):
        clevels = [self.data.confidence_density]
        legend_element = Line2D(
            [0],
            [0],
            color="k",
            lw=1,
            label="95% Confidence Level",
        )

        xx = self.data.lcoe_pdf.coords["Discounted OPEX"].values
        yy = self.data.lcoe_pdf.coords["Discounted Energy"].values
        zz = self.data.lcoe_pdf.data.values

        plt.figure()
        cf = plt.contourf(
            xx,
            yy,
            zz.T,
            32,
            cmap="OrRd",
            norm=colors.PowerNorm(
                gamma=1,
                vmin=0.5 * self.data.confidence_density,
            ),
        )
        cf.cmap.set_under("w")
        plt.contour(xx, yy, zz.T, clevels, colors="k")

        opex = self.data.economics_metrics["Discounted OPEX"]
        energy = self.data.economics_metrics["Discounted Energy"] / 1000

        sp = plt.scatter(
            opex,
            energy,
            marker="x",
            s=20,
            zorder=10,
            color="k",
            label="Data Points",
        )
        plt.colorbar(cf)
        plt.legend(
            handles=[legend_element, sp],
            scatterpoints=1,
        )

        plt.xlabel("Discounted OPEX [Euro]")
        plt.ylabel("Discounted Energy [kWh]")
