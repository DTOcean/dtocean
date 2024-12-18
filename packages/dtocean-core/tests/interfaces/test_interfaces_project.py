
# pylint: disable=redefined-outer-name

import os
from copy import deepcopy
from pprint import pprint

import pytest
import pandas as pd

from dtocean_core.core import Core
from dtocean_core.menu import ProjectMenu
from dtocean_core.pipeline import Tree, _get_connector

dir_path = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
    
    return new_core


@pytest.fixture(scope="module") 
def wave_project(core):
    '''Share a Project object'''

    project_menu = ProjectMenu()
    var_tree = Tree()

    new_project = project_menu.new_project(core, "test wave")
        
    options_branch = var_tree.get_branch(core,
                                         new_project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, new_project)

    return new_project


def test_system_type_interface(core, wave_project):
        
    project_menu = ProjectMenu()
    var_tree = Tree()
    interface_name = "System Type Selection"
    
    project = deepcopy(wave_project)
    system_type_branch = var_tree.get_branch(core, project, interface_name)
                                                       
    can_execute = project_menu.is_executable(core, project, interface_name)
    
    if not can_execute:
        
        inputs = system_type_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "project")
    interface = connector.get_interface(core,
                                        project,
                                        interface_name)
                                        
    interface.connect()
                                        
    assert interface.data.output == True
    
    
def test_options_interface_sites(core, wave_project):
    
    project_menu = ProjectMenu()
    var_tree = Tree()
    interface_name = "Site and System Options"
    
    project = deepcopy(wave_project)
    project_menu.activate(core, project, interface_name)

    site_system_branch = var_tree.get_branch(core,
                                             project,
                                             interface_name)
    available_sites = site_system_branch.get_input_variable(
                                                    core,
                                                    project,
                                                    "hidden.available_sites")
    
    available_sites_dict = {"id": [1, 2],
                            "site_name": ["a", "b"],
                            "lease_area_proj4_string": ["a", "b"]
                            }
    available_sites_df = pd.DataFrame(available_sites_dict)
    
    available_sites.set_raw_interface(core, available_sites_df)
    available_sites.read(core, project)
                                                       
    can_execute = project_menu.is_executable(core, project, interface_name)
    
    if not can_execute:
        
        inputs = site_system_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "project")
    interface = connector.get_interface(core,
                                        project,
                                        interface_name)
                                        
    interface.connect()
                                        
    assert interface.data.site_names.equals(available_sites_df["site_name"])
    assert interface.data.corridor_selected == False
    assert interface.data.lease_selected == False


def test_options_interface_systems(core, wave_project):
    
    project_menu = ProjectMenu()
    var_tree = Tree()
    interface_name = "Site and System Options"
    
    project = deepcopy(wave_project)
    project_menu.activate(core, project, interface_name)

    site_system_branch = var_tree.get_branch(core,
                                             project,
                                             interface_name)
    available_systems = site_system_branch.get_input_variable(
                                                    core,
                                                    project,
                                                    "hidden.available_systems")
    
    
    available_systems_dict = {"id": [1, 2],
                              "description": ["a", "b"],
                              "device_type": ["a", "Wave Floating"]
                            }
    available_systems_df = pd.DataFrame(available_systems_dict)
    
    available_systems.set_raw_interface(core, available_systems_df)
    available_systems.read(core, project)
                                                       
    can_execute = project_menu.is_executable(core, project, interface_name)
    
    if not can_execute:
        
        inputs = site_system_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "project")
    interface = connector.get_interface(core,
                                        project,
                                        interface_name)
                                        
    interface.connect()
                                        
    assert interface.data.system_names.equals(pd.Series(["b"]))


def test_boundaries_interface(core, wave_project):
    
    project_menu = ProjectMenu()
    var_tree = Tree()
    interface_name = "Project Boundaries Interface"
    
    project = deepcopy(wave_project)
    project_menu.activate(core, project, interface_name)
    
    boundaries_branch = var_tree.get_branch(core, project, interface_name)
    
    projection = boundaries_branch.get_input_variable(core,
                                                      project,
                                                      "site.projection")
    projection.set_raw_interface(core, "UTM10")
    projection.read(core, project)
    
    can_execute = project_menu.is_executable(core, project, interface_name)
    
    if not can_execute:
        
        inputs = boundaries_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
    
    assert can_execute
