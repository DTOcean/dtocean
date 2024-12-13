
import os
from copy import deepcopy

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from dtocean_core.core import Core
from dtocean_core.interfaces import ModuleInterface
from dtocean_core.interfaces.plots_array_layout import clockwise
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
        
        input_list = ['project.layout',
                      'site.lease_boundary',
                      'corridor.landing_point']
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        output_list = ['project.cable_routes',
                       'project.substation_layout',
                       'project.foundations_component_data']
        
        return output_list
        
    @classmethod
    def declare_optional(cls):
        
        return None
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy": "project.layout",
                  "dummy2": "site.lease_boundary",
                  "dummy3": "project.cable_routes",
                  "dummy4": "corridor.landing_point",
                  "dummy5": "project.substation_layout",
                  "dummy6": "project.foundations_component_data"}
                  
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


def test_ArrayLeasePlot_available(core, project, tree):

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path, "inputs_wp3.pkl"))

    # Force addition of lease area
    lease_area = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    core.add_datastate(project,
                       identifiers=["site.lease_boundary"],
                       values=[lease_area])


    layout = mod_branch.get_input_variable(core, project, "project.layout")
    result = layout.get_available_plots(core, project)

    assert "Lease Area Array Layout" in result


def test_ArrayLeasePlot(core, project, tree):

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path, "inputs_wp3.pkl"))

    # Force addition of lease area and padding
    lease_area = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    padding = 1.
    core.add_datastate(project,
                       identifiers=["site.lease_boundary",
                                    "options.boundary_padding"],
                       values=[lease_area,
                               padding])

    layout = mod_branch.get_input_variable(core, project, "project.layout")
    layout.plot(core, project, "Lease Area Array Layout")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_ArrayLeasePlotNumbers_available(core, project, tree):

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path, "inputs_wp3.pkl"))

    # Force addition of lease area
    lease_area = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    core.add_datastate(project,
                       identifiers=["site.lease_boundary"],
                       values=[lease_area])


    layout = mod_branch.get_input_variable(core, project, "project.layout")
    result = layout.get_available_plots(core, project)

    assert "Lease Area Array Layout (With Device Numbers)" in result


def test_ArrayLeasePlotNumbers(core, project, tree):

    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core,
                              project,
                              os.path.join(dir_path, "inputs_wp3.pkl"))

    # Force addition of lease area
    lease_area = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    core.add_datastate(project,
                       identifiers=["site.lease_boundary"],
                       values=[lease_area])

    layout = mod_branch.get_input_variable(core, project, "project.layout")
    layout.plot(core, project, "Lease Area Array Layout (With Device Numbers)")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_ArrayCablesPlot_available(core, project, tree):
    
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    # Need to provide these inputs:
    #   "site.lease_boundary",
    #   "corridor.landing_point",
    #   "project.layout",
    #   "project.cable_routes",
    #   "project.substation_layout"
    
    lease_area = Polygon([(0, 0), (20, 0), (20, 50), (0, 50)])
    landing_point = [10, 0]
    layout = {"device001": (10, 40)}
    substation = {"array": [10, 20]}
    
    cable_dict = {"Marker": [0, 0, 0, 1, 1, 1],#
                  "UTM X": [10, 10, 10, 10, 10, 10],
                  "UTM Y": [40, 30, 20, 20, 10, 0],
                  "Key Identifier": [None, None, None, None, None, None],
                  "Depth": [None, None, None, None, None, None],
                  "Burial Depth": [None, None, None, None, None, None],
                  "Sediment": [None, None, None, None, None, None],
                  "Split Pipe": [None, None, None, None, None, None]}
    cable_df = pd.DataFrame(cable_dict)
    
    core.add_datastate(project,
                       identifiers=["site.lease_boundary",
                                    "corridor.landing_point",
                                    "project.layout",
                                    "project.substation_layout",
                                    "project.cable_routes"],
                       values=[lease_area,
                               landing_point,
                               layout,
                               substation,
                               cable_df])

    mod_branch = tree.get_branch(core, project, mod_name)
    cables = mod_branch.get_output_variable(core,
                                            project,
                                            "project.cable_routes")
    result = cables.get_available_plots(core, project)

    assert "Array Cable Layout" in result


def test_ArrayCablesPlot(core, project, tree):
    
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    # Need to provide these inputs:
    #   "site.lease_boundary",
    #   "corridor.landing_point",
    #   "project.layout",
    #   "project.cable_routes",
    #   "project.substation_layout"
    
    lease_area = Polygon([(0, 0), (20, 0), (20, 50), (0, 50)])
    landing_point = [10, 0]
    layout = {"device001": (10, 40)}
    substation = {"array": [10, 20]}
    
    cable_dict = {"Marker": [0, 0, 0, 1, 1, 1],
                  "UTM X": [10, 10, 10, 10, 10, 10],
                  "UTM Y": [40, 30, 20, 20, 10, 0],
                  "Key Identifier": [None, None, None, None, None, None],
                  "Depth": [None, None, None, None, None, None],
                  "Burial Depth": [None, None, None, None, None, None],
                  "Sediment": [None, None, None, None, None, None],
                  "Split Pipe": [None, None, None, None, None, None]}
    cable_df = pd.DataFrame(cable_dict)
    
    core.add_datastate(project,
                       identifiers=["site.lease_boundary",
                                    "corridor.landing_point",
                                    "project.layout",
                                    "project.substation_layout",
                                    "project.cable_routes"],
                       values=[lease_area,
                               landing_point,
                               layout,
                               substation,
                               cable_df])

    mod_branch = tree.get_branch(core, project, mod_name)
    cables = mod_branch.get_output_variable(core,
                                            project,
                                            "project.cable_routes")
    cables.plot(core, project, "Array Cable Layout")

    assert len(plt.get_fignums()) == 1

    plt.close("all")
    

def test_ArrayFoundationsPlot_available(core, project, tree):
    
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    # Need to provide these inputs:
    #   "site.lease_boundary",
    #   "project.layout",
    #   "project.substation_layout"
    #   "project.foundations_component_data"
    
    lease_area = Polygon([(0, 0), (20, 0), (20, 50), (0, 50)])
    layout = {"device001": (10, 40)}
    substation = {"array": [10, 20]}
    
    foundations_dict = {u'Depth': {0: -38.520000000000003,
                                   1: -40.299999999999997,
                                   2: -36.780000000000001,
                                   8: -37.850000000000001},
                        u'Dry Mass': {0: 107506.9289256667,
                                      1: 53351.541402463197,
                                      2: 126780.5181144721,
                                      8: 6435.3313852360807},
                        u'Grout Type': {0: u'n/a',
                                        1: u'n/a',
                                        2: u'n/a',
                                        8: u'grout'},
                        u'Grout Volume': {0: 0.0,
                                          1: 0.0,
                                          2: 0.0,
                                          8: 1.065569984623332},
                        u'Height': {0: 1.409402628668293,
                                    1: 0.92718879062712711,
                                    2: 1.4890425199298569,
                                    8: 19.0},
                        u'Installation Depth': {0: np.nan,
                                                1: np.nan,
                                                2: np.nan,
                                                8: 19.0},
                        u'Length': {0: 5.637610514673173,
                                    1: 3.708755162508508,
                                    2: 5.9561700797194286,
                                    8: 0.81299999999999994},
                        u'Marker': {0: 0,
                                    1: 1,
                                    2: 2,
                                    8: 8},
                        u'Sub-Type': {0: u'concrete/steel composite structure',
                                      1: u'concrete/steel composite structure',
                                      2: u'concrete/steel composite structure',
                                      8: u'pipe pile'},
                        u'Type': {0: u'gravity',
                                  1: u'gravity',
                                  2: u'gravity',
                                  8: u'pile'},
                        u'UTM X': {0: 5,
                                   1: 10,
                                   2: 15,
                                   8: 10},
                        u'UTM Y': {0: 40,
                                   1: 45,
                                   2: 40,
                                   8: 20},
                        u'Width': {0: 5.637610514673173,
                                   1: 3.708755162508508,
                                   2: 5.9561700797194286,
                                   8: 0.81299999999999994}}
                       
    foundations_df = pd.DataFrame(foundations_dict)
    
    core.add_datastate(project,
                       identifiers=["site.lease_boundary",
                                    "project.layout",
                                    "project.substation_layout",
                                    "project.foundations_component_data"],
                       values=[lease_area,
                               layout,
                               substation,
                               foundations_df])

    mod_branch = tree.get_branch(core, project, mod_name)
    foundations = mod_branch.get_output_variable(
                                        core,
                                        project,
                                        "project.foundations_component_data")
    result = foundations.get_available_plots(core, project)

    assert "Array Foundations Layout" in result


@pytest.mark.parametrize("soiltype", [
    'shallowfoundation',
    'gravity',
    'pile',
    'suctioncaisson',
    'directembedment',
    'drag'
])
def test_ArrayFoundationsPlot(core, project, tree, soiltype):
    
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    # Need to provide these inputs:
    #   "site.lease_boundary",
    #   "project.layout",
    #   "project.substation_layout"
    #   "project.foundations_component_data"
    
    lease_area = Polygon([(0, 0), (20, 0), (20, 50), (0, 50)])
    layout = {"device001": (10, 40)}
    substation = {"array": [10, 20]}
    
    foundations_dict = {u'Depth': {0: -38.520000000000003,
                                   1: -40.299999999999997,
                                   2: -36.780000000000001,
                                   8: -37.850000000000001},
                        u'Dry Mass': {0: 107506.9289256667,
                                      1: 53351.541402463197,
                                      2: 126780.5181144721,
                                      8: 6435.3313852360807},
                        u'Grout Type': {0: u'n/a',
                                        1: u'n/a',
                                        2: u'n/a',
                                        8: u'grout'},
                        u'Grout Volume': {0: 0.0,
                                          1: 0.0,
                                          2: 0.0,
                                          8: 1.065569984623332},
                        u'Height': {0: 1.409402628668293,
                                    1: 0.92718879062712711,
                                    2: 1.4890425199298569,
                                    8: 19.0},
                        u'Installation Depth': {0: np.nan,
                                                1: np.nan,
                                                2: np.nan,
                                                8: 19.0},
                        u'Length': {0: 5.637610514673173,
                                    1: 3.708755162508508,
                                    2: 5.9561700797194286,
                                    8: 0.81299999999999994},
                        u'Marker': {0: 0,
                                    1: 1,
                                    2: 2,
                                    8: 8},
                        u'Sub-Type': {0: u'concrete/steel composite structure',
                                      1: u'concrete/steel composite structure',
                                      2: u'concrete/steel composite structure',
                                      8: u'something'},
                        u'Type': {0: u'gravity',
                                  1: u'gravity',
                                  2: u'gravity',
                                  8: soiltype},
                        u'UTM X': {0: 5,
                                   1: 10,
                                   2: 15,
                                   8: 10},
                        u'UTM Y': {0: 40,
                                   1: 45,
                                   2: 40,
                                   8: 20},
                        u'Width': {0: 5.637610514673173,
                                   1: 3.708755162508508,
                                   2: 5.9561700797194286,
                                   8: 0.81299999999999994}}
                       
    foundations_df = pd.DataFrame(foundations_dict)
    
    core.add_datastate(project,
                       identifiers=["site.lease_boundary",
                                    "project.layout",
                                    "project.substation_layout",
                                    "project.foundations_component_data"],
                       values=[lease_area,
                               layout,
                               substation,
                               foundations_df])

    mod_branch = tree.get_branch(core, project, mod_name)
    foundations = mod_branch.get_output_variable(
                                        core,
                                        project,
                                        "project.foundations_component_data")
    foundations.plot(core, project, "Array Foundations Layout")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


@pytest.mark.parametrize("x, y, expected",
                         [([0, 0, 1, 1, 0], [0, 1, 1, 0, 0], True),
                          ([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], False)])
def test_clockwise(x, y, expected):
        
    result = clockwise(x, y)
    
    assert result is expected
