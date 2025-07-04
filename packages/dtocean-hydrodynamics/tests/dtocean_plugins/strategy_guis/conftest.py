import pytest

pytest.importorskip("dtocean_app")

from dtocean_app.core import GUICore  # noqa: E402
from dtocean_app.shell import Shell  # noqa: E402
from dtocean_core.menu import ModuleMenu, ProjectMenu  # noqa: E402
from dtocean_core.pipeline import Tree  # noqa: E402

from dtocean_plugins.modules.base import ModuleInterface  # noqa: E402


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
            "device.turbine_performance",
            "device.cut_in_velocity",
            "device.system_type",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = None

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "device.turbine_performance",
            "dummy2": "device.cut_in_velocity",
            "dummy3": "device.system_type",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        return


@pytest.fixture()
def core():
    core = GUICore()
    core._create_data_catalog()
    core._create_control()
    core._create_sockets()
    core._init_plots()

    socket = core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)

    return core


@pytest.fixture
def project(core):
    project_title = "Test"

    project_menu = ProjectMenu()
    var_tree = Tree()

    project = project_menu.new_project(core, project_title)

    options_branch = var_tree.get_branch(core, project, "System Type Selection")
    device_type = options_branch.get_input_variable(
        core, project, "device.system_type"
    )
    assert device_type is not None

    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, project)

    project_menu.initiate_pipeline(core, project)

    return project


@pytest.fixture
def mock_shell(core, project):
    module_menu = ModuleMenu()
    module_menu.activate(core, project, MockModule.get_name())

    shell = Shell(core)
    shell.project = project

    return shell


@pytest.fixture
def hydro_shell(core, project):
    module_menu = ModuleMenu()
    module_menu.activate(core, project, "Hydrodynamics")

    shell = Shell(core)
    shell.project = project

    return shell


@pytest.fixture()
def config():
    return {
        "base_penalty": 2.0,
        "clean_existing_dir": True,
        "max_evals": 2,
        "max_resample_factor": 5,
        "max_simulations": 10,
        "maximise": True,
        "min_evals": 3,
        "n_threads": 7,
        "objective": "project.annual_energy",
        "parameters": {
            "delta_col": {
                "range": {
                    "max_multiplier": 2.0,
                    "min_multiplier": 1.0,
                    "type": "multiplier",
                    "variable": "device.minimum_distance_y",
                }
            },
            "delta_row": {
                "range": {
                    "max_multiplier": 2.0,
                    "min_multiplier": 1.0,
                    "type": "multiplier",
                    "variable": "device.minimum_distance_x",
                }
            },
            "grid_orientation": {
                "range": {"max": 90.0, "min": -90.0, "type": "fixed"}
            },
            "n_nodes": {
                "range": {"max": 20, "min": 1, "type": "fixed"},
                "x0": 15,
            },
            "t1": {"range": {"max": 1.0, "min": 0.0, "type": "fixed"}},
            "t2": {"range": {"max": 1.0, "min": 0.0, "type": "fixed"}},
        },
        "popsize": 4,
        "results_params": [
            "project.number_of_devices",
            "project.annual_energy",
            "project.q_factor",
            "project.capex_total",
            "project.capex_breakdown",
            "project.lifetime_opex_mean",
            "project.lifetime_cost_mean",
            "project.lifetime_energy_mean",
            "project.lcoe_mean",
        ],
        "root_project_path": None,
        "timeout": 12,
        "tolfun": 1.0,
        "worker_dir": "mock",
    }
