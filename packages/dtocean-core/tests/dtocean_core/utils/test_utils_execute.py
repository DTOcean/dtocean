
import os
import sys

import pytest

from dtocean_core.core import Core, Project
from dtocean_core.extensions import StrategyManager
from dtocean_core.menu import ModuleMenu
from dtocean_core.strategies import Strategy
from dtocean_core.utils.execute import main, main_interface # pylint: disable=no-name-in-module


class MockCore(Core):
    
    def load_project(self, fpath): # pylint: disable=arguments-differ,unused-argument
        return Project("mock")


class MockStrategy(Strategy):
    
    @classmethod
    def get_name(cls):
        
        '''A class method for the common name of the strategy.
        
        Returns:
          str: A unique string
        '''
        
        return "Mock"
    
    def configure(self):
    
        '''The configure method is collect information required for executing
        the strategy.
        '''
        
        return 
        
    def get_variables(self):
        
        '''The get_variables method returns the list of any variables that
        will be set by the strategy
        '''
        
        return None
        
    def execute(self, core, project):
        
        '''The execute method is used to execute the strategy. It should always
        take a Core and a Project class as the only inputs.
        '''
        
        return


class MockMenu(ModuleMenu):
    
    def execute_current(self, core,
                              project,
                              execute_themes=True,
                              allow_unavailable=False,
                              log_execution_time=True):
        return


class MockManager(StrategyManager):
    
    def get_strategy(self, name): # pylint: disable=arguments-differ,unused-argument
        return MockStrategy()


def test_main_full(mocker, capsys, tmpdir):
    
    mocker.patch('dtocean_core.utils.execute.start_logging',
                 autospec=True)
    
    mocker.patch('dtocean_core.utils.execute.Core',
                 new=MockCore)
    
    mocker.patch('dtocean_core.utils.execute.StrategyManager',
                 new=MockManager)
    
    fpath = str(tmpdir.join('test.prj'))
    
    main(fpath,
         save=True,
         full=True,
         warn=True,
         log=True)
    
    captured = capsys.readouterr()
    test = captured[0]
    
    assert "all scheduled modules" in test
    assert fpath in test
    assert "warning tracebacks" in test
    assert "logging" in test
    assert "Execution time" in test
    assert "Saving project" in test
    assert len(os.listdir(str(tmpdir))) == 1
    assert os.listdir(str(tmpdir))[0] == 'test_complete.prj'


def test_main_next(mocker, capsys, tmpdir):
    
    mocker.patch('dtocean_core.utils.execute.start_logging',
                 autospec=True)
    
    mocker.patch('dtocean_core.utils.execute.Core',
                 new=MockCore)
    
    mocker.patch('dtocean_core.utils.execute.ModuleMenu',
                 new=MockMenu)
    
    mocker.patch('dtocean_core.utils.execute.StrategyManager',
                 new=MockManager)
    
    fpath = str(tmpdir.join('test.prj'))
    
    main(fpath,
         save=False,
         full=False,
         warn=False,
         log=False)
    
    captured = capsys.readouterr()
    test = captured[0]
    
    assert "next scheduled module" in test


def test_main_save_path(mocker, tmpdir):
    
    mocker.patch('dtocean_core.utils.execute.start_logging',
                 autospec=True)
    
    mocker.patch('dtocean_core.utils.execute.Core',
                 new=MockCore)
    
    mocker.patch('dtocean_core.utils.execute.ModuleMenu',
                 new=MockMenu)
    
    mocker.patch('dtocean_core.utils.execute.StrategyManager',
                 new=MockManager)
    
    fpath = str(tmpdir.join('test.prj'))
    spath = str(tmpdir.join('other.prj'))
    
    main(fpath,
         save=spath)
    
    assert len(os.listdir(str(tmpdir))) == 1
    assert os.listdir(str(tmpdir))[0] == 'other.prj'


@pytest.mark.parametrize("arg, expected",
                         [("", True),
                          ("-o out.prj", "out.prj"),
                          ("-n", False)])
def test_main_interface(mocker, arg, expected):
    
    testargs = ["execute_dtocean_project",
                "mock.prj",
                "-fwl"]
    if arg: testargs.append(arg)
    
    mocker.patch.object(sys, 'argv', testargs)
    
    test = mocker.patch("dtocean_core.utils.execute.main",
                        autospec=True)
    
    main_interface()
    
    assert test.call_args.args == ('mock.prj', expected, True, True, True)
