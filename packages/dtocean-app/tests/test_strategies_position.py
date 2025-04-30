# -*- coding: utf-8 -*-

#    Copyright (C) 2025 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=redefined-outer-name,protected-access,unused-argument
# pylint: disable=no-self-use,wrong-import-order,wrong-import-position

import pytest
pytest.importorskip("dtocean_hydro")

import os
import sys
import time
from copy import deepcopy

import pandas as pd
from PIL import Image
from PySide6 import QtCore, QtGui

from dtocean_app.core import GUICore
from dtocean_app.main import Shell
from dtocean_app.strategies.position import AdvancedPositionWidget
from dtocean_core.interfaces import ModuleInterface
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree


class MockModule(ModuleInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Module"
    
    @classmethod
    def declare_weight(cls):
        
        return 998
    
    @classmethod
    def declare_inputs(cls):
        
        input_list = ["device.turbine_performance",
                      "device.cut_in_velocity",
                      "device.system_type"]
        
        return input_list
    
    @classmethod
    def declare_outputs(cls):
        
        output_list = None
        
        return output_list
    
    @classmethod
    def declare_optional(cls):
        
        return None
    
    @classmethod
    def declare_id_map(cls):
        
        id_map = {"dummy1": "device.turbine_performance",
                  "dummy2": "device.cut_in_velocity",
                  "dummy3": "device.system_type"}
        
        return id_map
    
    def connect(self, debug_entry=False,
                      export_data=True):


@pytest.fixture(scope="module")
def core():
    
    core = GUICore()
    core._create_data_catalog()
    core._create_control()
    core._create_sockets()
    core._init_plots()
    
    socket = core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)
    
    return core


@pytest.fixture
def project(core):
    
    project_title = "Test"
    
    project_menu = ProjectMenu()
    var_tree = Tree()
    
    project = project_menu.new_project(core, project_title)
    
    options_branch = var_tree.get_branch(core,
                                         project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, project)
    
    project_menu.initiate_pipeline(core, project)
    
    return project


@pytest.fixture
def mock_shell(core, project):
    
    module_menu = ModuleMenu()
    module_menu.activate(core, project, MockModule.get_name())
    
    shell = Shell(core)
    shell.project = project
    
    return shell


@pytest.fixture
def hydro_shell(core, project):
    
    module_menu = ModuleMenu()
    module_menu.activate(core, project, "Hydrodynamics")
    
    shell = Shell(core)
    shell.project = project
    
    return shell


@pytest.fixture()
def config():
    
    return {
     'base_penalty': 2.0,
     'clean_existing_dir': True,
     'max_evals': 2,
     'max_resample_factor': 5,
     'max_simulations': 10,
     'maximise': True,
     'min_evals': 3,
     'n_threads': 7,
     'objective': 'project.annual_energy',
     'parameters': {'delta_col': 
                       {'range': {'max_multiplier': 2.0,
                                   'min_multiplier': 1.0,
                                   'type': 'multiplier',
                                   'variable': 'device.minimum_distance_y'}},
                     'delta_row': 
                       {'range': {'max_multiplier': 2.0,
                                   'min_multiplier': 1.0,
                                   'type': 'multiplier',
                                   'variable': 'device.minimum_distance_x'}},
                     'grid_orientation': {'range': {'max': 90.0,
                                                      'min': -90.0,
                                                      'type': 'fixed'}},
                     'n_nodes': {'range': {'max': 20,
                                             'min': 1,
                                             'type': 'fixed'},
                                  'x0': 15},
                     't1': {'range': {'max': 1.0,
                                        'min': 0.0,
                                        'type': 'fixed'}},
                     't2': {'range': {'max': 1.0,
                                        'min': 0.0,
                                        'type': 'fixed'}}},
     'popsize': 4,
     'results_params': ['project.number_of_devices',
                         'project.annual_energy',
                         'project.q_factor',
                         'project.capex_total',
                         'project.capex_breakdown',
                         'project.lifetime_opex_mean',
                         'project.lifetime_cost_mean',
                         'project.lifetime_energy_mean',
                         'project.lcoe_mean'],
     'root_project_path': None,
     'timeout': 12,
     'tolfun': 1.0,
     'worker_dir': 'mock'
    }


@pytest.fixture()
def config_alt():
    
    return {
     'base_penalty': 2.0,
     'clean_existing_dir': True,
     'max_evals': 3,
     'max_resample_factor': "auto2",
     'max_simulations': 1,
     'maximise': False,
     'min_evals': None,
     'n_threads': 9,
     'objective': 'project.annual_energy',
     'parameters': {'delta_col': 
                       {'fixed': 1},
                     'delta_row': 
                       {'range': {'max_multiplier': 2.0,
                                   'min_multiplier': 1.0,
                                   'type': 'multiplier',
                                   'variable': 'device.minimum_distance_x'}},
                     'grid_orientation': {'range': {'max': 90.0,
                                                      'min': -90.0,
                                                      'type': 'fixed'}},
                     'n_nodes': {'range': {'max': 20,
                                             'min': 1,
                                             'type': 'fixed'},
                                  'x0': 15},
                     't1': {'range': {'max': 1.0,
                                        'min': 0.0,
                                        'type': 'fixed'}},
                     't2': {'range': {'max': 1.0,
                                        'min': 0.0,
                                        'type': 'fixed'}}},
     'popsize': None,
     'results_params': ['project.number_of_devices',
                         'project.annual_energy',
                         'project.q_factor',
                         'project.capex_total',
                         'project.capex_breakdown',
                         'project.lifetime_opex_mean',
                         'project.lifetime_cost_mean',
                         'project.lifetime_energy_mean',
                         'project.lcoe_mean'],
     'root_project_path': None,
     'timeout': 1,
     'tolfun': 1,
     'worker_dir': 'mock'
    }


def test_AdvancedPositionWidget_bad_status(qtbot, mock_shell):
    
    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    assert not window.tabWidget.isTabEnabled(1)
    assert not window.tabWidget.isTabEnabled(2)
    assert not window.tabWidget.isTabEnabled(3)
    assert not window.tabWidget.isTabEnabled(4)


def test_AdvancedPositionWidget_settings_open(qtbot, tmp_path, hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)


def test_AdvancedPositionWidget_with_config(mocker,
                                            qtbot,
                                            hydro_shell,
                                            config):
    
    max_cpu = 8
    mocker.patch("dtocean_app.strategies.position.multiprocessing.cpu_count",
                 return_value=max_cpu,
                 autospec=True)
    
    window = AdvancedPositionWidget(None, hydro_shell, config)
    window.show()
    qtbot.addWidget(window)
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)
    assert float(window.penaltySpinBox.value()) == config['base_penalty']
    assert not window.cleanDirCheckBox.isChecked()
    assert int(window.maxNoiseSpinBox.value()) == config['min_evals']
    assert int(window.maxResamplesComboBox.currentIndex()) == 0
    assert int(window.maxResamplesSpinBox.value()) == \
                                                config['max_resample_factor']
    assert int(window.abortXSpinBox.value()) == config['max_simulations']
    assert window.costVarCheckBox.isChecked() is config['maximise']
    assert not window.minNoiseCheckBox.isChecked()
    assert int(window.minNoiseSpinBox.value()) == config['min_evals']
    assert int(window.maxNoiseSpinBox.minimum()) == config['min_evals']
    assert int(window.nThreadSpinBox.value()) == config['n_threads']
    assert str(window.costVarBox.currentText()) == \
                                        "Array Annual Energy Production (MWh)"
    assert not window.populationCheckBox.isChecked()
    assert int(window.populationSpinBox.value()) == config['popsize']
    assert int(window.abortTimeSpinBox.value()) == config['timeout']
    assert float(window.toleranceSpinBox.value()) == config['tolfun']
    assert str(window.workDirLineEdit.text()) == config['worker_dir']


def test_AdvancedPositionWidget_with_config_alt(mocker,
                                                qtbot,
                                                hydro_shell,
                                                config_alt):
    
    max_cpu = 8
    mocker.patch("dtocean_app.strategies.position.multiprocessing.cpu_count",
                 return_value=max_cpu,
                 autospec=True)
    
    window = AdvancedPositionWidget(None, hydro_shell, config_alt)
    window.show()
    qtbot.addWidget(window)
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)
    assert float(window.penaltySpinBox.value()) == config_alt['base_penalty']
    assert not window.cleanDirCheckBox.isChecked()
    assert int(window.maxNoiseSpinBox.value()) == config_alt['max_evals']
    assert int(window.maxResamplesComboBox.currentIndex()) == 1
    assert int(window.maxResamplesSpinBox.value()) == \
                                    int(config_alt['max_resample_factor'][-1])
    assert int(window.abortXSpinBox.value()) == config_alt['max_simulations']
    assert window.costVarCheckBox.isChecked() is config_alt['maximise']
    assert window.minNoiseCheckBox.isChecked()
    assert int(window.maxNoiseSpinBox.minimum()) == 1
    assert int(window.nThreadSpinBox.value()) == max_cpu
    assert str(window.costVarBox.currentText()) == \
                                        "Array Annual Energy Production (MWh)"
    assert window.populationCheckBox.isChecked()
    assert int(window.abortTimeSpinBox.value()) == config_alt['timeout']
    assert float(window.toleranceSpinBox.value()) == config_alt['tolfun']
    assert str(window.workDirLineEdit.text()) == config_alt['worker_dir']


def test_AdvancedPositionWidget_import_config(mocker,
                                              qtbot,
                                              mock_shell,
                                              config):
    
    from dtocean_app.strategies.position import GUIAdvancedPosition
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value="mock")
    mocker.patch.object(GUIAdvancedPosition,
                        "load_config",
                        return_value=config)
    
    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.cleanDirCheckBox.setChecked(True)
    qtbot.mouseClick(window.importConfigButton, QtCore.Qt.LeftButton)
    
    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)


def test_AdvancedPositionWidget_export_config(mocker,
                                              qtbot,
                                              tmp_path,
                                              mock_shell,
                                              config):
    
    f = tmp_path / "config.yaml"
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=str(f))
    
    window = AdvancedPositionWidget(None, mock_shell, config)
    window.show()
    qtbot.addWidget(window)
    
    qtbot.mouseClick(window.exportConfigButton, QtCore.Qt.LeftButton)
    
    assert f.is_file()


def test_AdvancedPositionWidget_reset_worker_dir(qtbot,
                                                 mock_shell,
                                                 config):
    
    window = AdvancedPositionWidget(None, mock_shell, config)
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert('not_mock')
    window.workDirLineEdit.editingFinished.emit()
    
    assert str(window.workDirLineEdit.text()) == config['worker_dir']


def test_AdvancedPositionWidget_reset_worker_dir_none(qtbot,
                                                      mock_shell):
    
    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert('not_mock')
    window.workDirLineEdit.editingFinished.emit()
    
    assert str(window.workDirLineEdit.text()) == ""


def test_AdvancedPositionWidget_select_worker_dir(mocker,
                                                  qtbot,
                                                  mock_shell,
                                                  config):
    
    mock = mocker.patch.object(QtGui.QFileDialog,
                               'getExistingDirectory',
                               return_value="another_mock")
    
    window = AdvancedPositionWidget(None, mock_shell, config)
    window.show()
    qtbot.addWidget(window)
    
    qtbot.mouseClick(window.workDirToolButton, QtCore.Qt.LeftButton)
    
    assert mock.call_args.args[2] == config['worker_dir']
    assert str(window.workDirLineEdit.text()) == "another_mock"


def test_AdvancedPositionWidget_select_worker_dir_none(mocker,
                                                       qtbot,
                                                       mock_shell):
    
    mock = mocker.patch.object(QtGui.QFileDialog,
                               'getExistingDirectory',
                               return_value="another_mock")
    
    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    qtbot.mouseClick(window.workDirToolButton, QtCore.Qt.LeftButton)
    
    assert mock.call_args.args[2] == os.path.expanduser("~")
    assert str(window.workDirLineEdit.text()) == "another_mock"


@pytest.mark.parametrize("toggles, expected", [(1, True), (2, False)])
def test_AdvancedPositionWidget_update_clean_existing_dir(qtbot,
                                                          hydro_shell,
                                                          toggles,
                                                          expected):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    for _ in range(toggles): window.cleanDirCheckBox.toggle()
    assert window.get_configuration()["clean_existing_dir"] is expected


def test_AdvancedPositionWidget_update_objective(qtbot,
                                                 tmp_path,
                                                 hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    window.costVarBox.setCurrentIndex(1)
    
    assert str(window.penaltyUnitsLabel.text()) == "MWh"
    assert str(window.toleranceUnitsLabel.text()) == "MWh"
    
    window.costVarBox.setCurrentIndex(2)
    
    assert str(window.penaltyUnitsLabel.text()) == ""
    assert str(window.toleranceUnitsLabel.text()) == ""


@pytest.mark.parametrize("toggles, expected", [(1, True), (2, False)])
def test_AdvancedPositionWidget_update_maximise(qtbot,
                                                tmp_path,
                                                hydro_shell,
                                                toggles,
                                                expected):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    for _ in range(toggles): window.costVarCheckBox.toggle()
    assert window.get_configuration()["maximise"] is expected


def test_AdvancedPositionWidget_update_max_simulations(qtbot,
                                                       tmp_path,
                                                       hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    window.abortXSpinBox.setValue(1)
    assert window.get_configuration()["max_simulations"] == 1
    
    window.abortXSpinBox.setValue(0)
    assert window.get_configuration()["max_simulations"] is None


def test_AdvancedPositionWidget_update_max_time(qtbot,
                                                tmp_path,
                                                hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    window.abortTimeSpinBox.setValue(1)
    assert window.get_configuration()["timeout"] == 1
    
    window.abortTimeSpinBox.setValue(0)
    assert window.get_configuration()["timeout"] is None


def test_AdvancedPositionWidget_update_min_noise_auto(qtbot,
                                                      tmp_path,
                                                      hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    window.maxNoiseSpinBox.setMinimum(4)
    window.minNoiseCheckBox.setChecked(False)
    window.minNoiseCheckBox.toggle()
    
    assert window.get_configuration()["min_evals"] is None
    assert not window.minNoiseSpinBox.isEnabled()
    assert window.maxNoiseSpinBox.minimum() == 1
    
    window.minNoiseCheckBox.toggle()
    
    assert window.get_configuration()["min_evals"] == window._default_popsize
    assert window.minNoiseSpinBox.isEnabled()


def test_AdvancedPositionWidget_update_population_auto(qtbot,
                                                       tmp_path,
                                                       hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    window.populationCheckBox.setChecked(False)
    window.populationCheckBox.toggle()
    
    assert window.get_configuration()["popsize"] is None
    assert not window.populationSpinBox.isEnabled()
    
    window.populationCheckBox.toggle()
    
    assert window.get_configuration()["popsize"] == window._default_popsize
    assert window.populationSpinBox.isEnabled()


def test_AdvancedPositionWidget_update_max_resamples_algorithm(qtbot,
                                                               tmp_path,
                                                               hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    window.maxResamplesComboBox.setCurrentIndex(0)
    
    assert isinstance(window.get_configuration()["max_resample_factor"], int)
    
    window.maxResamplesComboBox.setCurrentIndex(1)
    
    assert "auto" in window.get_configuration()["max_resample_factor"]


def test_AdvancedPositionWidget_update_max_resamples(qtbot,
                                                     tmp_path,
                                                     hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    value = 5
    window.maxResamplesComboBox.setCurrentIndex(0)
    window.maxResamplesSpinBox.setValue(value)
    
    assert window.get_configuration()["max_resample_factor"] == value
    
    value = 6
    window.maxResamplesComboBox.setCurrentIndex(1)
    window.maxResamplesSpinBox.setValue(value)
    
    auto_value = "auto{}".format(value)
    assert window.get_configuration()["max_resample_factor"] == auto_value


def test_AdvancedPositionWidget_fixed_combo_slot_uncheck(qtbot,
                                                         tmp_path,
                                                         hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    delta_row = window._param_boxes["delta_row"]
    delta_row["fixed.check"].toggle()
    
    def range_group_disabled():
        assert not delta_row["range.group"].isEnabled()
    
    qtbot.waitUntil(range_group_disabled)
    
    assert window._config["parameters"]["delta_row"] == {"fixed": 0.0}


def test_AdvancedPositionWidget_fixed_combo_slot_check(qtbot,
                                                       tmp_path,
                                                       hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    delta_row = window._param_boxes["delta_row"]
    delta_row["fixed.check"].toggle()
    
    def range_group_disabled():
        assert not delta_row["range.group"].isEnabled()
    
    qtbot.waitUntil(range_group_disabled)
    
    delta_row["fixed.check"].toggle()
    
    def range_group_enabled():
        assert delta_row["range.group"].isEnabled()
    
    qtbot.waitUntil(range_group_enabled)
    
    assert window._config["parameters"]["delta_row"].keys() == ["range"]


def test_AdvancedPositionWidget_fixed_value_slot(qtbot,
                                                 tmp_path,
                                                 hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    delta_row = window._param_boxes["delta_row"]
    delta_row["fixed.check"].toggle()
    
    def range_group_disabled():
        assert not delta_row["range.group"].isEnabled()
    
    qtbot.waitUntil(range_group_disabled)
    
    delta_row["fixed.box"].setValue(1)
    
    assert window._config["parameters"]["delta_row"] == {"fixed": 1.0}


def test_AdvancedPositionWidget_range_type_slot_multiplier(qtbot,
                                                           tmp_path,
                                                           hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    delta_row = window._param_boxes["delta_row"]
    delta_row["range.box.type"].setCurrentIndex(1)
    
    def range_box_var_enabled(): assert delta_row["range.box.var"].isEnabled()
    
    qtbot.waitUntil(range_box_var_enabled)
    
    assert window._config[
                "parameters"]["delta_row"]["range"]["type"] == "multiplier"


def test_AdvancedPositionWidget_range_type_slot_fixed(qtbot,
                                                      tmp_path,
                                                      hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    delta_row = window._param_boxes["delta_row"]
    delta_row["range.box.type"].setCurrentIndex(1)
    
    def range_box_var_enabled(): assert delta_row["range.box.var"].isEnabled()
    
    qtbot.waitUntil(range_box_var_enabled)
    
    delta_row["range.box.type"].setCurrentIndex(0)
    
    def range_box_var_disabled():
        assert not delta_row["range.box.var"].isEnabled()
    
    qtbot.waitUntil(range_box_var_disabled)
    
    assert window._config[
                "parameters"]["delta_row"]["range"]["type"] == "fixed"


def test_AdvancedPositionWidget_generic_range_slot(qtbot,
                                                   tmp_path,
                                                   hydro_shell):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.workDirLineEdit.insert(str(tmp_path))
    window.workDirLineEdit.returnPressed.emit()
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    delta_row = window._param_boxes["delta_row"]
    delta_row["range.box.max"].setValue(2)
    
    assert window._config["parameters"]["delta_row"]["range"]["max"] == 2


@pytest.fixture
def results_df():
    
    data = {'project.annual_energy': {0L: 28023.48059,
                                      1L: 26643.27071,
                                      2L: 26778.45299,
                                      3L: 27814.33542,
                                      4L: 26757.21522,
                                      5L: 27764.08384,
                                      6L: 26550.5673,
                                      7L: 26514.06173,
                                      8L: 26643.27087,
                                      9L: 28023.47982,
                                      10L: 27239.98945,
                                      11L: 26806.925209999998,
                                      12L: 27015.241060000004,
                                      13L: 26902.301689999997,
                                      14L: 27703.89522,
                                      15L: 27592.686130000002,
                                      16L: 27135.776339999997,
                                      17L: 26920.497939999997,
                                      18L: 26806.92582,
                                      19L: 27239.98869},
            'project.q_factor': {0L: 0.643158496,
                                 1L: 0.623552046,
                                 2L: 0.619544776,
                                 3L: 0.638151372,
                                 4L: 0.627739436,
                                 5L: 0.639574664,
                                 6L: 0.621381745,
                                 7L: 0.6219333429999999,
                                 8L: 0.623552048,
                                 9L: 0.643158482,
                                 10L: 0.628048709,
                                 11L: 0.621347485,
                                 12L: 0.624239722,
                                 13L: 0.624158242,
                                 14L: 0.6397536,
                                 15L: 0.635736073,
                                 16L: 0.626756041,
                                 17L: 0.624501289,
                                 18L: 0.6213474929999999,
                                 19L: 0.6280486999999999},
            'delta_col': {0L: 64.52022757,
                          1L: 76.45367283,
                          2L: 71.15118317,
                          3L: 59.4973027,
                          4L: 71.77538159,
                          5L: 20.852555300000002,
                          6L: 68.28236751,
                          7L: 68.20489517,
                          8L: 76.45367694,
                          9L: 64.52023109,
                          10L: 68.2075193,
                          11L: 74.75166956,
                          12L: 62.97270795,
                          13L: 67.20068782,
                          14L: 59.94350211,
                          15L: 65.31181504,
                          16L: 69.15202565,
                          17L: 72.23155823,
                          18L: 74.75166870000001,
                          19L: 68.20752592},
            'grid_orientation': {0L: 44.40745668,
                                 1L: 33.37571009,
                                 2L: 31.08369837,
                                 3L: 44.20467039,
                                 4L: 37.60163529,
                                 5L: 314.2614026,
                                 6L: 33.60661513,
                                 7L: 35.39741359,
                                 8L: 33.37571142,
                                 9L: 44.40745683,
                                 10L: 23.73700194,
                                 11L: 27.35090955,
                                 12L: 24.72097026,
                                 13L: 37.02701777,
                                 14L: 44.06050874,
                                 15L: 43.03812177,
                                 16L: 38.92446379,
                                 17L: 35.23278284,
                                 18L: 27.35090645,
                                 19L: 23.73699979},
            'n_nodes': {0L: 1L,
                        1L: 3L,
                        2L: 3L,
                        3L: 4L,
                        4L: 5L,
                        5L: 6L,
                        6L: 7L,
                        7L: 8L,
                        8L: 9L,
                        9L: 10L,
                        10L: 11L,
                        11L: 12L,
                        12L: 13L,
                        13L: 1L,
                        14L: 2L,
                        15L: 3L,
                        16L: 4L,
                        17L: 5L,
                        18L: 6L,
                        19L: 7L},
            'n_evals': {0L: 1L,
                        1L: 1L,
                        2L: 1L,
                        3L: 1L,
                        4L: 1L,
                        5L: 1L,
                        6L: 1L,
                        7L: 1L,
                        8L: 1L,
                        9L: 1L,
                        10L: 1L,
                        11L: 1L,
                        12L: 1L,
                        13L: 1L,
                        14L: 1L,
                        15L: 1L,
                        16L: 1L,
                        17L: 1L,
                        18L: 1L,
                        19L: 1L},
            'project.number_of_devices': {0L: 13L,
                                          1L: 13L,
                                          2L: 13L,
                                          3L: 13L,
                                          4L: 13L,
                                          5L: 13L,
                                          6L: 13L,
                                          7L: 13L,
                                          8L: 13L,
                                          9L: 13L,
                                          10L: 13L,
                                          11L: 13L,
                                          12L: 13L,
                                          13L: 13L,
                                          14L: 13L,
                                          15L: 13L,
                                          16L: 13L,
                                          17L: 13L,
                                          18L: 13L,
                                          19L: 13L},
            'delta_row': {0L: 22.92577303,
                          1L: 20.88411836,
                          2L: 20.69190282,
                          3L: 20.42196081,
                          4L: 20.18076208,
                          5L: 65.57126996,
                          6L: 20.17591929,
                          7L: 22.60274014,
                          8L: 20.88411952,
                          9L: 22.92576718,
                                10L: 20.30129026,
                                11L: 21.357913,
                                12L: 22.49606414,
                                13L: 22.13374607,
                                14L: 20.74594427,
                                15L: 22.47424913,
                                16L: 22.21391043,
                                17L: 20.21319696,
                                18L: 21.35790763,
                                19L: 20.301297299999998},
            'sim_number': {0L: 1L,
                           1L: 2L,
                           2L: 3L,
                           3L: 4L,
                           4L: 5L,
                           5L: 8L,
                           6L: 10L,
                           7L: 11L,
                           8L: 12L,
                           9L: 13L,
                           10L: 14L,
                           11L: 15L,
                           12L: 16L,
                           13L: 18L,
                           14L: 20L,
                           15L: 21L,
                           16L: 22L,
                           17L: 23L,
                           18L: 24L,
                           19L: 25L},
            't1': {0L: 0.5825523539999999,
                   1L: 0.335333514,
                   2L: 0.649960257,
                   3L: 0.598152204,
                   4L: 0.358674858,
                   5L: 0.11531966099999999,
                   6L: 0.7516376490000001,
                   7L: 0.626618264,
                   8L: 0.335333535,
                   9L: 0.582552348,
                   10L: 0.639915098,
                   11L: 0.44859446299999994,
                   12L: 0.440489291,
                   13L: 0.68587213,
                   14L: 0.599689381,
                   15L: 0.685054472,
                   16L: 0.879525573,
                   17L: 0.521208095,
                   18L: 0.448594492,
                   19L: 0.639915119},
            't2': {0L: 0.837202551,
                   1L: 0.852131616,
                   2L: 0.065172178,
                   3L: 0.201124935,
                   4L: 0.948168792,
                   5L: 0.23561065399999997,
                   6L: 0.222081996,
                   7L: 0.20230825100000002,
                   8L: 0.8521316290000001,
                   9L: 0.8372025470000001,
                   10L: 0.8775905009999999,
                   11L: 0.859587812,
                   12L: 0.778496615,
                   13L: 0.8157775970000001,
                   14L: 0.743709152,
                   15L: 0.79916979,
                   16L: 0.76798122,
                   17L: 0.843732638,
                   18L: 0.8595878240000001,
                   19L: 0.8775905190000001}}
    table_cols = ["sim_number",
                  'project.annual_energy',
                  "grid_orientation",
                  "delta_row",
                  "delta_col",
                  "n_nodes",
                  "t1",
                  "t2",
                  "n_evals",
                  'project.number_of_devices']
    
    return pd.DataFrame(data, columns=table_cols)


@pytest.fixture
def window_results(mocker,
                   qtbot,
                   tmp_path,
                   hydro_shell,
                   config,
                   results_df):
    
    from dtocean_app.strategies.position import GUIAdvancedPosition
    
    status_str = "Project ready"
    status_code = 1
    mocker.patch.object(GUIAdvancedPosition,
                        "get_project_status",
                        return_value=(status_str, status_code))
    
    status_str = "Configuration complete"
    status_code = 1
    mocker.patch.object(GUIAdvancedPosition,
                        "get_config_status",
                        return_value=(status_str, status_code))
    
    status_str = "Worker directory contains files"
    status_code = 0
    mocker.patch.object(GUIAdvancedPosition,
                        "get_worker_directory_status",
                        return_value=(status_str, status_code))
    
    status_str = "Optimisation complete"
    status_code = 1
    mocker.patch.object(GUIAdvancedPosition,
                        "get_optimiser_status",
                        return_value=(status_str, status_code))
    
    config['worker_dir'] = str(tmp_path)
    config['clean_existing_dir'] = True
    side_effect = lambda *args: deepcopy(config)
    mocker.patch.object(GUIAdvancedPosition,
                        "load_config",
                        side_effect=side_effect)
    
    mocker.patch.object(GUIAdvancedPosition,
                        "get_all_results",
                        return_value=results_df)
    
    window = AdvancedPositionWidget(None, hydro_shell, config)
    window.show()
    qtbot.addWidget(window)
    
    yield window
    
    def no_load_sims_thread():
        assert window._load_sims_thread is None
    
    qtbot.waitUntil(no_load_sims_thread)


def test_AdvancedPositionWidget_results_open(window_results):
    assert window_results.tabWidget.isTabEnabled(3)
    assert window_results.tabWidget.isTabEnabled(4)


def test_AdvancedPositionWidget_update_delete_sims(qtbot, window_results):
    
    qtbot.mouseClick(window_results.deleteSimsBox, QtCore.Qt.LeftButton)
    
    assert not window_results._delete_sims
    assert not window_results.protectDefaultBox.isEnabled()
    
    qtbot.mouseClick(window_results.deleteSimsBox, QtCore.Qt.LeftButton)
    
    assert window_results._delete_sims
    assert window_results.protectDefaultBox.isEnabled()


def test_AdvancedPositionWidget_update_protect_default(qtbot, window_results):
    
    qtbot.mouseClick(window_results.protectDefaultBox, QtCore.Qt.LeftButton)
    
    assert not window_results._protect_default
    
    qtbot.mouseClick(window_results.protectDefaultBox, QtCore.Qt.LeftButton)
    
    assert window_results._protect_default


@pytest.mark.parametrize("button, expected", [
                        ("bestSimButton", [1]),
                        ("worstSimButton", [11]),
                        ("top5SimButton", [1, 13, 4, 8, 20]),
                        ("bottom5SimButton", [11, 10, 2, 12, 5])])
def test_AdvancedPositionWidget_select_sims_to_load(qtbot,
                                                    window_results,
                                                    button,
                                                    expected):
    
    window_results.tabWidget.setCurrentIndex(3)
    
    button = getattr(window_results, button)
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)
    
    assert window_results._sims_to_load == expected
    assert not window_results.simsLabel.isEnabled()
    assert not window_results.simSelectEdit.isEnabled()
    assert not window_results.simHelpLabel.isEnabled()
    assert window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_select_sims_to_load_custom(qtbot,
                                                           window_results):
    
    window_results.tabWidget.setCurrentIndex(3)
    
    button = getattr(window_results, "customSimButton")
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)
    
    assert window_results._sims_to_load is None
    assert window_results.simsLabel.isEnabled()
    assert window_results.simSelectEdit.isEnabled()
    assert window_results.simHelpLabel.isEnabled()
    assert not window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_update_custom_sims(qtbot,
                                                   window_results):
    
    window_results.tabWidget.setCurrentIndex(3)
    
    button = getattr(window_results, "customSimButton")
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)
    
    expected = [1, 2, 3, 4]
    expected_str = ", ".join([str(x) for x in expected])
    window_results.simSelectEdit.insert(expected_str)
    window_results.simSelectEdit.returnPressed.emit()
    
    assert window_results._sims_to_load == expected
    assert window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_update_custom_sims_bad(qtbot,
                                                       window_results):
    
    window_results.tabWidget.setCurrentIndex(3)
    
    button = getattr(window_results, "customSimButton")
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)
    
    window_results.simSelectEdit.insert("1, two, 3")
    window_results.simSelectEdit.returnPressed.emit()
    
    assert window_results._sims_to_load is None
    assert not window_results.simLoadButton.isEnabled()


def test_AdvancedPositionWidget_load_sims(qtbot,
                                          mocker,
                                          window_results):
    
    strategy = window_results._shell.strategy = mocker.MagicMock()
    sleep = lambda *args: time.sleep(0.5)
    strategy.load_simulation_ids.side_effect = sleep
    
    # Need to assert that the progress bar was shown
    spy = mocker.spy(window_results, "_progress")
    
    window_results.tabWidget.setCurrentIndex(3)
    
    button = getattr(window_results, "bestSimButton")
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window_results.simLoadButton, QtCore.Qt.LeftButton)
    
    def progress_closed(): assert spy.close.call_count == 1
    qtbot.waitUntil(progress_closed, timeout=1500)
    
    assert spy.show.call_count == 1
    assert spy.close.call_count == 1


def test_AdvancedPositionWidget_export_data_table(mocker,
                                                  qtbot,
                                                  tmp_path,
                                                  window_results):
    
    f = tmp_path / "mock.csv"
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=str(f))
    
    window_results.tabWidget.setCurrentIndex(3)
    qtbot.mouseClick(window_results.dataExportButton, QtCore.Qt.LeftButton)
    
    assert f.is_file()


def test_AdvancedPositionWidget_set_plot(qtbot, window_results):
    
    window_results.tabWidget.setCurrentIndex(4)
    
    window_results.xAxisVarBox.setCurrentIndex(4)
    window_results.yAxisVarBox.setCurrentIndex(2)
    window_results.colorAxisVarBox.setCurrentIndex(6)
    window_results.filterVarBox.setCurrentIndex(5)
    
    window_results.xAxisMinBox.setChecked(True)
    window_results.xAxisMinSpinBox.setValue(20.5)
    window_results.xAxisMaxBox.setChecked(True)
    window_results.xAxisMaxSpinBox.setValue(22.5)
    
    window_results.yAxisMinBox.setChecked(True)
    window_results.yAxisMinSpinBox.setValue(26800)
    window_results.yAxisMaxBox.setChecked(True)
    window_results.yAxisMaxSpinBox.setValue(27600)
    
    min_value = 3
    max_value = 10
    window_results.colorAxisMinBox.setChecked(True)
    window_results.colorAxisMinSpinBox.setValue(min_value)
    window_results.colorAxisMaxBox.setChecked(True)
    window_results.colorAxisMaxSpinBox.setValue(max_value)
    
    window_results.filterVarMinBox.setChecked(True)
    window_results.filterVarMinSpinBox.setValue(65)
    window_results.filterVarMaxBox.setChecked(True)
    window_results.filterVarMaxSpinBox.setValue(70)
    
    qtbot.mouseClick(window_results.plotButton, QtCore.Qt.LeftButton)
    
    assert window_results.plotExportButton.isEnabled()
    
    xlim = window_results.plotWidget.figure.axes[0].get_xlim()
    ylim = window_results.plotWidget.figure.axes[0].get_ylim()
    
    assert xlim == (20.5, 22.5)
    assert ylim == (26800.0, 27600.0)
    
    cb_yaxis = window_results.plotWidget.figure.axes[1].get_children()[8]
    cb_ticks = cb_yaxis.get_ticklabels()
    
    assert int(cb_ticks[0].get_text()) == min_value
    assert int(cb_ticks[-1].get_text()) == max_value
    
    window_results.colorAxisMinBox.setChecked(False)
    qtbot.mouseClick(window_results.plotButton, QtCore.Qt.LeftButton)
    
    cb_yaxis = window_results.plotWidget.figure.axes[1].get_children()[8]
    cb_ticks = cb_yaxis.get_ticklabels()
    
    assert int(cb_ticks[0].get_text()) != min_value
    assert int(cb_ticks[-1].get_text()) == max_value
    
    window_results.colorAxisMinBox.setChecked(True)
    window_results.colorAxisMaxBox.setChecked(False)
    qtbot.mouseClick(window_results.plotButton, QtCore.Qt.LeftButton)
    
    cb_yaxis = window_results.plotWidget.figure.axes[1].get_children()[8]
    cb_ticks = cb_yaxis.get_ticklabels()
    
    assert int(cb_ticks[0].get_text()) == min_value
    assert int(cb_ticks[-1].get_text()) != max_value
    
    window_results.colorAxisMinBox.setChecked(True)
    window_results.colorAxisMinSpinBox.setValue(5)
    window_results.colorAxisMaxBox.setChecked(True)
    window_results.colorAxisMaxSpinBox.setValue(5)
    
    qtbot.mouseClick(window_results.plotButton, QtCore.Qt.LeftButton)
    
    assert len(window_results.plotWidget.figure.axes) == 1


def test_AdvancedPositionWidget_export_plot(mocker,
                                            qtbot,
                                            tmp_path,
                                            window_results):
    
    f = tmp_path / "mock.png"
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=str(f))
    
    window_results.tabWidget.setCurrentIndex(4)
    
    window_results.xAxisVarBox.setCurrentIndex(4)
    window_results.yAxisVarBox.setCurrentIndex(2)
    window_results.colorAxisVarBox.setCurrentIndex(6)
    window_results.filterVarBox.setCurrentIndex(5)
    
    qtbot.mouseClick(window_results.plotButton, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window_results.customSizeBox, QtCore.Qt.LeftButton)
    
    window_results.customWidthSpinBox.setValue(6)
    window_results.customHeightSpinBox.setValue(3)
    
    f = tmp_path / "mock1.png"
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=str(f))
    
    qtbot.mouseClick(window_results.plotExportButton, QtCore.Qt.LeftButton)
    
    assert f.is_file()
    
    im = Image.open(str(f))
    width, height = im.size
    
    expected_width = 981
    expected_height = 624
    
    assert width == expected_width
    assert height == expected_height
    
    f = tmp_path / "mock2.png"
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=str(f))
    
    qtbot.mouseClick(window_results.customSizeBox, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window_results.plotExportButton, QtCore.Qt.LeftButton)
    
    assert f.is_file()
    
    im = Image.open(str(f))
    width, height = im.size
    
    assert width != expected_width
    assert height != expected_height


def test_AdvancedPositionWidget_import_yaml(mocker, qtbot, mock_shell):
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value="mock")
    
    window = AdvancedPositionWidget(None, mock_shell, {})
    mock = window._shell.strategy = mocker.MagicMock()
    
    window.show()
    qtbot.addWidget(window)
    window.tabWidget.setCurrentIndex(5)
    qtbot.mouseClick(window.importYAMLButton, QtCore.Qt.LeftButton)
    
    assert mock.import_simulation_file.call_args.args[-1] == "mock"


@pytest.mark.parametrize("article, etype", [
                                    ("A", KeyError),
                                    ("An", IOError)])
def test_AdvancedPositionWidget_display_error(mocker,
                                              qtbot,
                                              mock_shell,
                                              article,
                                              etype):
    
    mock = mocker.patch.object(QtGui.QMessageBox,
                               'critical')
    
    window = AdvancedPositionWidget(None, mock_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    evalue = etype('mock')
    _, _, etraceback = sys.exc_info()
    window._display_error(etype, evalue, etraceback)
    
    expected_msg = "{} {} occurred: {}".format(article, etype.__name__, evalue)
    assert mock.call_args.args[1] == 'ERROR'
    assert mock.call_args.args[2] == expected_msg


def test_AdvancedPositionWidget_set_configuration(mocker,
                                                  qtbot,
                                                  hydro_shell,
                                                  config):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    window.show()
    qtbot.addWidget(window)
    
    window.set_configuration(config)
    
    def settings_tab_enabled(): assert window.tabWidget.isTabEnabled(1)
    
    qtbot.waitUntil(settings_tab_enabled)
    
    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)


def test_AdvancedPositionWidget_set_configuration_has_stored(mocker,
                                                             qtbot,
                                                             hydro_shell,
                                                             config,
                                                             config_alt):
    
    window = AdvancedPositionWidget(None, hydro_shell, {})
    mock = window._shell.strategy = mocker.MagicMock()
    config['clean_existing_dir'] = None
    mock._config = config
    
    window.show()
    qtbot.addWidget(window)
    
    window.set_configuration(config_alt)
    
    assert window.tabWidget.isTabEnabled(1)
    assert window.tabWidget.isTabEnabled(2)


def test_AdvancedPositionWidget_optimiser_restart(mocker,
                                                  qtbot,
                                                  tmp_path,
                                                  hydro_shell,
                                                  config,
                                                  results_df):
    
    from dtocean_app.strategies.position import GUIAdvancedPosition
    
    status_str = "Project ready"
    status_code = 1
    mocker.patch.object(GUIAdvancedPosition,
                        "get_project_status",
                        return_value=(status_str, status_code))
    
    status_str = "Configuration complete"
    status_code = 1
    mocker.patch.object(GUIAdvancedPosition,
                        "get_config_status",
                        return_value=(status_str, status_code))
    
    status_str = "Worker directory contains files"
    status_code = 0
    mocker.patch.object(GUIAdvancedPosition,
                        "get_worker_directory_status",
                        return_value=(status_str, status_code))
    
    status_str = "Optimisation incomplete (restart may be possible)"
    status_code = 2
    mocker.patch.object(GUIAdvancedPosition,
                        "get_optimiser_status",
                        return_value=(status_str, status_code))
    
    config['worker_dir'] = str(tmp_path)
    config['clean_existing_dir'] = True
    side_effect = lambda *args: deepcopy(config)
    mocker.patch.object(GUIAdvancedPosition,
                        "load_config",
                        side_effect=side_effect)
    
    mocker.patch.object(GUIAdvancedPosition,
                        "get_all_results",
                        return_value=results_df)
    
    window = AdvancedPositionWidget(None, hydro_shell, config)
    window.show()
    qtbot.addWidget(window)
    
    assert not window.tabWidget.isTabEnabled(3)
    assert not window.tabWidget.isTabEnabled(4)
