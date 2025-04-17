from unittest.mock import MagicMock

import pytest

from dtocean_core.core import Core
from dtocean_core.extensions import ToolManager
from dtocean_core.menu import ProjectMenu
from dtocean_plugins.tools.base import Tool


class MockTool(Tool):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the tool.

        Returns:
          str: A unique string
        """

        return "Mock"

    @classmethod
    def declare_inputs(cls):
        return None

    @classmethod
    def declare_outputs(cls):
        return None

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        return {}

    def configure(self):
        pass

    def connect(self):
        pass


@pytest.fixture()
def manager():
    manager = ToolManager()
    manager._plugin_classes = {"Mock": MockTool}
    manager._plugin_names = manager._discover_names()
    return manager


@pytest.fixture()
def core():
    return Core()


@pytest.fixture()
def project(core):
    project_menu = ProjectMenu()
    return project_menu.new_project(core, "mock")


def test_get_available(manager):
    result = manager.get_available()
    assert len(result) == 1
    assert result[0] == "Mock"


def test_get_tool(manager):
    tool = manager.get_tool("Mock")
    assert isinstance(tool, MockTool)


def test_can_execute_tool(manager, core, project):
    tool = manager.get_tool("Mock")
    assert manager.can_execute_tool(core, project, tool)


def test_execute_tool(mocker, manager, core, project):
    connect_interface: MagicMock = mocker.patch.object(
        core,
        "connect_interface",
    )
    tool = manager.get_tool("Mock")
    manager.execute_tool(core, project, tool)

    connect_interface.assert_called_once()
