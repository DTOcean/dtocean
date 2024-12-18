# -*- coding: utf-8 -*-

# pylint: disable=protected-access

from dtocean_core.strategies import Strategy


class MockStrategy(Strategy):
    """A mock strategy"""
    
    @classmethod
    def get_name(cls):
        return "Mock"
    
    def configure(self, kwargs=None): # pylint: disable=arguments-differ
        mock = {"mock": "mock"}
        self.set_config(mock)
        return
    
    def get_variables(self):
        return None
    
    def execute(self, core, project):
        return


def test_strategy_get_config():
    
    strategy = MockStrategy()
    strategy.configure()
    
    test = strategy.get_config()
    
    assert "mock" in test
    assert id(test) != id(strategy._config)


def test_strategy_dump_config_hook():
    
    strategy = MockStrategy()
    strategy.configure()
    
    config = strategy.get_config()
    test = strategy.dump_config_hook(config)
    
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
