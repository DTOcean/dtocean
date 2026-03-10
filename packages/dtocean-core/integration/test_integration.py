from pathlib import Path

import pytest

from dtocean_core.core import Core
from dtocean_plugins.modules.base import ModuleInterface
from dtocean_plugins.themes.base import ThemeInterface

THIS_DIR = Path(__file__).parent


class MockModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Module"

    @classmethod
    def declare_weight(cls):
        return 998

    @classmethod
    def declare_inputs(cls):
        input_list = [
            "bathymetry.layers",
            "device.system_type",
            "device.power_rating",
            "device.cut_in_velocity",
            "device.turbine_interdistance",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = [
            "project.layout",
            "project.annual_energy",
            "project.number_of_devices",
        ]

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "bathymetry.layers",
            "dummy2": "device.cut_in_velocity",
            "dummy3": "device.system_type",
            "dummy4": "device.power_rating",
            "dummy5": "project.layout",
            "dummy6": "project.annual_energy",
            "dummy7": "project.number_of_devices",
            "dummy8": "device.turbine_interdistance",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


class MockTheme(ThemeInterface):
    @classmethod
    def get_name(cls):
        return "Mock Theme"

    @classmethod
    def declare_weight(cls):
        return 999

    @classmethod
    def declare_inputs(cls):
        input_list = ["project.discount_rate"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = ["project.capex_total"]

        return output_list

    @classmethod
    def declare_optional(cls):
        option_list = ["project.discount_rate"]

        return option_list

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "project.discount_rate",
            "dummy2": "project.capex_total",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


def get_projects_list():
    projects_dir = THIS_DIR.parent / "test_data" / "projects"
    if not projects_dir.exists():
        return []

    projects = [
        str(dtop) for dtop in projects_dir.iterdir() if dtop.suffix == ".dtop"
    ]

    return projects


PROJECTS = get_projects_list()


@pytest.mark.parametrize("project", PROJECTS)
def test_load_project(project):
    projects_dir = THIS_DIR.parent / "test_data" / "projects"
    if not projects_dir.exists():
        return

    core = Core()

    socket = core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)

    socket = core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)

    core.load_project(project)
