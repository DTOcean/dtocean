import datetime as dt
import os
from copy import deepcopy

import matplotlib.pyplot as plt
import pandas as pd
import pytest

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
        input_list = None

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = [
            "project.installation_plan",
            "project.install_support_structure_dates",
            "project.install_devices_dates",
            "project.install_dynamic_cable_dates",
            "project.install_export_cable_dates",
            "project.install_array_cable_dates",
            "project.install_surface_piercing_substation_dates",
            "project.install_subsea_collection_point_dates",
            "project.install_cable_protection_dates",
            "project.install_driven_piles_dates",
            "project.install_direct_embedment_dates",
            "project.install_gravity_based_dates",
            "project.install_pile_anchor_dates",
            "project.install_drag_embedment_dates",
            "project.install_suction_embedment_dates",
            "project.device_phase_installation_times",
            "project.electrical_phase_installation_times",
            "project.mooring_phase_installation_times",
        ]

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(self):
        id_map = {
            "dummy": "project.installation_plan",
            "dummy1": "project.install_support_structure_dates",
            "dummy2": "project.install_devices_dates",
            "dummy3": "project.install_dynamic_cable_dates",
            "dummy4": "project.install_export_cable_dates",
            "dummy5": "project.install_array_cable_dates",
            "dummy6": "project.install_surface_piercing_substation_dates",
            "dummy7": "project.install_subsea_collection_point_dates",
            "dummy8": "project.install_cable_protection_dates",
            "dummy9": "project.install_driven_piles_dates",
            "dummy10": "project.install_direct_embedment_dates",
            "dummy11": "project.install_gravity_based_dates",
            "dummy12": "project.install_pile_anchor_dates",
            "dummy13": "project.install_drag_embedment_dates",
            "dummy14": "project.install_suction_embedment_dates",
            "dummy15": "project.device_phase_installation_times",
            "dummy16": "project.electrical_phase_installation_times",
            "dummy17": "project.mooring_phase_installation_times",
        }

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

    return new_project


def test_InstallationGanttChartPlot_available(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)

    plan = [
        "Installation of support structure",
        "Installation of driven piles anchors/foundations",
        "Installation of direct-embedment anchors/foundations",
        "Installation of gravity based anchors/foundations",
        "Installation of pile anchor anchors/foundations",
        "Installation of drag-embedment anchors/foundations",
        "Installation of suction-embedment anchors/foundations",
        "Installation of collection point (surface piercing)",
        "Installation of collection point (seabed)",
        "Installation of dynamic cables",
        "Installation of static export cables",
        "Installation of static array cables",
        "Installation of cable protection",
        "Installation of devices",
    ]
    install_support_structure_dates = {
        "Start": dt.datetime(
            2000,
            6,
            25,
            4,
            55,
            31,
        ),
        "End": dt.datetime(2000, 7, 29, 3, 24, 19),
        "Depart": dt.datetime(2000, 7, 25, 7, 55, 31),
    }
    install_devices_dates = {
        "Start": dt.datetime(
            2000,
            6,
            25,
            4,
            55,
            31,
        ),
        "End": dt.datetime(2000, 7, 29, 3, 24, 19),
        "Depart": dt.datetime(2000, 7, 25, 7, 55, 31),
    }
    install_dynamic_cable_dates = {
        "Start": dt.datetime(2000, 5, 2, 19, 11, 47),
        "End": dt.datetime(2000, 6, 18, 19, 12, 9),
        "Depart": dt.datetime(2000, 6, 14, 15, 11, 47),
    }
    install_export_cable_dates = {
        "Start": dt.datetime(2000, 5, 2, 19, 11, 47),
        "End": dt.datetime(2000, 6, 18, 19, 12, 9),
        "Depart": dt.datetime(2000, 6, 14, 15, 11, 47),
    }
    install_array_cable_dates = {
        "Start": dt.datetime(2000, 5, 2, 21, 48, 59),
        "End": dt.datetime(2000, 6, 19, 0, 55, 31),
        "Depart": dt.datetime(2000, 6, 14, 15, 48, 59),
    }
    install_surface_piercing_substation_dates = {
        "Start": dt.datetime(2000, 1, 5, 1, 0),
        "End": dt.datetime(2000, 4, 30, 17, 42, 6),
        "Depart": dt.datetime(2000, 4, 26, 7, 0),
    }
    install_subsea_collection_point_dates = {
        "Start": dt.datetime(2000, 1, 5, 1, 0),
        "End": dt.datetime(2000, 4, 30, 17, 42, 6),
        "Depart": dt.datetime(2000, 4, 26, 7, 0),
    }
    install_cable_protection_dates = {
        "Start": dt.datetime(2000, 1, 5, 1, 0),
        "End": dt.datetime(2000, 4, 30, 17, 42, 6),
        "Depart": dt.datetime(2000, 4, 26, 7, 0),
    }
    install_driven_piles_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_direct_embedment_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_gravity_based_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_pile_anchor_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_drag_embedment_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_suction_embedment_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_device_times = pd.DataFrame(
        {
            "Preparation": {0: 148.0, 1: 100},
            "Operations": {0: 32.0, 1: 30},
            "Transit": {0: 59.480022782839399, 1: 60},
            "Component": {0: "Device", 1: "Support Structure"},
            "Waiting": {0: 0, 1: 0},
        }
    )
    install_electrical_times = pd.DataFrame(
        {
            "Preparation": {0: 49.49, 1: 52.11, 2: 97.0, 3: 90, 4: 10},
            "Operations": {0: 7.48, 1: 12.72, 2: 21.0, 3: 20, 4: 50},
            "Transit": {0: 92.51, 1: 92.38, 2: 85.70, 3: 80, 4: 90},
            "Component": {
                0: "Export Cables",
                1: "Inter-Array Cables",
                2: "Collection Points",
                3: "Dynamic Cables",
                4: "External Cable Protection",
            },
            "Waiting": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }
    )
    install_mooring_times = pd.DataFrame(
        {
            "Preparation": {
                0: 53.0,
                1: 53.0,
                2: 53.0,
                3: 53.0,
                4: 53.0,
                5: 53.0,
            },
            "Operations": {
                0: 83.00,
                1: 83.00,
                2: 83.00,
                3: 83.00,
                4: 83.00,
                5: 83.00,
            },
            "Transit": {
                0: 75.06,
                1: 75.06,
                2: 75.06,
                3: 75.06,
                4: 75.06,
                5: 75.06,
            },
            "Component": {
                0: "Driven Piles",
                1: "Direct-Embedment Anchors",
                2: "Gravity Based Foundations",
                3: "Pile Anchors",
                4: "Drag-Embedment Anchors",
                5: "Suction-Caisson Anchors",
            },
            "Waiting": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }
    )

    identifiers = [
        "project.installation_plan",
        "project.install_support_structure_dates",
        "project.install_devices_dates",
        "project.install_dynamic_cable_dates",
        "project.install_export_cable_dates",
        "project.install_array_cable_dates",
        "project.install_surface_piercing_substation_dates",
        "project.install_subsea_collection_point_dates",
        "project.install_cable_protection_dates",
        "project.install_driven_piles_dates",
        "project.install_direct_embedment_dates",
        "project.install_gravity_based_dates",
        "project.install_pile_anchor_dates",
        "project.install_drag_embedment_dates",
        "project.install_suction_embedment_dates",
        "project.device_phase_installation_times",
        "project.electrical_phase_installation_times",
        "project.mooring_phase_installation_times",
    ]

    # Force addition of variables
    core.add_datastate(
        project,
        identifiers=identifiers,
        values=[
            plan,
            install_support_structure_dates,
            install_devices_dates,
            install_dynamic_cable_dates,
            install_export_cable_dates,
            install_array_cable_dates,
            install_surface_piercing_substation_dates,
            install_subsea_collection_point_dates,
            install_cable_protection_dates,
            install_driven_piles_dates,
            install_direct_embedment_dates,
            install_gravity_based_dates,
            install_pile_anchor_dates,
            install_drag_embedment_dates,
            install_suction_embedment_dates,
            install_device_times,
            install_electrical_times,
            install_mooring_times,
        ],
    )

    gantt = mod_branch.get_output_variable(
        core, project, "project.installation_plan"
    )
    result = gantt.get_available_plots(core, project)

    assert "Installation Gantt Chart" in result


def test_InstallationGanttChartPlot(core, project, tree):
    project = deepcopy(project)
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()

    mod_name = "Mock Module"
    module_menu.activate(core, project, mod_name)
    project_menu.initiate_dataflow(core, project)

    mod_branch = tree.get_branch(core, project, mod_name)

    plan = [
        "Installation of support structure",
        "Installation of driven piles anchors/foundations",
        "Installation of mooring systems with direct-embedment anchors",
        "Installation of gravity based foundations",
        "Installation of mooring systems with pile anchors",
        "Installation of mooring systems with drag-embedment anchors",
        "Installation of mooring systems with suction-embedment anchors",
        "Installation of collection point (surface piercing)",
        "Installation of collection point (seabed)",
        "Installation of dynamic cables",
        "Installation of static export cables",
        "Installation of static array cables",
        "Installation of external cable protection",
        "Installation of devices",
    ]
    install_support_structure_dates = {
        "Start": dt.datetime(
            2000,
            6,
            25,
            4,
            55,
            31,
        ),
        "End": dt.datetime(2000, 7, 29, 3, 24, 19),
        "Depart": dt.datetime(2000, 7, 25, 7, 55, 31),
    }
    install_devices_dates = {
        "Start": dt.datetime(
            2000,
            6,
            25,
            4,
            55,
            31,
        ),
        "End": dt.datetime(2000, 7, 29, 3, 24, 19),
        "Depart": dt.datetime(2000, 7, 25, 7, 55, 31),
    }
    install_dynamic_cable_dates = {
        "Start": dt.datetime(2000, 5, 2, 19, 11, 47),
        "End": dt.datetime(2000, 6, 18, 19, 12, 9),
        "Depart": dt.datetime(2000, 6, 14, 15, 11, 47),
    }
    install_export_cable_dates = {
        "Start": dt.datetime(2000, 5, 2, 19, 11, 47),
        "End": dt.datetime(2000, 6, 18, 19, 12, 9),
        "Depart": dt.datetime(2000, 6, 14, 15, 11, 47),
    }
    install_array_cable_dates = {
        "Start": dt.datetime(2000, 5, 2, 21, 48, 59),
        "End": dt.datetime(2000, 6, 19, 0, 55, 31),
        "Depart": dt.datetime(2000, 6, 14, 15, 48, 59),
    }
    install_surface_piercing_substation_dates = {
        "Start": dt.datetime(2000, 1, 5, 1, 0),
        "End": dt.datetime(2000, 4, 30, 17, 42, 6),
        "Depart": dt.datetime(2000, 4, 26, 7, 0),
    }
    install_subsea_collection_point_dates = {
        "Start": dt.datetime(2000, 1, 5, 1, 0),
        "End": dt.datetime(2000, 4, 30, 17, 42, 6),
        "Depart": dt.datetime(2000, 4, 26, 7, 0),
    }
    install_cable_protection_dates = {
        "Start": dt.datetime(2000, 1, 5, 1, 0),
        "End": dt.datetime(2000, 4, 30, 17, 42, 6),
        "Depart": dt.datetime(2000, 4, 26, 7, 0),
    }
    install_driven_piles_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_direct_embedment_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_gravity_based_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_pile_anchor_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_drag_embedment_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_suction_embedment_dates = {
        "Start": dt.datetime(2000, 1, 3, 5, 0),
        "End": dt.datetime(2000, 2, 11, 5, 4, 21),
        "Depart": dt.datetime(2000, 2, 4, 15, 0),
    }
    install_device_times = pd.DataFrame(
        {
            "Preparation": {0: 148.0, 1: 100},
            "Operations": {0: 32.0, 1: 30},
            "Transit": {0: 59.480022782839399, 1: 60},
            "Component": {0: "Device", 1: "Support Structure"},
            "Waiting": {0: 0, 1: 0},
        }
    )
    install_electrical_times = pd.DataFrame(
        {
            "Preparation": {0: 49.49, 1: 52.11, 2: 97.0, 3: 90, 4: 10},
            "Operations": {0: 7.48, 1: 12.72, 2: 21.0, 3: 20, 4: 50},
            "Transit": {0: 92.51, 1: 92.38, 2: 85.70, 3: 80, 4: 90},
            "Component": {
                0: "Export Cables",
                1: "Inter-Array Cables",
                2: "Collection Points",
                3: "Dynamic Cables",
                4: "External Cable Protection",
            },
            "Waiting": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        }
    )
    install_mooring_times = pd.DataFrame(
        {
            "Preparation": {
                0: 53.0,
                1: 53.0,
                2: 53.0,
                3: 53.0,
                4: 53.0,
                5: 53.0,
            },
            "Operations": {
                0: 83.00,
                1: 83.00,
                2: 83.00,
                3: 83.00,
                4: 83.00,
                5: 83.00,
            },
            "Transit": {
                0: 75.06,
                1: 75.06,
                2: 75.06,
                3: 75.06,
                4: 75.06,
                5: 75.06,
            },
            "Component": {
                0: "Driven Piles",
                1: "Direct-Embedment Anchors",
                2: "Gravity Based Foundations",
                3: "Pile Anchors",
                4: "Drag-Embedment Anchors",
                5: "Suction-Caisson Anchors",
            },
            "Waiting": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }
    )

    identifiers = [
        "project.installation_plan",
        "project.install_support_structure_dates",
        "project.install_devices_dates",
        "project.install_dynamic_cable_dates",
        "project.install_export_cable_dates",
        "project.install_array_cable_dates",
        "project.install_surface_piercing_substation_dates",
        "project.install_subsea_collection_point_dates",
        "project.install_cable_protection_dates",
        "project.install_driven_piles_dates",
        "project.install_direct_embedment_dates",
        "project.install_gravity_based_dates",
        "project.install_pile_anchor_dates",
        "project.install_drag_embedment_dates",
        "project.install_suction_embedment_dates",
        "project.device_phase_installation_times",
        "project.electrical_phase_installation_times",
        "project.mooring_phase_installation_times",
    ]

    # Force addition of variables
    core.add_datastate(
        project,
        identifiers=identifiers,
        values=[
            plan,
            install_support_structure_dates,
            install_devices_dates,
            install_dynamic_cable_dates,
            install_export_cable_dates,
            install_array_cable_dates,
            install_surface_piercing_substation_dates,
            install_subsea_collection_point_dates,
            install_cable_protection_dates,
            install_driven_piles_dates,
            install_direct_embedment_dates,
            install_gravity_based_dates,
            install_pile_anchor_dates,
            install_drag_embedment_dates,
            install_suction_embedment_dates,
            install_device_times,
            install_electrical_times,
            install_mooring_times,
        ],
    )

    gantt = mod_branch.get_output_variable(
        core, project, "project.installation_plan"
    )
    gantt.plot(core, project, "Installation Gantt Chart")

    assert len(plt.get_fignums()) == 1

    plt.close("all")
