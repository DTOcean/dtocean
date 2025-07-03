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


import pytest
from dtocean_core.menu import ModuleMenu, ProjectMenu
from dtocean_core.pipeline import Tree
from PySide6 import QtCore

from dtocean_app.core import GUICore
from dtocean_app.extensions import GUIStrategyManager
from dtocean_app.shell import Shell
from dtocean_app.widgets.dialogs import Message
from dtocean_plugins.modules.base import ModuleInterface
from dtocean_plugins.strategies.base import Strategy
from dtocean_plugins.strategy_guis.base import GUIStrategy, StrategyWidget


class MockModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Module"

    @classmethod
    def declare_weight(cls):
        return 998

    @classmethod
    def declare_inputs(cls):
        input_list = [
            "device.turbine_performance",
            "device.cut_in_velocity",
            "device.system_type",
        ]

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
        id_map = {
            "dummy1": "device.turbine_performance",
            "dummy2": "device.cut_in_velocity",
            "dummy3": "device.system_type",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        return


class MockWidget(Message, StrategyWidget):
    config_set = QtCore.Signal()
    config_null = QtCore.Signal()
    reset = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent, "Mock")

    def get_configuration(self):
        return {}

    def set_configuration(self, *args):
        pass

    def paintEvent(self, event):
        super(MockWidget, self).paintEvent(event)
        self.config_set.emit()


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
        widget = MockWidget(parent)
        return widget

    def get_weight(self):
        return -1


@pytest.fixture
def core(mocker):
    mocker.patch(
        "dtocean_core.extensions.StrategyManager._discover_classes",
        return_value={"MockStrategy": MockStrategy},
        autospec=True,
    )

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

    options_branch = var_tree.get_branch(core, project, "System Type Selection")
    device_type = options_branch.get_input_variable(
        core,
        project,
        "device.system_type",
    )
    assert device_type is not None

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
    for idx in range(window.listWidget.count()):
        item = window.listWidget.item(idx)
        rect = window.listWidget.visualItemRect(item)
        qtbot.mouseClick(
            window.listWidget.viewport(),
            QtCore.Qt.MouseButton.LeftButton,
            pos=rect.center(),
        )

        def widget_changed():
            assert id(window.mainWidget) != widget_id

        qtbot.waitUntil(widget_changed)
        widget_id = id(window.mainWidget)


def test_GUIStrategyManager_load_strategy(qtbot, mock_shell):
    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)

    mock_strategy = MockStrategy()
    window._load_strategy(mock_strategy)

    assert str(window.topDynamicLabel.text()) == "Mock Strategy"


def test_GUIStrategyManager_load_strategy_unavailable(
    mocker,
    qtbot,
    mock_shell,
):
    mock_strategy = MockStrategy()
    mocker.patch.object(
        mock_strategy,
        "allow_run",
        return_value=False,
        autospec=True,
    )

    window = GUIStrategyManager(mock_shell)
    window.show()
    qtbot.addWidget(window)

    window._load_strategy(mock_strategy)

    assert str(window.topDynamicLabel.text()) == "Mock Strategy (unavailable)"


def test_GUIStrategyManager_configure_strategy(mocker, qtbot, mock_shell):
    mock_strategy = MockStrategy()
    window = GUIStrategyManager(mock_shell)
    window._load_strategy(mock_strategy)
    mocker.patch.object(
        window,
        "get_strategy",
        return_value=mock_strategy,
        autospec=True,
    )

    window.show()
    qtbot.addWidget(window)

    window._configure_strategy()

    assert str(window.topDynamicLabel.text()) == "Mock Strategy"


def test_GUIStrategyManager_configure_strategy_unavailable(
    mocker,
    qtbot,
    mock_shell,
):
    mock_strategy = MockStrategy()
    mocker.patch.object(
        mock_strategy,
        "allow_run",
        return_value=False,
        autospec=True,
    )

    window = GUIStrategyManager(mock_shell)
    window._load_strategy(mock_strategy)
    mocker.patch.object(
        window,
        "get_strategy",
        return_value=mock_strategy,
        autospec=True,
    )

    window.show()
    qtbot.addWidget(window)

    window._configure_strategy()

    assert str(window.topDynamicLabel.text()) == "Mock Strategy (unavailable)"
