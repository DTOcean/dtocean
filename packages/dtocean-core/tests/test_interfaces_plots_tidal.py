
import os
from copy import deepcopy

import pytest
import matplotlib.pyplot as plt

from dtocean_core.core import Core
from dtocean_core.interfaces import ModuleInterface
from dtocean_core.menu import ModuleMenu, ProjectMenu 
from dtocean_core.pipeline import Tree

dir_path = os.path.dirname(__file__)


class MockModule(ModuleInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Module"
        
    @classmethod         
    def declare_weight(cls):
        
        return 999

    @classmethod
    def declare_inputs(cls):
        
        input_list = ["device.turbine_performance",
                      "device.cut_in_velocity",
                      "device.cut_out_velocity",
                      "farm.tidal_series"]
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        return None
        
    @classmethod
    def declare_optional(cls):
        
        return None
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy": "device.turbine_performance",
                  "dummy2": "device.cut_in_velocity",
                  "dummy3": "device.cut_out_velocity",
                  "dummy4": "farm.tidal_series"}
                  
        return id_map
                 
    def connect(self, debug_entry=False,
                      export_data=True):
        
        return


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)
    
    return new_core


@pytest.fixture(scope="module")
def tree():
    '''Share a Tree object'''
    
    new_tree = Tree()
        
    return new_tree


@pytest.fixture(scope="module")
def project(core, tree):
    '''Share a Project object'''

    project_title = "Test"  
    
    project_menu = ProjectMenu()
    
    new_project = project_menu.new_project(core, project_title)
    
    options_branch = tree.get_branch(core,
                                     new_project,
                                     "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)
    
    project_menu.initiate_pipeline(core, new_project)
             
    return new_project


def test_TidalPowerPerformancePlot_available(core, project, tree):
    
    project = deepcopy(project) 
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    
    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    ct_curve = hydro_branch.get_input_variable(core,
                                               project,
                                               "device.turbine_performance")
    result = ct_curve.get_available_plots(core, project)
    
    assert 'Tidal Power Performance' in result


def test_TidalPowerPerformancePlot(core, project, tree):
    
    project = deepcopy(project) 
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    
    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    ct_curve = hydro_branch.get_input_variable(core,
                                               project,
                                               "device.turbine_performance")
    ct_curve.plot(core, project, 'Tidal Power Performance')
    
    assert len(plt.get_fignums()) == 1
    
    plt.close("all")
    
    
def test_TidalVelocityPlot_available(core, project, tree):
    
    project = deepcopy(project) 
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    
    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    hydro_branch = tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    currents = hydro_branch.get_input_variable(core,
                                               project,
                                               "farm.tidal_series")
    result = currents.get_available_plots(core, project)
    
    assert "Tidal Currents" in result
    

def test_TidalVelocityPlot(core, project, tree):

    project = deepcopy(project) 
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    
    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    hydro_branch = tree.get_branch(core, project, mod_name)
    hydro_branch.read_test_data(core,
                                project,
                                os.path.join(dir_path,
                                             "inputs_wp2_tidal.pkl"))
                                                       
    currents = hydro_branch.get_input_variable(core,
                                               project,
                                               "farm.tidal_series")
    currents.plot(core, project, "Tidal Currents")
    
    assert len(plt.get_fignums()) == 1
    
    plt.close("all")
