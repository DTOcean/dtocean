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

"""
Created on Wed Apr 06 15:59:04 2016

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from . import PlotInterface


class WaveOccurrencePlot(PlotInterface):

    @classmethod
    def get_name(cls):

        '''A class method for the common name of the interface.

        Returns:
          str: A unique string
        '''

        return "Wave Resource Occurrence Matrix"

    @classmethod
    def declare_inputs(cls):

        '''A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''

        input_list = ["farm.wave_occurrence"]

        return input_list

    @classmethod
    def declare_id_map(self):

        '''Declare the mapping for variable identifiers in the data description
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

        '''

        id_map = {"occurrence_matrix": "farm.wave_occurrence"
                  }

        return id_map

    def connect(self):

        occurrence_grid = self.data.occurrence_matrix
        occurrence_flat = occurrence_grid.sum("Dir")
        vals = occurrence_flat.values.T

        col_normals = Normalize(vals.min(), vals.max())

        cellStrs = []

        for row in vals:
            rowStrs = ["{:.2%}".format(x) for x in row]
            cellStrs.append(rowStrs)

        fig = plt.figure()
        ax1 = fig.add_subplot(111,
                              frameon=True,
                              xticks=[],
                              yticks=[])

        # Add headers and a table at the bottom of the axes
        header_0 = plt.table(cellText=[['']],
                             colLabels=['Te [$s$]'],
                             loc='center',
                             bbox=[0, 0.85, 1.0, 0.1]
                             )

        header_1 = plt.table(cellText=[['Bob']],
                             rowLabels=['Hm0 [$m$]          '],
                             loc='center',
                             bbox=[0, 0, 1, 0.845]
                             )

        the_table = plt.table(cellText=cellStrs,
                              rowLabels=occurrence_flat.Hm0.values,
                              colLabels=occurrence_flat.Te.values,
                              cellColours=plt.cm.RdYlGn_r(col_normals(vals)),
                              loc='center',
                              bbox=[0, 0, 1, 0.9])

        plt.title("Joint Probability Plot (Over All Directions)")

        self.fig_handle = plt.gcf()

        return
    
    
class PowerMatrixPlot(PlotInterface):

    @classmethod
    def get_name(cls):

        '''A class method for the common name of the interface.

        Returns:
          str: A unique string
        '''

        return "Single Wave Device Power Matrix"

    @classmethod
    def declare_inputs(cls):

        '''A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''

        input_list = ['device.wave_power_matrix']

        return input_list

    @classmethod
    def declare_id_map(self):

        '''Declare the mapping for variable identifiers in the data description
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

        '''

        id_map = {"power_matrix": 'device.wave_power_matrix'
                  }

        return id_map

    def connect(self):

        occurrence_grid = self.data.power_matrix
        occurrence_flat = occurrence_grid.mean("Dir")
        vals = occurrence_flat.values.T
    
        col_normals = Normalize(vals.min(), vals.max())
    
        cellStrs = []
    
        for row in vals:
            rowStrs = ["{0:d}".format(int(x)) for x in row]
            cellStrs.append(rowStrs)
    
        fig = plt.figure()
        ax1 = fig.add_subplot(111,
                              frameon=True,
                              xticks=[],
                              yticks=[])
    
        # Add headers and a table at the bottom of the axes
        header_0 = plt.table(cellText=[['']],
                             colLabels=['Te [$s$]'],
                             loc='center',
                             bbox=[0, 0.85, 1.0, 0.1]
                             )
    
        header_1 = plt.table(cellText=[['Bob']],
                             rowLabels=['Hm0 [$m$]          '],
                             loc='center',
                             bbox=[0, 0, 1, 0.8575]
                             )
        
        short_hm0 = ["{:.2f}".format(x) for x in occurrence_flat.Hm0.values]
        short_te = ["{:.2f}".format(x) for x in occurrence_flat.Te.values]
    
        the_table = plt.table(cellText=cellStrs,
                              rowLabels=short_hm0,
                              colLabels=short_te,
                              cellColours=plt.cm.RdYlGn_r(col_normals(vals)),
                              loc='center',
                              bbox=[0, 0, 1, 0.9])
    
        plt.title("Single Device Power Matrix (Mean Over All Directions) [kW]")

        self.fig_handle = plt.gcf()

        return


class TeHm0Plot(PlotInterface):

    @classmethod
    def get_name(cls):

        '''A class method for the common name of the interface.

        Returns:
          str: A unique string
        '''

        return "Te & Hm0 Time Series"

    @classmethod
    def declare_inputs(cls):

        '''A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        '''

        input_list = ["farm.wave_series"]

        return input_list

    @classmethod
    def declare_id_map(self):

        '''Declare the mapping for variable identifiers in the data description
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

        '''

        id_map = {"wave_series": "farm.wave_series"
                  }

        return id_map

    def connect(self):

        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        # Add headers and a table at the bottom of the axes
        ax1 = self.data.wave_series.Te.plot(ax=ax1)
        ax2 = self.data.wave_series.Hm0.plot(secondary_y=True,
                                             style='g')

        ax1.set_ylabel('Te [$s$]')
        ax2.set_ylabel('Hm0 [$m$]')

        plt.title("Te & Hm0 Time Series")

        self.fig_handle = plt.gcf()

        return
