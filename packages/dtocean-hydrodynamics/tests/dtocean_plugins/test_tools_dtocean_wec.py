# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest

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
def project(core):
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

    return new_project


def test_available():
    tool_man = ToolManager()
    assert "WEC Simulator" in tool_man.get_available()


def test_can_execute_tool(core, project):
    tool_man = ToolManager()
    tool = tool_man.get_tool("WEC Simulator")

    assert tool_man.can_execute_tool(core, project, tool)


def test_execute_tool(mocker, core, project):
    from dtocean_plugins.tools.dtocean_wec import subprocess

    call: MagicMock = mocker.patch.object(subprocess, "call")

    tool_man = ToolManager()
    tool = tool_man.get_tool("WEC Simulator")
    tool_man.execute_tool(core, project, tool)

    assert "dtocean-wec.exe" in call.call_args[0][0]
