from pathlib import Path

import pytest
from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree
from matplotlib import pyplot as plt

from dtocean_plugins.modules.base import ModuleInterface

DIR_PATH = Path(__file__).parent
ROOT_DIR_PATH = DIR_PATH.parents[2]
TEST_DATA_DIR_PATH = ROOT_DIR_PATH / "test_data" / "lcoe_pdf_plot"


class MockModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Module"

    @classmethod
    def declare_weight(cls):
        return 999

    @classmethod
    def declare_inputs(cls):
        input_list = [
            "project.economics_metrics",
            "project.lcoe_pdf",
            "project.confidence_density",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        return None

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "economics_metrics": "project.economics_metrics",
            "confidence_density": "project.confidence_density",
            "lcoe_pdf": "project.lcoe_pdf",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


@pytest.fixture()
def tree():
    """Share a Tree object"""

    new_tree = Tree()

    return new_tree


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture()
def core():
    """Share a Core object"""

    new_core = Core()
    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)

    return new_core


@pytest.fixture()
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

    return new_project


def test_LCOEPDFPlot_available(
    core,
    project,
    tree,
):
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    eco_metrics = mod_branch.get_input_variable(
        core,
        project,
        "project.economics_metrics",
    )
    assert eco_metrics is not None

    eco_metrics.set_file_interface(
        core,
        TEST_DATA_DIR_PATH / "eco_metrics.xlsx",
    )
    eco_metrics.read(core, project)

    lcoe_pdf = mod_branch.get_input_variable(
        core,
        project,
        "project.lcoe_pdf",
    )
    assert lcoe_pdf is not None

    lcoe_pdf.set_file_interface(
        core,
        TEST_DATA_DIR_PATH / "lcoe_pdf.nc",
    )
    lcoe_pdf.read(core, project)

    confidence_density = mod_branch.get_input_variable(
        core,
        project,
        "project.confidence_density",
    )
    assert confidence_density is not None

    confidence_density.set_raw_interface(core, 1.40122390504e-07)
    confidence_density.read(core, project)

    result = lcoe_pdf.get_available_plots(core, project)

    assert "LCOE PDF Analysis" in result


def test_LCOEPDFPlot(
    core,
    project,
    tree,
):
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)
    eco_metrics = mod_branch.get_input_variable(
        core,
        project,
        "project.economics_metrics",
    )
    assert eco_metrics is not None

    eco_metrics.set_file_interface(
        core,
        TEST_DATA_DIR_PATH / "eco_metrics.xlsx",
    )
    eco_metrics.read(core, project)

    lcoe_pdf = mod_branch.get_input_variable(
        core,
        project,
        "project.lcoe_pdf",
    )
    assert lcoe_pdf is not None

    lcoe_pdf.set_file_interface(
        core,
        TEST_DATA_DIR_PATH / "lcoe_pdf.nc",
    )
    lcoe_pdf.read(core, project)

    confidence_density = mod_branch.get_input_variable(
        core,
        project,
        "project.confidence_density",
    )
    assert confidence_density is not None

    confidence_density.set_raw_interface(core, 1.40122390504e-07)
    confidence_density.read(core, project)

    lcoe_pdf.plot(core, project, "LCOE PDF Analysis")

    assert len(plt.get_fignums()) == 1
    plt.close("all")
