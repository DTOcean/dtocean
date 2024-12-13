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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import PlotInterface


class TidalPowerPerformancePlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Tidal Power Performance"
        
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

        input_list  =  ["device.turbine_performance",
                        "device.cut_in_velocity",
                        "device.cut_out_velocity"
                        ]
                                                
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
                  
        id_map = {"perf_curves": "device.turbine_performance",
                  "cut_in": "device.cut_in_velocity",
                  "cut_out": "device.cut_out_velocity"
                  }

        return id_map

    def connect(self):
        
        self.data.perf_curves.plot()

        cut_in = self.data.cut_in
        cut_in_title = self.meta.cut_in.title
        
        plt.axvline(x=cut_in,
                    color='r',
                    linestyle='--')
        plt.text(cut_in + 0.1,
                 0.1,
                 cut_in_title,
                 verticalalignment='bottom',
                 rotation=90)
        
        cut_out = self.data.cut_out
        cut_out_title = self.meta.cut_out.title
        
        plt.axvline(x=cut_out,
                    color='r',
                    linestyle='--')
        plt.text(cut_out + 0.1,
                 0.1,
                 cut_out_title,
                 verticalalignment='bottom',
                 rotation=90)
    
        plt.title(self.get_name())
        plt.xlabel("Velocity m/s")
        
        self.fig_handle = plt.gcf()
        
        return


class TidalVelocityPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Tidal Currents"
        
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

        input_list  =  ["farm.tidal_series"
                        ]
                                                
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
                  
        id_map = {"tidal_series": "farm.tidal_series"}

        return id_map

    def connect(self):
        
        tidal_xset = self.data.tidal_series
        
        # Get a random time point
        times = tidal_xset.t
        random_time = np.random.choice(times)
        
        time_slice = tidal_xset.sel(t=random_time)
        
        x = time_slice.coords["UTM x"]
        y = time_slice.coords["UTM y"]

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
        
        mag = np.sqrt(time_slice.U ** 2 + time_slice.V ** 2)
        
        plt.contourf(x, y, mag.T)
        clb = plt.colorbar()
        clb.set_label("$m/s$")
        
        Q = plt.quiver(x[::6],
                       y[::6],
                       time_slice.U.T[::6, ::6],
                       time_slice.V.T[::6, ::6],
                       pivot='mid',
                       units='inches')
        
        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"
        
        dt_time = pd.to_datetime(str(random_time))
        time_str = dt_time.strftime('%Y-%m-%d %H:%M:%S')

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.ticklabel_format(useOffset=False)
        
        plt.title("Tidal Current Velocities: {}".format(time_str))

        self.fig_handle = plt.gcf()
        
        return
