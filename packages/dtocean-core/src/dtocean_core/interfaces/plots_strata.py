# -*- coding: utf-8 -*-

#    Copyright (C) 2018 Mathew Topper
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

import numpy as np
import matplotlib.pyplot as plt
import cmocean

from . import PlotInterface


class CombinedBathyPlot(PlotInterface):
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Combined Bathymetry"
        
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

        input_list  =  ['bathymetry.layers',
                        'corridor.layers'
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
                  
        id_map = {"deployment_strata": "bathymetry.layers", 
                  "cable_corridor_strata": "corridor.layers"
                  }

        return id_map

    def connect(self):
                    
        deployment_bathy = self.data.deployment_strata[
                                                "depth"].sel(layer="layer 1")
        cable_corridor_bathy = self.data.cable_corridor_strata[
                                                "depth"].sel(layer="layer 1")
        
        fig = plt.figure()
        fig.add_subplot(1, 1, 1, aspect='equal')
  
        step = 5
        bm = np.amin(deployment_bathy)
        bm = int(10 * round(float(bm) / 10))
        levels = np.arange(bm, 0.0 + step, step)
        
        x = deployment_bathy.coords["x"]
        y = deployment_bathy.coords["y"]
        
        plt.contourf(x,
                     y,
                     deployment_bathy.T,
                     levels=levels,
                     cmap=cmocean.cm.deep_r)
            
        x = cable_corridor_bathy.coords["x"]
        y = cable_corridor_bathy.coords["y"]
        
        plt.contourf(x,
                     y,
                     cable_corridor_bathy.T,
                     levels=levels,
                     cmap=cmocean.cm.deep_r)
        
        clb = plt.colorbar()
    
        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"
        zlabel = "Depth [$m$]"
    
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        clb.set_label(zlabel)
        
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha='right')
        
        plt.title("Combined Bathymetry")
        plt.gcf().tight_layout(rect=(0.05, 0.05, 0.95, 0.95))
        
        self.fig_handle = plt.gcf()

        return


class CombinedSedimentPlot(PlotInterface):
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Combined Sediment (First Layer)"
        
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

        input_list  =  ['bathymetry.layers',
                        'corridor.layers'
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
                  
        id_map = {"deployment_strata": "bathymetry.layers", 
                  "cable_corridor_strata": "corridor.layers"
                  }

        return id_map

    def connect(self):
        
        # These are the "Tableau 20" colors as RGB.
        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14),
                     (255, 187, 120), (44, 160, 44), (152, 223, 138), 
                     (214, 39, 40), (255, 152, 150), (148, 103, 189), 
                     (197, 176, 213), (140, 86, 75), (196, 156, 148), 
                     (227, 119, 194), (247, 182, 210), (127, 127, 127), 
                     (199, 199, 199),  (188, 189, 34), (219, 219, 141), 
                     (23, 190, 207), (158, 218, 229)]
          
        # Scale the RGB values to the [0, 1] range, which is the format 
        # matplotlib accepts.
        for i in range(len(tableau20)):
            r, g, b = tableau20[i]
            tableau20[i] = (r / 255., g / 255., b / 255.)

        sediment_map = {None: np.nan,
                        'loose sand': 1,
                        'medium sand': 2,
                        'dense sand': 3,
                        'very soft clay': 4,
                        'soft clay': 5,
                        'firm clay': 6,
                        'stiff clay': 7,
                        'hard glacial till': 8,
                        'cemented': 9,
                        'soft rock coral': 10,
                        'hard rock': 11,
                        'gravel cobble': 12}
        
        sediment_map_r = {v: k for k, v in sediment_map.items()}

        deployment_sediment = self.data.deployment_strata[
                                        "sediment"].sel(layer="layer 1").values
        cable_corridor_sediment = self.data.cable_corridor_strata[
                                        "sediment"].sel(layer="layer 1").values
    
        new_deployment_sediment = np.vectorize(sediment_map.get)(
                                                        deployment_sediment)
            
        new_cable_corridor_sediment = np.vectorize(sediment_map.get)(
                                                    cable_corridor_sediment)
            
        # Find out how many codes were used to get the levels and legend
        deployment_codes = np.unique(new_deployment_sediment)
        deployment_codes = deployment_codes[~np.isnan(deployment_codes)]
        cable_corridor_codes = np.unique(new_cable_corridor_sediment)
        cable_corridor_codes = cable_corridor_codes[
                                            ~np.isnan(cable_corridor_codes)]
        
        all_codes = set(deployment_codes) | set(cable_corridor_codes)
        all_codes = list(all_codes)
        all_codes.sort()

        levels = [0] + all_codes
        legend_names = [sediment_map_r[x] for x in all_codes]
        
        color_index = [int(x - 1) for x in all_codes]
        colors = [tableau20[x] for x in color_index]
        
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1,aspect='equal')
        
        x = self.data.deployment_strata.coords["x"]
        y = self.data.deployment_strata.coords["y"]
        
        cs = plt.contourf(x,
                          y,
                          new_deployment_sediment.T,
                          colors=colors,
                          levels=levels)
        
        plt.contour(x,
                    y,
                    new_deployment_sediment.T,
                    levels=levels,
                    colors=('0.8',),
                    linewidths=(1.2,))
        
        x = self.data.cable_corridor_strata.coords["x"]
        y = self.data.cable_corridor_strata.coords["y"]

        plt.contourf(x,
                     y,
                     new_cable_corridor_sediment.T,
                     colors=colors,
                     levels=levels)
        
        plt.contour(x,
                    y,
                    new_cable_corridor_sediment.T,
                    levels=levels,
                    colors=('0.8',),
                    linewidths=(1.2,))
        
        proxy = [plt.Rectangle((0,0),
                               1,
                               1,
                               fc = pc.get_facecolor()[0]) 
                                                for pc in cs.collections]
        
        lgd = ax.legend(proxy,
                        legend_names,
                        bbox_to_anchor=(1.04, 1),
                        loc="upper left")
        
        xlabel = "UTM x [$m$]"
        ylabel = "UTM y [$m$]"
    
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        plt.ticklabel_format(useOffset=False)
        plt.xticks(rotation=30, ha='right')
        
        plt.title("Combined Sediment (First Layer)")
        
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