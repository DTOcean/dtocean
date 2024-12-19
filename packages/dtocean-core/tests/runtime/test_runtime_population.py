from copy import deepcopy

import pytest

from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu
from dtocean_core.pipeline import InputVariable, Tree


# Test for a database connection
def _is_port_open():
    data_menu = DataMenu()

    return data_menu.check_database("local")


port_open = _is_port_open()


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    """Share a Core object"""

    new_core = Core()

    return new_core


@pytest.fixture(scope="module")
def tree():
    """Share a Tree object"""

    new_tree = Tree()

    return new_tree


@pytest.fixture(scope="module")
def project(core, tree):
    """Share a Project object"""

    project_title = "Test"

    project_menu = ProjectMenu()

    new_project = project_menu.new_project(core, project_title)

    options_branch = tree.get_branch(core, new_project, "System Type Selection")
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )
    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, new_project)

    return new_project


@pytest.mark.skipif(not port_open, reason="can't connect to DB")
def test_get_query_interface(core, project, tree):
    mod_name = "Site and System Options"
    var_id = "hidden.available_sites"

    data_menu = DataMenu()
    project_menu = ProjectMenu()

    project = deepcopy(project)

    data_menu.select_database(project, "local")
    project_menu.initiate_pipeline(core, project)

    options_branch = tree.get_branch(core, project, mod_name)
    new_var = options_branch.get_input_variable(core, project, var_id)

    result = new_var._get_query_interface(core, project)

    assert result is not None


@pytest.mark.skipif(not port_open, reason="can't connect to DB")
@pytest.mark.xfail
def test_filter_interface(core, project, tree):
    project = deepcopy(project)

    data_menu = DataMenu()
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    tree = Tree()

    data_menu.select_database(project, "local")
    project_menu.initiate_pipeline(core, project)
    project_menu.initiate_options(core, project)

    filter_branch = tree.get_branch(
        core, project, "Database Filtering Interface"
    )
    new_var = filter_branch.get_input_variable(
        core, project, "device.selected_name"
    )

    assert isinstance(new_var, InputVariable)
    new_var.set_raw_interface(core, "ExampleWaveDevice")
    new_var.read(core, project)

    module_menu.activate(core, project, "Hydrodynamics")

    project_menu.initiate_filter(core, project)

    assert True


@pytest.mark.skipif(not port_open, reason="can't connect to DB")
@pytest.mark.xfail
def test_connect_TableDataColumn(core, project, tree):
    var_id = "hidden.available_sites"

    project = deepcopy(project)

    data_menu = DataMenu()
    project_menu = ProjectMenu()

    data_menu.select_database(project, "local")
    project_menu.initiate_pipeline(core, project)

    proj_branch = tree.get_branch(core, project, "Site and System Options")
    var = proj_branch.get_input_variable(core, project, var_id)
    inputs = proj_branch.get_input_status(core, project)

    assert inputs[var_id] == "satisfied"
    assert "ExampleSite" in var.get_value(core, project)["site_name"].values


def test_SimpleListColumn_available(core, project):
    test = InputVariable("hidden.available_sites")
    result = test._find_providing_interface(core, "AutoQuery")

    assert result is not None
    assert "AutoQuery" in result.get_name()


# @pytest.mark.skipif(port_open == False,
#                    reason="can't connect to DB")
# def test_connect_SimpleColumn(core, project, tree):
#
#    var_id = "device.power_rating"
#
#    project = deepcopy(project)
#
#    data_menu = DataMenu()
#    module_menu = ModuleMenu()
#    project_menu = ProjectMenu()
#
#    tree = Tree()
#    data_menu.select_database(project, "local")
#
#    project_menu.initiate_pipeline(core, project)
#    project_menu.initiate_options(core, project)
#
#    filter_branch = tree.get_branch(core,
#                                    project,
#                                    'Database Filtering Interface')
#    new_var = filter_branch.get_input_variable(core,
#                                               project,
#                                               "device.selected_name")
#    new_var.set_raw_interface(core, "Pelamis")
#    new_var.read(core, project)
#
#    project_menu.initiate_filter(core, project)
#
#    module_menu.activate(core, project, "Hydrodynamics")
#
#    project_menu.initiate_dataflow(core, project)
#
#    hydro_branch = tree.get_branch(core, project, "Hydrodynamics")
#    hydro_branch.read_auto(core, project, log_exceptions=False)
#    var = hydro_branch.get_input_variable(core, project, var_id)
#
#    inputs = hydro_branch.get_input_status(core, project)
#
#    assert inputs[var_id] == 'satisfied'
#    assert np.isclose(var.get_value(core, project), 0.0)

# def test_SimpleDictColumns_available(core, project):
#
#    test = InputVariable("device.models_dict")
#    result = test._get_auto_queries(core)
#
#    assert 'AutoQuery' in result[0]

# @pytest.mark.skipif(port_open == False,
#                    reason="Can't connect to DB")
# def test_connect_SimpleDictColumns(core, project):
#
#    mod_name = "Project Data Interface"
#    var_id = "device.models_dict"
#
#    proj_branch = var_tree.get_branch(project, mod_name)
#    var = proj_branch.get_input_variable(core, project, var_id)
#
#    var.read_auto(core, project, log_exceptions=False)
#
#    inputs = proj_branch.get_input_status(core, project)
#
#    assert inputs[var_id] == 'satisfied'
#    assert 'Tide Turner TM' in var.get_value(core, project).values()

# @pytest.mark.skipif(port_open == False,
#                    reason="Can't connect to DB")
# def test_LeaseArea_available(core, project, module_menu):
#
#    module_menu.activate(core, project, "Hydrodynamics")
#
#    test = InputVariable("site.lease_boundary")
#    result = test._get_auto_queries(core)
#
#    assert 'AutoQuery' in result[0]

# @pytest.mark.skipif(port_open == False,
#                    reason="Can't connect to DB")
# def test_connect_LeaseArea(core, project, module_menu):
#
#    mod_name = "Hydrodynamics"
#    var_id = "site.lease_boundary"
#
#    module_menu.activate(core, project, mod_name)
#
#    hydro_branch = var_tree.get_branch(project, mod_name)
#    var = hydro_branch.get_input_variable(core, project, var_id)
#
#    var.read_auto(core, project, log_exceptions=False)
#
#    with pytest.warns(None) as record:
#
#        inputs = hydro_branch.get_input_status(core, project)
#        lease_area = var.get_value(core)
#
#    assert len(record) == 0
#    assert inputs[var_id] == 'satisfied'
#    assert not lease_area
