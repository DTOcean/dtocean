# pylint: disable=redefined-outer-name,protected-access

import pickle
from collections import OrderedDict

import matplotlib.pyplot as plt
import pytest

from dtocean_core.core import OrderedSim, Project
from dtocean_core.data import CoreMetaData
from dtocean_core.extensions import StrategyManager
from dtocean_plugins.strategies.strategies import Strategy


class MockStrategy(Strategy):
    @classmethod
    def get_name(cls):
        """A class method for the common name of the strategy.

        Returns:
          str: A unique string
        """

        return "Mock"

    def configure(self):
        """The configure method is collect information required for executing
        the strategy.
        """
        pass

    def get_variables(self):
        """The get_variables method returns the list of any variables that
        will be set by the strategy
        """

        return None

    def execute(self, core, project):
        """The execute method is used to execute the strategy. It should always
        take a Core and a Project class as the only inputs.
        """
        pass


@pytest.fixture()
def manager():
    return StrategyManager()


def test_get_available(manager):
    result = manager.get_available()

    assert len(result) > 0


def test_get_strategy(manager):
    strategies = manager.get_available()

    for strategy_name in strategies:
        manager.get_strategy(strategy_name)

    assert True


def test_get_level_values_project(mocker, manager):
    level_values = OrderedDict(
        [
            (
                "Default",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            28263096.852039404,
                        ),
                        ("installation global output", 31673780.41058045),
                        (
                            "operations and maintenance global output",
                            31673780.41058045,
                        ),
                    ]
                ),
            ),
            (
                "Default Clone 1",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            119195335.02247664,
                        ),
                        ("installation global output", 123875364.39132734),
                        (
                            "operations and maintenance global output",
                            123875364.39132734,
                        ),
                    ]
                ),
            ),
        ]
    )

    core = mocker.Mock()
    core.get_level_values.return_value = level_values

    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    project.add_simulation(OrderedSim("Default Clone 1"))

    active_levels = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        manager._module_menu,
        "get_active",
        return_value=active_levels,
        autospec=True,
    )

    level_values = manager.get_level_values(core, project, None)

    assert level_values == level_values


def test_get_level_values_strategy(mocker, manager):
    level_values = OrderedDict(
        [
            (
                "Default",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            28263096.852039404,
                        ),
                        ("installation global output", 31673780.41058045),
                        (
                            "operations and maintenance global output",
                            31673780.41058045,
                        ),
                    ]
                ),
            ),
            (
                "Default Clone 1",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            119195335.02247664,
                        ),
                        ("installation global output", 123875364.39132734),
                        (
                            "operations and maintenance global output",
                            123875364.39132734,
                        ),
                    ]
                ),
            ),
        ]
    )

    core = mocker.Mock()
    core.get_level_values.return_value = level_values

    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    project.add_simulation(OrderedSim("Default Clone 1"))
    project.add_simulation(OrderedSim("Default Clone 2"))

    strategy = MockStrategy()
    strategy.add_simulation_title("Default")
    strategy.add_simulation_title("Default Clone 1")

    active_levels = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        manager._module_menu,
        "get_active",
        return_value=active_levels,
        autospec=True,
    )

    level_values = manager.get_level_values(
        core, project, None, strategy=strategy
    )

    assert level_values == level_values


def test_get_level_values_sim_titles(mocker, manager):
    level_values = OrderedDict(
        [
            (
                "Default",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            28263096.852039404,
                        ),
                        ("installation global output", 31673780.41058045),
                        (
                            "operations and maintenance global output",
                            31673780.41058045,
                        ),
                    ]
                ),
            ),
            (
                "Default Clone 1",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            119195335.02247664,
                        ),
                        ("installation global output", 123875364.39132734),
                        (
                            "operations and maintenance global output",
                            123875364.39132734,
                        ),
                    ]
                ),
            ),
        ]
    )

    core = mocker.Mock()
    core.get_level_values.return_value = level_values

    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    project.add_simulation(OrderedSim("Default Clone 1"))
    project.add_simulation(OrderedSim("Default Clone 2"))

    sim_titles = ["Default", "Default Clone 1"]

    active_levels = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    mocker.patch.object(
        manager._module_menu,
        "get_active",
        return_value=active_levels,
        autospec=True,
    )

    level_values = manager.get_level_values(
        core, project, None, sim_titles=sim_titles
    )

    assert level_values == level_values


def test_get_level_values_df(mocker, manager):
    level_values = OrderedDict(
        [
            (
                "Default",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            28263096.852039404,
                        ),
                        ("installation global output", 31673780.41058045),
                        (
                            "operations and maintenance global output",
                            31673780.41058045,
                        ),
                    ]
                ),
            ),
            (
                "Default Clone 1",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            119195335.02247664,
                        ),
                        ("installation global output", 123875364.39132734),
                        (
                            "operations and maintenance global output",
                            123875364.39132734,
                        ),
                    ]
                ),
            ),
        ]
    )

    completed_levels = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    mocker.patch.object(
        manager, "get_level_values", return_value=level_values, autospec=True
    )

    mocker.patch.object(
        manager._module_menu,
        "get_completed",
        return_value=completed_levels,
        autospec=True,
    )

    core = mocker.Mock()
    core.get_metadata.return_value = meta

    df = manager.get_level_values_df(core, None, None)

    assert set(df["Simulation Name"].values) == set(
        ["Default", "Default Clone 1"]
    )


def test_get_level_values_plot(mocker, manager):
    level_values = OrderedDict(
        [
            (
                "Default",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            28263096.852039404,
                        ),
                        ("installation global output", 31673780.41058045),
                        (
                            "operations and maintenance global output",
                            31673780.41058045,
                        ),
                    ]
                ),
            ),
            (
                "Default Clone 1",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            119195335.02247664,
                        ),
                        ("installation global output", 123875364.39132734),
                        (
                            "operations and maintenance global output",
                            123875364.39132734,
                        ),
                    ]
                ),
            ),
        ]
    )

    completed_levels = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    mocker.patch.object(
        manager, "get_level_values", return_value=level_values, autospec=True
    )

    mocker.patch.object(
        manager._module_menu,
        "get_completed",
        return_value=completed_levels,
        autospec=True,
    )

    core = mocker.Mock()
    core.get_metadata.return_value = meta

    manager.get_level_values_plot(core, None, None)

    assert len(plt.get_fignums()) == 1

    ax = plt.gca()
    _, labels = ax.get_legend_handles_labels()

    assert len(labels) == 2

    plt.close("all")


def test_get_level_values_plot_max_lines(mocker, manager):
    level_values = OrderedDict(
        [
            (
                "Default",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            28263096.852039404,
                        ),
                        ("installation global output", 31673780.41058045),
                        (
                            "operations and maintenance global output",
                            31673780.41058045,
                        ),
                    ]
                ),
            ),
            (
                "Default Clone 1",
                OrderedDict(
                    [
                        ("hydrodynamics global output", 20000000.0),
                        (
                            "electrical sub-systems global output",
                            23065408.054377057,
                        ),
                        (
                            "mooring and foundations global output",
                            119195335.02247664,
                        ),
                        ("installation global output", 123875364.39132734),
                        (
                            "operations and maintenance global output",
                            123875364.39132734,
                        ),
                    ]
                ),
            ),
        ]
    )

    completed_levels = [
        "Hydrodynamics",
        "Electrical Sub-Systems",
        "Mooring and Foundations",
        "Installation",
        "Operations and Maintenance",
    ]

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    mocker.patch.object(
        manager, "get_level_values", return_value=level_values, autospec=True
    )

    mocker.patch.object(
        manager._module_menu,
        "get_completed",
        return_value=completed_levels,
        autospec=True,
    )

    core = mocker.Mock()
    core.get_metadata.return_value = meta

    manager.get_level_values_plot(core, None, None, max_lines=1)

    assert len(plt.get_fignums()) == 1

    ax = plt.gca()
    _, labels = ax.get_legend_handles_labels()

    assert len(labels) == 1

    plt.close("all")


def test_load_strategy(mocker, manager):
    strategy = MockStrategy()
    mocker.patch.object(
        manager, "get_strategy", return_value=strategy, autospec=True
    )

    mocker.patch(
        "dtocean_core.extensions.os.path.isfile",
        return_value=True,
        autospec=True,
    )

    test_strategy = MockStrategy()
    test_strategy.add_simulation_title("Default")
    test_strategy.add_simulation_title("Default Clone 1")

    mock_stg_dict = manager._get_dump_dict(test_strategy)

    mocker.patch(
        "dtocean_core.extensions.open",
        mocker.mock_open(read_data=pickle.dumps(mock_stg_dict, -1)),
    )

    result = manager.load_strategy("mock.pkl")

    assert isinstance(result, MockStrategy)
    assert set(strategy._sim_record) == set(["Default", "Default Clone 1"])


def test_load_strategy_no_version(mocker, manager):
    strategy = MockStrategy()
    mocker.patch.object(
        manager, "get_strategy", return_value=strategy, autospec=True
    )

    mocker.patch(
        "dtocean_core.extensions.os.path.isfile",
        return_value=True,
        autospec=True,
    )

    mock_stg_dict = {
        "name": "basic",
        "sim_record": ["Default", "Default Clone 1"],
        "config": None,
        "sim_details": None,
    }

    mocker.patch(
        "dtocean_core.extensions.open",
        mocker.mock_open(read_data=pickle.dumps(mock_stg_dict, -1)),
    )

    with pytest.raises(ValueError) as excinfo:
        manager.load_strategy("mock.pkl")

    assert "project object is required" in str(excinfo.value)


def test_load_strategy_old(mocker, manager):
    strategy = MockStrategy()
    mocker.patch.object(
        manager, "get_strategy", return_value=strategy, autospec=True
    )

    mocker.patch(
        "dtocean_core.extensions.os.path.isfile",
        return_value=True,
        autospec=True,
    )

    mock_stg_dict = {
        "name": "basic",
        "sim_record": [0, 1],
        "config": None,
        "sim_details": None,
    }

    mocker.patch(
        "dtocean_core.extensions.open",
        mocker.mock_open(read_data=pickle.dumps(mock_stg_dict, -1)),
    )

    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    project.add_simulation(OrderedSim("Default Clone 1"))

    result = manager.load_strategy("mock.pkl", project)

    assert isinstance(result, MockStrategy)
    assert set(strategy._sim_record) == set(["Default", "Default Clone 1"])
