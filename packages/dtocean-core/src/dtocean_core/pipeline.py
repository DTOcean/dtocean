
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

import sys
import logging
from pickle import load as load_pkl

import matplotlib.pyplot as plt

from .core import Connector

# Set up logging
module_logger = logging.getLogger(__name__)


class Tree(object):

    '''Interface class for the pipeline at the tree level'''
        
    def get_available_branches(self, core, project, hub_names=None):
        
        hub_branch_names = self._get_branch_names(core, project, hub_names)
        all_branch_names = [y for x in hub_branch_names.itervalues()
                                                                for y in x]
        
        return all_branch_names
        
    def get_branch(self, core, project, branch_name):
        
        available_branches = self.get_available_branches(core, project)
        
        if branch_name not in available_branches:
            
            errStr = ("Branch name {} not in list of available "
                      "branches.").format(branch_name)
            raise ValueError(errStr)
            
        if available_branches.count(branch_name) > 1:
            
            errStr = ("Branch name {} is not unique.").format(branch_name)
            raise ValueError(errStr)
            
        # Find the branch and hub
        hub_branch_names = self._get_branch_names(core, project)       
        result = None
            
        for hub_name, branch_names in hub_branch_names.iteritems():
            
            if branch_name in branch_names:
                
                new_branch = Branch(hub_name, branch_name)
                result = new_branch
                break
            
        if result is None:
            
            errStr = "Branch not found. Evil forces are at play!"
            raise RuntimeError(errStr)
            
        return result
            
    def read(self, core,
                   project,
                   hub_names=None,
                   overwrite=False,
                   skip_unavailable=True,
                   set_auto=False,
                   log_exceptions=False):                      
         
        branch_names = self.get_available_branches(core, project, hub_names)
        branch_list = [self.get_branch(core, project, name) for
                                                        name in branch_names]
            
        # Work out the unique inputs across all branches.
        unique_branch_inputs = set()
        variables = []
        
        for branch in branch_list:

            branch_input_status = branch.get_input_status(core, project)
            
            if skip_unavailable:            
                branch_inputs = [k for k, v in branch_input_status.iteritems()
                                                     if "unavailable" not in v]
            else:
                branch_inputs = branch_input_status.keys()

            unique_branch_inputs.update(branch_inputs)
            
        for variable_id in unique_branch_inputs:
            
            new_variable = InputVariable(variable_id)
            variables.append(new_variable)
            
        _read_variables(core,
                        project,
                        variables,
                        overwrite,
                        set_auto,
                        log_exceptions)

        return
    
    def read_auto(self, core,
                        project,
                        hub_names=None,
                        overwrite=False,
                        skip_unavailable=True,
                        log_exceptions=True):
                            
        """Calls read with set_auto set to True."""
                            
        self.read(core,
                  project,
                  hub_names,
                  overwrite,
                  skip_unavailable,
                  True,
                  log_exceptions)
                                 
        return
        
    def _get_branch_names(self, core, project, hub_names=None):

        all_branch_names = {}
        
        if hub_names is None:
            simulation = project.get_simulation()
            hub_names = simulation.get_hub_ids()
        
        for hub_name in hub_names:
            
            connector = _get_connector(project, hub_name)
            branch_names = connector.get_active_interface_names(core,
                                                                project)
            all_branch_names[hub_name] = branch_names

        return all_branch_names


class Branch(object):

    '''Interface class for the pipeline at the branch level'''

    def __init__(self, hub_name, name):
        
        self._hub_name = hub_name
        self._name = name

        return
        
    def get_inputs(self, core, project):
        
        connector = _get_connector(project, self._hub_name)
        input_declaration = connector.get_interface_inputs(core,
                                                           project,
                                                           self._name)
        
        return input_declaration
            
    def get_outputs(self, core, project):
        
        connector = _get_connector(project, self._hub_name)
        output_declaration = connector.get_interface_outputs(core,
                                                             project,
                                                             self._name)
        
        return output_declaration
        
    def get_input_status(self, core, project, variable=None):
        
        connector = _get_connector(project, self._hub_name)

        branch_status = connector.get_interface_inputs_status(project,
                                                              self._name)
        
        if variable is not None:
            
            if not isinstance(variable, InputVariable):
                
                errStr = ("Argument 'variable' only accepts InputVariable "
                          "objects.")
                raise ValueError(errStr)
                
            if variable._id not in branch_status:
                
                errStr = ("Variable {} is not an input to branch "
                          "{}.").format(variable._id, self._name)
                raise ValueError(errStr)
            
            variable_status = branch_status[variable._id]
            
            return  variable_status
            
        else:
            
            return branch_status

    def get_output_status(self, core, project, variable=None):

        connector = _get_connector(project, self._hub_name)

        branch_status = connector.get_interface_outputs_status(project,
                                                               self._name)
        
        if variable is not None:
            
            if not isinstance(variable, OutputVariable):
                
                errStr = ("Argument 'variable' only accepts OutputVariable "
                          "objects.")
                raise ValueError(errStr)
                
            if variable._id not in branch_status:
                
                errStr = ("Variable {} is not an output of branch "
                          "{}.").format(variable._id, self._name)
                raise ValueError(errStr)
            
            variable_status = branch_status[variable._id]
            
            return  variable_status
            
        else:
            
            return branch_status
            
    def get_input_variable(self, core,
                                 project,
                                 variable_id,
                                 skip_missing=False):
        
        core.check_valid_variable(variable_id)
        
        # Check that the inputs exist in the tree
        module_inputs = self.get_input_status(core,
                                              project)

        if variable_id not in module_inputs.keys():
            
            msgStr = ("Variable {} is not an input to branch "
                      "{}.").format(variable_id, self._name)
            
            if skip_missing:
                module_logger.debug(msgStr)                
                return None

            raise KeyError(msgStr)

        new_variable = InputVariable(variable_id)

        return new_variable

    def get_output_variable(self, core, project, variable_id):
        
        core.check_valid_variable(variable_id)
        
        # Check that the inputs exist in the tree
        module_inputs = self.get_output_status(core,
                                               project)

        if variable_id not in module_inputs.keys():

            errStr = ("Variable {} is not an output of branch "
                      "{}.").format(variable_id, self._name)

            raise KeyError(errStr)

        new_variable = OutputVariable(variable_id)

        return new_variable
            
    def inspect(self, core, project, scope=None):
        
        connector = _get_connector(project, self._hub_name)

        # Can't inspect unless the interface has executed.
        if not connector.is_interface_completed(core,
                                                project,
                                                self._name): return
        
        output_level = "{} {}".format(self._name.lower(),
                                      core._markers["output"])
        register_level = "{} {}".format(self._name.lower(),
                                         core._markers["register"])

        # Call inspect level on the output level, but force the inspection
        # level to the theme scope.
        core.inspect_level(project,
                           output_level,
                           inspection_level=register_level,
                           update_status=False)
                                        
        # Unmask the levels relevant to the chosen theme output scope.
        set_output_scope(core,
                         project,
                         scope)
        
        return
        
    def reset(self, core, project):
        
        connector = _get_connector(project, self._hub_name)

        # Can't reset unless the interface has executed.
        if not connector.is_interface_completed(core,
                                                project,
                                                self._name): return

        registered_level = "{} {}".format(self._name.lower(),
                                          core._markers["register"])
        core.reset_level(project,
                         registered_level,
                         force_scheduled="themes",
                         skip_missing=True)
        
        return
        
    def read(self, core,
                   project,
                   overwrite=False,
                   skip_unavailable=True,
                   set_auto=False,
                   log_exceptions=False):
        
        # Control bulk reads for post project hubs
        if (self._hub_name in ["modules", "themes"] and 
            not core.has_data(project, "hidden.dataflow_active")):
            
            errStr = ("Bulk data can not be loaded until the dataflow has "
                      "been initiated.")
            raise RuntimeError(errStr)

        branch_input_status = self.get_input_status(core,
                                                    project)
                                                            
        variables = []
        
        for identifier, status in branch_input_status.iteritems():
            
            if skip_unavailable and "unavailable" in status: continue
            
            var = self.get_input_variable(core,
                                          project,
                                          identifier)
                
            variables.append(var)

        _read_variables(core,
                        project,
                        variables,
                        overwrite,
                        set_auto,
                        log_exceptions)
                
        return
        
    def read_auto(self, core,
                        project,
                        overwrite=False,
                        skip_unavailable=True,
                        log_exceptions=True):
                            
        """Calls read with set_auto set to True."""
                            
        self.read(core,
                  project,
                  overwrite,
                  skip_unavailable,
                  True,
                  log_exceptions)
                                 
        return
        
    def read_test_data(self, core,
                             project,
                             data_path,
                             overwrite=False,
                             skip_unavailable=True,
                             skip_missing=True):
                                         
        with open(data_path, "r") as dataf:
            test_data = load_pkl(dataf)
                
        variables = []
                
        for variable_id, value in test_data.iteritems():
                        
            variable = self.get_input_variable(core,
                                               project,
                                               variable_id,
                                               skip_missing=skip_missing)
                                               
            if skip_unavailable:
                
                 status = self.get_input_status(core, project, variable)
                 
                 if "unavailable" in status: continue
            
            # Loop if no variable is found
            if variable is None: continue
            
            variable.set_raw_interface(core, value)
            variables.append(variable)
        
        _read_variables(core,
                        project,
                        variables,
                        overwrite=overwrite)
                
        return
        

class Variable(object):

    '''Interface class for the pipeline at the variable level'''
    
    def __init__(self, identifier):

        self._id = identifier
        self._interface = None
        
        return

    def get_metadata(self, core):

        # Get the meta data from the core data catalog
        metadata = core.get_metadata(self._id)

        return metadata
        
    def has_value(self, core, project):
        
        result = core.has_data(project, self._id)
        
        return result

    def get_value(self, core, project):

        data_value = core.get_data_value(project, self._id)

        return data_value
        
    def get_file_output_interfaces(self, core, project, include_auto=False):
        
        kargs = {"core": core,
                 "project": project,
                 "interface_name": "FileOutputInterface",
                 "dict_value_attr": "get_valid_extensions"}
        if include_auto: kargs["auto_interface_name"] = "AutoFileOutput"
                
        provider_names = self._get_receivers(**kargs)

        return provider_names
        
    def get_available_plots(self, core, project, include_auto=False):
        
        args = [core, project, "PlotInterface"]
        if include_auto: args.append("AutoPlot")
        
        active_receivers = self._get_receivers(*args)
        active_receivers.sort()

        return active_receivers
        
    def write_file(self, core,
                         project,
                         file_path,
                         interface_name=None):
        
        interface = self._get_receiving_interface(core,
                                                  project,
                                                  "FileOutputInterface",
                                                  "AutoFileOutput",
                                                  interface_name)

        if interface is None or not core.has_data(project, self._id): return
        
        interface.set_file_path(file_path)
        self._write_interface(core, project, interface)
        
        return
        
    def plot(self, core, project, plot_name=None):
        
        interface = self._get_receiving_interface(core,
                                                  project,
                                                  "PlotInterface",
                                                  "AutoPlot",
                                                  plot_name)

        if interface is None or not core.has_data(project, self._id): return
                                                                        
        self._write_interface(core, project, interface)
        plt.show(block=False)
        
        return
        
    def _get_named_interface(self, core,
                                   socket_cls_name,
                                   interface_name,
                                   allow_missing=False):
                                  
        socket = core.socket_map[socket_cls_name]
            
        interface_name_map = socket.get_interface_names()
        
        if interface_name in interface_name_map:
            
            interface_cls_name = interface_name_map[interface_name]
            interface = socket.get_interface_object(interface_cls_name)
            
        elif allow_missing:
            
            interface = None
            
        else:
            
            errStr = ("Interface {} not found for socket "
                      "class {}").format(interface_name, socket_cls_name)
            raise ValueError(errStr)

        return interface

    def _find_providing_interface(self, core,
                                        socket_cls_name,
                                        allow_missing=False,
                                        allow_multiple=False):
        
        interfaces = self._find_providing_interfaces(core, socket_cls_name)
        interface = self._select_interface(interfaces,
                                           socket_cls_name,
                                           allow_missing,
                                           allow_multiple)

        return interface
        
    def _find_receiving_interface(self, core,
                                        socket_cls_name,
                                        allow_missing=False,
                                        allow_multiple=False):
                                  
        
        interfaces = self._find_receiving_interfaces(core, socket_cls_name)
        interface = self._select_interface(interfaces,
                                           socket_cls_name,
                                           allow_missing,
                                           allow_multiple)

        return interface

    def _find_providing_interfaces(self, core, socket_cls_name):
        
        socket = core.socket_map[socket_cls_name]
        providers = socket.get_providing_interfaces(self._id)
                
        interfaces = self._get_socket_interfaces(socket, providers)

        return interfaces
        
    def _find_receiving_interfaces(self, core, socket_cls_name):

        socket = core.socket_map[socket_cls_name]
        receivers = socket.get_receiving_interfaces(self._id)
        interfaces = self._get_socket_interfaces(socket, receivers)

        return interfaces
        
    def _get_providers(self, core,
                             interface_name,
                             auto_interface_name=None,
                             dict_value_attr=None):
        
        providers = self._find_providing_interfaces(core, interface_name)
        
        provider_names = [x.get_name() for x in providers]
                          
        if dict_value_attr is None:
            
            result = provider_names
            
        else:
            
            provider_values = []

            for provider in providers:
                
                provider_attr = getattr(provider, dict_value_attr)
                provider_values.append(provider_attr())
                
            result = {name: value for name, value in zip(provider_names,
                                                         provider_values)}
                
        if auto_interface_name is None: return result
        
        providers = self._find_providing_interfaces(core, auto_interface_name)
        
        auto_provider_names = [x.get_name() for x in providers]
                               
        if dict_value_attr is None:
            
            result.extend(auto_provider_names)
            
        else:
            
            provider_values = []

            for provider in providers:
                
                provider_attr = getattr(provider, dict_value_attr)
                provider_values.append(provider_attr())
                
            auto_provider_dict = {name: value for name, value in
                                                       zip(auto_provider_names,
                                                           provider_values)}
                                                           
            result.update(auto_provider_dict)
                                       
        return result
        
    def _get_receivers(self, core,
                             project,
                             interface_name,
                             auto_interface_name=None,
                             dict_value_attr=None):
        
        receivers = self._find_receiving_interfaces(core, interface_name)
        
        active_receivers = []
        
        for interface in receivers:
            if core.can_load_interface(project, interface, self._id):
                active_receivers.append(interface)
                
        active_receiver_names = [x.get_name() for x in active_receivers]
                
        if dict_value_attr is None:
            
            result = active_receiver_names
            
        else:
            
            receiver_values = []

            for receiver in active_receivers:
                
                receiver_attr = getattr(receiver, dict_value_attr)
                receiver_values.append(receiver_attr())
                
            result = {name: value for name, value in zip(active_receiver_names,
                                                         receiver_values)}
                
        if auto_interface_name is None: return result
        
        receivers = self._find_receiving_interfaces(core, auto_interface_name)
                
        for interface in receivers:
            if core.can_load_interface(project, interface, self._id):
                active_receivers.append(interface)
                
        active_receiver_names = [x.get_name() for x in active_receivers]
                
        if dict_value_attr is None:
            
            result.extend(active_receiver_names)
            
        else:
                        
            receiver_values = []

            for receiver in active_receivers:
                
                receiver_attr = getattr(receiver, dict_value_attr)
                receiver_values.append(receiver_attr())
                
            auto_receiver_dict = {name: value for name, value in
                                                  zip(active_receiver_names,
                                                      receiver_values)}
                                                           
            result.update(auto_receiver_dict)
                                       
        return result
    
    def _get_providing_interface(self, core,
                                       super_interface_name,
                                       auto_interface_name=None,
                                       interface_name=None):
        
        interface = None
                
        if interface_name is not None:
            
            if interface_name in self._get_providers(core,
                                                     super_interface_name):
        
                interface = self._get_named_interface(core,
                                                      super_interface_name,
                                                      interface_name)
            
            elif (auto_interface_name is not None and
                  interface_name in self._get_providers(core,
                                                        auto_interface_name)):
                
                interface = self._get_named_interface(core,
                                                      auto_interface_name,
                                                      interface_name)
            
            else:
                
                errStr = ("Interface {} is not available for "
                          "variable {}.").format(interface_name,
                                                 self._id)
                raise ValueError(errStr)
        
                                            
        if interface is None and auto_interface_name is not None:
            
            interface = self._find_providing_interface(core,
                                                       auto_interface_name,
                                                       allow_missing=True)
                                                       
        if interface is None:
            
            interface = self._find_providing_interface(core,
                                                       super_interface_name,
                                                       allow_missing=True,
                                                       allow_multiple=True)
                                                       
        return interface
        
    def _get_receiving_interface(self, core,
                                       project,
                                       super_interface_name,
                                       auto_interface_name=None,
                                       interface_name=None):
        
        interface = None
                
        if interface_name is not None:
            
            if interface_name in self._get_receivers(core,
                                                     project,
                                                     super_interface_name):
        
                interface = self._get_named_interface(core,
                                                      super_interface_name,
                                                      interface_name)
            
            elif (auto_interface_name is not None and
                  interface_name in self._get_receivers(core,
                                                        project,
                                                        auto_interface_name)):
                
                interface = self._get_named_interface(core,
                                                      auto_interface_name,
                                                      interface_name)
            
            else:
                
                errStr = ("Interface {} is not available for "
                          "variable {}.").format(interface_name,
                                                 self._id)
                raise ValueError(errStr)
                                            
        if interface is None and auto_interface_name is not None:
            
            interface = self._find_receiving_interface(core,
                                                       auto_interface_name,
                                                       allow_missing=True)
            
        if interface is None:
            
            interface = self._find_receiving_interface(core,
                                                       super_interface_name,
                                                       allow_missing=True,
                                                       allow_multiple=True)
            
        return interface
        
    def _select_interface(self, interfaces,
                                socket_cls_name,
                                allow_missing=False,
                                allow_multiple=False):
        
        if len(interfaces) == 0 and allow_missing:
                
            return None
                
        elif len(interfaces) == 0:
                
            errStr = ("No interfaces found of type {} for variable "
                      "{}.").format(socket_cls_name, self._id)
            raise IOError(errStr)
                
        elif not allow_multiple and len(interfaces) > 1:
            
            interface_strs = [x.get_name() for x in interfaces]
            infoStr = ", ".join(interface_strs)
            errStr = ("Multiple interfaces of type {} found for variable {}: "
                      "{}.").format(socket_cls_name, self._id, infoStr)
            raise ValueError(errStr)
            
        interface = interfaces[0]
            
        return interface
        
    def _write_interface(self, core, project, interface):
        
        if not core.can_load_interface(project, interface):
            
            errStr = ("The inputs to interface {} are not "
                      "satisfied.").format(interface.get_name())
            raise ValueError(errStr)
        
        interface = core.load_interface(project, interface)
        core.connect_interface(project, interface)

        return
    
    @classmethod
    def _get_socket_interfaces(cls, socket,
                                    interface_cls_names):
        
        interfaces = []
        
        for interface_cls_name in interface_cls_names:
    
            interface = socket.get_interface_object(interface_cls_name)
            interfaces.append(interface)
            
        return interfaces


class InputVariable(Variable):

    '''Class to indentify a particular input varible in the pipeline and set
    interfaces for it.
    '''

    def get_interface(self):
        
        return self._interface

    def get_file_input_interfaces(self, core, include_auto=False):
        
        kargs = {"core": core,
                 "interface_name": "FileInputInterface",
                 "dict_value_attr": "get_valid_extensions"}
        if include_auto: kargs["auto_interface_name"] = "AutoFileInput"
                
        provider_names = self._get_providers(**kargs)

        return provider_names

    def get_raw_interfaces(self, core, include_auto=False):
        
        args = [core, "RawInterface"]
        if include_auto: args.append("AutoRaw")

        provider_names = self._get_providers(*args)

        return provider_names

    def get_query_interfaces(self, core, include_auto=False):
        
        args = [core, "QueryInterface"]
        if include_auto: args.append("AutoQuery")

        provider_names = self._get_providers()

        return provider_names
        
    def set_raw_interface(self, core,
                                value,
                                interface_name=None):
                                    
        interface = self._get_providing_interface(core,
                                                  "RawInterface",
                                                  "AutoRaw",
                                                  interface_name)
        
        if interface is None:
            
            errStr = ("No raw input interface found for "
                      "variable ").format()
            raise RuntimeError(errStr)

        interface.set_variables({self._id: value})
        self._interface = interface

        return

    def set_file_interface(self, core,
                                 file_path,
                                 interface_name=None):
                                     
        interface = self._get_providing_interface(core,
                                                  "FileInputInterface",
                                                  "AutoFileInput",
                                                  interface_name)
                                                
        if interface is None:
            
            errStr = ("No file input interface found for "
                      "variable ").format()
            raise RuntimeError(errStr)
        
        interface.set_file_path(file_path)
        self._interface = interface

        return

    def set_query_interface(self, core,
                                  project,
                                  interface_name=None):
                                      
        # Check the status of the database.
        if project.get_database_credentials() is None:
            
            errStr = "No database credentials found"
            raise RuntimeError(errStr)
                
        interface = self._get_query_interface(core,
                                              project,
                                              interface_name)
                                                
        if interface is None:
            
            errStr = ("No database access interface found for "
                      "variable ").format()
            raise RuntimeError(errStr)
        
        self._interface = interface

        return

    def read(self, core,
                   project,
                   overwrite=True,
                   set_auto=False,
                   log_exceptions=False):

        '''Read data from the variable and inject the data into the active data
        state'''
        
        _read_variables(core,
                        project,
                        [self],
                        overwrite,
                        set_auto,
                        log_exceptions)

        return
        
    def read_auto(self, core,
                        project,
                        overwrite=True,
                        log_exceptions=True):
                            
        """Calls read with set_auto set to True."""
                            
        self.read(core,
                  project,
                  overwrite,
                  True,
                  log_exceptions)
                                 
        return
        
    def read_file(self, core,
                        project,
                        file_path,
                        file_interface=None,
                        overwrite=True):
                            
        self.set_file_interface(core,
                                file_path,
                                file_interface)
                                
        self.read(core,
                  project,
                  overwrite)
                  
        return
    
    def _get_query_interface(self, core,
                                   project,
                                   interface_name=None):
                                       
        interface = self._get_providing_interface(
                                                core,
                                                "QueryInterface",
                                                "AutoQuery",
                                                interface_name)
                                                
        if interface is not None:
            if core.can_load_interface(project, interface):
                interface = core.load_interface(project, interface)
            else:
                interface = None
        
        if interface is None: return None
        
        metadata = self.get_metadata(core)
            
        # Allow the auto_only meta data variable to restrict execution of the
        # auto recovery.
        if (not metadata.auto_only or
            metadata.auto_only and core.has_data(project, metadata.auto_only)):
                                
            result = interface
        
        else:
            
            result = None

        return result


class OutputVariable(Variable):

    '''Class to to indentify for a particular output varible in the pipeline
    '''



### MODULE FUNCTIONS

def set_output_scope(core,
                     project,
                     scope=None,
                     sim_index=None,
                     sim_title=None,
                     default_scope="global"):
    
    simulation = project.get_simulation(sim_index, sim_title)
    
    if scope is None:
        scope = simulation.output_scope
    
    if scope is None:
        scope = default_scope
                                          
    # Mask either global or local theme results
    if scope == "local":
        unmask_marker = core._markers["local"]
    elif scope == "global":
        unmask_marker = core._markers["global"]
    else:
        errStr = "Theme output scope '{}' is not valid".format(scope)
        raise ValueError(errStr)
        
    # Record the scope
    simulation.output_scope = scope
        
    # Get the level root from the inspection level
    interface_name = simulation.level_map[simulation.get_inspection_level()]
    
    if interface_name is None: return
    
    level_root = simulation.level_map[
                                    simulation.get_inspection_level()].lower()
                                   
    unmask_level = "{} {}".format(level_root,
                                  unmask_marker)

    # Mask all the local and global output levels
    core.mask_states(project,
                     simulation,
                     core._markers["local"],
                     no_merge=True,
                     update_status=False)
    core.mask_states(project,
                     simulation,
                     core._markers["global"],
                     no_merge=True,
                     update_status=False)
                                    
    # Unmask the levels relevant to the branch and scope.
    core.unmask_states(project,
                       simulation,
                       unmask_level,
                       update_status=False)
                       
    core.set_interface_status(project, simulation)
    
    return

def _get_connector(project, hub_name):
    
    simulation = project.get_simulation()
    hub_names = simulation.get_hub_ids()
        
    if hub_name not in hub_names:
        
        errStr = ('Hub name "{}" is not contained in the '
                  'project.').format(hub_name)
        raise ValueError(errStr)
        
    result = Connector(hub_name)
    
    return result
    
def _can_read_value(core,
                    project,
                    variable_id,
                    overwrite=True):
                        
    result = True
    
    if not overwrite and core.has_data(project, variable_id):
                
        result = False
        
    return result

def _get_read_values(core,
                     project,
                     interface,
                     variable_ids):

    if interface is None:

        errStr = 'No interface set. Aborting.'
        raise ValueError(errStr)

    variable_values = []

    # Test that the variables are in the data catalog
    for variable_id in variable_ids: core.check_valid_variable(variable_id)
    
    # Get the value for the variables from the interface
    interface = core.connect_interface(project, interface)
        
    for variable_id in variable_ids:

        value = interface.get_data(variable_id)
        variable_values.append(value)
    
    return variable_values
    
def _read_variables(core,
                    project,
                    variables,
                    overwrite=True,
                    set_auto=False,
                    log_exceptions=False):

    '''Read data from the given list of variables and inject the data 
    into the active data state'''
    
    results = {}
    
    while variables:
        
        variable = variables.pop()
        
        if not _can_read_value(core,
                               project,
                               variable._id,
                               overwrite):

            continue
       
        if set_auto:
            
            if project.get_database_credentials() is None: continue
            
            interface = variable._get_query_interface(core,
                                                      project)
        
            if interface is None: continue
                
        else:
            
            interface = variable._interface
        
        fetch_var_ids = [variable._id]
        all_var_ids = [x._id for x in variables]
        
        # Check if additional variables are provided by the same interface
        needed = set(all_var_ids)
        provided = set(interface.declare_outputs())
        
        add_var_ids = needed & provided
        
        for add_var_id in add_var_ids:
            
            # Remove the variable from the variables list
            var_dex = all_var_ids.index(add_var_id)
            add_var = variables.pop(var_dex)
            
            if add_var._interface is None:
                add_var_interface_name = None
            else:
                add_var_interface_name = add_var._interface.get_name()
            
            variable_interface_name = interface.get_name()
            
            # If this is happening without auto_queries and different
            # interfaces were set issue a warning
            if (not set_auto and
                add_var_interface_name is not None and
                variable_interface_name != add_var_interface_name):      
            
                msg = ("Variable {} is being retrieved from interface {} "
                       "rather than {}").format(add_var_id,
                                                add_var_interface_name,
                                                variable_interface_name)
                module_logger.warning(msg)
            
            if not _can_read_value(core,
                                   project,
                                   add_var_id,
                                   overwrite):
    
                continue
            
            fetch_var_ids.append(add_var_id)
        
        varsStr = ", ".join(fetch_var_ids)
        msg = "Reading variables {}".format(varsStr)
        module_logger.debug(msg)
        
        if log_exceptions:
            
            try:
                
                values = _get_read_values(core,
                                          project,
                                          interface,
                                          fetch_var_ids)
                
            except:
                
                e = sys.exc_info()[0]
                msg = ("Reading variables {} generated error: "
                       "{}").format(varsStr, e)
                logging.exception(msg)
                
                continue
            
        else:
        
            values = _get_read_values(core,
                                      project,
                                      interface,
                                      fetch_var_ids)
                                  
        for var_id, value in zip(fetch_var_ids, values):
        
            results[var_id] = value
            
    if not results: return

    # Add data to the cores active data state
    core.add_datastate(project,
                       identifiers=results.keys(),
                       values=results.values(),
                       log_exceptions=log_exceptions)

    return
