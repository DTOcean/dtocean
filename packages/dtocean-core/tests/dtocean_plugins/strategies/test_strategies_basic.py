# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access

import pytest

from dtocean_core.core import OrderedSim, Project
from dtocean_plugins.strategies.basic import BasicStrategy


@pytest.fixture()
def basic():
    return BasicStrategy()


def test_basic_get_name():
    assert BasicStrategy.get_name() == "Basic"


def test_basic_configure(basic):
    basic.configure()
    assert basic._config is None


def test_basic_get_variables(basic):
    assert basic.get_variables() is None


def test_basic_execute(mocker, basic):
    mocker.patch.object(
        basic._module_menu,
        "get_current",
        side_effect=["a", "b", None],
        autospec=True,
    )

    mocker.patch.object(basic._module_menu, "execute_current", autospec=True)

    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))

    basic.execute(None, project)

    assert basic._module_menu.execute_current.call_count == 2
