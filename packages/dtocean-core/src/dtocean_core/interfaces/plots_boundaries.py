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

from functools import partial

import pyproj
import numpy as np
import matplotlib.pyplot as plt

from descartes import PolygonPatch
from shapely.ops import transform
from mpl_toolkits.basemap import Basemap

from . import PlotInterface

BLUE = '#6699cc'
GREEN = '#32CD32'
RED = '#B20000'


class SiteBoundaryPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Site Boundary"
        
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

        input_list  =  ["site.selected_name",
                        "hidden.site_boundaries"
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
                  
        id_map = {"name": "site.selected_name",
                  "boundaries": "hidden.site_boundaries"
                  }

        return id_map

    def connect(self):
        
        site_poly = self.data.boundaries[self.data.name]
        
        centroid = np.array(site_poly.centroid)
        llcrnrlon = centroid[0] - 5.
        llcrnrlat = centroid[1] - 5.
        urcrnrlon = centroid[0] + 5.
        urcrnrlat = centroid[1] + 5.
        
        m = Basemap(llcrnrlon=llcrnrlon,
                    llcrnrlat=llcrnrlat,
                    urcrnrlon=urcrnrlon,
                    urcrnrlat=urcrnrlat,
                    projection='lcc',
                    lat_1=centroid[1],
                    lon_0=centroid[0],
                    resolution="l",
                    area_thresh=1000.)

        m.drawcountries(linewidth=0.25)
        m.fillcontinents(color='#8B7500')
        m.drawmapboundary(fill_color='lightblue')
        m.drawmeridians(np.arange(0, 360, 5),
                        labels=[0, 0, 0, 1],
                        fontsize=10)
        m.drawparallels(np.arange(-90, 90, 5),
                        labels=[1, 0, 0, 0],
                        fontsize=10)

        x, y = m(*centroid)
        
        m.plot(x, y, 's',
               mew=3,
               ms=20,
               fillstyle='none',
               markeredgecolor='yellow')
        
        ax = plt.gca()
        ax.annotate(self.data.name, 
                    xy=(x, y + 50000),
                    horizontalalignment='center',
                    color='black',
                    backgroundcolor="white",
                    size="large",
                    weight="roman")
        
        self.fig_handle = plt.gcf()
        
        return
        
class AllBoundaryPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "All Boundaries"
        
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

        input_list  =  ["hidden.site_boundary",
                        "site.lease_boundary",
                        "site.corridor_boundary",
                        "corridor.landing_point",
                        "site.projection"
                        ]
                                                
        return input_list
        
    @classmethod
    def declare_optional(cls):
        
        option_list  =  ["site.lease_boundary",
                         "site.corridor_boundary",
                         "corridor.landing_point"
                         ]

        return option_list
        
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
                  
        id_map = {"site_poly": "hidden.site_boundary",
                  "lease_poly": "site.lease_boundary",
                  "corridor_poly": "site.corridor_boundary",
                  "landing_point": "corridor.landing_point",
                  "projection": "site.projection"
                  }

        return id_map

    def connect(self):
        
        self.fig_handle = boundaries_plot(
                                        site_poly=self.data.site_poly,
                                        projection=self.data.projection,
                                        lease_poly=self.data.lease_poly,
                                        corridor_poly=self.data.corridor_poly,
                                        landing_point=self.data.landing_point)
        
        return
        

class DesignBoundaryPlot(PlotInterface):
    
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return "Design Boundaries"
        
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

        input_list = ["site.lease_boundary",
                      "site.corridor_boundary",
                      "farm.nogo_areas",
                      "corridor.nogo_areas",
                      "corridor.landing_point",
                      "project.lease_area_entry_point"
                      ]
                                                
        return input_list
        
    @classmethod
    def declare_optional(cls):
        
        option_list = ["site.lease_boundary",
                       "site.corridor_boundary",
                       
                       "farm.nogo_areas",
                       "corridor.nogo_areas",
                       
                       "corridor.landing_point",
                       "project.lease_area_entry_point"
                       ]

        return option_list
        
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
                  
        id_map = {"lease_poly": "site.lease_boundary",
                  "corridor_poly": "site.corridor_boundary",
                  "landing_point": "corridor.landing_point",
                  "lease_entry_point": "project.lease_area_entry_point",
                  "nogo_areas": "farm.nogo_areas",
                  "corridor_nogo_areas": "corridor.nogo_areas"
                  }

        return id_map

    def connect(self):
        
        self.fig_handle = boundaries_plot(
                          lease_poly=self.data.lease_poly,
                          corridor_poly=self.data.corridor_poly,
                          nogo_polys=self.data.nogo_areas,
                          corridor_nogo_polys=self.data.corridor_nogo_areas,
                          landing_point=self.data.landing_point,
                          lease_entry_point=self.data.lease_entry_point)
        
        return


def boundaries_plot(site_poly=None,
                    projection=None,
                    lease_poly=None,
                    corridor_poly=None,
                    nogo_polys=None,
                    corridor_nogo_polys=None,
                    landing_point=None,
                    lease_entry_point=None):
    
    if (site_poly is None and
        lease_poly is None and
        corridor_poly is None): return None
        
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
    
    # Convert the site polygon to local coordinate system
    if site_poly is not None:
        
        project = partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:4326'), # source coordinate system
            pyproj.Proj(projection)) # destination coordinate system
    
        local_site_poly = transform(project, site_poly)  # apply projection
    
        patch = PolygonPatch(local_site_poly,
                             fc=RED,
                             ec=RED,
                             fill=False,
                             linewidth=1)
        ax1.add_patch(patch)
    
    if lease_poly is not None:
            
        patch = PolygonPatch(lease_poly,
                             fc=BLUE,
                             ec=BLUE,
                             fill=False,
                             linewidth=2)
        ax1.add_patch(patch)
        
        maxy = lease_poly.bounds[3] + 50.
        centroid = np.array(lease_poly.centroid)
        
        ax1.annotate("Lease Area",
                     xy=(centroid[0], maxy),
                     horizontalalignment='center',
                     verticalalignment='bottom',
                     weight="bold",
                     size='large')
            
    if corridor_poly is not None:
        
        patch = PolygonPatch(corridor_poly,
                             fc=GREEN,
                             ec=GREEN,
                             fill=False,
                             linewidth=2)
        ax1.add_patch(patch)
        
        miny = corridor_poly.bounds[1] - 50.
        centroid = np.array(corridor_poly.centroid)
        
        ax1.annotate("Cable Corridor",
                     xy=(centroid[0], miny),
                     horizontalalignment='center',
                     verticalalignment='top',
                     weight="bold",
                     size='large')
        
    if nogo_polys is not None:
        
        for key, polygon in nogo_polys.iteritems():
            
            patch = PolygonPatch(polygon,
                                 fc=RED,
                                 ec=RED,
                                 fill=True,
                                 alpha=0.3,
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
            
    if corridor_nogo_polys is not None:
        
        for key, polygon in nogo_polys.iteritems():
            
            patch = PolygonPatch(polygon,
                                 fc=RED,
                                 ec=RED,
                                 fill=True,
                                 alpha=0.3,
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
        
    if landing_point is not None:
        
        xy = list(landing_point.coords)[0]
        ax1.plot(xy[0], xy[1], 'or')
        
        label_xy = (xy[0] + 50, xy[1])
        
        ax1.annotate("Export Cable Landing",
                     xy=label_xy,
                     horizontalalignment='left',
                     verticalalignment='center',
                     weight="bold",
                     size='large')
        
    if lease_entry_point is not None:
        
        xy = list(lease_entry_point.coords)[0]
        ax1.plot(xy[0], xy[1], 'sb')
        
        label_xy = (xy[0] + 50, xy[1])
        
        ax1.annotate("Lease Area Entry Point",
                     xy=label_xy,
                     horizontalalignment='left',
                     verticalalignment='center',
                     weight="bold",
                     size='large')

    ax1.margins(0.1, 0.1)
    ax1.autoscale_view()

    xlabel = 'UTM x (m)'
    ylabel = 'UTM y (m)'

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ticklabel_format(useOffset=False)
            
    return fig
    