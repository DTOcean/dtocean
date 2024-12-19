# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access

import pytest
import pandas as pd

from dtocean_core.core import OrderedSim, Project
from dtocean_core.strategies.multi import MultiSensitivity # pylint: disable=no-name-in-module


@pytest.fixture()
def multi():
    return MultiSensitivity()


@pytest.fixture()
def inputs_df():
    
    data = {'Module': ['Hydrodynamics',
                       'Electrical Sub-Systems'],
            'Variable': ['device.power_rating',
                         'device.power_factor'],
             'Values': [(1, 2, 3), (4, 5)]}
    
    return pd.DataFrame(data)


def test_multi_get_name():
    assert MultiSensitivity.get_name() == "Multi Sensitivity"


@pytest.mark.parametrize("subsp_ratio, expected",
                         [(1, 6),
                          (0.5, 3)])
def test_multi_count_selections(multi, inputs_df, subsp_ratio, expected):
    assert multi.count_selections(inputs_df, subsp_ratio) == expected


def test_multi_configure(multi):
    
    multi.configure("inputs_df", "subsp_ratio", skip_errors=False)
    
    assert multi._config == {"inputs_df": "inputs_df",
                             "subsp_ratio": "subsp_ratio",
                             "skip_errors": False}


def test_multi_get_variables(multi, inputs_df):
    multi.configure(inputs_df, 1)
    assert (multi.get_variables() == inputs_df["Variable"].values).all()


def test_multi_execute(mocker, multi, inputs_df):
    
    modules = ['Hydrodynamics',
               'Electrical Sub-Systems',
               'Mooring and Foundations',
               'Installation',
               'Operations and Maintenance']
    
    mocker.patch.object(multi._module_menu,
                        'get_available',
                        return_value=modules,
                        autospec=True)
    
    mocker.patch.object(multi._tree,
                        'get_branch',
                        autospec=True)
    
    mocker.patch.object(multi,
                        '_safe_exe',
                        return_value=True,
                        autospec=True)
    
    core = mocker.MagicMock()
    
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    
    multi.configure(inputs_df, 1)
    multi.execute(core, project)
    
    assert multi._sim_record == ['Simulation 0',
                                 'Simulation 1',
                                 'Simulation 2',
                                 'Simulation 3',
                                 'Simulation 4',
                                 'Simulation 5']
    assert len(multi.sim_details) == 12


def test_multi_execute_no_config(multi):
    
    with pytest.raises(ValueError) as excinfo:
        multi.execute(None, None)
    
    assert "configuration values are None" in str(excinfo)


def test_multi_execute_no_simulation(mocker, multi, inputs_df):
    
    modules = ['Hydrodynamics',
               'Electrical Sub-Systems',
               'Mooring and Foundations',
               'Installation',
               'Operations and Maintenance']
    
    mocker.patch.object(multi._module_menu,
                        'get_available',
                        return_value=modules,
                        autospec=True)
    
    mocker.patch.object(multi._tree,
                        'get_branch',
                        autospec=True)
    
    core = mocker.MagicMock()
    project = Project("mock")
    multi.configure(inputs_df, 1)
    
    with pytest.raises(RuntimeError) as excinfo:
        multi.execute(core, project)
    
    assert "Project has not been activated." in str(excinfo)


@pytest.mark.parametrize("skip_errors", [True, False])
def test_multi_safe_exe(mocker, multi, skip_errors):
    
    mocker.patch.object(multi,
                        '_run_simulation',
                        autospec=True)
    
    multi.configure(None, None, skip_errors)
    success_flag = multi._safe_exe(None, None, None, None)
    
    assert success_flag


def test_multi_safe_exe_raise(mocker, multi):
    
    mocker.patch.object(multi,
                        '_run_simulation',
                        side_effect=SystemExit('foo'),
                        autospec=True)
    
    multi.configure(None, None, True)
    
    with pytest.raises(SystemExit) as excinfo:
        multi._safe_exe(None, None, None, None)
    
    assert 'foo' in str(excinfo)


def test_multi_safe_exe_pass(mocker, multi):
    
    mocker.patch.object(multi,
                        '_run_simulation',
                        side_effect=ValueError('foo'),
                        autospec=True)
    
    multi.configure(None, None, True)
    success_flag = multi._safe_exe(None, None, None, None)
    
    assert not success_flag


def test_multi_run_simulation(mocker, multi):
    
    modules = ['Hydrodynamics',
               'Electrical Sub-Systems',
               'Mooring and Foundations',
               'Installation',
               'Operations and Maintenance']
    
    mocker.patch.object(multi._module_menu,
                        'get_available',
                        return_value=modules,
                        autospec=True)
    
    mocker.patch.object(multi._module_menu,
                        'get_active',
                        return_value=modules,
                        autospec=True)
    
    mock_branch = mocker.MagicMock()
    mock_branch.get_input_status.return_value = {'device.power_rating': "",
                                                 'device.power_factor': ""}
    
    mocker.patch.object(multi._tree,
                        'get_branch',
                        return_value=mock_branch,
                        autospec=True)
    
    mock_basic = mocker.patch('dtocean_core.strategies.multi.BasicStrategy',
                              autospec=True)
    
    core = mocker.MagicMock()
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    
    multi.configure(None, None)
    
    data = {'Module': ['Hydrodynamics',
                       'Electrical Sub-Systems'],
            'Variable': ['device.power_rating',
                         'device.power_factor'],
            'Values': [1, 4]}
    sorted_df = pd.DataFrame(data)
    
    multi._run_simulation(core, project, sorted_df, "Default")
    
    assert mock_basic.call_count == 1


def test_multi_run_simulation_no_module(mocker, multi):
    
    modules = ['Mooring and Foundations',
               'Installation',
               'Operations and Maintenance']
    
    mocker.patch.object(multi._module_menu,
                        'get_available',
                        return_value=modules,
                        autospec=True)
    
    core = mocker.MagicMock()
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    
    multi.configure(None, None)
    
    data = {'Module': ['Hydrodynamics',
                       'Electrical Sub-Systems'],
            'Variable': ['device.power_rating',
                         'device.power_factor'],
            'Values': [1, 4]}
    sorted_df = pd.DataFrame(data)
    
    with pytest.raises(ValueError) as excinfo:
        multi._run_simulation(core, project, sorted_df, "Default")
    
    assert "does not exist" in str(excinfo)


def test_multi_run_simulation_not_activated(mocker, multi):
    
    available_modules = ['Hydrodynamics',
                         'Electrical Sub-Systems',
                         'Mooring and Foundations',
                         'Installation',
                         'Operations and Maintenance']
    
    mocker.patch.object(multi._module_menu,
                        'get_available',
                        return_value=available_modules,
                        autospec=True)
    
    active_modules = ['Mooring and Foundations',
                      'Installation',
                      'Operations and Maintenance']
    
    mocker.patch.object(multi._module_menu,
                        'get_active',
                        return_value=active_modules,
                        autospec=True)
    
    core = mocker.MagicMock()
    project = Project("mock")
    project.add_simulation(OrderedSim("Default"))
    
    multi.configure(None, None)
    
    data = {'Module': ['Hydrodynamics',
                       'Electrical Sub-Systems'],
            'Variable': ['device.power_rating',
                         'device.power_factor'],
            'Values': [1, 4]}
    sorted_df = pd.DataFrame(data)
    
    with pytest.raises(ValueError) as excinfo:
        multi._run_simulation(core, project, sorted_df, "Default")
    
    assert "has not been activated" in str(excinfo)
