# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Vincenzo Nava
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

import sys
import logging

from . import Strategy
from .basic import BasicStrategy

# Set up logging
module_logger = logging.getLogger(__name__)


class UnitSensitivity(Strategy):
    
    """A sensitivity study on a single unit variables over a given range of
    values, adjusted before execution of a chosen module."""
    
    def __init__(self):
        
        super(UnitSensitivity, self).__init__()
        
        # Borrow the Basic strategy
        self._basic = BasicStrategy()
        
        return
    
    @classmethod
    def get_name(cls):
        
        return "Unit Sensitivity"
    
    def configure(self, module_name,
                        variable_name,
                        variable_values,
                        skip_errors=True):
        
        config_dict = {"module_name":  module_name,
                       "var_name": variable_name,
                       "var_values": variable_values,
                       "skip_errors": skip_errors}
                       
        self.set_config(config_dict)
        
        return
    
    def get_variables(self):
        
        return [self._config["var_name"]]
    
    def execute(self, core, project):
        
        # Test for Nones
        if (self._config is None or
            self._config["module_name"] is None or
            self._config["var_name"] is None or
            self._config["var_values"] is None):
                
            errStr = ("Some configuration values are None. Have you called "
                      "the configure method?")
            raise ValueError(errStr)
        
        module_name = self._config["module_name"]
        variable_name = self._config["var_name"]
        variable_values = self._config["var_values"]
        
        # Pick up the branch
        if not module_name in self._module_menu.get_available(core, project):
            
            errStr = "Module {} does not exist".format(module_name)
            raise ValueError(errStr)
          
        if not module_name in self._module_menu.get_active(core, project):
        
            errStr = "Module {} has not been activated".format(module_name)
            raise ValueError(errStr)
        
        mod_branch = self._tree.get_branch(core, project, module_name)
        
        # Check for existance of the variable
        module_inputs = mod_branch.get_input_status(core,
                                                    project)
        
        if variable_name not in module_inputs.keys():
        
            msgStr = ("Variable {} is not an input to module "
                      "{}.").format(variable_name, module_name)
            raise ValueError(msgStr)
        
        unit_var = mod_branch.get_input_variable(core,
                                                 project,
                                                 variable_name)
        
        unit_meta = unit_var.get_metadata(core)
        
        # Check the project is active and record the simulation number
        sim_index = project.get_active_index()
        
        if sim_index is None:
            
            errStr = "Project has not been activated."
            raise RuntimeError(errStr)
        
        sim_titles = []
        
        # Iterate through the values up to last entry
        for unit_value in variable_values[:-1]:
            
            # Set the variable
            new_title = self._get_title_str(unit_meta, unit_value)
            
            # Deal with identical titles
            if new_title in sim_titles:
                n_reps = sum((x.count(new_title) for x in sim_titles))
                new_title = "{} [repeat {}]".format(new_title, n_reps)
            
            sim_titles.append(new_title)
            
            project.set_simulation_title(new_title)
            
            unit_var.set_raw_interface(core, unit_value)
            unit_var.read(core, project)
            
            success_flag = self._safe_exe(core, project, new_title)
            
            # Move to the required branch and create a new simulation clone
            if success_flag:
                
                self.add_simulation_title(new_title)
                core.clone_simulation(project)
                sim_index = project.get_active_index()
            
            mod_branch.reset(core, project)
        
        # Set the last variable
        new_title = self._get_title_str(unit_meta,  variable_values[-1])
        
        # Deal with identical titles
        if new_title in sim_titles:
            n_reps = sum((x.count(new_title) for x in sim_titles))
            new_title = "{} [repeat {}]".format(new_title, n_reps)
        
        project.set_simulation_title(new_title)
        
        unit_var.set_raw_interface(core, variable_values[-1])
        unit_var.read(core, project)
        
        # Run the simulation
        success_flag = self._safe_exe(core, project, new_title)
        
        if success_flag:
            self.add_simulation_title(new_title)
        
        return
    
    def _safe_exe(self, core, project, sim_title):
        
        msg = 'Executing simulation "{}"'.format(sim_title)
        module_logger.info(msg)
        
        success_flag = True
        
        if self._config["skip_errors"]:
            
            try: 
                
                # Run the simulation
                self._basic.execute(core, project)
            
            except (KeyboardInterrupt, SystemExit):
                
                exc_info = sys.exc_info()
                raise exc_info[0], exc_info[1], exc_info[2]
            
            except BaseException as e:
                
                msg = ("Passing exception '{}' for simulation "
                       "{}").format(type(e).__name__, sim_title)
                module_logger.exception(msg)
                
                success_flag = False
        
        else:
            
            # Run the simulation
            self._basic.execute(core, project)
        
        return success_flag
    
    def _get_title_str(self, meta, value):
        
        title_str = "{} = {}".format(meta.title, value)  
        
        if meta.units is not None:
            title_str = "{} ({})".format(title_str, meta.units[0])
        
        return title_str

