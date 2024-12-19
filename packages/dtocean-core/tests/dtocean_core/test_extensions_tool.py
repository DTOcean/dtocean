import pytest

from dtocean_core.extensions import ToolManager


@pytest.fixture(scope="module")
def manager():
    return ToolManager()


def test_get_available(manager):
    result = manager.get_available()
    assert len(result) >= 0


def test_get_tool(manager):
    tools = manager.get_available()

    for tool_name in tools:
        manager.get_tool(tool_name)

    assert True
