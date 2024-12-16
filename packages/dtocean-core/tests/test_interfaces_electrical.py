
import os
import pkg_resources
from copy import deepcopy
from pprint import pprint

import pytest

from polite_config.paths import Directory
from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree, _get_connector
from dtocean_core.utils.version import Version

# Check for module and version
pkg_title = "dtocean-electrical"
pkg_import = "dtocean_electrical"
major_version = 2

pytest.importorskip(pkg_import)
version = pkg_resources.get_distribution(pkg_title).version
pytestmark = pytest.mark.skipif(Version(version).major != major_version,
                                reason="module has incorrect major version")

dir_path = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()
    
    return new_core


@pytest.fixture(scope="module")
def var_tree():

    return Tree()


@pytest.fixture(scope="module")
def module_menu(core):
    '''Share a ModuleMenu object'''  
       
    return ModuleMenu()


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def tidal_project(core, var_tree):
    '''Share a Project object'''

    project_menu = ProjectMenu()
    
    new_project = project_menu.new_project(core, "test tidal")
    
    options_branch = var_tree.get_branch(core,
                                         new_project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)
        
    project_menu.initiate_pipeline(core, new_project)

    return new_project


def test_electrical_inputs(module_menu, core, tidal_project, var_tree):
        
    mod_name = "Electrical Sub-Systems"
#    project_menu = ProjectMenu()
    data_menu = DataMenu()
    project_menu = ProjectMenu()
    
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    data_menu.load_data(core, project)
    
    electrical_branch = var_tree.get_branch(core, project, mod_name)
   
    
    electrical_input_status = electrical_branch.get_input_status(core, 
                                                                 project)
                                                    
    assert "component.transformers" in electrical_input_status


def test_get_electrical_interface(module_menu, core, tidal_project, var_tree):
    
    mod_name = "Electrical Sub-Systems"
#    project_menu = ProjectMenu()
    
    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    electrical_branch = var_tree.get_branch(core, project, mod_name)
    electrical_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp3.pkl"))
    electrical_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = electrical_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    assert interface.data.voltage is not None


def test_electrical_interface_entry(module_menu,
                                    core,
                                    tidal_project,
                                    var_tree,
                                    mocker,
                                    tmpdir):
    
    # Make a source directory with some files
    config_tmpdir = tmpdir.mkdir("config")
    mock_dir = Directory(str(config_tmpdir))
        
    mocker.patch('dtocean_core.interfaces.electrical.UserDataDirectory',
                 return_value=mock_dir,
                 autospec=True)
        
    mod_name = "Electrical Sub-Systems"
    #    project_menu = ProjectMenu()

    project_menu = ProjectMenu()
    project = deepcopy(tidal_project) 
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)
    
    electrical_branch = var_tree.get_branch(core, project, mod_name)
    electrical_branch.read_test_data(core,
                                     project,
                                     os.path.join(dir_path,
                                                  "inputs_wp3.pkl"))
    electrical_branch.read_auto(core, project)
    
    can_execute = module_menu.is_executable(core, project,  mod_name)
    
    if not can_execute:
        
        inputs = electrical_branch.get_input_status(core, project)
        pprint(inputs)
        assert can_execute
        
    connector = _get_connector(project, "modules")
    interface = connector.get_interface(core,
                                        project,
                                        mod_name)
                                        
    interface.connect(debug_entry=True,
                      export_data=True)
    
    debugdir = config_tmpdir.join("..", "debug")
    
    assert len(debugdir.listdir()) == 1
