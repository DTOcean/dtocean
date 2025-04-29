# -*- coding: utf-8 -*-

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

import matplotlib.pyplot as plt

from dtocean_core.tools.cable_constraints import (CableConstraintsTool,
                                                  get_constraints)
from dtocean_electrical.output import plot_devices

from . import GUITool
from ..widgets.display import MPLWidget


class GUICableConstraintsTool(GUITool, CableConstraintsTool):
    
    """A basic strategy which will run all selected modules and themes in
    sequence."""
    
    def __init__(self):
        
        CableConstraintsTool.__init__(self)
        GUITool.__init__(self)
        self._elec = None
        self._constrained_lines = None
        self._fig = None
        
        return
    
    def get_weight(self):
        
        '''A method for getting the order of priority of the strategy.
        
        Returns:
          int
        '''
        
        return 2
    
    def has_widget(self):
        return True
    
    def get_widget(self):
        
        if self._elec is None or self._constrained_lines is None:
            return None
        
        fig = plot_devices(self._elec.grid,
                           self._constrained_lines,
                           self._elec.array_data.layout,
                           self._elec.array_data.landing_point,
                           self._elec.array_data.device_footprint,
                           [],
                           [],
                           [],
                           []
                           )
        widget = MPLWidget(fig, self.parent)
        self._fig = fig
        
        return widget
    
    def destroy_widget(self):
        plt.close(self._fig)
        self._fig = None
        return
    
    def connect(self, **kwargs): # pylint: disable=unused-argument
        self._elec, self._constrained_lines = get_constraints(self.data)
        return
