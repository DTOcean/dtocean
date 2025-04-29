# -*- coding: utf-8 -*-

#    Copyright (C) 2022 Mathew Topper
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

# pylint: disable=redefined-outer-name,protected-access,no-self-use,unused-argument

import pytest
from PyQt4 import QtCore

from dtocean_app.core import GUICore
from dtocean_app.extensions import GUIStrategyManager
from dtocean_app.main import Shell
from dtocean_app.strategies import GUIStrategy
from dtocean_app.strategies.basic import BasicWidget
from dtocean_core.interfaces import ModuleInterface
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree
from dtocean_core.strategies import Strategy



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
        return


class MockStrategy(GUIStrategy, Strategy):
    
    @classmethod
    def get_name(cls):
        return "Mock Strategy"
    
    def configure(self):
        return None
        
    def get_variables(self):
        return None
        
    def execute(self, core, project):
        return
    
    def allow_run(self, core, project):
        return True
    
    def get_widget(self, parent, shell):
        widget = BasicWidget(parent, "Mock")
        return widget
    
    def get_weight(self):
        return -1



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


def test_GUIStrategyManager_init(qtbot, mock_shell):
    
    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)
    
    assert str(window.topDynamicLabel.text()) == "None"


def test_strategy_select(qtbot, mock_shell):
    
    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)
    
    widget_id = id(window.mainWidget)
    
    # Click on all strategies
    for idx in xrange(window.listWidget.count()): # pylint: disable=undefined-variable
        
        item = window.listWidget.item(idx)
        rect = window.listWidget.visualItemRect(item)
        qtbot.mouseClick(window.listWidget.viewport(),
                         QtCore.Qt.LeftButton,
                         pos=rect.center())
        
        def widget_changed():
            assert id(window.mainWidget) != widget_id
        
        qtbot.waitUntil(widget_changed)
        
        widget_id = id(window.mainWidget)


@pytest.fixture
def strategy_basic(mocker, qtbot, mock_shell):
    
    mocker.patch.object(GUIStrategyManager,
                        'get_available',
                        return_value=["Basic"],
                        autospec=True)
    
    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)
    
    if "Basic" not in window._plugin_names.keys():
        pytest.skip("Test requires Basic strategy")
    
    # Click on first strategy and apply
    item = window.listWidget.item(0)
    rect = window.listWidget.visualItemRect(item)
    qtbot.mouseClick(window.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    def apply_enabled():
        assert window.applyButton.isEnabled()
        
    qtbot.waitUntil(apply_enabled)
    
    qtbot.mouseClick(window.applyButton,
                     QtCore.Qt.LeftButton)
    
    def strategy_set():
        assert str(window.topDynamicLabel.text()) == str(item.text())
    
    qtbot.waitUntil(strategy_set)
    
    return window


def test_strategy_basic_apply(strategy_basic):
    assert str(strategy_basic.topDynamicLabel.text()) == "Basic"


def test_strategy_basic_reset(qtbot, strategy_basic):
    
    # Reset the strategy
    qtbot.mouseClick(
            strategy_basic.resetButton,
            QtCore.Qt.LeftButton)
    
    assert str(strategy_basic.topDynamicLabel.text()) == "None"


@pytest.fixture
def strategy_sensitivity(mocker, qtbot, mock_shell):
    
    mocker.patch.object(GUIStrategyManager,
                        'get_available',
                        return_value=["Unit Sensitivity"],
                        autospec=True)
    
    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)
    
    if "Unit Sensitivity" not in window._plugin_names.keys():
        pytest.skip("Test requires Unit Sensitivity strategy")
    
    widget_id = id(window.mainWidget)
    
    # Click on first strategy and apply
    item = window.listWidget.item(0)
    rect = window.listWidget.visualItemRect(item)
    qtbot.mouseClick(window.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    def widget_changed():
        assert id(window.mainWidget) != widget_id
    
    qtbot.waitUntil(widget_changed)
    
    return window


def test_strategy_sensitivity_apply_null(strategy_sensitivity):
    assert not strategy_sensitivity.applyButton.isEnabled()


@pytest.fixture
def strategy_sensitivity_variable(qtbot, strategy_sensitivity):
    
    sensitivity = strategy_sensitivity.mainWidget
    
    # Select module
    idx = sensitivity.modBox.findText("Mock Module",
                                      QtCore.Qt.MatchFixedString)
    sensitivity.modBox.setCurrentIndex(idx)
    
    def varBox_not_empty():
        assert int(sensitivity.varBox.count()) > 0
        
    qtbot.waitUntil(varBox_not_empty)
    
    # Select variable
    idx = sensitivity.varBox.findText("Tidal Turbine Cut-In Velocity (m/s)",
                                      QtCore.Qt.MatchFixedString)
    sensitivity.varBox.setCurrentIndex(idx)
    
    def lineEdit_enabled():
        assert sensitivity.lineEdit.isEnabled()
        
    qtbot.waitUntil(lineEdit_enabled)
    
    return strategy_sensitivity


def test_strategy_sensitivity_lineEdit_enabled(strategy_sensitivity_variable):
    assert strategy_sensitivity_variable.mainWidget.lineEdit.isEnabled()


def test_strategy_sensitivity_apply(strategy_sensitivity_variable):
    
    line = strategy_sensitivity_variable.mainWidget.lineEdit
    line.setText("1")
    
    assert strategy_sensitivity_variable.applyButton.isEnabled()


def test_strategy_sensitivity_apply_disable(strategy_sensitivity_variable):
    
    line = strategy_sensitivity_variable.mainWidget.lineEdit
    line.setText("1")
    
    assert strategy_sensitivity_variable.applyButton.isEnabled()
    
    line.setText("")
    
    assert not strategy_sensitivity_variable.applyButton.isEnabled()


def test_GUIStrategyManager_load_strategy(mocker, qtbot, mock_shell):
    
    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)
    
    mock_strategy = MockStrategy()
    window._load_strategy(mock_strategy)
    
    assert str(window.topDynamicLabel.text()) == "Mock Strategy"


def test_GUIStrategyManager_load_strategy_unavailable(mocker,
                                                      qtbot,
                                                      mock_shell):
    
    mock_strategy = MockStrategy()
    mocker.patch.object(mock_strategy,
                        'allow_run',
                        return_value=False,
                        autospec=True)
    
    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)
    
    window._load_strategy(mock_strategy)
    
    assert str(window.topDynamicLabel.text()) == "Mock Strategy (unavailable)"


def test_GUIStrategyManager_configure_strategy(mocker, qtbot, mock_shell):
    
    mock_strategy = MockStrategy()
    window = GUIStrategyManager(mock_shell)
    window._load_strategy(mock_strategy)
    mocker.patch.object(window,
                        'get_strategy',
                        return_value=mock_strategy,
                        autospec=True)
    
    window.show()
    qtbot.addWidget(window)
    
    window._configure_strategy()
    
    assert str(window.topDynamicLabel.text()) == "Mock Strategy"


def test_GUIStrategyManager_configure_strategy_unavailable(mocker,
                                                           qtbot,
                                                           mock_shell):
    
    mock_strategy = MockStrategy()
    mocker.patch.object(mock_strategy,
                        'allow_run',
                        return_value=False,
                        autospec=True)
    
    window = GUIStrategyManager(mock_shell)
    window._load_strategy(mock_strategy)
    mocker.patch.object(window,
                        'get_strategy',
                        return_value=mock_strategy,
                        autospec=True)
    
    window.show()
    qtbot.addWidget(window)
    
    window._configure_strategy()
    
    assert str(window.topDynamicLabel.text()) == "Mock Strategy (unavailable)"
