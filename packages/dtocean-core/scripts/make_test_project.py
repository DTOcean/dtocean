import platform
import shutil
import subprocess
import sys
from pathlib import Path

from dtocean_core.core import Core
from dtocean_core.menu import ModuleMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree
from dtocean_plugins.modules.base import ModuleInterface
from dtocean_plugins.themes.base import ThemeInterface

THIS_DIR = Path(__file__).parent.resolve()


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


def main():
    new_core = Core()

    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)

    socket = new_core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)

    project_title = "Test"

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    theme_menu = ThemeMenu()

    new_project = project_menu.new_project(new_core, project_title)
    var_tree = Tree()

    options_branch = var_tree.get_branch(
        new_core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        new_core, new_project, "device.system_type"
    )
    assert device_type is not None

    device_type.set_raw_interface(new_core, "Tidal Fixed")
    device_type.read(new_core, new_project)

    project_menu.initiate_pipeline(new_core, new_project)
    module_menu.activate(new_core, new_project, "Mock Module")
    theme_menu.activate(new_core, new_project, "Mock Theme")
    project_menu.initiate_dataflow(new_core, new_project)

    test_data_path = THIS_DIR.parent / "test_data"

    try:
        inputs_wp2_tidal = _make_test_data(test_data_path, "inputs_wp2_tidal")
        inputs_economics = _make_test_data(test_data_path, "inputs_economics")

        hydro_branch = var_tree.get_branch(new_core, new_project, "Mock Module")
        hydro_branch.read_test_data(new_core, new_project, inputs_wp2_tidal)

        eco_branch = var_tree.get_branch(new_core, new_project, "Mock Theme")
        eco_branch.read_test_data(new_core, new_project, inputs_economics)
    finally:
        _remove_test_data("inputs_wp2_tidal")
        _remove_test_data("inputs_economics")

    project_path = test_data_path / "projects"
    project_path.mkdir(exist_ok=True)
    project_file_name = (
        f"project-{platform.system().lower()}-{platform.python_version()}.dtop"
    )
    project_file_path = project_path / project_file_name

    new_core.dump_project(new_project, project_file_path)


def _make_test_data(data_dir: Path, name: str):
    # Pickle data files and move to test directory
    src_path_py = (data_dir / name).with_suffix(".py")
    result = subprocess.run(
        [sys.executable, src_path_py],
        capture_output=True,
        text=True,
    )

    if result.returncode:
        raise ChildProcessError(result.stderr)

    src_path_pkl = (data_dir / name).with_suffix(".pkl")
    dst_path_pkl = (THIS_DIR / name).with_suffix(".pkl")
    shutil.move(src_path_pkl, dst_path_pkl)

    return dst_path_pkl


def _remove_test_data(name: str):
    (THIS_DIR / name).with_suffix(".pkl").unlink()


if __name__ == "__main__":
    main()
