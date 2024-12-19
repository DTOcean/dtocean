import os
from copy import deepcopy

import matplotlib.pyplot as plt
import pytest
from shapely.geometry import Polygon

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree
from dtocean_plugins.modules.modules import ModuleInterface

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
        input_list = ["project.lease_area_entry_point"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        return None

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(self):
        id_map = {"dummy": "project.lease_area_entry_point"}

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        return


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    """Share a Core object"""

    new_core = Core()
    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)

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
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    project_menu.activate(core, new_project, "Site Boundary Selection")

    boundaries_branch = tree.get_branch(
        core, new_project, "Site Boundary Selection"
    )
    boundaries_branch.read_test_data(
        core, new_project, os.path.join(dir_path, "inputs_boundary.pkl")
    )
    project_menu._execute(
        core, new_project, "Site Boundary Selection", set_output_level=False
    )

    return new_project


def test_SiteBoundaryPlot_available(core, project, tree):
    project = deepcopy(project)

    boundaries_branch = tree.get_branch(
        core, project, "Site Boundary Selection"
    )

    site_boundary = boundaries_branch.get_input_variable(
        core, project, "hidden.site_boundaries"
    )
    result = site_boundary.get_available_plots(core, project)

    assert "Site Boundary" in result


def test_SiteBoundaryPlot(core, project, tree):
    project = deepcopy(project)

    boundaries_branch = tree.get_branch(
        core, project, "Site Boundary Selection"
    )

    site_boundary = boundaries_branch.get_input_variable(
        core, project, "hidden.site_boundaries"
    )
    site_boundary.plot(core, project, "Site Boundary")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_AllBoundaryPlot_available(core, project, tree):
    project = deepcopy(project)

    boundaries_branch = tree.get_branch(
        core, project, "Site Boundary Selection"
    )

    site_boundary = boundaries_branch.get_output_variable(
        core, project, "hidden.site_boundary"
    )
    result = site_boundary.get_available_plots(core, project)

    assert "All Boundaries" in result


def test_AllBoundaryPlot(core, project, tree):
    project = deepcopy(project)

    boundaries_branch = tree.get_branch(
        core, project, "Site Boundary Selection"
    )

    site_boundary = boundaries_branch.get_output_variable(
        core, project, "hidden.site_boundary"
    )
    site_boundary.plot(core, project, "All Boundaries")

    assert len(plt.get_fignums()) == 1

    plt.close("all")


def test_DesignBoundaryPlot_available(core, project, tree):
    project = deepcopy(project)

    module_menu = ModuleMenu()
    module_menu.activate(core, project, "Mock Module")

    project_menu = ProjectMenu()
    project_menu.initiate_dataflow(core, project)

    installation_branch = tree.get_branch(core, project, "Mock Module")
    installation_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_boundary.pkl")
    )
    installation_branch.read_auto(core, project)

    lease_entry = installation_branch.get_input_variable(
        core, project, "project.lease_area_entry_point"
    )

    result = lease_entry.get_available_plots(core, project)

    assert "Design Boundaries" in result


def test_DesignBoundaryPlot(core, project, tree):
    project = deepcopy(project)

    module_menu = ModuleMenu()
    module_menu.activate(core, project, "Mock Module")

    project_menu = ProjectMenu()
    project_menu.initiate_dataflow(core, project)

    installation_branch = tree.get_branch(core, project, "Mock Module")
    installation_branch.read_test_data(
        core, project, os.path.join(dir_path, "inputs_boundary.pkl")
    )
    installation_branch.read_auto(core, project)

    # Add nogo area
    nogo_area = {"test": Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])}
    core.add_datastate(
        project,
        identifiers=["farm.nogo_areas", "corridor.nogo_areas"],
        values=[nogo_area, nogo_area],
    )

    lease_entry = installation_branch.get_input_variable(
        core, project, "project.lease_area_entry_point"
    )
    lease_entry.plot(core, project, "Design Boundaries")

    assert len(plt.get_fignums()) == 1

    plt.close("all")
