# -*- coding: utf-8 -*-

# pylint: disable=protected-access

from dtocean_plugins.strategies.base import Strategy


class MockStrategy(Strategy):
    """A mock strategy"""

    @property
    def version(self) -> int:
        return 1

    @classmethod
    def get_name(cls):
        return "Mock"

    def configure(self, kwargs=None):  # pylint: disable=arguments-differ
        mock = {"mock": "mock"}
        self.set_config(mock)

    def get_variables(self):
        return None

    def execute(self, core, project):
        pass

    @staticmethod
    def dump_config(config):
        return config

    @staticmethod
    def load_config(serial_config, version):
        if version != 1:
            raise RuntimeError("Data version not recognised")

        return serial_config

    @staticmethod
    def dump_sim_details(sim_details):
        return None

    @staticmethod
    def load_sim_details(serial_sim_details):
        return None


def test_strategy_get_config():
    strategy = MockStrategy()
    strategy.configure()

    test = strategy.get_config()

    assert test is not None
    assert "mock" in test
    assert id(test) != id(strategy._config)


def test_strategy_dump_config():
    strategy = MockStrategy()
    strategy.configure()

    config = strategy.get_config()
    test = strategy.dump_config(config)

    assert id(test) == id(config)


def test_strategy_add_remove_simulation_title():
    strategy = MockStrategy()
    test_names = ["one", "two", "three"]

    for name in test_names:
        strategy.add_simulation_title(name)
        assert name in strategy.get_simulation_record()

        strategy.remove_simulation_title(name)
        assert name not in strategy.get_simulation_record()


def test_strategy_restart():
    strategy = MockStrategy()
    strategy.sim_details = 1
    strategy.add_simulation_title("mock")

    strategy.restart()

    assert not strategy.get_simulation_record()
    assert strategy.sim_details is None
