# pylint: disable=redefined-outer-name

import pytest

from dtocean_hydro.utils.convert import make_tide_statistics

pytest.importorskip("dtocean_core")

from dtocean_core.core import Core  # noqa: E402
from dtocean_core.extensions import ToolManager  # noqa: E402
from dtocean_core.menu import ModuleMenu, ProjectMenu  # noqa: E402
from dtocean_core.pipeline import InputVariable, Tree  # noqa: E402


@pytest.fixture(scope="module")
def core():
    """Share a Core object"""
    return Core()


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture()
def project(core, inputs_wp2_tidal):
    """Share a Project object"""

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    var_tree = Tree()
    mod_name = "Hydrodynamics"

    new_project = project_menu.new_project(core, "test tidal")

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )
    assert isinstance(device_type, InputVariable)

    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    module_menu.activate(core, new_project, mod_name)
    project_menu.initiate_dataflow(core, new_project)

    hydro_branch = var_tree.get_branch(core, new_project, mod_name)
    hydro_branch.read_test_data(core, new_project, inputs_wp2_tidal)

    return new_project


@pytest.fixture()
def wave_project(core, inputs_wp2_wave):
    """Share a Project object"""

    project_menu = ProjectMenu()
    module_menu = ModuleMenu()
    var_tree = Tree()
    mod_name = "Hydrodynamics"

    new_project = project_menu.new_project(core, "test wave")

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )
    assert isinstance(device_type, InputVariable)

    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    module_menu.activate(core, new_project, mod_name)
    project_menu.initiate_dataflow(core, new_project)

    hydro_branch = var_tree.get_branch(core, new_project, mod_name)
    hydro_branch.read_test_data(core, new_project, inputs_wp2_wave)

    return new_project


def test_available():
    tool_man = ToolManager()
    assert "Device Minimum Spacing Check" in tool_man.get_available()


def test_can_execute_tool(core, project):
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    assert tool_man.can_execute_tool(core, project, tool)


def test_execute_tool_no_config(core, project):
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    with pytest.raises(RuntimeError) as excinfo:
        tool_man.execute_tool(core, project, tool)

    assert "Was configure called?" in str(excinfo)


def test_execute_tool(core, project):
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    layout = [(450.0, 100.0), (550.0, 100.0), (450.0, 150.0), (550.0, 150.0)]
    tool.configure(layout)

    tool_man.execute_tool(core, project, tool)


def test_execute_tool_occurrence_matrix(core, project):
    tidal_nbins = core.get_data_value(project, "project.tidal_occurrence_nbins")
    tidal_series = core.get_data_value(project, "farm.tidal_series")
    tidal_occurrence_point = core.get_data_value(
        project, "farm.tidal_occurrence_point"
    )

    x = tidal_series.coords["UTM x"]
    y = tidal_series.coords["UTM y"]

    tide_dict = {
        "U": tidal_series.U.values,
        "V": tidal_series.V.values,
        "SSH": tidal_series.SSH.values,
        "TI": tidal_series.TI.values,
        "x": x.values,
        "y": y.values,
        "t": tidal_series.t.values,
        "xc": tidal_occurrence_point.x,
        "yc": tidal_occurrence_point.y,
        "ns": tidal_nbins,
    }

    occurrence_matrix = make_tide_statistics(tide_dict)

    occurrence_matrix_coords = [
        occurrence_matrix["x"],
        occurrence_matrix["y"],
        occurrence_matrix["p"],
    ]

    matrix_xset = {
        "values": {
            "U": occurrence_matrix["U"],
            "V": occurrence_matrix["V"],
            "SSH": occurrence_matrix["SSH"],
            "TI": occurrence_matrix["TI"],
        },
        "coords": occurrence_matrix_coords,
    }

    core.add_datastate(
        project, identifiers=["farm.tidal_occurrence"], values=[matrix_xset]
    )

    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    layout = [(450.0, 100.0), (550.0, 100.0), (450.0, 150.0), (550.0, 150.0)]
    tool.configure(layout)

    tool_man.execute_tool(core, project, tool)


@pytest.mark.parametrize(
    "identifier,           expected",
    [
        ("farm.tidal_series", "Tidal time series"),
        ("farm.tidal_occurrence_point", "tidal occurance extraction point"),
    ],
)
def test_execute_tool_tidal_missing(core, project, identifier, expected):
    core.add_datastate(project, identifiers=[identifier], values=[None])

    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    layout = [(450.0, 100.0), (550.0, 100.0), (450.0, 150.0), (550.0, 150.0)]
    tool.configure(layout)

    with pytest.raises(ValueError) as excinfo:
        tool_man.execute_tool(core, project, tool)

    assert expected in str(excinfo)


def test_execute_tool_tidal_no_nbins_main_direction(core, project):
    core.add_datastate(
        project,
        identifiers=[
            "project.tidal_occurrence_nbins",
            "project.main_direction",
        ],
        values=[None, 0],
    )

    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    layout = [(450.0, 100.0), (550.0, 100.0), (450.0, 150.0), (550.0, 150.0)]
    tool.configure(layout)

    tool_man.execute_tool(core, project, tool)


def test_execute_tool_wave(core, wave_project):
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    layout = [(450.0, 100.0), (550.0, 100.0), (450.0, 150.0), (550.0, 150.0)]
    tool.configure(layout)

    tool_man.execute_tool(core, wave_project, tool)


def test_execute_tool_fail_minimum_distance(core, project):
    tool_man = ToolManager()
    tool = tool_man.get_tool("Device Minimum Spacing Check")

    layout = [(450.0, 100.0), (455.0, 100.0), (450.0, 105.0), (455.0, 105.0)]
    tool.configure(layout)

    with pytest.raises(RuntimeError) as excinfo:
        tool_man.execute_tool(core, project, tool)

    assert "Violation of the minimum distance constraint" in str(excinfo)
