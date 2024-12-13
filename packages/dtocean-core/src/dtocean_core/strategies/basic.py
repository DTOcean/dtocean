# -*- coding: utf-8 -*-

#    Copyright (C) 2021 Mathew Topper
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

import logging

from . import Strategy

# Set up logging
module_logger = logging.getLogger(__name__)


class BasicStrategy(Strategy):
    
    """A basic strategy which will run all selected modules and themes in
    sequence."""
    
    @classmethod
    def get_name(cls):
        
        return "Basic"
    
    def configure(self, kwargs=None):
        
        """Does nothing in this case"""
        
        return
    
    def get_variables(self):
        
        return None
    
    def execute(self, core, project):
        
        # Check the project is active and record the simulation title
        sim_index = project.get_active_index()
        
        if sim_index is None:
            
            errStr = "Project has not been activated."
            raise RuntimeError(errStr)
        
        sim_title = project.get_simulation_title(index=sim_index)
        self.add_simulation_title(sim_title)
        
        current_mod = self._module_menu.get_current(core, project)
        
        while current_mod:
            
            self._module_menu.execute_current(core,
                                              project,
                                              allow_unavailable=True)
            current_mod = self._module_menu.get_current(core, project)
        
        return

